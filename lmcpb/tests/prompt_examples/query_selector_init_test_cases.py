"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from lmcrec.playback.codec import LmcVarType

from .query_selector_def import (
    LmcrecQuerySelectorInitTestCase,
    q_d,
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
                n:  "Indented JSON mix",
                i: [
                    host.1.ads.part1.part2,
                    ~.part3,
                    "/host\\.1\\.ads\\.\\S+\\.part4/",
                ],
                c: class,
                T:  boolean_config,
                t: [
                    gauge,
                    numeric:dr,
                ],
                V:  exclude_var,
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
]

# fmt: on
