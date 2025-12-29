# Using Recorded Data Programmatically In Python

<!-- TOC tocDepth:2..5 chapterDepth:2..6 -->

- [General Considerations](#general-considerations)
- [lmcrec.playback](#lmcrecplayback)
  - [LmcrecQueryIntervalStateCache](#lmcrecqueryintervalstatecache)
    - [Constructor](#constructor)
    - [Methods](#methods)
      - [apply_next_scan()](#apply_next_scan)
      - [get_inst_var()](#get_inst_var)
      - [get_inst_vars()](#get_inst_vars)
      - [get_inst_curr_prev_var()](#get_inst_curr_prev_var)
      - [get_inst_curr_prev_vars()](#get_inst_curr_prev_vars)
      - [get_inst_class_name()](#get_inst_class_name)
      - [get_inst_var_types()](#get_inst_var_types)
      - [get_class_var_types()](#get_class_var_types)
      - [get_class_inst_names()](#get_class_inst_names)
      - [run_with_cb()](#run_with_cb)
    - [Attributes](#attributes)
      - [ts, prev_ts](#ts-prev_ts)
      - [duration](#duration)
      - [scan_tally](#scan_tally)
      - [new_inst, deleted_inst](#new_inst-deleted_inst)
      - [num_scans](#num_scans)
      - [first_ts, last_ts](#first_ts-last_ts)
      - [new_chain](#new_chain)
  - [Utility Functions](#utility-functions)
    - [get_record_files_dir()](#get_record_files_dir)
    - [parse_ts()](#parse_ts)
    - [format_ts()](#format_ts)
- [Writing New Command Tools](#writing-new-command-tools)

<!-- /TOC -->

## General Considerations

The API provides programmatic access to recorded data via a state cache object
whereby recorded scans are applied to a Python object thus restoring the entire
LMC state at the time when the scan took place.

Potential API use cases:

- complex explorations/queries involving logic constructs, cross references,
  etc. that cannot be accommodated by the simple, built-in
  [queries](QueryDescription.md)
- plotting
- periodic capacity reports

All of the above could be accomplished using the [Jupiter
Notebook](https://jupyter-notebook.readthedocs.io/en/latest/notebook.html)
framework or by developing new command line tools.

It should be noted that before writing code one should explore the available
information using the available [Playback Tools](PlaybackToolsUserGuide.md).

## lmcrec.playback

The API comes as a Python module: `lmcrec.playback`. While many objects and
internals are available through that module, the API focus is the LMC state
cache: an object that recreates the entire LMC state at the moment of the scan.

### LmcrecQueryIntervalStateCache

#### Constructor

```python
from lmcrec.playback import (
    LmcRecord,
    LmcrecQueryIntervalStateCache, 
    LmcrecScanRetCode,
    get_record_files_dir,
    parse_ts,
    format_ts,
)

LmcrecQueryIntervalStateCache(
    record_files_dir: str = "",
    from_ts: Optional[float] = None,
    to_ts: Optional[float] = None,
    have_prev: bool = False,
)
    """
        Args:

            record_files_dir (str):
                Either the top record files dir or one of its sub-dirs.

            from_ts (float):
                The start of the timestamp window. If None then consider files
                starting with the earliest available.

            to_ts (float):
                The start of the timestamp window. If None then consider files up to
                the most recent available.

            have_prev (bool):
                Whether to maintain previous variable values or not.
    """
```

About `have_prev`: most LMC variables are counters, or counter-like so their
absolute value is less important than the change/delta. The latter requires the
previous scan value, which, as a convenience for the user, is maintained by the
cache if `have_prev=True`.

#### Methods

##### apply_next_scan()

```python
apply_next_scan() -> LmcrecScanRetCode
```

Apply next scan from the record file and return status as
[LmcrecScanRetCode](../lmcpb/src/lmcrec/playback/cache/state_cache.py#L25).
The normal responses are `LmcrecScanRetCode.COMPLETE`, when the scan was properly
applied or `LmcrecScanRetCode.ATEOR`, the end of the time window available data.

##### get_inst_var()

```python
get_inst_var(inst_name: str, var_name: str) -> Any
```

Return the current value for variable `var_name` from instance `inst_name`. The
value can be `bool`, `int`, `str` or `None`, if the variable was not found.

##### get_inst_vars()

```python
get_inst_vars(inst_name: str, *var_name: str) -> Dict[str, Any]
```

Given an instance name and an optional list of variable names, return a
dictionary with the current values for the found variables. If no variable names
are provided, all variables in the instance are returned. The values in the
dictionary can be `bool`, `int` or `str`.

##### get_inst_curr_prev_var()

```python
get_inst_curr_prev_var(inst_name: str, var_name: str) -> Tuple[Any, Any]
```

Return the current and the previous values for variable `var_name` from instance
`inst_name`. The values can be `bool`, `int`, `str` or `None`, if the variable
was not found. This requires that the object was initialized w/
`have_prev=True`.

##### get_inst_curr_prev_vars()

```python
get_inst_vars(inst_name: str, *var_name: str) -> Dict[str, Tuple[Any, Any]]
```

Given an instance name and an optional list of variable names, return a
dictionary with the current and previous values for the found variables. If no
variable names are provided, all variables in the instance are returned. The
values in the dictionary can be `bool`, `int`, `str` or `None` (the latter if
there is no previous value). This requires that the object was initialized w/
`have_prev=True`.

##### get_inst_class_name()

```python
get_inst_class_name(inst_name: str) -> Optional[str]
```

Return the class name for a given instance, or `None` if the instance doesn't
exist.

##### get_inst_var_types()

```python
get_inst_var_types(inst_name: str) -> Dict[str, LmcVarType]
```

Return the
[LmcVarType](../lmcpb/src/lmcrec/playback/codec/decoder.py#L44) for each
variable in the class of the instance `inst_name`.

##### get_class_var_types()

```python
get_class_var_types(class_name: str) -> Dict[str, LmcVarType]
```

Return the
[LmcVarType](../lmcpb/src/lmcrec/playback/codec/decoder.py#L44) for each
variable in the class `class_name`.

##### get_class_inst_names()

```python
get_class_inst_names(class_name: str) -> Set[str]
```

Return the set of all instance names currently using class `class_name`.

##### run_with_cb()

```python
run_with_cb(cb: Optional[Callable[[LmcrecQueryIntervalStateCache], bool]]) -> LmcrecScanRetCode
```

Invoke the callback `cb` repeatedly until it either returns `False` or the
current scan returned code different than `LmcrecScanRetCode.COMPLETE`.

The argument `cb` is a callable that takes the LMC state cache as an argument
and which returns `True` if the callback loop is to continue or `False`
otherwise.

#### Attributes

##### ts, prev_ts

`ts: float` and `prec_ts: float`  are the timestamps of the current and previous
scan, the latter only if if the object was initialized w/ `have_prev=True`.

##### duration

`duration: float` the duration, in seconds, it took to retrieve and record the current scan.

##### scan_tally

`scan_tally: LmcRecord` the current scan tally. The relevant attributes of
[LmcRecord](../lmcpb/src/lmcrec/playback/codec/decoder.py#L60) are:
`scan_in_byte_count`, `scan_in_inst_count`, `scan_in_var_count`,
`scan_out_var_count` representing the current scan's number of bytes (the HTTP
body length), the number of input instances and variables and the number of
output variables (typically only the variables whose value changed are
recorded).

##### new_inst, deleted_inst

`new_inst: bool` and `deleted_inst: bool` are flags indicating whether
new/deleted (vanished, that is) instances were detected at the current scan.

##### num_scans

`num_scans: int` the number of scans applied so far.

##### first_ts, last_ts

`first_ts: float`, `last_ts: float` the first and the last timestamps, in
seconds, within the time window.

In other words, if `from_ts` and `to_ts` parameters were used to initialize
`LmcrecQueryIntervalStateCache`, then `first_ts` is that of first scan such that `from_ts
<= first_ts` and `last_ts` is either the current scan's timestamp, or, if
`apply_next_scan()` or `run_with_cb()` returned `LmcrecScanRetCode.ATEOR` then it
is that of the last scan whose `ts <= to_ts`.

The time window used at `LmcrecQueryIntervalStateCache` intialization is aspirational,
whereas `first_ts` and `last_ts` are actual timestamps found in the recording.

##### new_chain

`new_chain: bool` if `True` it indicates that a chain if record files was
opened and there is no previous state, see [Record File
Chains](Internals.md#recording-file-chains) for details.

### Utility Functions

#### get_record_files_dir()

```python
get_record_files_dir(inst: str, config_file: Optional[str] = None) -> str
```

Return the record files dir for the given [inst](Internals.md#instances) and `config_file`; if the latter is not provided then `$LMCREC_CONFIG` is used, with a fallback over `lmcrec-config.yaml`.

#### parse_ts()

```python
parse_ts(spec: str) -> float
```

Parse ISO 8601 datetime specification, `YYYY-DD-MMTHH:MM:SS[±HH:MM|Z]` into a
timestamp observing [Datetime Handling](PlaybackToolsCatalogue.md#datetime-handling)

#### format_ts()

```python
format_ts(ts: Optional[float] = None) -> str
```

Convert `ts` or `time.time()` if `ts` is `None` to ISO 8601 format
`YYYY-DD-MMTHH:MM:SS[±HH:MM]` observing [Datetime
Handling](PlaybackToolsCatalogue.md#datetime-handling)

## Writing New Command Tools

Most command line tools should peruse the standard file selection argument set from [lmcrec.playback.query.args](../lmcpb/src/lmcrec/playback/query/args.py), as illustrated below:

```python
from query import (
    build_lmcrec_file_chains,
    chain_to_file_list,
    get_file_selection_arg_parser,
    process_file_selection_args,
)

def main():
    parser = argparse.ArgumentParser(
        parents=[get_file_selection_arg_parser()],
    )

    args = parser.parse_args()
    record_files_dir, from_ts, to_ts = process_file_selection_args(args)

```

See: [lmcrec_query.py](../lmcpb/src/lmcrec/playback/commands/lmcrec_query.py)
for reference.
