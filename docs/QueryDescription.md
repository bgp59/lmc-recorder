# Query Description

## Structure

A single query selector consists of the following parts:

- name
- instance selector
- class selector
- type exclusion
- type selector
- variable exclusion
- variable selector

### Name (n)

An optional name to identify the query. If not provided then "queryN" is used,
where N the query number in the order of discovery, starting from 1.

### Instance Selector (i)

A (list of) instance name(s) or /regexp/ to match.

A name may start with `~` which is shortcut for any prefix; instance names
ending what follows `~` will be selected. All LMC instance names are prefixed by
HOSTNAME.I.COMP where I is the component instance (e.g. `2` for `adh -i 2`) and
COMP is `adh`, `ads`, etc. To make the query portable across multiple LMC
instances, `~` can be used as a placeholder for whatever prefix.

E.g. given the instance name
`lseg1.1.adh.1.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages`, the
instance selector `~.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages`
will match all instances regardless of hostname and thread#.

To match the above for all services though, a regexp may be needed:
`/\.sourceThread\.rrmpConsumer\.[^.]+\.\d+.outgoingMessages$/`. Please note that
`.` should to be escaped to be matched verbatim, instead of being considered
regexp any-char.

### Class Selector (c)

A class name;  if instance selector is present then only the instances with a
matching the class are used. If no instance selector is present then all
instances of that class are used.

### Type Exclusion (T)

A (list of) [variable type(s)](#variable-types) that should be excluded from the query result.

### Type Selector (t)

A (list of) [variable type(s)](#variable-types), each with an optional
suffix `:vpdDr` [value qualifiers](#value-qualifiers) that should be included in
the query result.

### Variable Exclusion (V)

A (list of) var name(s) that should be excluded from the query result.

### Variable Selector (v)

A (list of) var name(s), each with an optional suffix `:vpdDr` [value
qualifiers](#value-qualifiers) that should be included in the query result.

## Variable Resolution

How the type and variable selectors work together (pseudo-code):

```text
for each var_name in class_variables do
    if var_name in variable_exclusion then
        ignore
    if var_name in variable_selector then
        select
    if var_type in type_exclusion then
        ignore
    if var_type in type_selector then
        select
    if variable_selector is empty and type_selector is empty then
        select
```

## Format

The query will be specified in [YAML](https://yaml.org/spec/1.2.2/) format. Each part is prefixed by a key,
`(k)` above.

E.g.

```yaml
n:  sample_query
i:  
    - host.n.comp.sub.comp
    - ~.sub.comp
    - /\.sub\.[^.]+\.last$/
c:  Class
T:
    - boolean_config
    - gauge_config
    - numeric_config
    - string_config
t:
    - counter:dr
    - gauge:vd
    - numeric:dr
    - large_numeric:dr
V:  ignore_var
v:  
    - var1
    - var2:dr
    - var3:vd

```

### Variable Types

The variable types are the enumeration names from
[LmcVarType](../lmcpb/src/lmcrec/playback/codec/decoder.py#L44), case
insensitive:

- `BOOLEAN`
- `BOOLEAN_CONFIG`
- `COUNTER`
- `GAUGE`
- `GAUGE_CONFIG`
- `NUMERIC`
- `LARGE_NUMERIC`
- `NUMERIC_RANGE`
- `NUMERIC_CONFIG`
- `STRING`
- `STRING_CONFIG`

### Value Qualifiers

A type or variable selector name may end with `:vpdDr` (any combination of the
letters) which act as qualifiers on how to handle the variable's value:

| Qualifier | Meaning |
| --------- | ------- |
| v | return the value (default) |
| p | return the previous value |
| d | return delta, adjusted for rollover |
| D | return delta, unadjusted |
| r | return rate |

#### Value Rollover

Counters used in delta calculations rollover to `0` after `max_val`, resulting
in negative deltas. Assuming that the rollover occurred only once since the last
sampling, the negative delta can be adjusted to the true value by adding
`max_val - 1` to it.

This adjustment is applied to `COUNTER`, `NUMERIC` and `LARGE_NUMERIC` types
only. For `GAUGE` and `NUMERIC_RANGE` negative deltas make sense so no
adjustment will be applied.

If delta w/o adjustment is desired then `D` qualifier can be used.

### Single Element V. List

Instance, type and variable selectors can specify a single element or a list,
the query parser will understand this from the context. See `V:` v. `v:` above.

Additionally a query selector may contain a single query or a list of queries.

E.g.:

```yaml
- n:  first_query
  c:  Class1
  T:
    - boolean_config
    - gauge_config
    - numeric_config
    - string_config
  t:
    - counter:dr
    - gauge:vd
    - numeric:dr
    - large_numeric:dr
- n: second_query
  c: Class2
  v:
    - var1
    - var2
```

### Pseudo-JSON Format

The [YAML](https://yaml.org/spec/1.2.2/) parser supports a relaxed [JSON](https://www.json.org/json-en.html) syntax too, either indented:

```yaml
{
    n: "Indented JSON", 
    i: [
        host.1.ads.part1.part2, 
        "/host\\.1\\.ads\\.\\S+\\.part3/", 
        ~.part4,
    ],
    t: [
        numeric:d, numeric_range, counter:d, gauge
    ]
    c: class, 
    v: [
        var1, var2:vd
    ]
}
```

or single line, useful for command line, ad-hoc, queries:

```yaml
'{n: "Single line JSON",i:[host.1.ads.part1.part2,"/host\\.1\\.ads\\.\\S+.\\.part3/",~.part4,"],c: class,v:[var1,var2:vd]}'
```

**IMPORTANT!** `\` should be doubled for [JSON](https://www.json.org/json-en.html) style, since it is the escape character.
