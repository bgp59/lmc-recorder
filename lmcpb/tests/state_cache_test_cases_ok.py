# Prompt: .github/prompts/state_cache_test_cases_ok.py.prompt.md
# Model: Claude Sonnet 4.5
"""Test cases for test_lmcrec_state_cache_ok"""

# noqa
# fmt: off

from lmcrec.playback.cache.state_cache import (
    LmcrecClassCacheEntry,
    LmcrecInstCacheEntry,
    LmcrecVarInfo,
)
from lmcrec.playback.codec.decoder import LmcRecord, LmcrecType, LmcVarType

from .state_cache_def import LmcrecStateCacheTestCase

test_cases_ok = [
    LmcrecStateCacheTestCase(
        name="OneInstOneClassFewTypes",
        description="Single instance with numeric and string variables",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=1000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Class1"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.NUMERIC, name="num11"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=12, lmc_var_type=LmcVarType.STRING, name="string12"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=113, parent_inst_id=0, name="inst1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=42, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value="twelve"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.40),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Class1", class_id=1,
                var_info_by_id={
                    11: LmcrecVarInfo(name="num11", var_id=11, var_type=LmcVarType.NUMERIC),
                    12: LmcrecVarInfo(name="string12", var_id=12, var_type=LmcVarType.STRING, max_size=6),
                },
                last_update_ts=1000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="inst1", inst_id=113, class_id=1, parent_inst_id=0,
                vars={
                    11: 42,
                    12: "twelve",
                },
            )
        ],
        expect_inst_by_class_name={
            "Class1": {"inst1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="MultipleClassesAndInstances",
        description="Multiple classes with multiple instances each",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=2000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Sensor"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.GAUGE, name="temperature"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.STRING, name="location"),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=2, name="Controller"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=2, var_id=20, lmc_var_type=LmcVarType.BOOLEAN, name="active"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=2, var_id=21, lmc_var_type=LmcVarType.COUNTER, name="cycles"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="sensor1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=25, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value="room1"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=101, parent_inst_id=0, name="sensor2"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=30, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value="room2"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=2, inst_id=200, parent_inst_id=0, name="ctrl1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=20, value=True, file_record_type=LmcrecType.VAR_BOOL_TRUE),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=21, value=100, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.50),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Sensor", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="temperature", var_id=10, var_type=LmcVarType.GAUGE),
                    11: LmcrecVarInfo(name="location", var_id=11, var_type=LmcVarType.STRING, max_size=5),
                },
                last_update_ts=2000,
            ),
            LmcrecClassCacheEntry(
                name="Controller", class_id=2,
                var_info_by_id={
                    20: LmcrecVarInfo(name="active", var_id=20, var_type=LmcVarType.BOOLEAN),
                    21: LmcrecVarInfo(name="cycles", var_id=21, var_type=LmcVarType.COUNTER),
                },
                last_update_ts=2000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="sensor1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: 25,
                    11: "room1",
                },
            ),
            LmcrecInstCacheEntry(
                name="sensor2", inst_id=101, class_id=1, parent_inst_id=0,
                vars={
                    10: 30,
                    11: "room2",
                },
            ),
            LmcrecInstCacheEntry(
                name="ctrl1", inst_id=200, class_id=2, parent_inst_id=0,
                vars={
                    20: True,
                    21: 100,
                },
            )
        ],
        expect_inst_by_class_name={
            "Sensor": {"sensor1", "sensor2"},
            "Controller": {"ctrl1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="ParentChildInstances",
        description="Instance hierarchy with parent-child relationships",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=3000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Parent"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.STRING, name="name"),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=2, name="Child"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=2, var_id=20, lmc_var_type=LmcVarType.NUMERIC, name="value"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="parent1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="MainParent"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=2, inst_id=200, parent_inst_id=100, name="child1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=20, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=2, inst_id=201, parent_inst_id=100, name="child2"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=20, value=75, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.45),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Parent", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="name", var_id=10, var_type=LmcVarType.STRING, max_size=10),
                },
                last_update_ts=3000,
            ),
            LmcrecClassCacheEntry(
                name="Child", class_id=2,
                var_info_by_id={
                    20: LmcrecVarInfo(name="value", var_id=20, var_type=LmcVarType.NUMERIC),
                },
                last_update_ts=3000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="parent1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: "MainParent",
                },
            ),
            LmcrecInstCacheEntry(
                name="child1", inst_id=200, class_id=2, parent_inst_id=100,
                vars={
                    20: 50,
                },
            ),
            LmcrecInstCacheEntry(
                name="child2", inst_id=201, class_id=2, parent_inst_id=100,
                vars={
                    20: 75,
                },
            )
        ],
        expect_inst_by_class_name={
            "Parent": {"parent1"},
            "Child": {"child1", "child2"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="SetInstIdAndUpdate",
        description="Update existing instance using SET_INST_ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=4000),
            LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=100),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=100, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=3995),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        have_prev=True,
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Counter", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="count", var_id=10, var_type=LmcVarType.COUNTER),
                },
                last_update_ts=3995,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="counter1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: 100,
                },
                prev_vars={
                    10: 50,
                },
            )
        ],
        expect_inst_by_class_name={
            "Counter": {"counter1"},
        },
    ),
    LmcrecStateCacheTestCase(
        name="BooleanVariables",
        description="Test boolean true and false values",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=5000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Flags"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.BOOLEAN, name="enabled"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.BOOLEAN, name="disabled"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="flags1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=True, file_record_type=LmcrecType.VAR_BOOL_TRUE),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=False, file_record_type=LmcrecType.VAR_BOOL_FALSE),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.30),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Flags", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="enabled", var_id=10, var_type=LmcVarType.BOOLEAN),
                    11: LmcrecVarInfo(name="disabled", var_id=11, var_type=LmcVarType.BOOLEAN),
                },
                last_update_ts=5000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="flags1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: True,
                    11: False,
                },
            )
        ],
        expect_inst_by_class_name={
            "Flags": {"flags1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="EmptyStringAndZeroValue",
        description="Test empty string and zero numeric values",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=6000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Edge"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.STRING, name="text"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.NUMERIC, name="num"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="edge1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="", file_record_type=LmcrecType.VAR_EMPTY_STRING),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=0, file_record_type=LmcrecType.VAR_ZERO_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.28),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Edge", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="text", var_id=10, var_type=LmcVarType.STRING, max_size=0),
                    11: LmcrecVarInfo(name="num", var_id=11, var_type=LmcVarType.NUMERIC),
                },
                last_update_ts=6000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="edge1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: "",
                    11: 0,
                },
            )
        ],
        expect_inst_by_class_name={
            "Edge": {"edge1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="InstanceDeletion",
        description="Creating and then deleting an instance",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=7000),
            LmcRecord(record_type=LmcrecType.DELETE_INST_ID, inst_id=200),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.35),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=6998),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Temp"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.STRING, name="data"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=200, parent_inst_id=0, name="temp1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="temporary"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.40),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Temp", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="data", var_id=10, var_type=LmcVarType.STRING, max_size=9),
                },
                last_update_ts=6998,
            )
        ],
        expect_inst_cache=[],
        expect_inst_by_class_name={
            "Temp": set(),
        },
        expect_deleted_inst=True,
    ),
    LmcrecStateCacheTestCase(
        name="NegativeNumeric",
        description="Test negative numeric values with signed and unsigned encoding",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=8000),
            LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=100),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=55, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=-60, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value=65, file_record_type=LmcrecType.VAR_SINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=7987),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="NegativeNum"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.NUMERIC, name="num1"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.NUMERIC, name="num2"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=12, lmc_var_type=LmcVarType.NUMERIC, name="num3"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=13, lmc_var_type=LmcVarType.NUMERIC, name="num4"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="negatives"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_SINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=-55, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=60, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value=65, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="NegativeNum", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="num1", var_id=10, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    11: LmcrecVarInfo(name="num2", var_id=11, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    12: LmcrecVarInfo(name="num3", var_id=12, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    13: LmcrecVarInfo(name="num4", var_id=13, var_type=LmcVarType.NUMERIC, neg_vals=True),
                },
                last_update_ts=7987,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="negatives", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: 50,
                    11: 55,
                    12: -60,
                    13: 65,
                },
            )
        ],
        expect_inst_by_class_name={
            "NegativeNum": {"negatives"},
        },
    ),
    LmcrecStateCacheTestCase(
        name="AllVarTypes",
        description="Test all LMC variable types in a single class",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=9000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="AllTypes"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.BOOLEAN, name="bool_var"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.BOOLEAN_CONFIG, name="bool_cfg"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=12, lmc_var_type=LmcVarType.COUNTER, name="counter_var"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=13, lmc_var_type=LmcVarType.GAUGE, name="gauge_var"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=14, lmc_var_type=LmcVarType.GAUGE_CONFIG, name="gauge_cfg"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=15, lmc_var_type=LmcVarType.NUMERIC, name="numeric_var"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=16, lmc_var_type=LmcVarType.LARGE_NUMERIC, name="large_num"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=17, lmc_var_type=LmcVarType.NUMERIC_RANGE, name="num_range"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=18, lmc_var_type=LmcVarType.NUMERIC_CONFIG, name="num_cfg"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=19, lmc_var_type=LmcVarType.STRING, name="string_var"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=20, lmc_var_type=LmcVarType.STRING_CONFIG, name="string_cfg"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="alltypes1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=True, file_record_type=LmcrecType.VAR_BOOL_TRUE),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=False, file_record_type=LmcrecType.VAR_BOOL_FALSE),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=123, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value=456, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=14, value=789, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=15, value=111, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=16, value=999999, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=17, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=18, value=25, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=19, value="test"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=20, value="config"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.55),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="AllTypes", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="bool_var", var_id=10, var_type=LmcVarType.BOOLEAN),
                    11: LmcrecVarInfo(name="bool_cfg", var_id=11, var_type=LmcVarType.BOOLEAN_CONFIG),
                    12: LmcrecVarInfo(name="counter_var", var_id=12, var_type=LmcVarType.COUNTER),
                    13: LmcrecVarInfo(name="gauge_var", var_id=13, var_type=LmcVarType.GAUGE),
                    14: LmcrecVarInfo(name="gauge_cfg", var_id=14, var_type=LmcVarType.GAUGE_CONFIG),
                    15: LmcrecVarInfo(name="numeric_var", var_id=15, var_type=LmcVarType.NUMERIC),
                    16: LmcrecVarInfo(name="large_num", var_id=16, var_type=LmcVarType.LARGE_NUMERIC),
                    17: LmcrecVarInfo(name="num_range", var_id=17, var_type=LmcVarType.NUMERIC_RANGE),
                    18: LmcrecVarInfo(name="num_cfg", var_id=18, var_type=LmcVarType.NUMERIC_CONFIG),
                    19: LmcrecVarInfo(name="string_var", var_id=19, var_type=LmcVarType.STRING, max_size=4),
                    20: LmcrecVarInfo(name="string_cfg", var_id=20, var_type=LmcVarType.STRING_CONFIG, max_size=6),
                },
                last_update_ts=9000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="alltypes1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: True,
                    11: False,
                    12: 123,
                    13: 456,
                    14: 789,
                    15: 111,
                    16: 999999,
                    17: 50,
                    18: 25,
                    19: "test",
                    20: "config",
                },
            )
        ],
        expect_inst_by_class_name={
            "AllTypes": {"alltypes1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="RedefineInstIdAndUpdate",
        description="Redefine instance with same ID and update variables",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=10000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=100, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=9995),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Counter", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="count", var_id=10, var_type=LmcVarType.COUNTER),
                },
                last_update_ts=9995,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="counter1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: 100,
                },
            )
        ],
        expect_inst_by_class_name={
            "Counter": {"counter1"},
        },
    ),
    LmcrecStateCacheTestCase(
        name="MultipleVariableUpdates",
        description="Update multiple variables of the same instance in one scan",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=11000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Monitor"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.GAUGE, name="cpu"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.GAUGE, name="memory"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=12, lmc_var_type=LmcVarType.GAUGE, name="disk"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=13, lmc_var_type=LmcVarType.STRING, name="status"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="monitor1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=45, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=70, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=85, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value="healthy"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.38),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Monitor", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="cpu", var_id=10, var_type=LmcVarType.GAUGE),
                    11: LmcrecVarInfo(name="memory", var_id=11, var_type=LmcVarType.GAUGE),
                    12: LmcrecVarInfo(name="disk", var_id=12, var_type=LmcVarType.GAUGE),
                    13: LmcrecVarInfo(name="status", var_id=13, var_type=LmcVarType.STRING, max_size=7),
                },
                last_update_ts=11000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="monitor1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: 45,
                    11: 70,
                    12: 85,
                    13: "healthy",
                },
            )
        ],
        expect_inst_by_class_name={
            "Monitor": {"monitor1"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
    LmcrecStateCacheTestCase(
        name="LongStringValues",
        description="Test string variables with varying lengths to track max_size",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=12000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Messages"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.STRING, name="msg"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="msg1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="short"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=101, parent_inst_id=0, name="msg2"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="this is a much longer message"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=102, parent_inst_id=0, name="msg3"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="medium length"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.42),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Messages", class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="msg", var_id=10, var_type=LmcVarType.STRING, max_size=29),
                },
                last_update_ts=12000,
            )
        ],
        expect_inst_cache=[
            LmcrecInstCacheEntry(
                name="msg1", inst_id=100, class_id=1, parent_inst_id=0,
                vars={
                    10: "short",
                },
            ),
            LmcrecInstCacheEntry(
                name="msg2", inst_id=101, class_id=1, parent_inst_id=0,
                vars={
                    10: "this is a much longer message",
                },
            ),
            LmcrecInstCacheEntry(
                name="msg3", inst_id=102, class_id=1, parent_inst_id=0,
                vars={
                    10: "medium length",
                },
            )
        ],
        expect_inst_by_class_name={
            "Messages": {"msg1", "msg2", "msg3"},
        },
        expect_new_inst=True,
        expect_new_class_def=True,
    ),
]

# fmt: on
