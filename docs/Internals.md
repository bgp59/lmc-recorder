# Internals

## Instances

lmcrec runs a recorder for each instance of LSEG Real-Time Distribution System
components. lmcrec too uses the term of instance to identify a specific recorder
and while lmcrec assumes no meaning for the instance value (it is simply an
identifier), it is recommended, for consistency sake, to follow the LSEG
convention: HOST.N.COMP, e.g. `lseg1.bgp59.com.1.adh`, most likely w/o the
domain part of the FQDN: `lseg1.1.adh`.

## Record File Chains

lmcrec uses creation time for file name and they are grouped under date styles
subdirectory, as follows:

```text
YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec[.gz]
           HH:MM:SS±HH:MM.lmcrec[.gz].info
           HH:MM:SS±HH:MM.lmcrec[.gz].index
```

During normal operation lmcrec will rollover the record files:

- at regular intervals and/or midnight [^1]
- after a failed scan
- upon detecting that the recorded process has changed between scans[^2]

lmcrec will indicate if the new file is a continuation of the previous one or not,
by populating (or leaving empty) the `prev_name` field in the companion [info
file](DataModel.md#info-file). This is important for delta calculations since it
indicates if the first scan of new record file is next scan of the last one
of the previous file or not.

When the playback state object is being initialized, it organizes the recording
files in chains of consecutive files, sorted chronologically:

```text
chain#1 -> file1-1 -> file1-2 -> ... -> file1-n1
chain#2 -> file2-1 -> file2-2 -> ... -> file2-n2
...
```

During playback, when a new chain is started, the previous state is invalidated
and [new_chain](API.md#new_chain) attribute is set to `True` for the first scan.

[^1]: This is configurable and theoretically it could be disabled, although it
    is not clear why that would beneficial
[^2]: The determination whether the process changed between scans is based on
    PID and start time info provided in the JSON response. If a scan attempt
    fails, then obviously the first successful scan is considered to be for a
    new process
