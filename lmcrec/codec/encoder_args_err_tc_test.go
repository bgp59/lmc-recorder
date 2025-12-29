// Prompt: .github/prompts/encoder_args_err_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package codec

var EncoderArgsErrTestCases = []*EncoderErrTestCase{
	{
		Name:                "VarValueWithNilValue",
		Description:         "VarValue with nil value should return an error",
		Record:              &LmcrecVarVal{VarId: 1, Value: nil},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithFloat32",
		Description:         "VarValue with float32 value should return an error",
		Record:              &LmcrecVarVal{VarId: 2, Value: float32(3.14)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithFloat64",
		Description:         "VarValue with float64 value should return an error",
		Record:              &LmcrecVarVal{VarId: 3, Value: float64(2.718)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithInt",
		Description:         "VarValue with int value should return an error",
		Record:              &LmcrecVarVal{VarId: 4, Value: int(42)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithInt32",
		Description:         "VarValue with int32 value should return an error",
		Record:              &LmcrecVarVal{VarId: 5, Value: int32(100)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithUint",
		Description:         "VarValue with uint value should return an error",
		Record:              &LmcrecVarVal{VarId: 6, Value: uint(255)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithUint32",
		Description:         "VarValue with uint32 value should return an error",
		Record:              &LmcrecVarVal{VarId: 7, Value: uint32(1000)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithByteSlice",
		Description:         "VarValue with []byte value should return an error",
		Record:              &LmcrecVarVal{VarId: 8, Value: []byte{1, 2, 3}},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithStruct",
		Description:         "VarValue with struct value should return an error",
		Record:              &LmcrecVarVal{VarId: 9, Value: struct{ X int }{X: 10}},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithMap",
		Description:         "VarValue with map value should return an error",
		Record:              &LmcrecVarVal{VarId: 10, Value: map[string]int{"key": 1}},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithSlice",
		Description:         "VarValue with slice value should return an error",
		Record:              &LmcrecVarVal{VarId: 11, Value: []int{1, 2, 3}},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
	{
		Name:                "VarValueWithPointer",
		Description:         "VarValue with pointer value should return an error",
		Record:              &LmcrecVarVal{VarId: 12, Value: new(int)},
		WriteErrAtCallCount: -1,
		WantErr:             "invalid value type",
	},
}
