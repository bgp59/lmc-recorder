# Prompt: .github/prompts/state_cache_test_cases_err.prompt.md
# Model: Claude Sonnet 4.5
"""Test cases for test_lmcrec_state_cache_err"""

# noqa
# fmt: off

from lmcrec.playback.codec.decoder import LmcRecord, LmcrecType, LmcVarType
from lmcrec.playback.misc.timeutils import parse_ts

from .state_cache_def import LmcrecStateCacheTestCase

ts = parse_ts('2025-11-15T17:28:29-08:00')

test_cases_err = [
    LmcrecStateCacheTestCase(
        name="RedefineInstId",
        description="Redefine an existing instance ID with different class ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=2, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="definition change for inst ID 100",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineInstName",
        description="Redefine an instance name with different inst ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=101, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="definition change for inst 'counter1'",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineInstParent",
        description="Redefine an instance with different parent instance ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=50, name="counter1"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=100, parent_inst_id=0, name="counter1"),
            LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=50, file_record_type=LmcrecType.VAR_UINT_VAL),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="definition change for inst ID 100",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineClassName",
        description="Redefine a class name with different class ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=2, name="Counter"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="class definition changed for class 'Counter'",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineClassId",
        description="Redefine a class ID with different class name",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Gauge"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="class definition changed for class ID 1",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineVarName",
        description="Redefine a variable name with different var ID",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=11, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="var definition change for var 'count'",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineVarType",
        description="Redefine a variable with different type",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.GAUGE, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="var definition change for var ID 10",
    ),
    LmcrecStateCacheTestCase(
        name="RedefineVarId",
        description="Redefine a variable ID with different name",
        next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="total"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.25),
        ],
        prime_next_records=[
            LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=ts - 1.0),
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=10, lmc_var_type=LmcVarType.COUNTER, name="count"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="var definition change for var ID 10",
    ),
    LmcrecStateCacheTestCase(
        name="MissingTimestamp",
        description="Scan without initial timestamp record",
        next_records=[
            LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name="Counter"),
            LmcRecord(record_type=LmcrecType.SCAN_TALLY),
            LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.20),
        ],
        expect_exception=RuntimeError,
        expect_exception_str="want: <LmcrecType.TIMESTAMP_USEC",
    ),
]
