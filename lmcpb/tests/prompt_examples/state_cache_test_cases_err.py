"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from lmcrec.playback.codec.decoder import LmcRecord, LmcrecType, LmcVarType
from lmcrec.playback.misc.timeutils import parse_ts

from .state_cache_def import LmcrecStateCacheTestCase

ts = parse_ts('2025-11-15T17:28:29-08:00')

test_cases_err = [
    LmcrecStateCacheTestCase(
        name="RedefineInstId",
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
]
