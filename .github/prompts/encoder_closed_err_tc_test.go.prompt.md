---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestEncoderClosedErr'
---

# Test Cases For `TestEncoderClosedErr`

Generate test cases for `TestEncoderClosedErr` with the following requirements:

* use context from:

  * [lmcrec/codec/encoder.go](../../lmcrec/codec/encoder.go)
  * [lmcrec/codec/decoder.go](../../lmcrec/codec/decoder.go)
  * [lmcrec/codec/codec_test.go](../../lmcrec/codec/codec_test.go)

* test all record generating methods `*CodecLmcrecEncoder`

* the `WriteErrAtCallCount` field in `EncoderErrTestCase` should be set to 0

* assign the test cases to:
  
  ```go
  EncoderClosedErrTestCases = []*EncoderErrTestCase{

  }
  ```
  
  in [lmcrec/codec/encoder_closed_err_tc_test.go](../../lmcrec/codec/encoder_closed_err_tc_test.go)
