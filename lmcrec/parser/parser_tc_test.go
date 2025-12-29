// Prompt: .github/prompts/parser_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package parser

var ParserTestCases = []*ParserTestCase{
	// processChanged == false: no prior scan
	{
		Name:        "NoPriorScan",
		Description: "First scan with no prior data, should set process signature and treat as checkpoint",
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 12345
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "var1",
							"Type": "String",
							"Value": "value1"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents:        false,
		WantVariables:      map[string]map[uint32]any{},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   3,
	},

	// processChanged == false: variable value changes without events
	{
		Name:        "VariableValueChange",
		Description: "Variable values change between scans without new instances, classes, or variables",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 12345
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 100
						},
						{
							"Name": "name",
							"Type": "String",
							"Value": "initial"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 12345
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 150
						},
						{
							"Name": "name",
							"Type": "String",
							"Value": "updated"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst1": {
				0: uint64(150),
				1: "updated",
			},
		},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   4,
	},

	// processChanged == false: new instances of same class with same variables
	{
		Name:        "NewInstancesSameClassSameVariables",
		Description: "New instances appear with the same class and variable definitions",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 67890
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "DataClass",
					"Variables": [
						{
							"Name": "value",
							"Type": "Numeric",
							"Value": 42
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 67890
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "DataClass",
					"Variables": [
						{
							"Name": "value",
							"Type": "Numeric",
							"Value": 42
						}
					],
					"Children": []
				},
				{
					"Instance": "inst2",
					"Class": "DataClass",
					"Variables": [
						{
							"Name": "value",
							"Type": "Numeric",
							"Value": 84
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst2": {
				0: uint64(84),
			},
		},
		WantEvents: []any{
			&LmcParserNewInstanceEvent{"inst2", uint32(3), uint32(0), uint32(2)},
		},
		WantProcessChanged: false,
		WantNumInstances:   3,
		WantNumVariables:   4,
	},

	// processChanged == false: new instances with new variables
	{
		Name:        "NewInstancesNewVariables",
		Description: "New instances appear with additional variables not seen before",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 11111
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "ExpandClass",
					"Variables": [
						{
							"Name": "field1",
							"Type": "String",
							"Value": "val1"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 11111
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "ExpandClass",
					"Variables": [
						{
							"Name": "field1",
							"Type": "String",
							"Value": "val1"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst2",
					"Class": "ExpandClass",
					"Variables": [
						{
							"Name": "field1",
							"Type": "String",
							"Value": "val2"
						},
						{
							"Name": "field2",
							"Type": "Numeric",
							"Value": 999
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst2": {
				0: "val2",
				1: uint64(999),
			},
		},
		WantEvents: []any{
			&LmcParserNewVariableEvent{"field2", LMC_VAR_TYPE_NUMERIC, uint32(1), uint32(2)},
			&LmcParserNewInstanceEvent{"inst2", uint32(3), uint32(0), uint32(2)},
		},
		WantProcessChanged: false,
		WantNumInstances:   3,
		WantNumVariables:   5,
	},

	// processChanged == false: new instances with missing variables
	{
		Name:        "NewInstancesMissingVariables",
		Description: "New instances appear with a subset of variables defined for the class",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 22222
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "PartialClass",
					"Variables": [
						{
							"Name": "required",
							"Type": "String",
							"Value": "present"
						},
						{
							"Name": "optional",
							"Type": "Numeric",
							"Value": 100
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 22222
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "PartialClass",
					"Variables": [
						{
							"Name": "required",
							"Type": "String",
							"Value": "present"
						},
						{
							"Name": "optional",
							"Type": "Numeric",
							"Value": 100
						}
					],
					"Children": []
				},
				{
					"Instance": "inst2",
					"Class": "PartialClass",
					"Variables": [
						{
							"Name": "required",
							"Type": "String",
							"Value": "also_present"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst2": {
				0: "also_present",
			},
		},
		WantEvents: []any{
			&LmcParserNewInstanceEvent{"inst2", uint32(3), uint32(0), uint32(2)},
		},
		WantProcessChanged: false,
		WantNumInstances:   3,
		WantNumVariables:   5,
	},

	// processChanged == false: deleted instances
	{
		Name:        "DeletedInstances",
		Description: "Instances present in prior scan are missing in current scan",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 33333
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "TempClass",
					"Variables": [
						{
							"Name": "data",
							"Type": "String",
							"Value": "keep"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst2",
					"Class": "TempClass",
					"Variables": [
						{
							"Name": "data",
							"Type": "String",
							"Value": "delete"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 33333
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "TempClass",
					"Variables": [
						{
							"Name": "data",
							"Type": "String",
							"Value": "keep"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst1": {
				0: "keep",
			},
		},
		WantEvents: []any{
			&LmcParserInstanceDeletionEvent{uint32(3)},
		},
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   3,
	},

	// processChanged == false: mix of scenarios
	{
		Name:        "MixedScenarios",
		Description: "Combination of value changes, new instances, and deletions in single scan",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 44444
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "existing",
					"Class": "MixClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 10
						}
					],
					"Children": []
				},
				{
					"Instance": "toDelete",
					"Class": "MixClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 20
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 44444
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "existing",
					"Class": "MixClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 50
						}
					],
					"Children": []
				},
				{
					"Instance": "newInst",
					"Class": "MixClass",
					"Variables": [
						{
							"Name": "counter",
							"Type": "Counter",
							"Value": 30
						},
						{
							"Name": "extra",
							"Type": "String",
							"Value": "new_field"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"existing": {
				0: uint64(50),
			},
			"newInst": {
				0: uint64(30),
				1: "new_field",
			},
		},
		WantEvents: []any{
			&LmcParserNewVariableEvent{"extra", LMC_VAR_TYPE_STRING, uint32(1), uint32(2)},
			&LmcParserNewInstanceEvent{"newInst", uint32(4), uint32(0), uint32(2)},
			&LmcParserInstanceDeletionEvent{uint32(3)},
		},
		WantProcessChanged: false,
		WantNumInstances:   3,
		WantNumVariables:   5,
	},

	// processChanged == true: process ID changed
	{
		Name:        "ProcessIdChanged",
		Description: "Process ID changes indicating process restart",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 55555
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 99999
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T01:00:00Z"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents:        false,
		WantVariables:      map[string]map[uint32]any{},
		WantEvents:         nil,
		WantProcessChanged: true,
		WantNumInstances:   1,
		WantNumVariables:   2,
	},

	// processChanged == true: time changed
	{
		Name:        "ProcessTimeChanged",
		Description: "Process start time changes indicating process restart",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 66666
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SinkDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 66666
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T02:00:00Z"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents:        false,
		WantVariables:      map[string]map[uint32]any{},
		WantEvents:         nil,
		WantProcessChanged: true,
		WantNumInstances:   1,
		WantNumVariables:   2,
	},

	// Error: duplicate instances
	{
		Name:        "ErrorDuplicateInstances",
		Description: "Same instance appears twice in the scan",
		JsonData: `
			[
				{
					"Instance": "duplicate",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "String",
							"Value": "first"
						}
					],
					"Children": []
				},
				{
					"Instance": "duplicate",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "String",
							"Value": "second"
						}
					],
					"Children": []
				}
			]
		`,
		WantErrStr: "duplicate inst:",
	},

	// Error: inconsistent variable type
	{
		Name:        "ErrorInconsistentVariableType",
		Description: "Variable appears with different type in new instance of same class",
		PrimeJsonData: `
			[
				{
					"Instance": "inst1",
					"Class": "TypeClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "String",
							"Value": "text"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "inst1",
					"Class": "TypeClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "String",
							"Value": "text"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst2",
					"Class": "TypeClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "Numeric",
							"Value": 123
						}
					],
					"Children": []
				}
			]
		`,
		WantErrStr: "inconsistent variable type",
	},

	// Error: invalid JSON
	{
		Name:        "ErrorInvalidJson",
		Description: "Malformed JSON input",
		JsonData:    `[{invalid json}]`,
		WantErrStr:  "invalid character",
	},

	// Error: invalid variable type
	{
		Name:        "ErrorInvalidVariableType",
		Description: "Variable has unrecognized type",
		JsonData: `
			[
				{
					"Instance": "inst1",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "UnknownType",
							"Value": "value"
						}
					],
					"Children": []
				}
			]
		`,
		WantErrStr: "invalid variable type",
	},

	// Error: invalid numeric value
	{
		Name:        "ErrorInvalidNumericValue",
		Description: "Numeric variable has non-numeric value",
		JsonData: `
			[
				{
					"Instance": "inst1",
					"Class": "TestClass",
					"Variables": [
						{
							"Name": "count",
							"Type": "Counter",
							"Value": "not_a_number"
						}
					],
					"Children": []
				}
			]
		`,
		WantErrStr: "error parsing",
	},

	// Test with negative numbers
	{
		Name:        "NegativeNumbers",
		Description: "Test handling of negative numeric values",
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 77777
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "inst1",
					"Class": "NegativeClass",
					"Variables": [
						{
							"Name": "negValue",
							"Type": "Numeric",
							"Value": -42
						},
						{
							"Name": "posValue",
							"Type": "Numeric",
							"Value": 42
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"inst1": {
				0: int64(-42),
				1: uint64(42),
			},
		},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   4,
	},

	// Test with all variable types
	{
		Name:        "AllVariableTypes",
		Description: "Test all supported LMC variable types",
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 88888
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "allTypes",
					"Class": "AllTypesClass",
					"Variables": [
						{
							"Name": "boolVar",
							"Type": "Boolean",
							"Value": true
						},
						{
							"Name": "boolConfigVar",
							"Type": "Boolean Config",
							"Value": false
						},
						{
							"Name": "counterVar",
							"Type": "Counter",
							"Value": 100
						},
						{
							"Name": "gaugeVar",
							"Type": "Gauge",
							"Value": 50
						},
						{
							"Name": "gaugeConfigVar",
							"Type": "Gauge Config",
							"Value": 75
						},
						{
							"Name": "numericVar",
							"Type": "Numeric",
							"Value": 123
						},
						{
							"Name": "largeNumericVar",
							"Type": "Large Numeric",
							"Value": 9999999999
						},
						{
							"Name": "numericRangeVar",
							"Type": "Numeric Range",
							"Value": "42 (0..100)"
						},
						{
							"Name": "numericConfigVar",
							"Type": "Numeric Config",
							"Value": 88
						},
						{
							"Name": "stringVar",
							"Type": "String",
							"Value": "test"
						},
						{
							"Name": "stringConfigVar",
							"Type": "String Config",
							"Value": "config"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"allTypes": {
				0:  true,
				1:  false,
				2:  uint64(100),
				3:  uint64(50),
				4:  uint64(75),
				5:  uint64(123),
				6:  uint64(9999999999),
				7:  uint64(42),
				8:  uint64(88),
				9:  "test",
				10: "config",
			},
		},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   13,
	},

	// Test with nested children
	{
		Name:        "NestedChildren",
		Description: "Test instances with nested child instances",
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 10000
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "parent",
					"Class": "ParentClass",
					"Variables": [
						{
							"Name": "parentField",
							"Type": "String",
							"Value": "parent_value"
						}
					],
					"Children": [
						{
							"Instance": "child1",
							"Class": "ChildClass",
							"Variables": [
								{
									"Name": "childField",
									"Type": "Numeric",
									"Value": 1
								}
							],
							"Children": [
								{
									"Instance": "grandchild",
									"Class": "GrandchildClass",
									"Variables": [
										{
											"Name": "gcField",
											"Type": "String",
											"Value": "gc_value"
										}
									],
									"Children": []
								}
							]
						},
						{
							"Instance": "child2",
							"Class": "ChildClass",
							"Variables": [
								{
									"Name": "childField",
									"Type": "Numeric",
									"Value": 2
								}
							],
							"Children": []
						}
					]
				}
			]
		`,
		NoNewEvents: false,
		WantVariables: map[string]map[uint32]any{
			"parent": {
				0: "parent_value",
			},
			"child1": {
				0: uint64(1),
			},
			"child2": {
				0: uint64(2),
			},
			"grandchild": {
				0: "gc_value",
			},
		},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   5,
		WantNumVariables:   6,
	},

	// Test NoNewEvents flag
	{
		Name:        "NoNewEventsFlag",
		Description: "Test that NoNewEvents flag suppresses event generation",
		PrimeJsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 20000
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				}
			]
		`,
		JsonData: `
			[
				{
					"Instance": "proc1",
					"Class": "ManagedProcess.SrcDist",
					"Variables": [
						{
							"Name": "processID",
							"Type": "Numeric",
							"Value": 20000
						},
						{
							"Name": "time",
							"Type": "String",
							"Value": "2024-01-01T00:00:00Z"
						}
					],
					"Children": []
				},
				{
					"Instance": "newInst",
					"Class": "NewClass",
					"Variables": [
						{
							"Name": "field",
							"Type": "String",
							"Value": "value"
						}
					],
					"Children": []
				}
			]
		`,
		NoNewEvents:        true,
		WantVariables:      map[string]map[uint32]any{},
		WantEvents:         nil,
		WantProcessChanged: false,
		WantNumInstances:   2,
		WantNumVariables:   3,
	},
}
