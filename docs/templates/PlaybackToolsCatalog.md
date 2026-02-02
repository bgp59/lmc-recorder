# Playback Tools Catalog

- [General Information](#general-information)
  - [Common Command Line Arguments](#common-command-line-arguments)
  - [`INST` v. `RECORD_FILES_DIR`](#inst-v-record_files_dir)
  - [`auto` Output Dir](#auto-output-dir)
  - [Datetime Handling](#datetime-handling)
- [Usage](#usage)

## General Information

The command line toolset for perusing lmcrec files.

### Common Command Line Arguments

```text
  -f FROM_TS, --from-ts FROM_TS
                        Starting timestamp for a query, either in ISO 8601 date
                        spec or -HhMmSs duration. A negative duration stands for
                        time back from --to-ts arg. If not specified then start
                        from the oldest available data. Note that a negative
                        value has to be specified using '=' rather that ' ',
                        (space), e.g. --from-ts=-30m or -f=-30m.
  -t TO_TS, --to-ts TO_TS
                        Ending timestamp for a query, either in ISO 8601 date
                        spec or +HhMmSs duration. A positive duration stands for
                        time after --from-ts arg. If not specified then end at
                        the newest available data.
  -c CONFIG, --config CONFIG
                        Config file used in conjunction with INST to determine
                        record files dir. It defaults to env var $LMCREC_CONFIG,
                        or if the latter is not set, to 'lmcrec-config.yaml'.
  -i INST, --inst INST  lmcrec inst(ance), used to locate the record files dir
                        based on the config. It is mandatory if --record-files-
                        dir is not specified.
  -d RECORD_FILES_DIR, --record-files-dir RECORD_FILES_DIR
                        Use RECORD_FILES_DIR instead of the one inferred using
                        --inst. lmcrec stores record files under date based sub-
                        dirs: RECORD_FILES_DIR/yyyy-mm-dd. The argument value
                        may be either the top dir RECORD_FILES_DIR or a sub-dir
                        RECORD_FILES_DIR/yyyy-mm-dd.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Save the data under OUTPUT_DIR...
```

### `INST` v. `RECORD_FILES_DIR`

When a lmcrec playback tool is used in the same environment where the data was
recorded, spcifying the [instance](Internals.md#instances) via `-i INST`  in
conjunction with the configuration file is the preferred way of locating the
record files location.

However in the context of external party support where the recorded data was
provided by a [lmcrec-report](#lmcrec-report) generated archive, `-d
RECORD_FILES_DIR` is the only option, where `RECORD_FILES_DIR` is the location
post extraction.

### `auto` Output Dir

Many commands can save the output in a file or files. While the name of the
files is predicated by the command, their parent directory can be specified via
`--output-dir` command line argument. The recommended value for it is `auto`
because it allows for self-explanatory locations while avoiding accidental
overwriting.

The output path is formed as follows:
`$LMCREC_RUNTIME/CATEGORY/INST/FIRST_TIMESTAMP--LAST_TIMESTAMP` where:

- `CATEGORY` is specific to the command: `inventory`, `query`, `export`, etc
- `INST` is the lmcrec instance for the command
- `FIRST_TIMESTAMP`, `LAST_TIMESTAMP` the first and last timestamps, in ISO
  8601, found in the recording and matching the time window of the command

e.g. `inventory/lseg2.1.ads/2025-12-11T10:06:01-08:00--2025-12-11T16:32:14-08:00`

### Datetime Handling

All timestamps are displayed in ISO 8601 format `YYYY-MM-DDTHH:MM:SS±HH:MM` and
parsed from the same, optionally without the UTC offset `±HH:MM` (`Z` is also
supported). The conversion uses `LMCREC_TZ` env var, if set, otherwise the local
timezone.

`LMCREC_TZ` is intended for external party support, to make the investigation
easier by matching the time zone of the reporting party only for the scope of
lmcrec playback commands; all other datetime conversions are unaffected.

For instance, if the reporting party is on US West Coast region and if it flags
`09:31` as the time around which the investigation should focus, then the
investigating party should set `LMCREC_TZ=US/Pacific` and then it can use
`2025-12-12T09:31:00` as a command line argument and it will match the reported
timestamp.

## Usage
