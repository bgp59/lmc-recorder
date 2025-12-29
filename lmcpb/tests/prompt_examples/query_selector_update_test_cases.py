"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from lmcrec.playback.codec import LmcVarType
from lmcrec.playback.query.query_selector import LmcrecQueryClassSelector

from .query_selector_def import (
    LmcrecQueryIntervalStateCacheBuilder,
    LmcrecQuerySelectorUpdateTestCase,
    q_v,
)

update_test_cases = [
    LmcrecQuerySelectorUpdateTestCase(
        name="OneInstanceOneVar",
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
                var_names=["gauge1", "num1", ],
                inst_names={"host.1.proc.part1", "host.1.proc.part2"},
                last_update_ts=123456,
            )
        }
    ),
]

# fmt: on
