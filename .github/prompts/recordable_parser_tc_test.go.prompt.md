---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestRecordableParser'
---

# Test Cases For `TestRecordableParser`

Generate test cases for `TestRecordableParser` with the following requirements:

* use context from:

  * [lmcrec/codec/encoder.go](../../lmcrec/codec/encoder.go)
  * [lmcrec/parser/parser.go](../../lmcrec/parser/parser.go)
  * [lmcrec/recorder/recordable_parser.go](../../lmcrec/recorder/recordable_parser.go)
  * [lmcrec/recorder/recordable_parser_test.go](../../lmcrec/recorder/recordable_parser_test.go)
  * [lmcrec/recorder/recorder_utils_test.go](../../lmcrec/recorder/recorder_utils_test.go)

* assign the test cases to:

  ```go
  var RecordableParserTestCases = []*RecordableParserTestCase {

  }
  ```

  in [lmcrec/recorder/recordable_parser_tc_test.go](../../lmcrec/recorder/recordable_parser_tc_test.go)
