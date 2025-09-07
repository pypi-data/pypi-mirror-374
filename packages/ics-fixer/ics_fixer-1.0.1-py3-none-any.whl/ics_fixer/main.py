import logging
import re
import sys
import uuid
from datetime import UTC, datetime, timedelta
from itertools import dropwhile
from pathlib import Path

import dateparser
import ftfy
import typer
from ftfy import TextFixerConfig
from icalendar import Calendar


def read_ical(filepath: Path) -> str:
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = list(dropwhile(lambda line: line.strip() != "BEGIN:VCALENDAR", f))
            return "".join(lines)
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}")
        raise typer.Exit(code=1)


def fix_calendar(cal):
    cal["METHOD"] = "PUBLISH"

    if cal.get("VERSION") != "2.0":
        cal["VERSION"] = "2.0"
        logging.debug("Set VERSION to 2.0")

    if not cal.get("PRODID"):
        cal["PRODID"] = "collective/icalendar"
        logging.debug("Set a PRODID")


def format_as_utc(dt_obj):
    utc_dt = dt_obj.astimezone(UTC)
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


def get_datetime_from_event(event_field):
    if hasattr(event_field, "dt"):
        dt_obj = event_field.dt
        if isinstance(dt_obj, datetime):
            return dt_obj.replace(second=0, microsecond=0)
        return dt_obj
    try:
        dt_obj = datetime.strptime(event_field, "%Y%m%dT%H%M%SZ")
        return dt_obj.replace(second=0, microsecond=0)
    except ValueError:
        return datetime.strptime(event_field, "%Y%m%d").date()


def fix_dtstamp(event):
    current_utc = format_as_utc(datetime.now(UTC))
    if not event.get("DTSTAMP"):
        event["DTSTAMP"] = current_utc
        logging.debug("Added missing DTSTAMP")


def fix_timestamps(event):
    if not hasattr(event, "errors") or not event.errors:
        return

    current_utc = format_as_utc(datetime.now(UTC))

    timestamp_attributes = {"DTSTART", "DTEND"}

    for prop_name, error_msg in event.errors:
        if prop_name in timestamp_attributes:
            match = re.search(r"got: '([^']*)'", error_msg)
            if match:
                original_value = match.group(1).strip()

                # Try to parse with dateparser
                parsed_dt = dateparser.parse(original_value, settings={"RETURN_AS_TIMEZONE_AWARE": True})

                if parsed_dt is not None:
                    event[prop_name] = format_as_utc(parsed_dt)
                    logging.debug(
                        f"{prop_name} was improperly formatted as {original_value} and parsed as {format_as_utc(parsed_dt)}"
                    )
                else:
                    # Fallback to current UTC time
                    event[prop_name] = current_utc
                    logging.debug(f"{prop_name} was not able to be parsed and was set to {current_utc}")


def fix_dtend(event):
    """Fix DTEND if it equals DTSTART"""
    dtstart = get_datetime_from_event(event["DTSTART"])
    dtend = get_datetime_from_event(event["DTEND"])

    if dtstart == dtend:
        new_dtend = dtstart + timedelta(hours=1) if isinstance(dtstart, datetime) else dtstart + timedelta(days=1)

        event["DTEND"] = format_as_utc(new_dtend)
        logging.debug("Fixed DTEND to be after DTSTART")


def fix_attendee_organizer_fields(event):
    for field_name in ("ATTENDEE", "ORGANIZER"):
        field_value = event.get(field_name)

        if not field_value:
            continue

        items = field_value if isinstance(field_value, list) else [field_value]

        valid_items = []
        for item in items:
            if str(item).startswith("mailto:"):
                valid_items.append(item)
            else:
                logging.debug(f"Removed invalid {field_name}: {item}")

        if valid_items:
            if field_name == "ATTENDEE":
                # Retain all valid attendees
                event[field_name] = valid_items if len(valid_items) > 1 else valid_items[0]
            else:
                # Only keep the first organizer to enforce RFC compliance
                event[field_name] = valid_items[0]
                logging.debug(f"Removed organizers after {valid_items[0]}")
        else:
            del event[field_name]


def fix_status(event):
    if not str(event.get("STATUS")):
        event["STATUS"] = "CONFIRMED"
        logging.debug("Added missing STATUS")


def fix_uid(event):
    if not str(event.get("UID")):
        event["UID"] = str(uuid.uuid4())
        logging.debug("Added missing UID")


def fix_method(event):
    if "METHOD" in event:
        del event["METHOD"]
        logging.debug("Removed METHOD from VEVENT level")


def fix_mojibake(event):
    for field_name in ("DESCRIPTION", "SUMMARY"):
        field_value = str(event.get(field_name))

        if not field_value:
            continue

        config = TextFixerConfig(unescape_html=True, explain=True)
        event[field_name], explanation = ftfy.fix_and_explain(field_value, config=config)
        if explanation:
            explanation_parameters = ",".join([x.parameter for x in explanation])
            logging.debug(f"Mojibake fix action(s) taken on {field_name}: {explanation_parameters}")


def fix_event(event, skip_mojibake_fix: bool):
    fix_dtstamp(event)
    fix_timestamps(event)
    fix_dtend(event)
    fix_attendee_organizer_fields(event)
    fix_status(event)
    fix_uid(event)
    fix_method(event)
    if not skip_mojibake_fix:
        fix_mojibake(event)
    else:
        logging.debug("Skipped mojibake fix.")


def fix_ics_file(cal: Calendar, skip_mojibake_fix: bool):
    fix_calendar(cal)
    # Process each event
    for component in cal.walk():
        if component.name == "VEVENT":
            fix_event(component, skip_mojibake_fix)

    return cal


app = typer.Typer()


@app.command()
def main(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the input ICS file.",
    ),
    output_file: Path | None = typer.Argument(
        None,
        help="Path for the output file. If omitted, the input file is overwritten.",
        resolve_path=True,
    ),
    skip_mojibake_fix: bool = typer.Option(
        False,
        "--skip-mojibake-fix",
        help="Do not run the mojibake (garbled text) fixer.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging."),
):
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if output_file is None:
        output_file = input_file
        logging.warning("Output path not set. Input file will be overwritten.")

    logging.debug(f"Reading calendar data from: {input_file}")
    ics_content = read_ical(input_file)

    try:
        cal = Calendar.from_ical(ics_content)
    except Exception as e:
        logging.error(f"Error parsing ICS file: {e}")
        logging.debug("Traceback:", exc_info=True)
        raise typer.Exit(code=1)

    fixed_cal = fix_ics_file(cal, skip_mojibake_fix)

    try:
        output_file.write_bytes(fixed_cal.to_ical())
        logging.info(f"Successfully fixed calendar and saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write to output file {output_file}: {e}")
        logging.debug("Traceback:", exc_info=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
