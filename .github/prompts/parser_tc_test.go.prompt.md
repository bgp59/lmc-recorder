---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestParser'
---

# Test Cases For `TestParser`

Requirements:

* use context from:

  * [lmcrec/parser/parser.go](../../lmcrec/parser/parser.go)
  * [lmcrec/parser/parser_test.go](../../lmcrec/parser/parser_test.go)

* numerical value types  should be `uint64` for positive (>=0) numbers and `int64` for strictly negative numbers (< 0)

* `LmcParser.Parse` returns `(processChanged bool, numInstances int, numVariables int, err error)`, where:
  * `numInstances` counts the **total** number of instances found in `JsonData`
  * `numVariables` counts the **total** number across all instances found in `JsonData`

* the `LmcParser.Events` should be `nil` if no events are expected, which is the case under the following conditions:
  * there is no prior scan (`PrimeJsonData` is empty)
  * a process change is detected
  * `checkpoint` is `true` and no instances are deleted

* all testcases returning `processChanged == false` should observe the following:
  * include an instance/instances with a class from `ProcessCheckClassAndVariables` with the same content in prior (if applicable) and current scan
  * include an instance/instances with a class not in `ProcessCheckClassAndVariables` for testing returned valued and events

* have testcases returning `processChanged == false` for the following scenario:
  * no prior scan
  * prior and current scan with some variable value change(s) but without any events
  * prior and current scan with new instances of the same class with the same variables
  * prior and current scan with new instances of the same class with new variables in the subsequent apparition
  * prior and current scan with new instances of the same class with missing variables in the subsequent apparition
  * prior and current scan with deleted instances
  * a mix of the above for prior and current scan cases

* have testcases returning `processChanged == true` where the same class from `ProcessCheckClassAndVariables` is used with one or more variable values changed

* have testcases for the following error scenarios:
  * duplicate instances
  * inconsistent variable type
  * invalid JSON
  * invalid variable types
  * invalid variable values, inconsistent with the type

* assign the test cases to:

  ```go
  var ParserTestCases = []*ParserTestCase{

  }
  ```

  in [lmcrec/parser/parser_tc_test.go](../../lmcrec/parser/parser_tc_test.go)
