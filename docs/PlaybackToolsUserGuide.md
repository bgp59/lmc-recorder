# Playback Tools User Guide

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [Running Queries](#running-queries)
  - [Running A Query In The Recording (AKA Local) Environment](#running-a-query-in-the-recording-aka-local-environment)
  - [Running A Query In An External Environment](#running-a-query-in-an-external-environment)
- [Merging Lmcrec Schemas](#merging-lmcrec-schemas)
- [Exporting Data For Database Import](#exporting-data-for-database-import)
  - [Creating An Export In The Recording (AKA Local) Environment](#creating-an-export-in-the-recording-aka-local-environment)
  - [Creating An Export In An External Environment](#creating-an-export-in-an-external-environment)
- [Cleaning Up Older Data](#cleaning-up-older-data)
- [Fine Tuning The Scan Interval](#fine-tuning-the-scan-interval)

<!-- /TOC -->

## Running Queries

[lmcrec-query](PlaybackToolsCatalogue.md#lmcrec-query) will run queries against
recording data from a single lmcrec instance. The query syntax is explained in
[Query Description](QueryDescription.md). While they can be specified on the
command line, that's impractical for more complex queries, files are better
suited for those.

Multiple queries are supported either as [a
list](QueryDescription.md#single-element-v-list) in the same file or via multiple
files.

The query result can be displayed to stdout or captured in file(s) under an
output directories. The latter should be the norm, maybe except for simple
queries with a very narrow time window (`--from-ts`, `--to-ts` parameters).

The following commands should be run before composing a query:

- [lmcrec-info](PlaybackToolsCatalogue.md#lmcrec-info) to gather time span
  information ([sample output](./sample-output/lmcrec-info/output.txt))
- [lmcrec-inventory](PlaybackToolsCatalogue.md#lmcrec-inventory) to gather
  instance, class and variable information ([sample
  output](./sample-output/lmcrec-inventory))

See:

- [sample queries](../reference/query)
- [query sample output](./sample-output/lmcrec-query)

The following examples illustrate the difference between running a query in the
recording environment (i.e. where data was collected) v. running in an external
one (external party support); see [`INST` v.
`RECORD_FILES_DIR`](PlaybackToolsCatalogue.md#inst-v-record_files_dir) and
[`auto` Output Dir](PlaybackToolsCatalogue.md#auto-output-dir).

### Running A Query In The Recording (AKA Local) Environment

This assumes that the local timezone is relevant for the recording and that the
configuration file is available and `LMCREC_CONFIG` is set to its path.

1. Display available data:

    ```bash
    lmcrec-info -i lseg1.1.adh
    ```

1. Gather the inventory of available instances, classes and variables for the
   desired period (a 10 min). Note that the timestamp does not specify a UTC
   offset ±HH:MM, since the data was recorded in the local timezone.

    ```bash
    lmcrec-inventory -i lseg1.1.adh -f 2025-12-11T14:00:00 -t +10m -o auto
    ```

1. Run the query:

    ```bash
    lmcrec-query -i lseg1.1.adh -f 2025-12-11T14:00:00 -t +10m -o auto \
        .../reference/query/rrcp-query-example.yaml
    ```

### Running A Query In An External Environment

The data was extrated from a tar archive created by
[lmcrec-report](PlaybackToolsCatalogue.md#lmcrec-report) command.

1. Make the extraction root the current directory:

    ```bash
    cd .../bgp59--lseg1.1.adh--2025-12-11T13-13-28-08-00--2025-12-11T15-13-23-08-00
    ls
    ```

1. Make the recording timezone the timezone for the lmcrec datetime displaying
   and parsing:

    ```bash
    export LMCREC_TZ=$(cat LMCREC_TZ); echo $LMCREC_TZ
    ```

1. Check for available data:

    ```bash
    lmcrec-info -d rec
    ```

1. Gather the inventory of available instances, classes and variables for the
   desired period (a 10 min). Note that the timestamp does not specify a UTC
   offset ±HH:MM, since LMCREC_TZ is set. Also set a specific output
   subdirectory under the same location, since the latter is investigation
   specific.

    ```bash
    lmcrec-inventory -d rec -f 2025-12-11T14:00:00 -t +10m -o inventory
    ```

1. Run the query; the above observations about timezone and output
   subdirectory apply here as well:

    ```bash
    lmcrec-query -d rec -f 2025-12-11T14:00:00 -t +10m -o query \
        .../reference/query/rrcp-query-example.yaml
    ```

## Merging Lmcrec Schemas

Lmcrec schemas are machine readable YAML files describing the LMC data model of
the recorded component (adh, ads):

- class names and their variables' attributes:
  - name
  - type
  - max size for strings
  - whether negative values were present or not for numeric types
- instance name max size

This information is needed for exporting lmcrec data into files that can be
imported into SQL databases (bcp like files).

[lmcrec-inventory](PlaybackToolsCatalogue.md#lmcrec-inventory) generates the
schema in addition to the inventory, see this
[example](sample-output/lmcrec-inventory/adh/lmcrec-schema.yaml).

In order to accommodate imports from multiple recordings into the same database,
the superset of each individual schemas is needed.

The superset can be either per component (one for adh and one for ads) or truly
global combining all components.

[lmcrec-merge-schema](PlaybackToolsCatalogue.md#lmcrec-merge-schema) is the tool
for this. The merge process will check for consistency (the same variable of a
given class has the same definition across all schemas) and it will raise a
runtime error if an inconsistency is detected, in other words the merge result
is reliable.

Typically the schemas are collected under `$LMCREC_RUNTIME/schema` directory in
files called `COMP-lmcrec-schema.yaml` or `global-lmcrec-schema.yaml`

The standard approach is to prime a schema category with the one generated by
[lmcrec-inventory](PlaybackToolsCatalogue.md#lmcrec-inventory) for the entire
available time span for the relevant component and to subsequently merge into it
new schemas to build the superset.

1. Prime the global schema using the inventory from adh:

    ```bash
    mkdir -p $LMCREC_RUNTIME/schema
    lmcrec-inventory -i lseg1.1.adh -o auto
    cp -p \
        .../runtime/lmcrec/inventory/lseg1.1.adh/2025-12-11T10:05:53-08:00--2025-12-17T15:32:02-08:00/lmcrec-schema.yaml \
        $LMCREC_RUNTIME/schema/global-lmcrec-schema.yaml
    ```

1. Generate the schema for a different component or the same component with a
   different deployment (to potentially expose new classes):

    ```bash
    lmcrec-inventory -i lseg2.1.ads -o auto
    ```

1. Merge the new schema with the global one:

    ```bash
    lmcrec-merge-schema \
        -m $LMCREC_RUNTIME/schema/global-lmcrec-schema.yaml \
        ...runtime/lmcrec/inventory/lseg2.1.ads/2025-12-11T10:06:01-08:00--2025-12-11T16:32:14-08:00/lmcrec-schema.yaml
    ```

## Exporting Data For Database Import

This is intended for people who prefer SQL style of queries. The export-import
paradigm should be limited to investigations around a narrow time span (~ 1
hour) due to the large number of files involved. As outlined in
[Motivation](../README.md#motivation), a separate project will provide the
continuous storage of LCM data into a timeseries database, which would make for
a more efficient solution.

Classes are mapped into tables and variables into columns. Database servers may
have certain restriction regarding the names of tables and columns (character
set, max size, etc). [lmcrec-export](PlaybackToolsCatalogue.md#lmcrec-export)
implements a conservative name mapping into lowercase, `camelCase` ->
`camel_case`, letters, digits and `_` only character set with configurable max
size. Other aspects of the export such as data types and output format are
controlled by a DB mapping file.

Refer to
[reference/export/sybase-db-mapping.yaml](../reference/export/sybase-db-mapping.yaml)
for mapping info; that file can be used as primer for a different flavor of
database implementation.

A lmcrec schema is required for export in addition to the mapping file. A
[merged schema](#merging-lmcrec-schemas) is required if records from multiple
components will be imported into the same database and it is recommended for
exports in the recording (AKA local) environment.

The [lmcrec-export](PlaybackToolsCatalogue.md#lmcrec-export) will create the following subdirectory and file structure under the output dir:

```text
.../runtime/lmcrec/export/lseg1.1.adh/2025-12-11T22:13:28+00:00--2025-12-11T22:23:23+00:00
    |
    +-- lmcrec-db-mapping.txt
    +-- sql/
    |     +-- create-TABLE.sql
...   ...
    |     +-- create-TABLE.sql
    +-- table-data/
        +-- TABLE/
        │     +-- batch[-NNNNNN].csv
        ...    +-- bcp.fmt
        +-- TABLE/
                +-- batch[-NNNNNN].csv
                +-- bcp.fmt
```

| File | Description | Obs |
| ---- | ----------- | --- |
| lmcrec-db-mapping.txt | LMC <-> DB mapping:<br>- class <->- table<br>- variable <-> column<br>- data type | |
| create-TABLE.sql | SQL command for creating the table | |
| batch[-NNNNNN].csv\[.gz\] | data for TABLE, suitable for import | `-NNNNN` is omitted if there is a single<br>file (`max_rows_per_file` is 0) |
| bcp.fmt | Text (non XML, that is) format for the bcp command | |

### Creating An Export In The Recording (AKA Local) Environment

This assumes that the local timezone is relevant for the recording and that the
configuration file is available and `LMCREC_CONFIG` is set to its path.

Follow the steps from [Merging Lmcrec Schemas](#merging-lmcrec-schemas) to prime
the component and/or global schema file.

1. Display available data:

    ```bash
    lmcrec-info -i lseg1.1.adh
    ```

1. Create the schema for the relevant time span. Note that the timestamp does
   not specify a UTC offset ±HH:MM, since the data was recorded in the local
   timezone.

    ```bash
    lmcrec-inventory -i lseg1.1.adh -f 2025-12-11T14:00:00 -t +10m -o auto
    ```

1. Merge the schema, as per best practices:

    ```bash
    lmcrec-merge-schema \
        -m $LMCREC_RUNTIME/schema/global-lmcrec-schema.yaml \
        .../runtime/lmcrec/inventory/lseg1.1.adh/2025-12-11T10:05:53-08:00--2025-12-17T15:32:02-08:00/lmcrec-schema.yaml
    ```

1. Prepare the DB mapping file specific for the database server, starting from [reference/export/sybase-db-mapping.yaml](../reference/export/sybase-db-mapping.yaml)

1. Export the data with [lmcrec-export](PlaybackToolsCatalogue.md#lmcrec-export):

    ```bash
    lmcrec-export -i lseg1.1.adh -f 2025-12-11T22:13:28 -t +10m \
        -S $LMCREC_RUNTIME/schema/adh-lmcrec-schema.yaml \
        -X .../reference/sybase-db-mapping.yaml \
        -o auto
    ```

### Creating An Export In An External Environment

The data was extrated from a tar archive created by
[lmcrec-report](PlaybackToolsCatalogue.md#lmcrec-report) command.

1. Make the extraction root the current directory:

    ```bash
    cd .../bgp59--lseg1.1.adh--2025-12-11T13:13:28-08:00--2025-12-11T15:13:23-08:00
    ls
    ```

1. Make the recording timezone the timezone for the lmcrec datetime displaying
   and parsing:

    ```bash
    export LMCREC_TZ=$(cat LMCREC_TZ); echo $LMCREC_TZ
    ```

1. Check for available data:

    ```bash
    lmcrec-info -d rec
    ```

1. Create the schema for the relevant time span. Note that the timestamp does
   not specify a UTC offset ±HH:MM, since LMCREC_TZ is set. Also set a specific
   output subdirectory under the same location, since the latter is
   investigation specific.

    ```bash
    lmcrec-inventory -d rec -f 2025-12-11T14:00:00 -t +10m -o inventory
    ```

1. If this data has to be imported along with exports from other reports (other
   components from the same org with the same time span) then
   [merge](#merging-lmcrec-schemas) their schemas.

1. Export the data with [lmcrec-export](PlaybackToolsCatalogue.md#lmcrec-export):

    ```bash
    lmcrec-export -d rec -f 2025-12-11T22:13:28 -t +10m \
        -S $LMCREC_RUNTIME/schema/adh-lmcrec-schema.yaml \
        -X .../reference/sybase-db-mapping.yaml \
        -o export
    ```

See [sample output](sample-output/lmcrec-export/adh/)

## Cleaning Up Older Data

There record files are organized under `YYYY-MM-DD` subdirectories, which lends
itself to daily cleanup. The retention period is controlled by
[keep_n_days](../reference/config/lmcrec-config-reference.yaml#L108) parameter
in the configuration file which can be set on a per instance basis, if needed.
It may also be amended or overridden by command line arguments.

[lmcrec-cleanup](PlaybackToolsCatalogue.md#lmcrec-cleanup) will read the config
file and it will remove older directories accordingly. Environment variables
`LMCREC_RUNTIME` and potentially `LMCREC_CONFIG` are expected by the command and
that should be taken into account from cronjob invocation.

## Fine Tuning The Scan Interval

The smaller the scan interval, the better chances are to capture/diagnose burst
driven events. [lmcrec-stats](PlaybackToolsCatalogue.md#lmcrec-stats) (see
[sample output](sample-output/lmcrec-stats/output.txt)) can be used to determine
how much the interval can be decreased: as a rule of thumb it should be at least
10x the `90%` quantile for `scan duration`.

Other factors to consider:

- the network bandwidth uptick due to `in byte#` burst repeated more often, also
  from stats output
- the `%CPU` increase for the recorded component (adh, ads); that should be
  assessed separately
  
## Record Data Viewer

[lmcrec-dump](./PlaybackToolsCatalogue.md#lmcrec-dump) can be used to display
record, info and index files.

See [sample output](./sample-output/lmcrec-dump/)
