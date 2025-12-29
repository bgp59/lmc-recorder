# Prompt: .github/prompts/query_selector_update_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from lmcrec.playback.codec import LmcVarType
from lmcrec.playback.query.query_selector import LmcrecQueryClassSelector

from .query_selector_def import (
    LmcrecQueryIntervalStateCacheBuilder,
    LmcrecQuerySelectorUpdateTestCase,
    q_d,
    q_D,
    q_p,
    q_r,
    q_v,
)

update_test_cases = [
    LmcrecQuerySelectorUpdateTestCase(
        name="OneInstanceOneVar",
        description="Single instance with one variable",
        query=r'''
            n: OneInstanceOneVar
            i: host.1.proc.part1
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
                ("host.1.proc.other", "class2"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC), 
                        ("gauge1", LmcVarType.GAUGE),
                    ],
                ),
                "class2": (
                    123456,
                    [],
                )
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="MultipleInstancesAndVars",
        description="Multiple instances with multiple variables",
        query=r'''
            n: MultipleInstancesAndVars
            i: 
               - host.1.proc.part1
               - host.1.proc.part2
            v: 
               - num1
               - gauge1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
                ("host.1.proc.other", "class2"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC), 
                        ("gauge1", LmcVarType.GAUGE),
                    ],
                ),
                "class2": (
                    123456,
                    [],
                )
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(1, q_v), (0, q_v)],
                var_names=["gauge1", "num1"],
                inst_names={"host.1.proc.part1", "host.1.proc.part2"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="SinglePrefixInstance",
        description="Single instance prefix match",
        query=r'''
            n: SinglePrefixInstance
            i: ~.part1
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.2.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.2.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="MultiplePrefixInstances",
        description="Multiple instance prefix matches",
        query=r'''
            n: MultiplePrefixInstances
            i: 
               - ~.part1
               - ~.other
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.other", "class1"),
                ("host.1.proc.part2", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.1.proc.other"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="SingleRegexpInstance",
        description="Single instance regexp match",
        query=r'''
            n: SingleRegexpInstance
            i: /^host\.1\.proc\.part\d+$/
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
                ("host.1.proc.other", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.1.proc.part2"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="RegexpWithDigitStarPattern",
        description="Regexp with \\d* pattern matching variable number of digits",
        query=r'''
            n: RegexpWithDigitStarPattern
            i: /host\.\d+\.proc\.part\d*$/
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.22.proc.part333", "class1"),
                ("host.33.proc.part", "class1"),
                ("host.1.proc.other", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.22.proc.part333", "host.33.proc.part"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="MultipleRegexpInstances",
        description="Multiple instance regexp matches",
        query=r'''
            n: MultipleRegexpInstances
            i: 
               - /^host\.1\.proc\.part\d+$/
               - /^host\.1\.proc\.other$/
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
                ("host.1.proc.other", "class1"),
                ("host.1.proc.ignored", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.1.proc.part2", "host.1.proc.other"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="MixedInstanceSelection",
        description="Mix of full name, prefix and regexp instance selection",
        query=r'''
            n: MixedInstanceSelection
            i: 
               - host.1.proc.part1
               - ~.part2
               - /^host\.3\.proc\.part\d+$/
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.2.proc.part2", "class1"),
                ("host.3.proc.part5", "class1"),
                ("host.1.proc.other", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.2.proc.part2", "host.3.proc.part5"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="WithClassSelection",
        description="Filter instances by class name",
        query=r'''
            n: WithClassSelection
            c: class1
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
                ("host.1.proc.other", "class2"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
                "class2": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1", "host.1.proc.part2"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="NoClassSelection",
        description="No class filter - select all instances",
        query=r'''
            n: NoClassSelection
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.other", "class2"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
                "class2": (
                    123457,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123458,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            ),
            "class2": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.other"},
                last_update_ts=123457,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="QualifiedVariables",
        description="Variables with value qualifiers (prev, delta, rate)",
        query=r'''
            n: QualifiedVariables
            i: host.1.proc.part1
            v: 
               - counter1:vpr
               - num1:vpd
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("counter1", LmcVarType.COUNTER),
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v | q_p | q_r), (1, q_v | q_p | q_d)],
                var_names=["counter1", "counter1:p", "counter1:r", "num1", "num1:p", "num1:d"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="QualifiedVariablesAllFlags",
        description="Variables with all value qualifier flags",
        query=r'''
            n: QualifiedVariablesAllFlags
            i: host.1.proc.part1
            v: counter1:vpdDr
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("counter1", LmcVarType.COUNTER),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v | q_p | q_d | q_D | q_r)],
                var_names=["counter1", "counter1:p", "counter1:d", "counter1:D", "counter1:r"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="SimpleTypes",
        description="Include variables by simple type",
        query=r'''
            n: SimpleTypes
            i: host.1.proc.part1
            t: 
               - numeric
               - counter
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("counter1", LmcVarType.COUNTER),
                        ("gauge1", LmcVarType.GAUGE),
                        ("num1", LmcVarType.NUMERIC),
                        ("str1", LmcVarType.STRING),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v), (2, q_v)],
                var_names=["counter1", "num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="QualifiedTypes",
        description="Include variables by type with qualifiers",
        query=r'''
            n: QualifiedTypes
            i: host.1.proc.part1
            t: 
               - numeric:vp
               - counter:vdDr
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("counter1", LmcVarType.COUNTER),
                        ("counter2", LmcVarType.COUNTER),
                        ("gauge1", LmcVarType.GAUGE),
                        ("num1", LmcVarType.NUMERIC),
                        ("num2", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[
                    (0, q_v | q_d | q_D | q_r),
                    (1, q_v | q_d | q_D | q_r),
                    (3, q_v | q_p),
                    (4, q_v | q_p),
                ],
                var_names=[
                    "counter1", "counter1:d", "counter1:D", "counter1:r",
                    "counter2", "counter2:d", "counter2:D", "counter2:r",
                    "num1", "num1:p",
                    "num2", "num2:p",
                ],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="NoInstances",
        description="No instances match the selection criteria",
        query=r'''
            n: NoInstances
            i: host.nonexistent
            v: num1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={}
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="NoVariables",
        description="No variables match the selection criteria",
        query=r'''
            n: NoVariables
            i: host.1.proc.part1
            v: nonexistent
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_chain=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[],
                var_names=[],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="NewInstanceAfterPrimer",
        description="New instance added after primer update",
        query=r'''
            n: NewInstanceAfterPrimer
            i: host.1.proc.part1
            v: num1
        ''',
        selector_primer=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123456,
        ),
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_inst=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="DeletedInstanceAfterPrimer",
        description="Instance deleted after primer update",
        query=r'''
            n: DeletedInstanceAfterPrimer
            v: num1
        ''',
        selector_primer=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.1.proc.part2", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123456,
        ),
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            deleted_inst=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v)],
                var_names=["num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123456,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="NewClassDefinitionAfterPrimer",
        description="New class definition (variable added) after primer update",
        query=r'''
            n: NewClassDefinitionAfterPrimer
            i: host.1.proc.part1
        ''',
        selector_primer=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123456,
        ),
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
            ],
            classes={
                "class1": (
                    123457,
                    [
                        ("gauge1", LmcVarType.GAUGE),
                        ("num1", LmcVarType.NUMERIC),
                    ],
                ),
            },
            ts=123457,
            new_class_def=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[(0, q_v), (1, q_v)],
                var_names=["gauge1", "num1"],
                inst_names={"host.1.proc.part1"},
                last_update_ts=123457,
            )
        }
    ),
    LmcrecQuerySelectorUpdateTestCase(
        name="ComplexMixedScenario",
        description="Complex scenario with multiple selection types, qualifiers, new/deleted instances",
        query=r'''
            n: ComplexMixedScenario
            i: 
               - host.1.proc.part1
               - ~.part2
               - /^host\.3\.proc\.part\d*$/
            t: 
               - counter:vdDr
               - numeric:vp
            v: 
               - gauge1
               - str1:v
            V: 
               - bool1
        ''',
        selector_primer=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.2.proc.part2", "class1"),
                ("host.3.proc.part3", "class1"),
                ("host.4.proc.part2", "class1"),
            ],
            classes={
                "class1": (
                    123456,
                    [
                        ("bool1", LmcVarType.BOOLEAN),
                        ("counter1", LmcVarType.COUNTER),
                        ("gauge1", LmcVarType.GAUGE),
                        ("num1", LmcVarType.NUMERIC),
                        ("str1", LmcVarType.STRING),
                    ],
                ),
            },
            ts=123456,
        ),
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1"),
                ("host.2.proc.part2", "class1"),
                ("host.3.proc.part3", "class1"),
                ("host.3.proc.part", "class1"),
            ],
            classes={
                "class1": (
                    123457,
                    [
                        ("bool1", LmcVarType.BOOLEAN),
                        ("counter1", LmcVarType.COUNTER),
                        ("counter2", LmcVarType.COUNTER),
                        ("gauge1", LmcVarType.GAUGE),
                        ("num1", LmcVarType.NUMERIC),
                        ("num2", LmcVarType.NUMERIC),
                        ("str1", LmcVarType.STRING),
                    ],
                ),
            },
            ts=123457,
            new_inst=True,
            deleted_inst=True,
            new_class_def=True,
        ),
        expect_selector={
            "class1": LmcrecQueryClassSelector(
                var_handling_info=[
                    (1, q_v | q_d | q_D | q_r),
                    (2, q_v | q_d | q_D | q_r),
                    (3, q_v),
                    (4, q_v | q_p),
                    (5, q_v | q_p),
                    (6, q_v),
                ],
                var_names=[
                    "counter1", "counter1:d", "counter1:D", "counter1:r",
                    "counter2", "counter2:d", "counter2:D", "counter2:r",
                    "gauge1",
                    "num1", "num1:p",
                    "num2", "num2:p",
                    "str1",
                ],
                inst_names={"host.1.proc.part1", "host.2.proc.part2", "host.3.proc.part3", "host.3.proc.part"},
                last_update_ts=123457,
            )
        }
    ),
]

# fmt: on
