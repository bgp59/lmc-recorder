# Prompt: .github/prompts/query_selector_run_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from lmcrec.playback.codec import LmcVarType
from lmcrec.playback.query.query_selector import LmcrecQueryClassResult

from .query_selector_def import (
    LmcrecQueryIntervalStateCacheBuilder,
    LmcrecQuerySelectorRunTestCase,
)

run_test_cases = [
    LmcrecQuerySelectorRunTestCase(
        name="BaseCase",
        description="Basic query with single instance and variable",
        query=r'''
            n: Base Case
            i: host.1.proc.part1
            v: var1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class", {
                        "var1": 42,
                    }
                )
            ]
        ),
        expect_result={
            "class": LmcrecQueryClassResult(
                var_names=["var1"],
                vals_by_inst={
                    "host.1.proc.part1": [42]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="BaseCaseDelta",
        description="Query with adjusted delta for counter variable",
        query=r'''
            n: Base case delta
            i: host.1.proc.part1
            v: var1:d
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class", {
                        "var1": (42, 41)
                    }
                )
            ],
        ),
        expect_result={
            "class": LmcrecQueryClassResult(
                var_names=["var1:d"],
                vals_by_inst={
                    "host.1.proc.part1": [1]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="InstancePrefixMatch",
        description="Query matching instances by prefix",
        query=r'''
            n: Instance Prefix Match
            i: ~.part1
            v: counter1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": 100}),
                ("host.2.proc.part1", "class1", {"counter1": 200}),
                ("host.3.proc.part2", "class1", {"counter1": 300}),
            ]
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1"],
                vals_by_inst={
                    "host.1.proc.part1": [100],
                    "host.2.proc.part1": [200],
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="InstanceRegexpMatch",
        description="Query matching instances by regular expression",
        query=r'''
            n: Instance Regexp Match
            i: /^host\.[12]\.proc/
            v: metric1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"metric1": 10}),
                ("host.2.proc.part2", "class1", {"metric1": 20}),
                ("host.3.proc.part1", "class1", {"metric1": 30}),
            ]
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["metric1"],
                vals_by_inst={
                    "host.1.proc.part1": [10],
                    "host.2.proc.part2": [20],
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="MultipleQualifiers",
        description="Query with multiple value qualifiers for the same variable",
        query=r'''
            n: Multiple Qualifiers
            i: host.1.proc.part1
            v: counter1:vpd
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (150, 100)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1", "counter1:p", "counter1:d"],
                vals_by_inst={
                    "host.1.proc.part1": [150, 100, 50]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="AdjustedDeltaWithRollover",
        description="Adjusted delta should apply rollover correction for negative delta",
        query=r'''
            n: Adjusted Delta With Rollover
            i: host.1.proc.part1
            v: counter1:d
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (100, 4294967290)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1:d"],
                vals_by_inst={
                    "host.1.proc.part1": [106]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="UnadjustedDeltaNegative",
        description="Unadjusted delta should not apply correction for negative delta",
        query=r'''
            n: Unadjusted Delta Negative
            i: host.1.proc.part1
            v: counter1:D
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (100, 4294967290)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1:D"],
                vals_by_inst={
                    "host.1.proc.part1": [-4294967190]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="RateCalculation",
        description="Rate calculation for counter variable",
        query=r'''
            n: Rate Calculation
            i: host.1.proc.part1
            v: counter1:r
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (200, 100)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            },
            d_time=10.0,
            ts=20.0
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1:r"],
                vals_by_inst={
                    "host.1.proc.part1": [10.0]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="DeltaForNonDeltaType",
        description="Delta qualifiers yield None for non-delta variable types",
        query=r'''
            n: Delta For Non Delta Type
            i: host.1.proc.part1
            v: str_var:dDr
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"str_var": ("value2", "value1")})
            ],
            classes={
                "class1": (0, [("str_var", LmcVarType.STRING)])
            },
            d_time=5.0
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["str_var:d", "str_var:D", "str_var:r"],
                vals_by_inst={
                    "host.1.proc.part1": [None, None, None]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="MixedVariableTypes",
        description="Query with mix of different variable types",
        query=r'''
            n: Mixed Variable Types
            i: host.1.proc.part1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "bool_var": True,
                        "counter1": 500,
                        "str_var": "hello",
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("bool_var", LmcVarType.BOOLEAN),
                    ("counter1", LmcVarType.COUNTER),
                    ("str_var", LmcVarType.STRING),
                ])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["bool_var", "counter1", "str_var"],
                vals_by_inst={
                    "host.1.proc.part1": [True, 500, "hello"]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="TypeInclusionFilter",
        description="Query with type inclusion filter",
        query=r'''
            n: Type Inclusion Filter
            i: host.1.proc.part1
            t: counter
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "bool_var": True,
                        "counter1": 100,
                        "counter2": 200,
                        "str_var": "test",
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("bool_var", LmcVarType.BOOLEAN),
                    ("counter1", LmcVarType.COUNTER),
                    ("counter2", LmcVarType.COUNTER),
                    ("str_var", LmcVarType.STRING),
                ])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1", "counter2"],
                vals_by_inst={
                    "host.1.proc.part1": [100, 200]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="TypeInclusionWithQualifiers",
        description="Query with type inclusion and value qualifiers",
        query=r'''
            n: Type Inclusion With Qualifiers
            i: host.1.proc.part1
            t: numeric:vd
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "metric1": (150, 100),
                        "metric2": (300, 250),
                        "str_var": "test",
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("metric1", LmcVarType.NUMERIC),
                    ("metric2", LmcVarType.NUMERIC),
                    ("str_var", LmcVarType.STRING),
                ])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["metric1", "metric1:d", "metric2", "metric2:d"],
                vals_by_inst={
                    "host.1.proc.part1": [150, 50, 300, 50]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="VariableExclusionFilter",
        description="Query with variable exclusion filter",
        query=r'''
            n: Variable Exclusion Filter
            i: host.1.proc.part1
            V: [excluded_var1, excluded_var2]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "excluded_var1": 10,
                        "excluded_var2": 20,
                        "included_var": 30,
                    }
                )
            ]
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["included_var"],
                vals_by_inst={
                    "host.1.proc.part1": [30]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="MultipleInstancesMultipleClasses",
        description="Query matching multiple instances across multiple classes",
        query=r'''
            n: Multiple Instances Multiple Classes
            i: /^host\./
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"var1": 10}),
                ("host.2.proc.part1", "class1", {"var1": 20}),
                ("host.1.proc.part2", "class2", {"var2": 30}),
                ("host.2.proc.part2", "class2", {"var2": 40}),
            ],
            classes={
                "class1": (0, [("var1", LmcVarType.NUMERIC)]),
                "class2": (0, [("var2", LmcVarType.NUMERIC)]),
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["var1"],
                vals_by_inst={
                    "host.1.proc.part1": [10],
                    "host.2.proc.part1": [20],
                }
            ),
            "class2": LmcrecQueryClassResult(
                var_names=["var2"],
                vals_by_inst={
                    "host.1.proc.part2": [30],
                    "host.2.proc.part2": [40],
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="ComplexMixedScenario",
        description="Complex query with prefix match, qualified variables, and mixed types",
        query=r'''
            n: Complex Mixed Scenario
            i: ~.service
            v: [counter1:vdr, status]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.app.service", "service_class", {
                        "counter1": (1000, 800),
                        "status": "active",
                    }
                ),
                (
                    "host.2.app.service", "service_class", {
                        "counter1": (2000, 1900),
                        "status": "inactive",
                    }
                ),
            ],
            classes={
                "service_class": (0, [
                    ("counter1", LmcVarType.COUNTER),
                    ("status", LmcVarType.STRING),
                ])
            },
            d_time=10.0,
            ts=100.0
        ),
        expect_result={
            "service_class": LmcrecQueryClassResult(
                var_names=["counter1", "counter1:d", "counter1:r", "status"],
                vals_by_inst={
                    "host.1.app.service": [1000, 200, 20.0, "active"],
                    "host.2.app.service": [2000, 100, 10.0, "inactive"],
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="LargeNumericRollover",
        description="Adjusted delta with rollover for large numeric type",
        query=r'''
            n: Large Numeric Rollover
            i: host.1.proc.part1
            v: large_counter:d
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"large_counter": (100, 18446744073709551610)})
            ],
            classes={
                "class1": (0, [("large_counter", LmcVarType.LARGE_NUMERIC)])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["large_counter:d"],
                vals_by_inst={
                    "host.1.proc.part1": [106]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="AlphabeticalSorting",
        description="Verify variables are sorted alphabetically (case-insensitive)",
        query=r'''
            n: Alphabetical Sorting
            i: host.1.proc.part1
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "Zebra": 1,
                        "apple": 2,
                        "Banana": 3,
                        "cherry": 4,
                    }
                )
            ]
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["apple", "Banana", "cherry", "Zebra"],
                vals_by_inst={
                    "host.1.proc.part1": [2, 3, 4, 1]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="RateWithoutDeltaTime",
        description="Rate calculation yields None when delta time is not available",
        query=r'''
            n: Rate Without Delta Time
            i: host.1.proc.part1
            v: counter1:r
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (200, 100)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            },
            d_time=None
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1:r"],
                vals_by_inst={
                    "host.1.proc.part1": [None]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="TypeExclusionFilter",
        description="Query with type exclusion filter",
        query=r'''
            n: Type Exclusion Filter
            i: host.1.proc.part1
            T: [string, boolean]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "bool_var": False,
                        "counter1": 100,
                        "counter2": 200,
                        "str_var": "excluded",
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("bool_var", LmcVarType.BOOLEAN),
                    ("counter1", LmcVarType.COUNTER),
                    ("counter2", LmcVarType.COUNTER),
                    ("str_var", LmcVarType.STRING),
                ])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1", "counter2"],
                vals_by_inst={
                    "host.1.proc.part1": [100, 200]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="QualifierOrderingMultipleVars",
        description="Verify qualifier ordering with multiple variables having different qualifiers",
        query=r'''
            n: Qualifier Ordering Multiple Vars
            i: host.1.proc.part1
            v: [varA:pd, varB:rd, varC:vp]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "varA": (200, 100),
                        "varB": (500, 400),
                        "varC": (800, 700),
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("varA", LmcVarType.COUNTER),
                    ("varB", LmcVarType.NUMERIC),
                    ("varC", LmcVarType.COUNTER),
                ])
            },
            d_time=10.0
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["varA:p", "varA:d", "varB:d", "varB:r", "varC", "varC:p"],
                vals_by_inst={
                    "host.1.proc.part1": [100, 100, 100, 10.0, 800, 700]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="AllQualifiersOrdered",
        description="Verify all qualifiers are ordered correctly per var_val_qual_flag_order",
        query=r'''
            n: All Qualifiers Ordered
            i: host.1.proc.part1
            v: counter1:vpdDr
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (250, 200)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            },
            d_time=5.0
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1", "counter1:p", "counter1:d", "counter1:D", "counter1:r"],
                vals_by_inst={
                    "host.1.proc.part1": [250, 200, 50, 50, 10.0]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="NoInstanceMatch",
        description="Query that matches no instances returns empty result",
        query=r'''
            n: No Instance Match
            i: /^nonexistent\./
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"var1": 10}),
            ]
        ),
        expect_result={}
    ),
    LmcrecQuerySelectorRunTestCase(
        name="ClassNameFilter",
        description="Query filtering by specific class name",
        query=r'''
            n: Class Name Filter
            c: specific_class
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "specific_class", {"var1": 10}),
                ("host.1.proc.part2", "other_class", {"var2": 20}),
            ]
        ),
        expect_result={
            "specific_class": LmcrecQueryClassResult(
                var_names=["var1"],
                vals_by_inst={
                    "host.1.proc.part1": [10]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="MixedPrefixAndRegexp",
        description="Query with both prefix and regexp instance matching",
        query=r'''
            n: Mixed Prefix And Regexp
            i: [~.service, /^host\.1\./]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.app.service", "class1", {"metric": 10}),
                ("host.1.db.part1", "class1", {"metric": 20}),
                ("host.2.app.service", "class1", {"metric": 30}),
                ("host.3.db.part2", "class1", {"metric": 40}),
            ]
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["metric"],
                vals_by_inst={
                    "host.1.app.service": [10],
                    "host.1.db.part1": [20],
                    "host.2.app.service": [30],
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="DeltaWithZeroPrevValue",
        description="Delta calculation with zero previous value",
        query=r'''
            n: Delta With Zero Prev Value
            i: host.1.proc.part1
            v: counter1:vdD
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"counter1": (100, 0)})
            ],
            classes={
                "class1": (0, [("counter1", LmcVarType.COUNTER)])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["counter1", "counter1:d", "counter1:D"],
                vals_by_inst={
                    "host.1.proc.part1": [100, 100, 100]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="CaseInsensitiveSortingWithQualifiers",
        description="Verify case-insensitive alphabetical sorting with mixed case variable names and qualifiers",
        query=r'''
            n: Case Insensitive Sorting With Qualifiers
            i: host.1.proc.part1
            v: [Zebra:d, apple:d, BANANA:d]
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                (
                    "host.1.proc.part1", "class1", {
                        "Zebra": (100, 90),
                        "apple": (200, 190),
                        "BANANA": (300, 290),
                    }
                )
            ],
            classes={
                "class1": (0, [
                    ("Zebra", LmcVarType.COUNTER),
                    ("apple", LmcVarType.COUNTER),
                    ("BANANA", LmcVarType.COUNTER),
                ])
            }
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["apple:d", "BANANA:d", "Zebra:d"],
                vals_by_inst={
                    "host.1.proc.part1": [10, 10, 10]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="BooleanVariablesNoDeltas",
        description="Boolean variables should return None for delta and rate qualifiers",
        query=r'''
            n: Boolean Variables No Deltas
            i: host.1.proc.part1
            v: bool_var:vpdDr
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host.1.proc.part1", "class1", {"bool_var": (True, False)})
            ],
            classes={
                "class1": (0, [("bool_var", LmcVarType.BOOLEAN)])
            },
            d_time=10.0
        ),
        expect_result={
            "class1": LmcrecQueryClassResult(
                var_names=["bool_var", "bool_var:p", "bool_var:d", "bool_var:D", "bool_var:r"],
                vals_by_inst={
                    "host.1.proc.part1": [True, False, None, None, None]
                }
            )
        }
    ),
    LmcrecQuerySelectorRunTestCase(
        name="ComplexMultiClassMultiInstance",
        description="Complex scenario with multiple classes, instances, and mixed qualifiers",
        query=r'''
            n: Complex Multi Class Multi Instance
            i: /^(host1|host2)\./
        ''',
        query_state_cache=LmcrecQueryIntervalStateCacheBuilder(
            instances=[
                ("host1.service.app", "service_class", {
                    "counter1": (1000, 900),
                    "status": "running",
                }),
                ("host2.service.app", "service_class", {
                    "counter1": (2000, 1800),
                    "status": "stopped",
                }),
                ("host1.db.main", "db_class", {
                    "queries": (5000, 4900),
                    "connections": 50,
                }),
                ("host2.db.main", "db_class", {
                    "queries": (6000, 5900),
                    "connections": 60,
                }),
            ],
            classes={
                "service_class": (0, [
                    ("counter1", LmcVarType.COUNTER),
                    ("status", LmcVarType.STRING),
                ]),
                "db_class": (0, [
                    ("queries", LmcVarType.COUNTER),
                    ("connections", LmcVarType.NUMERIC),
                ]),
            }
        ),
        expect_result={
            "service_class": LmcrecQueryClassResult(
                var_names=["counter1", "status"],
                vals_by_inst={
                    "host1.service.app": [1000, "running"],
                    "host2.service.app": [2000, "stopped"],
                }
            ),
            "db_class": LmcrecQueryClassResult(
                var_names=["connections", "queries"],
                vals_by_inst={
                    "host1.db.main": [50, 5000],
                    "host2.db.main": [60, 6000],
                }
            )
        }
    ),
]
