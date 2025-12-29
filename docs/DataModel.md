# Data Model

## REST Presentation

The LSEG Real-Time Platform components provide access to LMC information in JSON format as follows:

```json
[
    {
        "Instance": "hostname.1.ads.dacs",
        "Class": "DacsConnectionMgr",
        "Variables": [
            {
                "Name": "softwareUsageFileSize",
                "Type": "Numeric",
                "Value": 100
            },
            {
                "Name": "softwareUsageFileDirectory",
                "Type": "String",
                "Value": "./"
            },
            {
                "Name": "softwareUsageWithoutInit",
                "Type": "Boolean",
                "Value": true
            }
        ],
        "Children": [
            {
                "Instance": "hostname.1.ads.dacs.sink",
                "Class": "DacsConnectionMgrClient",
                "Variables": [
                    {
                        "Name": "enabled",
                        "Type": "Boolean Config",
                        "Value": false
                    }
                ],
                "Children": []
            }
        ]
    }
]              
```

## Record File

### Encoding And Record Types

For the purpose of efficiency the encoder and the decoder are custom hardcoded for the LMC use case.

There are essentially 2 types of binary data used for encoding: integers, encoded using varint/uvarint [^1] and UTF-8 strings, encoded as a pair: size (uvarint), followed by N bytes (N being the value in size).

A record file consists of series of records. Each record is made of 1..N fields. The 1st field, the record type, is mandatory and determines the number and type for the remaining fields.

Instance, class and variable names will be mapped to numerics ID's for the purpose of the recording. The instance and class ID have file scope, whereas the variable ID's have class scope.

| Record Type | Field       | Encoding | Obs |
| ----------- | ----------- | ------ | --- |
| LMCREC_TYPE_CLASS_INFO | rec_type<br>class_id<br>name_size<br>name | uvarint<br>uvarint<br>uvarint<br>UTF-8| Define a class name ->  ID mapping |
| LMCREC_TYPE_INST_INFO | rec_type<br>class_id<br>inst_id<br>parent_inst_id<br>name_size<br>name | uvarint<br>uvarint<br>uvarint<br>uvarint<br>uvarint<br>UTF-8 | Define an instance name -> ID + instance attributes<br>Set the inst ID for subsequent variable data[^2] |
| LMCREC_TYPE_VAR_INFO | rec_type<br>class_id<br>var_id<br>lmc_var_type<br>name_size<br>name | uvarint<br>uvarint<br>uvarint<br>uvarint<br>uvarint<br>UTF-8 | Define a variable name -> ID mapping within the class_id<br>scope + other variable attributes, such as the LMC type[^3] |
| LMCREC_TYPE_SET_INST_ID | rec_type<br>inst_id | uvarint<br>uvarint | Set the inst ID for subsequent variable data[^2] |
| LMCREC_TYPE_VAR_BOOL_FALSE | rec_type<br>var_id | uvarint<br>uvarint | Hardcoded `False`<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_BOOL_TRUE | rec_type<br>var_id | uvarint<br>uvarint | Hardcoded `True`<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_UINT_VAL | rec_type<br>var_id<br>value | uvarint<br>uvarint<br>uvarint | Unsigned integer for positive values to ensure that the max range can be accommodated<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_SINT_VAL | rec_type<br>var_id<br>value | uvarint<br>uvarint<br>varint | Signed integer needed for negative values<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_ZERO_VAL | rec_type<br>var_id | uvarint<br>uvarint | Hardcoded to `0` to save storage for the default type value<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_STRING_VAL | rec_type<br>var_id<br>value_size<br>value | uvarint<br>uvarint<br>uvarint<br>UTF-8 | Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_VAR_EMPTY_STRING | rec_type<br>var_id | uvarint<br>uvarint | Hardcoded to `""` to save storage for the default type value<br>Use the most recent inst ID to determine the instance to which the var belongs |
| LMCREC_TYPE_DELETE_INST_ID | rec_type<br>inst_id | uvarint<br>uvarint | The instance with inst ID was no longer found in the latest scan |
| LMCREC_TYPE_SCAN_TALLY | rec_type<br>scan_in_byte_count<br>scan_in_inst_count<br>scan_in_var_count<br>scan_out_var_count | uvarint<br>uvarint<br>uvarint<br>uvarint<br>uvarint | The number of:<br>- response body size in bytes <br>- scan input instance count<br>- scan input variable count<br>- scan output variable value record count |
| LMCREC_TYPE_TIMESTAMP_USEC | rec_type<br>µsec | uvarint<br>varint | µsec since the epoch to be used as the timestamp for the scan<br>Marks the beginning of a scan |
| LMCREC_TYPE_DURATION_USEC | rec_type<br>µsec | uvarint<br>varint | How long the scan took in µsec<br>Marks the end of a scan |
| LMCREC_TYPE_EOR | rec_type | uvarint | End Of Recording, the last record before closing the file<br>Inform the playback tool that no more data will be available |

