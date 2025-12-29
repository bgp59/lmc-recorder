// Prompt: .github/prompts/encoder_closed_err_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package codec

import "time"

var EncoderClosedErrTestCases = []*EncoderErrTestCase{
	{
		Name:                "ClassInfoClosed",
		Description:         "ClassInfo() should return error when encoder is already closed",
		Record:              &LmcrecClassInfo{ClassId: 1, Name: "TestClass"},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "InstInfoClosed",
		Description:         "InstInfo() should return error when encoder is already closed",
		Record:              &LmcrecInstInfo{ClassId: 1, InstId: 100, ParentInstId: 0, Name: "TestInstance"},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarInfoClosed",
		Description:         "VarInfo() should return error when encoder is already closed",
		Record:              &LmcrecVarInfo{ClassId: 1, VarId: 10, LmcVarType: 1, Name: "TestVar"},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "SetInstIdClosed",
		Description:         "SetInstId() should return error when encoder is already closed",
		Record:              &LmcrecSetInstId{InstId: 100},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueBoolTrueClosed",
		Description:         "VarValue() with bool true should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: true},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueBoolFalseClosed",
		Description:         "VarValue() with bool false should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: false},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueUint64Closed",
		Description:         "VarValue() with uint64 should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: uint64(12345)},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueUint64ZeroClosed",
		Description:         "VarValue() with uint64 zero should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: uint64(0)},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueInt64Closed",
		Description:         "VarValue() with int64 should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: int64(-12345)},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueInt64ZeroClosed",
		Description:         "VarValue() with int64 zero should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: int64(0)},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueStringClosed",
		Description:         "VarValue() with string should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: "test string"},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "VarValueEmptyStringClosed",
		Description:         "VarValue() with empty string should return error when encoder is already closed",
		Record:              &LmcrecVarVal{VarId: 10, Value: ""},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "DeleteInstIdClosed",
		Description:         "DeleteInstId() should return error when encoder is already closed",
		Record:              &LmcrecDeleteInstId{InstId: 100},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "ScanTallyClosed",
		Description:         "ScanTally() should return error when encoder is already closed",
		Record:              &LmcrecScanTally{ScanInByteCount: 1024, ScanInInstCount: 10, ScanInVarCount: 50, ScanOutVarCount: 45},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "TimestampUsecClosed",
		Description:         "TimestampUsec() should return error when encoder is already closed",
		Record:              &LmcrecTimestampUsec{Value: time.Date(2024, 1, 15, 10, 30, 0, 0, time.UTC)},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "DurationUsecClosed",
		Description:         "DurationUsec() should return error when encoder is already closed",
		Record:              &LmcrecDurationUsec{Value: 5 * time.Second},
		WriteErrAtCallCount: 0,
	},
	{
		Name:                "EORClosed",
		Description:         "EOR() should return error when encoder is already closed",
		Record:              &LmcrecEOR{},
		WriteErrAtCallCount: 0,
	},
}
