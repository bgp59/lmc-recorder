"""Examples for test case generation via Copilot prompt"""

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
                # var_info_by_name will be inferred from var_info_by_id
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
        name="SetInstIdAndUpdate",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=2000),
            LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=100),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=100, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=1995),
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
                last_update_ts=1995,
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
        name="RedefineInstIdAndUpdate",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=3000),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=100, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=2995),
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
                    10: LmcrecVarInfo(
                        name="count", var_id=10, var_type=LmcVarType.COUNTER
                    ),
                },
                last_update_ts=2995,
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
        name="InstanceDeletion",
        description="Creating and then deleting an instance",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=4000),
            LmcRecord(record_type=LmcrecType.DELETE_INST_ID, inst_id=200),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.35),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=3998),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Temp"),
            LmcRecord(
                record_type=LmcrecType.VAR_INFO,
                class_id=1,
                var_id=10,
                lmc_var_type=LmcVarType.STRING,
                name="data",
            ),
            LmcRecord(
                record_type=LmcrecType.INST_INFO,
                class_id=1,
                inst_id=200,
                parent_inst_id=0,
                name="temp1",
            ),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value="temporary"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.40),
        ],
        expect_class_cache=[
            LmcrecClassCacheEntry(
                name="Temp",
                class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(
                        name="data", var_id=10, var_type=LmcVarType.STRING, max_size=9
                    ),
                },
                last_update_ts=3998,
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
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=5000),
            LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=100),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=55, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=-60, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value=65, file_record_type=LmcrecType.VAR_SINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=4987),
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
                name="NegativeNum",
                class_id=1,
                var_info_by_id={
                    10: LmcrecVarInfo(name="num1", var_id=10, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    11: LmcrecVarInfo(name="num2", var_id=11, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    12: LmcrecVarInfo(name="num3", var_id=12, var_type=LmcVarType.NUMERIC, neg_vals=True),
                    13: LmcrecVarInfo(name="num4", var_id=13, var_type=LmcVarType.NUMERIC, neg_vals=True),
                },
                last_update_ts=4987,
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
]

# fmt: on