[lmcrec-dump](./PlaybackToolsCatalogue.md#lmcrec-dump) can be used to inspect a record file and its output next illustrates the logical succession of records:

1. New class discovered: record the name -> ID mapping and info about its variables:

    ```text
    <LmcrecType.CLASS_INFO: 1>, class_id=7, name='rrcpTransmissionBus'
    <LmcrecType.VAR_INFO: 3>, class_id=7, var_id=51, lmc_var_type=<LmcVarType.NUMERIC: 6>, name='reRxmtPktSent'
    <LmcrecType.VAR_INFO: 3>, class_id=7, var_id=67, lmc_var_type=<LmcVarType.NUMERIC: 6>, name='unackdPPPkt'
    <LmcrecType.VAR_INFO: 3>, class_id=7, var_id=71, lmc_var_type=<LmcVarType.NUMERIC: 6>, name='BCMsgsFromUsers'
    <LmcrecType.VAR_INFO: 3>, class_id=7, var_id=86, lmc_var_type=<LmcVarType.NUMERIC: 6>, name='BCMsgsMisordered'
    <LmcrecType.VAR_INFO: 3>, class_id=7, var_id=94, lmc_var_type=<LmcVarType.NUMERIC: 6>, name='totalBytesRcvd'
    ```

1. Subsequently, instances of `rrcpTransmissionBus` will use class ID `7` in their definitions:

    ```text
    <LmcrecType.INST_INFO: 2>, class_id=7, inst_id=88, parent_inst_id=1, name='lseg1.1.adh.0.rrcpTransport.0.srcSide.rrcp.send.transmissionBus'
    ```

1. The prior record also sets inst ID `88` for the variable values following immediately after:

    ```text
    <LmcrecType.VAR_VALUE: 17>, var_id=51, value=0, file_record_type=<LmcrecType.VAR_ZERO_VAL: 9>
    <LmcrecType.VAR_VALUE: 17>, var_id=67, value=0, file_record_type=<LmcrecType.VAR_ZERO_VAL: 9>
    <LmcrecType.VAR_VALUE: 17>, var_id=71, value=15901, file_record_type=<LmcrecType.VAR_UINT_VAL: 7>
    <LmcrecType.VAR_VALUE: 17>, var_id=86, value=0, file_record_type=<LmcrecType.VAR_ZERO_VAL: 9>
    <LmcrecType.VAR_VALUE: 17>, var_id=94, value=2345324, file_record_type=<LmcrecType.VAR_UINT_VAL: 7>
    ```

1. If no new instances were discovered in the current scan, then the recorder will set the inst ID prior to the variable values:

    ```text
    <LmcrecType.SET_INST_ID: 4>, inst_id=88
    <LmcrecType.VAR_VALUE: 17>, var_id=71, value=15911, file_record_type=<LmcrecType.VAR_UINT_VAL: 7>
    ```

    The decoder will then infer that var ID 71 belongs to inst ID 88, which,
    based on a prior record, has the name
    `lseg1.1.adh.0.rrcpTransport.0.srcSide.rrcp.send.transmissionBus` and class
    ID 7. Also based on a prior record, var ID 71 in class ID 7 has the name
    `BCMsgsFromUsers` and the LMC type `Numeric`. Ditto class ID 7 is associated
    w/ class `rrcpTransmissionBus`. Thus the decoder can reconstruct the state
    as it appeared in the JSON scan:

    ```json
    [
        {
            "Instance": "lseg1.1.adh.0.rrcpTransport.0.srcSide.rrcp.send.transmissionBus",
            "Class": "rrcpTransmissionBus",
            "Variables": [
                ...
                {
                    "Name": "BCMsgsFromUsers",
                    "Type": "Numeric",
                    "Value": 15911
                },
                ...
            ]
        }
    ]
    ```

    All this mapping is carried out by the encoder/decoder, transparent for the user of the playback module or tools.

### Record File Structure

```text
+-----------+------+--//--+-------+----------+     +-----+
| Timestamp | Data | Data | Tally | Duration |     | EOR |
+-----------+------+--//--+-------+----------+ ... +-----+
\____________________...____________________/       last
                    scan                            record
```

## Info File

The info is a companion file, named  _file_.info (_file_ being the record file), updated at every flush, checkpoint and upon close. It consists of a fixed set of fields, as follows:

| Field                 | Encoding   | Meaning | Obs |
| --------------------- | ---------- | ------- | --- |
| version_sz            | uvarint    |         |     |
| version               | UTF-8      | SemVer  |     |
| prev_name_sz          | uvarint    |         |     |
| prev_name             | UTF-8      | If non-empty, the name of previous file which was rolled over into<br>the current file | All name -> ID mappings are carried over to this file |
| start_ts              | varint     | First timestamp in µsec | |
| state                 | uvarint    | 0 = `Uninitialized`<br>1 = `Active`<br>2 = `Closed` | Starting from this field the file updates with every flush  |
| most_recent_ts        | varint     | Most recent flush timestamp in µsec. The record file is guaranteed<br>to contain all the scans in between | |
| total_in_num_bytes    | uvarint    | Total number of scan input bytes (the sum of the length of HTTP body reply) | |
| total_in_num_inst     | uvarint    | Total number of scan input instances | |
| total_in_num_var      | uvarint    | Total number of scan input variables | |
| total_out_num_var     | uvarint    | Total number of scan output variable values | |

## Index File

In order to navigate faster to a specific timestamp, checkpoints may be in effect. At a checkpoint **all** instance and variable data are recorded, regardless of whether they are old and/or unchanged. Thus a checkpoint represents the full state at that specific time.

The index is a companion file, named _file_.index (_file_ being the record file), updated at every checkpoint. It consists of pairs of _timestamp_, _offset_, both in varint format. The _timestamp_ (µsec since the epoch) is that of the checkpoint'ed scan and _offset_ is where the first record starts in the record file. If the record file is not compressed then the checkpoint can be reached by seek(_offset_) otherwise by read-and-discard _offset_ bytes.

Playing back a file requires reading a full scan and applying it to a cache state. If checkpoints are not used then the playback should start at the beginning. If checkpoints are used then it can start from the offset associated with the most recent timestamp predating the start timestamp, i.e. max(_timestamp_ <= _start\_timestamp_)`

```text
        +----+------+--//--+-------+----------+     +----+------+--//--+-------+----------+     +-----+
Rec:    | TS | Data | Data | Tally | Duration |     | TS | Data | Data | Tally | Duration |     | EOR |
        +----+------+--//--+-------+----------+ ... +----+------+--//--+-------+----------+ ... +-----+
        \_________________...________________/      \_________________...________________/      last
        ^                 scan                      ^                 scan                      record
        |  checkpoint                    checkpoint |
        +--------+              +-------------------+
                 |              |
        +----+--------+----+--------+
Index:  | TS | Offset | TS | Offset |
        +----+--------+----+--------+ ...
        Matches Rec TS (Timestamp)
```

The index file is also transparent for the user, the skip to the checkpoint is implemented by the playback module.

## Directory And File Structure

The recorder will create record files under a configurable directory. The files are rolled over periodically (e.g. every 2 hours and/or at local midnight), based on the configuration. The files are stored under subdirectories organized by date (day, that is), as follows:

```text
record_files_dir
    |
    +- YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec[.gz]
    |             HH:MM:SS±HH:MM.lmcrec[.gz].index
    |             HH:MM:SS±HH:MM.lmcrec[.gz].info
    |
    |
    +- YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec[.gz]
    |             HH:MM:SS±HH:MM.lmcrec[.gz].index
    |             HH:MM:SS±HH:MM.lmcrec[.gz].info
   ...
```

YYYY-MM-DD and HH:MM:SS±HH:MM are based on the local time of the recorder when the file was created, in ISO 8601 format. This structure is hardwired in the encoder/decoder and it is handled transparently for the user by the playback module. The user has only to specify the time window of interest and decoder will position itself in the appropriate chunk at the appropriate timestamp record, matching the start of the time window.

This structure has the following practical benefits:

- easy daily cleanup based on keep-the-most-recent-N-day criterion
- reasonable size when creating reports to be sent to a third party for
  investigation: assuming a 30 min event window, this would overlap at most 2
  files totalling a few megabytes, rather than the tens required for the entire
  day

Notes:

[^1]: See [Protobuf Encoding](https://protobuf.dev/programming-guides/encoding/) for details about varint

[^2]: Variables are grouped within an instance, so it is more efficient to set the inst ID once, before the 1st variable value, rather than setting it in every variable value record

[^3]: While the variable values are only of 3 types, bool, int and string, the LMC types are more nuanced:, `Boolean`, `Boolean Config`, `Counter`, `Gauge`, `Gauge Config`, `Numeric`, `Large Numeric`, `Numeric Range`, `Numeric Config`, `String`, `String Config`, hence the inclusion of LMCREC_TYPE_VAR_INFO
