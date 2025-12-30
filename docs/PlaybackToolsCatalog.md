# Playback Tools Catalog

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [General Information](#general-information)
  - [Common Command Line Arguments](#common-command-line-arguments)
  - [`INST` v. `RECORD_FILES_DIR`](#inst-v-record_files_dir)
  - [`auto` Output Dir](#auto-output-dir)
  - [Datetime Handling](#datetime-handling)
- [Usage](#usage)
  - [lmcrec-check-consistency](#lmcrec-check-consistency)
  - [lmcrec-check-index](#lmcrec-check-index)
  - [lmcrec-check-response](#lmcrec-check-response)
  - [lmcrec-cleanup](#lmcrec-cleanup)
  - [lmcrec-dump](#lmcrec-dump)
  - [lmcrec-export](#lmcrec-export)
  - [lmcrec-inflate](#lmcrec-inflate)
  - [lmcrec-info](#lmcrec-info)
  - [lmcrec-inventory](#lmcrec-inventory)
  - [lmcrec-merge-schema](#lmcrec-merge-schema)
  - [lmcrec-pb-perf](#lmcrec-pb-perf)
  - [lmcrec-query](#lmcrec-query)
  - [lmcrec-report](#lmcrec-report)
  - [lmcrec-stats](#lmcrec-stats)
  - [lmcrec-version](#lmcrec-version)

<!-- /TOC -->

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

### lmcrec-check-consistency

```text
usage: lmcrec-check-consistency [-h] [-s START_SAMPLE_NUM] [-e END_SAMPLE_NUM]
                                [-T]
                                sample_dir

Check the consistency between a number of sample files captured by
snap-samples.sh and the state cache updated from the record file generated
from those samples. This is an end-to-end sanity check for the recording +
playback tools.

The sample files are sorted in ascending order of their sample# suffix. After
each sample file is loaded, the state cache is updated with the next scan (which
was based on that very file) and the loaded data is compared against the cache.

positional arguments:
  sample_dir

options:
  -h, --help            show this help message and exit
  -s START_SAMPLE_NUM, --start-sample-num START_SAMPLE_NUM
                        Start sample#, default: 1
  -e END_SAMPLE_NUM, --end-sample-num END_SAMPLE_NUM
                        End sample#, if different than last. Use -1 for last,
                        default: -1
  -T, --no-timestamp-check
                        Disable timestamp check. The timestamp is inferred from
                        mtime of the sample files and if the latter were altered
                        by accident then the check is not possible anymore.
```

### lmcrec-check-index

```text
usage: lmcrec-check-index [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                          [-d RECORD_FILES_DIR]
                          [file ...]

Verify index consistency. 

The index file consists of TIMESTAMP,OFFSET pairs and this tool check that by
skipping OFFSET bytes (after decompression) at the beginning of the lmcrec file,
the next record is timestamp with TIMESTAMP value.

positional arguments:
  file                  Specific lmcrec file(s) to test, they override the query
                        style selection.

options:
  -h, --help            show this help message and exit
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
```

### lmcrec-check-response

```text
usage: lmcrec-check-response [-h] [-z] [-m] rest_json_file [rest_json_file ...]

 
Check REST response(s), like for instance those collected by snap-samples.sh,
for internal inconsistencies:
    * Critical, lmcrec will exit upon detecting any the of following:
        * duplicated instances
        * same variables from the same class but with different types
    * Silently ignored:
        * duplicated (within the instance) variables; the last value is the one
          that will populated the state cache during playback.
    * FYI:
        * missing variables from instances with the same class

positional arguments:
  rest_json_file

options:
  -h, --help            show this help message and exit
  -z, --inflate         Assume deflate(d) content even if the file does not end
                        in .gz and no headers file can be found
  -m, --missing-variables
                        Add missing variables from instances that share the same
                        class to the report
```

### lmcrec-cleanup

```text
usage: lmcrec-cleanup [-h] [-c CONFIG] [-n KEEP_N_DAYS_FALLBACK]
                      [-N KEEP_N_DAYS_OVERRIDE]

Cleanup older daily records for all instances in the config file

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file, it defaults to env var $LMCREC_CONFIG, or
                        if the latter is not set, to 'lmcrec-config.yaml'.
  -n KEEP_N_DAYS_FALLBACK, --keep-n-days-fallback KEEP_N_DAYS_FALLBACK
                        If > 0, fallback for the keep_n_days parameter from the
                        config file for each instance.
  -N KEEP_N_DAYS_OVERRIDE, --keep-n-days-override KEEP_N_DAYS_OVERRIDE
                        If > 0, override for the keep_n_days parameter from the
                        config file for each instance.
```

### lmcrec-dump

```text
usage: lmcrec-dump [-h] [-t RECORD_TYPE] file

Dump lmcrec recording, info or index file

positional arguments:
  file                  Recording, info ('.info' suffix) or index ('.index'
                        suffix) file.

options:
  -h, --help            show this help message and exit
  -t RECORD_TYPE, --record-type RECORD_TYPE
                        Comma separated list of record types to dump, valid
                        choices: ['class_info', 'delete_inst_id',
                        'duration_usec', 'eor', 'inst_info', 'scan_tally',
                        'set_inst_id', 'timestamp_usec', 'var_info',
                        'var_value']
```

### lmcrec-export

```text
usage: lmcrec-export [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                     [-d RECORD_FILES_DIR] [-S SCHEMA_FILE] [-X DB_MAPPING_FILE]
                     [-o OUTPUT_DIR] [-z [COMPRESS_LEVEL]] [-v]

Export LMC recorded data into CSV format, potentially for import into a data
base via bulk transfer (e.g. bcp)

The command requires:
    * a DB specific file describing LMC data type -> DB type mapping
    * a LMC schema file generated by lmcrec-inventory command or, better still
      by lmcrec-schema-merge based on individual inventories

options:
  -h, --help            show this help message and exit
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
  -S SCHEMA_FILE, --schema-file SCHEMA_FILE
                        LmcrecSchema file (YAML format) created by inventory or
                        merged from multiple inventory files.
  -X DB_MAPPING_FILE, --db-mapping-file DB_MAPPING_FILE
                        DB specific file (YAML format) to describe name and type
                        mapping and output formatting.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Save the information under OUTPUT_DIR/TABLE directory.
                        The directory will be created as needed. If OUTPUT_DIR
                        is specified as "auto" then it will default to
                        $LMCREC_RUNTIME/export/INST/FIRST_TIMESTAMP--
                        LAST_TIMESTAMP
  -z [COMPRESS_LEVEL], --compress-level [COMPRESS_LEVEL]
                        Indicate that the CSV files will be compressed and
                        optionally set the compression level, if it other than
                        Z_DEFAULT_COMPRESSION=-1.
  -v, --verbose         Display progress information
```

### lmcrec-inflate

```text
usage: lmcrec-inflate [-h] deflate_file [out_file]

Inflate deflate(d) REST response, for instance one captured using:

    curl -H 'Accept-Encoding: deflate' -o OUT_FILE URL

Notes:

    1. It should be used only if the response contains the following header:

        Content-Encoding: deflate
    
    2. gunzip / gzip -d commands cannot be used directly on that file since they
       would fail with:

            gzip: unknown compression format

       error

    3. The JSON body of the response is not formatted (one single very, very
       long line, that is), so is best passed through `jq':

            lmcrec-inflate RESP_FILE | jq

positional arguments:
  deflate_file
  out_file      Output file, if not specified then it defaults to stdout. Since
                the original content is not indented or line separated, it is
                advisable to pipe the output through `jq'

options:
  -h, --help    show this help message and exit
```

### lmcrec-info

```text
usage: lmcrec-info [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                   [-d RECORD_FILES_DIR] [-u]

Display information about the record files.

options:
  -h, --help            show this help message and exit
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
  -u, --display-usec    Display microseconds for timestamps
```

### lmcrec-inventory

```text
usage: lmcrec-inventory [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                        [-d RECORD_FILES_DIR] [-I] [-C] [-V] [-a]
                        [-o OUTPUT_DIR]
                        [lmcrec_file ...]

Given a (list of) record file(s) display the instance and class hierarchy and
the per class variable inventory.

IMPORTANT! Only record files from the same LSEG instance should be combined
           together, otherwise the results are unreliable or the tool may even
           crash.

positional arguments:
  lmcrec_file           Specific lmcrec file(s) for which to run the inventory,
                        they override the query style selection. Note that only
                        record files from the same LSEG instance should be
                        combined together, otherwise the results are unreliable
                        or the tool may even crash.

options:
  -h, --help            show this help message and exit
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
  -I, --instance-inventory
                        Include instance inventory, implied if output dir is
                        specified
  -C, --class-inventory
                        Include class inventory, implied if either of variable
                        inventory or output dir are specified
  -V, --variable-inventory
                        Include class variable inventory, implied if output dir
                        is specified
  -a, --use-ascii       Use ASCII separators when printing a tree, rather than
                        fancier Unicode, in case the terminal doesn't support
                        the latter.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Save the information under OUTPUT_DIR in 'lmcrec-
                        inventory.txt' and 'lmcrec-schema.yaml' files. The
                        directory will be created as needed. If OUTPUT_DIR is
                        specified as "auto" then it will default to
                        $LMCREC_RUNTIME/inventory/INST/FIRST_TIMESTAMP--
                        LAST_TIMESTAMP.
```

### lmcrec-merge-schema

```text
usage: lmcrec-merge-schema [-h] [-m MERGED_SCHEMA_FILE]
                           SCHEMA_FILE [SCHEMA_FILE ...]

Merge multiple LMC schemas built by lmcrec-inventory commands into a common one.

This is needed when importing lmcrec data from multiple instances of LSEG
components (e.g. adh or ads) into the same database. 

LMC classes are mapped into DB tables and their variables are mapped into
columns. Each instance, depending on its specific configuration and/or operating
condition may have only a subset of the classes and variables. If the data comes
from multiple instances then the DB lmcrec_schema should be the superset of each
individual one. 

positional arguments:
  SCHEMA_FILE           Lmcrec schema file from the inventory

options:
  -h, --help            show this help message and exit
  -m MERGED_SCHEMA_FILE, --merge-into MERGED_SCHEMA_FILE
                        Destination .yaml file for the merged schemas. If the
                        file exists then it updated as needed with new
                        information, if not then it is created. If not specified
                        then the merged info is displayed to stdout.
```

### lmcrec-pb-perf

```text
usage: lmcrec-pb-perf [-h] [-p] lmcrec_file [lmcrec_file ...]

Measure the playback performance as the time for applying lmcrec file(s) to the
state cache

positional arguments:
  lmcrec_file

options:
  -h, --help       show this help message and exit
  -p, --have-prev  Enable previous variable value state cache
```

### lmcrec-query

```text
usage: lmcrec-query [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                    [-d RECORD_FILES_DIR] [-F] [-o OUTPUT_DIR]
                    [-z [COMPRESS_LEVEL]]
                    QUERY_OR_FILE [QUERY_OR_FILE ...]

Run queries against recorded data.

For query syntax see:
    https://github.com/bgp59/lmc-recorder/docs/QueryDescription.md

For additional help with the command see:
    https://github.com/bgp59/lmc-recorder/docs/Commands.md#lmcrec-query

positional arguments:
  QUERY_OR_FILE         query or query_file, the latter if it has '.yaml' suffix

options:
  -h, --help            show this help message and exit
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
  -F, --full-data       Display all data instead of only the rows and columns
                        that have at least one value which is neither None nor
                        the default for the type: 0 for numbers, "" for strings;
                        booleans are always displayed.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Save the information under OUTPUT_DIR
                        QUERY/CLASS_NAME.txt[.gz] files. The directory will be
                        created as needed. If OUTPUT_DIR is specified as "auto"
                        then it will default to
                        $LMCREC_RUNTIME/query/INST/FIRST_TIMESTAMP--
                        LAST_TIMESTAMP
  -z [COMPRESS_LEVEL], --compress-level [COMPRESS_LEVEL]
                        Indicate that the output is to be compressed and
                        optionally set the compression level, if it other than
                        Z_DEFAULT_COMPRESSION=-1.
```

### lmcrec-report

```text
usage: lmcrec-report [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                     [-d RECORD_FILES_DIR] [-O ORG_NAME] [-o OUTPUT_DIR]

Create a tar archive with the relevant files for a given instance and time
window. This is useful for sending the information to outside experts.

The command requires an instance and a time window; the archive will contain all
files covering an interval that intersects with the time window.

The archive name is ORG--INST--FIRST_TS--LAST_TS where:

    ORG                 = the organization name, normalized such that it can 
                          be used in file paths
    INST                = instance
    FIRST_TS, LAST_TS   = the first (oldest) and the last (newest) of the
                          timestamps from the selected files.

The content of the archive is as follows:

    ORG--INST--FIRST_TS--LAST_TS/YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec*
    ORG--INST--FIRST_TS--LAST_TS/LMCREC_TZ

The organization name is set by command line arg or it is picked from
the config file.

This naming schema is intended to be both self-descriptive and to avoid clashes
w/ other reports.
    

options:
  -h, --help            show this help message and exit
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
  -O ORG_NAME, --org-name ORG_NAME
                        The organization name, used to override the config file
                        setting; is neither is set it defaults to 'anon'
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Where to store the archive, default:
                        $LMCREC_RUNTIME/report/INST
```

### lmcrec-stats

```text
usage: lmcrec-stats [-h] [-f FROM_TS] [-t TO_TS] [-c CONFIG] [-i INST]
                    [-d RECORD_FILES_DIR] [-q QUANTILES]
                    [lmcrec_file ...]

Given a (list of) record file(s) display stats regarding in/out instance and
variable count and scan time. This information can be used for fine tuning the
scan interval, e.g. using 10 x 90 percentile duration value. 

positional arguments:
  lmcrec_file           Specific lmcrec file(s) for which to collect the stats,
                        they override the query style selection

options:
  -h, --help            show this help message and exit
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
  -q QUANTILES, --quantiles QUANTILES
                        The number of quantiles, use 0 to disable, default: 10.
                        Applicable for scan duration only.
```

### lmcrec-version

```text
usage: lmcrec-version [-h] [-g]

Display version and git commit info

options:
  -h, --help      show this help message and exit
  -g, --git-info  Include git commit info
```
