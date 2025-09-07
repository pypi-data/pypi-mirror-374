# ics-fixer
This program will fix common issues with ICS files that prevent programs such as Mozilla Thunderbird from parsing them.

```
Usage: ics-fixer [OPTIONS] INPUT_FILE [OUTPUT_FILE]

Arguments:
  INPUT_FILE     Path to the input ICS file.  [required]
  [OUTPUT_FILE]  Path for the output file. If omitted, the input file is
                 overwritten.

Options:
  --skip-mojibake-fix             Do not run the mojibake (garbled text)
                                  fixer.
  --debug                         Enable debug logging.
  --help                          Show this message and exit.
```

## Installation

[uv](https://docs.astral.sh/uv/) is recommended to install the package in a managed environment:

    uv tool install ics-fixer

## Dependencies

* Python >= 3.13
* dateparser
* ftfy
* icalendar
* typer

## Notes

These fields may contain desired data but will be discarded if it is incorrectly formatted:

* Event orgainizer
* Event attendee list

In my use case, this is acceptable as I have only encountered ICS files where malformed `ORGANIZER` or `ATTENDEE` values were useless.

If start or end time is in the wrong format and can't be parsed, the current time at the program's execution will be substituted.

If the start and end time are equal and contain the time, the end time will be shifted one hour, as some programs do not work properly with 0-length events. If the intention is an all-day event, the end time should be 24 hours after the start time.

## Potential Implementations

* Unit tests
* Support for older Python versions
* Timezone shifter for dates incorrectly assumed as UTC
* Force all-day mode for events with same start and end time
* Better fixes for malformed `ORGANIZER` or `ATTENDEE`
  * I would need real world sample data


