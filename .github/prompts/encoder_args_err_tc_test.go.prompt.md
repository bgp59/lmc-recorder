---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestEncoderArgsErr'
---

# Test Cases For `TestEncoderArgsErr`

Generate test cases for `TestEncoderArgsErr` with the following requirements:

* use context from:

  * [lmcrec/codec/encoder.go](../../lmcrec/codec/encoder.go)
  * [lmcrec/codec/decoder.go](../../lmcrec/codec/decoder.go)
  * [lmcrec/codec/codec_test.go](../../lmcrec/codec/codec_test.go)

* all cases should generate an error due to mismatch args

* the `WriteErrAtCallCount` field in `EncoderErrTestCase` should be set to -1

* assign the test cases to:

  ```go
  EncoderArgsErrTestCases = []*EncoderDecoderTestCase{
  
  }
  ```

  in [lmcrec/codec/encoder_args_err_tc_test.go](../../lmcrec/codec/encoder_args_err_tc_test.go)
