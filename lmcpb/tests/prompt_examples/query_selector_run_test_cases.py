"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

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
]
