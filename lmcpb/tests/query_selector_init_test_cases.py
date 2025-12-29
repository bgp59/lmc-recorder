# Prompt: .github/prompts/query_selector_init_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5

"""Test cases for test_lmcrec_query_selector_init"""

# noqa
# fmt: off

from lmcrec.playback.codec import LmcVarType

from .query_selector_def import (
    LmcrecQuerySelectorInitTestCase,
    q_D,
    q_d,
    q_p,
    q_r,
    q_v,
)

init_test_cases = [
    LmcrecQuerySelectorInitTestCase(
        name="YAMLMix",
        query=r'''
            n:  YAML mix
            i:
                - host.1.ads.part1.part2
                - ~.part3
                - /host\.1\.ads\.\S+\.part4/
            c: class
            T:  boolean_config
            t:
                - gauge
                - numeric:dr
            V:  exclude_var
            v:
                - var1
                - var2:vd
        ''',  
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.1.ads.part1.part2"],
        expect_query_prefix_inst_names=[".part3"],
        expect_query_inst_re=[r'host\.1\.ads\.\S+\.part4'],
        expect_query_class_name="class",
        expect_query_include_types={LmcVarType.GAUGE: q_v, LmcVarType.NUMERIC: q_d | q_r},
        expect_query_exclude_types={LmcVarType.BOOLEAN_CONFIG},
        expect_query_include_vars={"var1": q_v, "var2": q_v | q_d},
        expect_query_exclude_vars={"exclude_var"}
    ),
    LmcrecQuerySelectorInitTestCase(
        name="IndentedJsonMix",
        query=r'''
            {
                n: "Indented JSON mix",
                i: [
                    host.1.ads.part1.part2,
                    ~.part3,
                    "/host\\.1\\.ads\\.\\S+\\.part4/",
                ],
                c: class,
                T: boolean_config,
                t: [
                    gauge,
                    numeric:dr,
                ],
                V: exclude_var,
                v: [
                    var1,
                    var2:vd,
                ],
            }
        ''',  
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.1.ads.part1.part2"],
        expect_query_prefix_inst_names=[".part3"],
        expect_query_inst_re=[r'host\.1\.ads\.\S+\.part4'],
        expect_query_class_name="class",
        expect_query_include_types={LmcVarType.GAUGE: q_v, LmcVarType.NUMERIC: q_d | q_r},
        expect_query_exclude_types={LmcVarType.BOOLEAN_CONFIG},
        expect_query_include_vars={"var1": q_v, "var2": q_v | q_d},
        expect_query_exclude_vars={"exclude_var"}
    ),
    LmcrecQuerySelectorInitTestCase(
        name="SimpleYAML",
        description="Simple query with just instance name and class",
        query=r'''
            n: Simple YAML
            i: host.ads.instance1
            c: MyClass
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.ads.instance1"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name="MyClass",
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="PrefixOnly",
        description="Query with only prefix instance names",
        query=r'''
            n: Prefix Only
            i:
                - ~.suffix1
                - ~.suffix2
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=[],
        expect_query_prefix_inst_names=[".suffix1", ".suffix2"],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="RegexpOnly",
        description="Query with only regexp patterns",
        query=r'''
            n: Regexp Only
            i:
                - /^host\..*\.device$/
                - /.*\.controller\.\d+/
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=[],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[r'^host\..*\.device$', r'.*\.controller\.\d+'],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="NoClass",
        description="Query without class specification",
        query=r'''
            n: No Class
            i: host.instance
            v:
                - var1
                - var2
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={"var1": q_v, "var2": q_v},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="QualifiedVariables",
        description="Query with all variable qualifiers",
        query=r'''
            n: Qualified Variables
            i: host.instance
            v:
                - var1:v
                - var2:p
                - var3:d
                - var4:D
                - var5:r
                - var6:vpdr
        ''',
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={
            "var1": q_v,
            "var2": q_p,
            "var3": q_d,
            "var4": q_D,
            "var5": q_r,
            "var6": q_v | q_p | q_d | q_r
        },
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="IncludeTypes",
        description="Query with multiple include types",
        query=r'''
            n: Include Types
            i: host.instance
            t:
                - counter
                - gauge:vp
                - numeric:dr
                - string
        ''',
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={
            LmcVarType.COUNTER: q_v,
            LmcVarType.GAUGE: q_v | q_p,
            LmcVarType.NUMERIC: q_d | q_r,
            LmcVarType.STRING: q_v
        },
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="ExcludeTypes",
        description="Query with multiple exclude types",
        query=r'''
            n: Exclude Types
            i: host.instance
            T:
                - boolean_config
                - string
                - large_numeric
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types={
            LmcVarType.BOOLEAN_CONFIG,
            LmcVarType.STRING,
            LmcVarType.LARGE_NUMERIC
        },
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="ExcludeVariables",
        description="Query with multiple exclude variables",
        query=r'''
            n: Exclude Variables
            i: host.instance
            V:
                - exclude_var1
                - exclude_var2
                - exclude_var3
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars={"exclude_var1", "exclude_var2", "exclude_var3"}
    ),
    LmcrecQuerySelectorInitTestCase(
        name="NoInstances",
        description="Query without instance specification (matches all)",
        query=r'''
            n: No Instances
            c: MyClass
            v: var1
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=[],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name="MyClass",
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={"var1": q_v},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="NoVariables",
        description="Query without variable specification (matches all)",
        query=r'''
            n: No Variables
            i: host.instance
            c: MyClass
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name="MyClass",
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="JSONRegexpEscaping",
        description="JSON format with properly escaped regexp",
        query=r'''
            {
                n: "JSON Regexp Escaping",
                i: [
                    "/host\\.\\d+\\.ads\\.[a-z]+/",
                    "/~\\.part5/",
                ],
            }
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=[],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[r'host\.\d+\.ads\.[a-z]+', r'~\.part5'],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="MixedInstanceTypes",
        description="Query mixing all instance specification types",
        query=r'''
            n: Mixed Instance Types
            i:
                - host.full.name
                - another.full.name
                - ~.suffix
                - /^prefix\..*$/
                - /.*\.middle\.\d+/
            c: TestClass
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.full.name", "another.full.name"],
        expect_query_prefix_inst_names=[".suffix"],
        expect_query_inst_re=[r'^prefix\..*$', r'.*\.middle\.\d+'],
        expect_query_class_name="TestClass",
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="IncludeExcludeMix",
        description="Query with both include and exclude specifications",
        query=r'''
            n: Include Exclude Mix
            i: host.instance
            t:
                - gauge
                - counter:dr
            T:
                - string
                - boolean_config
            v:
                - important_var:vp
                - metric_var:r
            V:
                - ignore_var
                - temp_var
        ''',
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={
            LmcVarType.GAUGE: q_v,
            LmcVarType.COUNTER: q_d | q_r
        },
        expect_query_exclude_types={LmcVarType.STRING, LmcVarType.BOOLEAN_CONFIG},
        expect_query_include_vars={
            "important_var": q_v | q_p,
            "metric_var": q_r
        },
        expect_query_exclude_vars={"ignore_var", "temp_var"}
    ),
    LmcrecQuerySelectorInitTestCase(
        name="SingleStringValues",
        description="Query with single string values instead of arrays",
        query=r'''
            n: Single String Values
            i: host.instance
            c: MyClass
            T: boolean_config
            t: gauge
            V: exclude_var
            v: include_var
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name="MyClass",
        expect_query_include_types={LmcVarType.GAUGE: q_v},
        expect_query_exclude_types={LmcVarType.BOOLEAN_CONFIG},
        expect_query_include_vars={"include_var": q_v},
        expect_query_exclude_vars={"exclude_var"}
    ),
    LmcrecQuerySelectorInitTestCase(
        name="AllQualifiersCombined",
        description="Query with all qualifiers on types and variables",
        query=r'''
            n: All Qualifiers Combined
            i: host.instance
            t:
                - numeric:vpDdr
                - counter:vd
                - large_numeric:r
            v:
                - var1:vpdDr
                - var2:vp
                - var3:dr
        ''',
        expect_needs_prev=True,
        expect_query_full_inst_names=["host.instance"],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={
            LmcVarType.NUMERIC: q_v | q_p | q_D | q_d | q_r,
            LmcVarType.COUNTER: q_v | q_d,
            LmcVarType.LARGE_NUMERIC: q_r
        },
        expect_query_exclude_types=set(),
        expect_query_include_vars={
            "var1": q_v | q_p | q_d | q_D | q_r,
            "var2": q_v | q_p,
            "var3": q_d | q_r
        },
        expect_query_exclude_vars=set()
    ),
    LmcrecQuerySelectorInitTestCase(
        name="MinimalQuery",
        description="Minimal query with only name",
        query=r'''
            n: Minimal Query
        ''',
        expect_needs_prev=False,
        expect_query_full_inst_names=[],
        expect_query_prefix_inst_names=[],
        expect_query_inst_re=[],
        expect_query_class_name=None,
        expect_query_include_types={},
        expect_query_exclude_types=set(),
        expect_query_include_vars={},
        expect_query_exclude_vars=set()
    ),
]

# fmt: on
