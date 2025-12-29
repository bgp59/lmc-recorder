// Prompt: .github/prompts/encoder_write_err_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package codec

import "time"

var EncoderWriteErrTestCases = []*EncoderErrTestCase{
	{
		Name:                "ClassInfoWriteErr",
		Description:         "Test write error during ClassInfo encoding",
		Record:              &LmcrecClassInfo{Name: "TestClass", ClassId: 1},
		WriteErrAtCallCount: 2,
	},
	{
		Name:                "InstInfoWriteErr",
		Description:         "Test write error during InstInfo encoding",
		Record:              &LmcrecInstInfo{Name: "TestInst", ClassId: 1, InstId: 10, ParentInstId: 0},
		WriteErrAtCallCount: 2,
	},
	{
		Name:                "VarInfoWriteErr",
		Description:         "Test write error during VarInfo encoding",
		Record:              &LmcrecVarInfo{Name: "TestVar", VarId: 1, ClassId: 1, LmcVarType: 1},
		WriteErrAtCallCount: 2,
	},
	{
		Name:                "SetInstIdWriteErr",
		Description:         "Test write error during SetInstId encoding",
		Record:              &LmcrecSetInstId{InstId: 10},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "DeleteInstIdWriteErr",
		Description:         "Test write error during DeleteInstId encoding",
		Record:              &LmcrecDeleteInstId{InstId: 10},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueUintWriteErr",
		Description:         "Test write error during VarValue encoding with uint value",
		Record:              &LmcrecVarVal{VarId: 1, Value: uint64(100)},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueSintWriteErr",
		Description:         "Test write error during VarValue encoding with signed int value",
		Record:              &LmcrecVarVal{VarId: 1, Value: int64(-100)},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueZeroWriteErr",
		Description:         "Test write error during VarValue encoding with zero value",
		Record:              &LmcrecVarVal{VarId: 1, Value: uint64(0)},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueStringWriteErr",
		Description:         "Test write error during VarValue encoding with string value",
		Record:              &LmcrecVarVal{VarId: 1, Value: "test string"},
		WriteErrAtCallCount: 2,
	},
	{
		Name:                "VarValueEmptyStringWriteErr",
		Description:         "Test write error during VarValue encoding with empty string",
		Record:              &LmcrecVarVal{VarId: 1, Value: ""},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueBoolTrueWriteErr",
		Description:         "Test write error during VarValue encoding with boolean true",
		Record:              &LmcrecVarVal{VarId: 1, Value: true},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "VarValueBoolFalseWriteErr",
		Description:         "Test write error during VarValue encoding with boolean false",
		Record:              &LmcrecVarVal{VarId: 1, Value: false},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "ScanTallyWriteErr",
		Description:         "Test write error during ScanTally encoding",
		Record:              &LmcrecScanTally{ScanInByteCount: 100, ScanInInstCount: 10, ScanInVarCount: 20, ScanOutVarCount: 15},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "TimestampUsecWriteErr",
		Description:         "Test write error during TimestampUsec encoding",
		Record:              &LmcrecTimestampUsec{Value: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "DurationUsecWriteErr",
		Description:         "Test write error during DurationUsec encoding",
		Record:              &LmcrecDurationUsec{Value: 1000 * time.Microsecond},
		WriteErrAtCallCount: 1,
	},
	{
		Name:                "EORWriteErr",
		Description:         "Test write error during EOR encoding",
		Record:              &LmcrecEOR{},
		WriteErrAtCallCount: 1,
	},
}
