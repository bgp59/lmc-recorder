---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestEncoderWriteErr'
---

# Test Cases For `TestEncoderWriteErr`

Generate test cases for `TestEncoderWriteErr`with the following requirements:

* use context from:

  * [lmcrec/codec/encoder.go](../../lmcrec/codec/encoder.go)
  * [lmcrec/codec/codec_test.go](../../lmcrec/codec/codec_test.go)

* all test cases should generate a write error based `WriteErrAtCallCount` field in `EncoderErrTestCase`

* assign the test cases to:

  ```go
  EncoderWriteErrTestCases = []*EncoderInfoTestCase{

  }
  ```

in [lmcrec/codec/encoder_write_err_tc_test.go](../../lmcrec/codec/encoder_write_err_tc_test.go)
