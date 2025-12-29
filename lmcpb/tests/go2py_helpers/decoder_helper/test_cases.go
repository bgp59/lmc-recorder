package main

import (
	"time"

	"lmcrec/codec"
	"lmcrec/parser"
)

var DecoderTestCases = []DecoderTestCase{
	// CLASS_INFO test cases
	{
		&codec.LmcrecClassInfo{ClassId: 1, Name: "TestClass"},
		`LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=1, name='TestClass')`,
	},
	{
		&codec.LmcrecClassInfo{ClassId: 100, Name: "ManagedProcess.SrcDist"},
		`LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=100, name='ManagedProcess.SrcDist')`,
	},
	{
		&codec.LmcrecClassInfo{ClassId: 255, Name: "Class_With_Underscores"},
		`LmcRecord(record_type=LmcrecType.CLASS_INFO, class_id=255, name='Class_With_Underscores')`,
	},

	// INST_INFO test cases
	{
		&codec.LmcrecInstInfo{ClassId: 1, InstId: 10, ParentInstId: 0, Name: "root_instance"},
		`LmcRecord(record_type=LmcrecType.INST_INFO, class_id=1, inst_id=10, parent_inst_id=0, name='root_instance')`,
	},
	{
		&codec.LmcrecInstInfo{ClassId: 5, InstId: 25, ParentInstId: 10, Name: "child_instance"},
		`LmcRecord(record_type=LmcrecType.INST_INFO, class_id=5, inst_id=25, parent_inst_id=10, name='child_instance')`,
	},
	{
		&codec.LmcrecInstInfo{ClassId: 100, InstId: 999, ParentInstId: 500, Name: "deeply.nested.instance"},
		`LmcRecord(record_type=LmcrecType.INST_INFO, class_id=100, inst_id=999, parent_inst_id=500, name='deeply.nested.instance')`,
	},

	// VAR_INFO test cases - covering all LMC variable types
	{
		&codec.LmcrecVarInfo{ClassId: 1, VarId: 0, LmcVarType: uint32(parser.LMC_VAR_TYPE_BOOLEAN), Name: "bool_var"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=1, var_id=0, lmc_var_type=LmcVarType.BOOLEAN, name='bool_var')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 2, VarId: 1, LmcVarType: uint32(parser.LMC_VAR_TYPE_BOOLEAN_CONFIG), Name: "bool_config"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=2, var_id=1, lmc_var_type=LmcVarType.BOOLEAN_CONFIG, name='bool_config')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 3, VarId: 2, LmcVarType: uint32(parser.LMC_VAR_TYPE_COUNTER), Name: "counter_var"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=3, var_id=2, lmc_var_type=LmcVarType.COUNTER, name='counter_var')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 4, VarId: 3, LmcVarType: uint32(parser.LMC_VAR_TYPE_GAUGE), Name: "gauge_var"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=4, var_id=3, lmc_var_type=LmcVarType.GAUGE, name='gauge_var')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 5, VarId: 4, LmcVarType: uint32(parser.LMC_VAR_TYPE_GAUGE_CONFIG), Name: "gauge_config"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=5, var_id=4, lmc_var_type=LmcVarType.GAUGE_CONFIG, name='gauge_config')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 6, VarId: 5, LmcVarType: uint32(parser.LMC_VAR_TYPE_NUMERIC), Name: "numeric_var"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=6, var_id=5, lmc_var_type=LmcVarType.NUMERIC, name='numeric_var')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 7, VarId: 6, LmcVarType: uint32(parser.LMC_VAR_TYPE_LARGE_NUMERIC), Name: "large_numeric"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=7, var_id=6, lmc_var_type=LmcVarType.LARGE_NUMERIC, name='large_numeric')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 8, VarId: 7, LmcVarType: uint32(parser.LMC_VAR_TYPE_NUMERIC_RANGE), Name: "numeric_range"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=8, var_id=7, lmc_var_type=LmcVarType.NUMERIC_RANGE, name='numeric_range')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 9, VarId: 8, LmcVarType: uint32(parser.LMC_VAR_TYPE_NUMERIC_CONFIG), Name: "numeric_config"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=9, var_id=8, lmc_var_type=LmcVarType.NUMERIC_CONFIG, name='numeric_config')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 10, VarId: 9, LmcVarType: uint32(parser.LMC_VAR_TYPE_STRING), Name: "string_var"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=10, var_id=9, lmc_var_type=LmcVarType.STRING, name='string_var')`,
	},
	{
		&codec.LmcrecVarInfo{ClassId: 11, VarId: 10, LmcVarType: uint32(parser.LMC_VAR_TYPE_STRING_CONFIG), Name: "string_config"},
		`LmcRecord(record_type=LmcrecType.VAR_INFO, class_id=11, var_id=10, lmc_var_type=LmcVarType.STRING_CONFIG, name='string_config')`,
	},

	// SET_INST_ID test cases
	{
		&codec.LmcrecSetInstId{InstId: 1},
		`LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=1)`,
	},
	{
		&codec.LmcrecSetInstId{InstId: 100},
		`LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=100)`,
	},
	{
		&codec.LmcrecSetInstId{InstId: 65535},
		`LmcRecord(record_type=LmcrecType.SET_INST_ID, inst_id=65535)`,
	},

	// VAR_VALUE test cases - Boolean values
	{
		&codec.LmcrecVarVal{VarId: 1, Value: false},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=1, value=False, file_record_type=LmcrecType.VAR_BOOL_FALSE)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 2, Value: true},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=2, value=True, file_record_type=LmcrecType.VAR_BOOL_TRUE)`,
	},

	// VAR_VALUE test cases - Unsigned integer values
	{
		&codec.LmcrecVarVal{VarId: 3, Value: uint64(0)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=3, value=0, file_record_type=LmcrecType.VAR_ZERO_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 4, Value: uint64(1)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=4, value=1, file_record_type=LmcrecType.VAR_UINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 5, Value: uint64(42)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=5, value=42, file_record_type=LmcrecType.VAR_UINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 6, Value: uint64(255)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=6, value=255, file_record_type=LmcrecType.VAR_UINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 7, Value: uint64(65535)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=7, value=65535, file_record_type=LmcrecType.VAR_UINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 8, Value: uint64(1000000)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=8, value=1000000, file_record_type=LmcrecType.VAR_UINT_VAL)`,
	},

	// VAR_VALUE test cases - Signed integer values
	{
		&codec.LmcrecVarVal{VarId: 9, Value: int64(0)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=9, value=0, file_record_type=LmcrecType.VAR_ZERO_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 10, Value: int64(-1)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=10, value=-1, file_record_type=LmcrecType.VAR_SINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 11, Value: int64(-42)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=11, value=-42, file_record_type=LmcrecType.VAR_SINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 12, Value: int64(100)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=12, value=100, file_record_type=LmcrecType.VAR_SINT_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 13, Value: int64(-1000000)},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=13, value=-1000000, file_record_type=LmcrecType.VAR_SINT_VAL)`,
	},

	// VAR_VALUE test cases - String values
	{
		&codec.LmcrecVarVal{VarId: 14, Value: ""},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=14, value='', file_record_type=LmcrecType.VAR_EMPTY_STRING)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 15, Value: "hello"},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=15, value='hello', file_record_type=LmcrecType.VAR_STRING_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 16, Value: "Hello World!"},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=16, value='Hello World!', file_record_type=LmcrecType.VAR_STRING_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 17, Value: "path/to/file.txt"},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=17, value='path/to/file.txt', file_record_type=LmcrecType.VAR_STRING_VAL)`,
	},
	{
		&codec.LmcrecVarVal{VarId: 18, Value: "value_with_underscores"},
		`LmcRecord(record_type=LmcrecType.VAR_VALUE, var_id=18, value='value_with_underscores', file_record_type=LmcrecType.VAR_STRING_VAL)`,
	},

	// DELETE_INST_ID test cases
	{
		&codec.LmcrecDeleteInstId{InstId: 1},
		`LmcRecord(record_type=LmcrecType.DELETE_INST_ID, inst_id=1)`,
	},
	{
		&codec.LmcrecDeleteInstId{InstId: 50},
		`LmcRecord(record_type=LmcrecType.DELETE_INST_ID, inst_id=50)`,
	},
	{
		&codec.LmcrecDeleteInstId{InstId: 999},
		`LmcRecord(record_type=LmcrecType.DELETE_INST_ID, inst_id=999)`,
	},

	// SCAN_TALLY test cases
	{
		&codec.LmcrecScanTally{ScanInByteCount: 0, ScanInInstCount: 0, ScanInVarCount: 0, ScanOutVarCount: 0},
		`LmcRecord(record_type=LmcrecType.SCAN_TALLY, scan_in_byte_count=0, scan_in_inst_count=0, scan_in_var_count=0, scan_out_var_count=0)`,
	},
	{
		&codec.LmcrecScanTally{ScanInByteCount: 1024, ScanInInstCount: 10, ScanInVarCount: 50, ScanOutVarCount: 45},
		`LmcRecord(record_type=LmcrecType.SCAN_TALLY, scan_in_byte_count=1024, scan_in_inst_count=10, scan_in_var_count=50, scan_out_var_count=45)`,
	},
	{
		&codec.LmcrecScanTally{ScanInByteCount: 1048576, ScanInInstCount: 1000, ScanInVarCount: 5000, ScanOutVarCount: 4999},
		`LmcRecord(record_type=LmcrecType.SCAN_TALLY, scan_in_byte_count=1048576, scan_in_inst_count=1000, scan_in_var_count=5000, scan_out_var_count=4999)`,
	},

	// TIMESTAMP_USEC test cases
	{
		&codec.LmcrecTimestampUsec{Value: time.Unix(0, 0)},
		`LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=0.0)`,
	},
	{
		&codec.LmcrecTimestampUsec{Value: time.Unix(1000000, 0)},
		`LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=1000000.0)`,
	},
	{
		&codec.LmcrecTimestampUsec{Value: time.Unix(1000000, 123000)},
		`LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=1000000.000123)`,
	},
	{
		&codec.LmcrecTimestampUsec{Value: time.Unix(1609459200, 500000000)},
		`LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=1609459200.5)`,
	},
	{
		&codec.LmcrecTimestampUsec{Value: time.Unix(-1000000, 0)},
		`LmcRecord(record_type=LmcrecType.TIMESTAMP_USEC, value=-1000000.0)`,
	},

	// DURATION_USEC test cases
	{
		&codec.LmcrecDurationUsec{Value: 0},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.0)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 1 * time.Microsecond},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.000001)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 1 * time.Millisecond},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=0.001)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 1 * time.Second},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=1.0)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 1000123 * time.Microsecond},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=1.000123)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 60 * time.Second},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=60.0)`,
	},
	{
		&codec.LmcrecDurationUsec{Value: 3600*time.Second + 500*time.Millisecond},
		`LmcRecord(record_type=LmcrecType.DURATION_USEC, value=3600.5)`,
	},

	// EOR test case
	{
		&codec.LmcrecEOR{},
		`LmcRecord(record_type=LmcrecType.EOR)`,
	},
}
