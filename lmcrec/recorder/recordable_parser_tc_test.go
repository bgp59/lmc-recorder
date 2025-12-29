// Prompt: .github/prompts/recordable_parser_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package recorder

import (
	"fmt"
	"lmcrec/parser"
)

var RecordableParserTestCases = []*RecordableParserTestCase{
	{
		Name:             "EmptyCacheFullRecord",
		Description:      "Full record with empty cache should return 0 variables",
		ClassCache:       map[string]*parser.LmcClassInfo{},
		InstanceCache:    map[uint32]*parser.LmcInstanceCacheEntry{},
		CurrIndex:        0,
		Events:           []any{},
		Full:             true,
		WantOutNumVars:   0,
		WantErr:          nil,
		WantEncoderCalls: []string{},
	},
	{
		Name:             "EmptyCacheIncrementalRecord",
		Description:      "Incremental record with empty cache should return 0 variables",
		ClassCache:       map[string]*parser.LmcClassInfo{},
		InstanceCache:    map[uint32]*parser.LmcInstanceCacheEntry{},
		CurrIndex:        0,
		Events:           []any{},
		Full:             false,
		WantOutNumVars:   0,
		WantErr:          nil,
		WantEncoderCalls: []string{},
	},
	{
		Name:        "FullRecordSingleInstance",
		Description: "Full record with single instance and variables should encode class info, variable info, instance info, and variable values",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
					"var2": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 1},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1", 1: int64(100)},
					{},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 2,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("TestClass", 1)`,
			`VarInfo("var1", 0, 1, 10)`,
			`VarInfo("var2", 1, 1, 6)`,
			`InstInfo("inst1", 1, 1, 0)`,
			`VarValue(0, "value1")`,
			`VarValue(1, 100)`,
		},
	},
	{
		Name:        "FullRecordWithParentChild",
		Description: "Full record with parent-child instance relationship should encode both instances with correct parent IDs",
		ClassCache: map[string]*parser.LmcClassInfo{
			"ParentClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"pvar": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
			"ChildClass": {
				ClassId: 2,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"cvar": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "parent1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "pvalue"},
					{},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 2,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("ParentClass", 1)`,
			`VarInfo("pvar", 0, 1, 10)`,
			`ClassInfo("ChildClass", 2)`,
			`VarInfo("cvar", 0, 2, 6)`,
			`InstInfo("parent1", 1, 1, 0)`,
			`VarValue(0, "pvalue")`,
			`InstInfo("child1", 2, 2, 1)`,
			`VarValue(0, 10)`,
		},
	},
	{
		Name:        "IncrementalRecordWithChanges",
		Description: "Incremental record should only encode changed variables",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
					"var2": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 1},
					"var3": {Type: parser.LMC_VAR_TYPE_BOOLEAN, VarId: 2},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "new_value", 1: int64(200), 2: true},
					{0: "old_value", 1: int64(200), 2: false},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           false,
		WantOutNumVars: 2,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`SetInstId(1)`,
			`VarValue(0, "new_value")`,
			`VarValue(2, true)`,
		},
	},
	{
		Name:        "IncrementalRecordNoChanges",
		Description: "Incremental record with no changes should return 0 variables and no encoder calls",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "same_value"},
					{0: "same_value"},
				},
			},
		},
		CurrIndex:        0,
		Events:           []any{},
		Full:             false,
		WantOutNumVars:   0,
		WantErr:          nil,
		WantEncoderCalls: []string{},
	},
	{
		Name:        "FullRecordWithEvents",
		Description: "Full record should process all events before encoding cache",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserNewClassEvent{Name: "NewClass", Id: 2},
			&parser.LmcParserNewVariableEvent{Name: "newvar", Id: 0, ClassId: 2, Type: parser.LMC_VAR_TYPE_NUMERIC},
			&parser.LmcParserNewInstanceEvent{Name: "newinst", Id: 2, ParentId: 0, ClassId: 2},
			&parser.LmcParserInstanceDeletionEvent{Id: 3},
		},
		Full:           true,
		WantOutNumVars: 1,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("NewClass", 2)`,
			`VarInfo("newvar", 0, 2, 6)`,
			`InstInfo("newinst", 2, 2, 0)`,
			`DeleteInstId(3)`,
			`ClassInfo("TestClass", 1)`,
			`VarInfo("var1", 0, 1, 10)`,
			`InstInfo("inst1", 1, 1, 0)`,
			`VarValue(0, "value1")`,
		},
	},
	{
		Name:        "IncrementalRecordWithEvents",
		Description: "Incremental record should process events before encoding changed variables",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(100)},
					{0: int64(50)},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserNewClassEvent{Name: "NewClass", Id: 2},
			&parser.LmcParserInstanceDeletionEvent{Id: 3},
		},
		Full:           false,
		WantOutNumVars: 1,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("NewClass", 2)`,
			`DeleteInstId(3)`,
			`SetInstId(1)`,
			`VarValue(0, 100)`,
		},
	},
	{
		Name:        "ErrorOnClassInfoEncoding",
		Description: "Error during ClassInfo encoding should be returned immediately",
		ClassCache:  map[string]*parser.LmcClassInfo{},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserNewClassEvent{Name: "TestClass", Id: 1},
		},
		Full:           true,
		WantOutNumVars: 0,
		WantErr:        "ClassInfo error",
		EncoderRetVals: map[string][]error{
			`ClassInfo("TestClass", 1)`: {fmt.Errorf("ClassInfo error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "ErrorOnVarInfoEncoding",
		Description: "Error during VarInfo encoding should be returned immediately",
		ClassCache:  map[string]*parser.LmcClassInfo{},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserNewClassEvent{Name: "TestClass", Id: 1},
			&parser.LmcParserNewVariableEvent{Name: "var1", Id: 0, ClassId: 1, Type: parser.LMC_VAR_TYPE_STRING},
		},
		Full:           true,
		WantOutNumVars: 0,
		WantErr:        "VarInfo error",
		EncoderRetVals: map[string][]error{
			`VarInfo("var1", 0, 1, 10)`: {fmt.Errorf("VarInfo error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "ErrorOnInstInfoEncoding",
		Description: "Error during InstInfo encoding should be returned immediately",
		ClassCache:  map[string]*parser.LmcClassInfo{},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserNewInstanceEvent{Name: "newinst", Id: 2, ParentId: 0, ClassId: 2},
		},
		Full:           false,
		WantOutNumVars: 0,
		WantErr:        "InstInfo error",
		EncoderRetVals: map[string][]error{
			`InstInfo("newinst", 2, 2, 0)`: {fmt.Errorf("InstInfo error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "ErrorOnDeleteInstIdEncoding",
		Description: "Error during DeleteInstId encoding should be returned immediately",
		ClassCache:  map[string]*parser.LmcClassInfo{},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex: 0,
		Events: []any{
			&parser.LmcParserInstanceDeletionEvent{Id: 3},
		},
		Full:           false,
		WantOutNumVars: 0,
		WantErr:        "DeleteInstId error",
		EncoderRetVals: map[string][]error{
			`DeleteInstId(3)`: {fmt.Errorf("DeleteInstId error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "ErrorOnVarValueEncoding",
		Description: "Error during VarValue encoding should be returned with instance name in error message",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 0,
		WantErr:        "instance: inst1:",
		EncoderRetVals: map[string][]error{
			`VarValue(0, "value1")`: {fmt.Errorf("VarValue error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "ErrorOnSetInstIdEncoding",
		Description: "Error during SetInstId encoding should be returned immediately",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(100)},
					{0: int64(50)},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           false,
		WantOutNumVars: 0,
		WantErr:        "SetInstId error",
		EncoderRetVals: map[string][]error{
			`SetInstId(1)`: {fmt.Errorf("SetInstId error")},
		},
		WantEncoderCalls: []string{},
	},
	{
		Name:        "MultipleInstancesIncremental",
		Description: "Incremental record with multiple instances should encode SetInstId for each instance with changes",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(100)},
					{0: int64(50)},
				},
			},
			2: {
				Name:      "inst2",
				InstId:    2,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(200)},
					{0: int64(200)},
				},
			},
			3: {
				Name:      "inst3",
				InstId:    3,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(300)},
					{0: int64(250)},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           false,
		WantOutNumVars: 2,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`SetInstId(1)`,
			`VarValue(0, 100)`,
			`SetInstId(3)`,
			`VarValue(0, 300)`,
		},
	},
	{
		Name:        "MultipleClassesFull",
		Description: "Full record with multiple classes should encode all class and variable info",
		ClassCache: map[string]*parser.LmcClassInfo{
			"Class1": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
			"Class2": {
				ClassId: 2,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var2": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1"},
					{},
				},
			},
			2: {
				Name:      "inst2",
				InstId:    2,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 2},
				Variables: [2]map[uint32]any{
					{0: int64(100)},
					{},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 2,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("Class1", 1)`,
			`VarInfo("var1", 0, 1, 10)`,
			`ClassInfo("Class2", 2)`,
			`VarInfo("var2", 0, 2, 6)`,
			`InstInfo("inst1", 1, 1, 0)`,
			`VarValue(0, "value1")`,
			`InstInfo("inst2", 2, 2, 0)`,
			`VarValue(0, 100)`,
		},
	},
	{
		Name:        "FullRecordWithCurrIndexOne",
		Description: "Full record with CurrIndex=1 should use second variable map",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "old_value"},
					{0: "new_value"},
				},
			},
		},
		CurrIndex:      1,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 1,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("TestClass", 1)`,
			`VarInfo("var1", 0, 1, 10)`,
			`InstInfo("inst1", 1, 1, 0)`,
			`VarValue(0, "new_value")`,
		},
	},
	{
		Name:        "IncrementalRecordWithCurrIndexOne",
		Description: "Incremental record with CurrIndex=1 should compare second vs first variable map",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 0},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: int64(50)},
					{0: int64(100)},
				},
			},
		},
		CurrIndex:      1,
		Events:         []any{},
		Full:           false,
		WantOutNumVars: 1,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`SetInstId(1)`,
			`VarValue(0, 100)`,
		},
	},
	{
		Name:        "FullRecordMultipleVariablesPerInstance",
		Description: "Full record with instance having multiple variables should encode all variables",
		ClassCache: map[string]*parser.LmcClassInfo{
			"TestClass": {
				ClassId: 1,
				VariableDescription: map[string]*parser.LmcVariableInfo{
					"var1": {Type: parser.LMC_VAR_TYPE_STRING, VarId: 0},
					"var2": {Type: parser.LMC_VAR_TYPE_NUMERIC, VarId: 1},
					"var3": {Type: parser.LMC_VAR_TYPE_BOOLEAN, VarId: 2},
					"var4": {Type: parser.LMC_VAR_TYPE_GAUGE, VarId: 3},
				},
			},
		},
		InstanceCache: map[uint32]*parser.LmcInstanceCacheEntry{
			1: {
				Name:      "inst1",
				InstId:    1,
				Parent:    nil,
				ClassInfo: &parser.LmcClassInfo{ClassId: 1},
				Variables: [2]map[uint32]any{
					{0: "value1", 1: int64(100), 2: true, 3: uint64(200)},
					{},
				},
			},
		},
		CurrIndex:      0,
		Events:         []any{},
		Full:           true,
		WantOutNumVars: 4,
		WantErr:        nil,
		WantEncoderCalls: []string{
			`ClassInfo("TestClass", 1)`,
			`VarInfo("var1", 0, 1, 10)`,
			`VarInfo("var2", 1, 1, 6)`,
			`VarInfo("var3", 2, 1, 1)`,
			`VarInfo("var4", 3, 1, 4)`,
			`InstInfo("inst1", 1, 1, 0)`,
			`VarValue(0, "value1")`,
			`VarValue(1, 100)`,
			`VarValue(2, true)`,
			`VarValue(3, 200)`,
		},
	},
}
