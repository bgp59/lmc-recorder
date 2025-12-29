// Prompt: .github/prompts/codec_no_err_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package codec

import (
	"time"
)

var EncoderDecoderNoErrTestCases = []*EncoderDecoderTestCase{
	{
		Name:        "SingleClassInfo",
		Description: "Encode and decode a single class info record",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "TestClass",
			},
		},
	},
	{
		Name:        "SingleInstInfo",
		Description: "Encode and decode a single instance info record",
		WantRecords: []any{
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       10,
				ParentInstId: 0,
				Name:         "TestInstance",
			},
		},
	},
	{
		Name:        "SingleVarInfo",
		Description: "Encode and decode a single variable info record",
		WantRecords: []any{
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      5,
				LmcVarType: 1,
				Name:       "TestVar",
			},
		},
	},
	{
		Name:        "SingleSetInstId",
		Description: "Encode and decode a single set instance ID record",
		WantRecords: []any{
			&LmcrecSetInstId{
				InstId: 42,
			},
		},
	},
	{
		Name:        "SingleVarValBoolTrue",
		Description: "Encode and decode a single variable value record with boolean true",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 1,
				Value: true,
			},
		},
	},
	{
		Name:        "SingleVarValBoolFalse",
		Description: "Encode and decode a single variable value record with boolean false",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 2,
				Value: false,
			},
		},
	},
	{
		Name:        "SingleVarValUintZero",
		Description: "Encode and decode a single variable value record with uint64 zero",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 3,
				Value: uint64(0),
			},
		},
	},
	{
		Name:        "SingleVarValUintNonZero",
		Description: "Encode and decode a single variable value record with non-zero uint64",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 4,
				Value: uint64(12345),
			},
		},
	},
	{
		Name:        "SingleVarValSintZero",
		Description: "Encode and decode a single variable value record with int64 zero",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 5,
				Value: uint64(0),
			},
		},
	},
	{
		Name:        "SingleVarValSintPositive",
		Description: "Encode and decode a single variable value record with positive int64",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 6,
				Value: int64(9876),
			},
		},
	},
	{
		Name:        "SingleVarValSintNegative",
		Description: "Encode and decode a single variable value record with negative int64",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 7,
				Value: int64(-5432),
			},
		},
	},
	{
		Name:        "SingleVarValStringEmpty",
		Description: "Encode and decode a single variable value record with empty string",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 8,
				Value: "",
			},
		},
	},
	{
		Name:        "SingleVarValStringNonEmpty",
		Description: "Encode and decode a single variable value record with non-empty string",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 9,
				Value: "Hello, World!",
			},
		},
	},
	{
		Name:        "SingleDeleteInstId",
		Description: "Encode and decode a single delete instance ID record",
		WantRecords: []any{
			&LmcrecDeleteInstId{
				InstId: 99,
			},
		},
	},
	{
		Name:        "SingleScanTally",
		Description: "Encode and decode a single scan tally record",
		WantRecords: []any{
			&LmcrecScanTally{
				ScanInByteCount: 1024,
				ScanInInstCount: 10,
				ScanInVarCount:  50,
				ScanOutVarCount: 45,
			},
		},
	},
	{
		Name:        "SingleScanTallyZeros",
		Description: "Encode and decode a single scan tally record with all zero values",
		WantRecords: []any{
			&LmcrecScanTally{
				ScanInByteCount: 0,
				ScanInInstCount: 0,
				ScanInVarCount:  0,
				ScanOutVarCount: 0,
			},
		},
	},
	{
		Name:        "SingleTimestampUsec",
		Description: "Encode and decode a single timestamp record",
		WantRecords: []any{
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 1, 15, 10, 30, 45, 123456000, time.UTC),
			},
		},
	},
	{
		Name:        "SingleDurationUsec",
		Description: "Encode and decode a single duration record",
		WantRecords: []any{
			&LmcrecDurationUsec{
				Value: 5*time.Second + 500*time.Millisecond,
			},
		},
	},
	{
		Name:        "SingleEOR",
		Description: "Encode and decode a single end-of-record marker",
		WantRecords: []any{
			&LmcrecEOR{},
		},
	},
	{
		Name:        "ClassAndInstInfo",
		Description: "Encode and decode class info followed by instance info",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "ParentClass",
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       100,
				ParentInstId: 0,
				Name:         "ParentInstance",
			},
		},
	},
	{
		Name:        "CompleteHierarchy",
		Description: "Encode and decode a complete class hierarchy with parent and child",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "ParentClass",
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       100,
				ParentInstId: 0,
				Name:         "ParentInstance",
			},
			&LmcrecClassInfo{
				ClassId: 2,
				Name:    "ChildClass",
			},
			&LmcrecInstInfo{
				ClassId:      2,
				InstId:       200,
				ParentInstId: 100,
				Name:         "ChildInstance",
			},
		},
	},
	{
		Name:        "VarInfoAndValues",
		Description: "Encode and decode variable info followed by multiple variable values",
		WantRecords: []any{
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      1,
				LmcVarType: 1,
				Name:       "StringVar",
			},
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      2,
				LmcVarType: 2,
				Name:       "NumericVar",
			},
			&LmcrecVarVal{
				VarId: 1,
				Value: "test value",
			},
			&LmcrecVarVal{
				VarId: 2,
				Value: uint64(42),
			},
		},
	},
	{
		Name:        "SetInstIdAndVarValues",
		Description: "Encode and decode set instance ID followed by variable values",
		WantRecords: []any{
			&LmcrecSetInstId{
				InstId: 100,
			},
			&LmcrecVarVal{
				VarId: 1,
				Value: "value1",
			},
			&LmcrecVarVal{
				VarId: 2,
				Value: uint64(123),
			},
			&LmcrecVarVal{
				VarId: 3,
				Value: true,
			},
		},
	},
	{
		Name:        "TimestampAndScanTally",
		Description: "Encode and decode timestamp followed by scan tally",
		WantRecords: []any{
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 2, 20, 14, 22, 33, 0, time.UTC),
			},
			&LmcrecScanTally{
				ScanInByteCount: 2048,
				ScanInInstCount: 20,
				ScanInVarCount:  100,
				ScanOutVarCount: 95,
			},
		},
	},
	{
		Name:        "CompleteRecordingSession",
		Description: "Encode and decode a complete recording session with timestamp, class/instance creation, variable updates, and EOR",
		WantRecords: []any{
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 3, 10, 9, 0, 0, 0, time.UTC),
			},
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "SystemClass",
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       1000,
				ParentInstId: 0,
				Name:         "SystemInstance",
			},
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      1,
				LmcVarType: 1,
				Name:       "status",
			},
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      2,
				LmcVarType: 2,
				Name:       "counter",
			},
			&LmcrecSetInstId{
				InstId: 1000,
			},
			&LmcrecVarVal{
				VarId: 1,
				Value: "running",
			},
			&LmcrecVarVal{
				VarId: 2,
				Value: uint64(0),
			},
			&LmcrecScanTally{
				ScanInByteCount: 512,
				ScanInInstCount: 1,
				ScanInVarCount:  2,
				ScanOutVarCount: 2,
			},
			&LmcrecEOR{},
		},
	},
	{
		Name:        "MultipleVarTypes",
		Description: "Encode and decode all variable value types in a single session",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 1,
				Value: true,
			},
			&LmcrecVarVal{
				VarId: 2,
				Value: false,
			},
			&LmcrecVarVal{
				VarId: 3,
				Value: uint64(0),
			},
			&LmcrecVarVal{
				VarId: 4,
				Value: uint64(999),
			},
			&LmcrecVarVal{
				VarId: 5,
				Value: int64(-123),
			},
			&LmcrecVarVal{
				VarId: 6,
				Value: int64(456),
			},
			&LmcrecVarVal{
				VarId: 7,
				Value: "",
			},
			&LmcrecVarVal{
				VarId: 8,
				Value: "non-empty string",
			},
		},
	},
	{
		Name:        "DeleteAndRecreate",
		Description: "Encode and decode instance deletion followed by recreation",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "TempClass",
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       500,
				ParentInstId: 0,
				Name:         "TempInstance",
			},
			&LmcrecDeleteInstId{
				InstId: 500,
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       501,
				ParentInstId: 0,
				Name:         "NewInstance",
			},
		},
	},
	{
		Name:        "LargeStringValue",
		Description: "Encode and decode a variable with a large string value",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 1,
				Value: "This is a very long string value that contains multiple words and sentences. " +
					"It is used to test the encoding and decoding of larger string values. " +
					"The string includes various characters and punctuation marks! @#$%^&*()",
			},
		},
	},
	{
		Name:        "LargeNumericValues",
		Description: "Encode and decode variables with large numeric values",
		WantRecords: []any{
			&LmcrecVarVal{
				VarId: 1,
				Value: uint64(18446744073709551615), // max uint64
			},
			&LmcrecVarVal{
				VarId: 2,
				Value: int64(9223372036854775807), // max int64
			},
			&LmcrecVarVal{
				VarId: 3,
				Value: int64(-9223372036854775808), // min int64
			},
		},
	},
	{
		Name:        "MultipleScanTallies",
		Description: "Encode and decode multiple scan tally records",
		WantRecords: []any{
			&LmcrecScanTally{
				ScanInByteCount: 100,
				ScanInInstCount: 1,
				ScanInVarCount:  5,
				ScanOutVarCount: 5,
			},
			&LmcrecScanTally{
				ScanInByteCount: 200,
				ScanInInstCount: 2,
				ScanInVarCount:  10,
				ScanOutVarCount: 9,
			},
			&LmcrecScanTally{
				ScanInByteCount: 300,
				ScanInInstCount: 3,
				ScanInVarCount:  15,
				ScanOutVarCount: 14,
			},
		},
	},
	{
		Name:        "MultipleTimestamps",
		Description: "Encode and decode multiple timestamp records",
		WantRecords: []any{
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
			},
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 1, 1, 0, 0, 1, 0, time.UTC),
			},
			&LmcrecTimestampUsec{
				Value: time.Date(2024, 1, 1, 0, 0, 2, 0, time.UTC),
			},
		},
	},
	{
		Name:        "DurationSequence",
		Description: "Encode and decode a sequence of duration records",
		WantRecords: []any{
			&LmcrecDurationUsec{
				Value: 1 * time.Microsecond,
			},
			&LmcrecDurationUsec{
				Value: 1 * time.Millisecond,
			},
			&LmcrecDurationUsec{
				Value: 1 * time.Second,
			},
			&LmcrecDurationUsec{
				Value: 1 * time.Minute,
			},
		},
	},
	{
		Name:        "EmptyNames",
		Description: "Encode and decode records with empty name strings",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 1,
				Name:    "",
			},
			&LmcrecInstInfo{
				ClassId:      1,
				InstId:       1,
				ParentInstId: 0,
				Name:         "",
			},
			&LmcrecVarInfo{
				ClassId:    1,
				VarId:      1,
				LmcVarType: 1,
				Name:       "",
			},
		},
	},
	{
		Name:        "ZeroIds",
		Description: "Encode and decode records with zero ID values",
		WantRecords: []any{
			&LmcrecClassInfo{
				ClassId: 0,
				Name:    "ZeroClass",
			},
			&LmcrecInstInfo{
				ClassId:      0,
				InstId:       0,
				ParentInstId: 0,
				Name:         "ZeroInstance",
			},
			&LmcrecSetInstId{
				InstId: 0,
			},
			&LmcrecDeleteInstId{
				InstId: 0,
			},
		},
	},
}
