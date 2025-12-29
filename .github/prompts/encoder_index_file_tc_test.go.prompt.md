---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for TestEncoderIndexFileNoErr'
---

# Test Cases For `TestEncoderIndexFileNoErr`

Generate test cases for `TestEncoderIndexFileNoErr`with the following requirements:

* use context from:

  * [lmcrec/codec/encoder.go](../../lmcrec/codec/encoder.go)
  * [lmcrec/codec/codec_test.go](../../lmcrec/codec/codec_test.go)

* no case should generate an error

* all offsets should in increasing order, in the [20..10000] range and with at least +16 increment between consecutive offsets

* all timestamps should be multiple of seconds

* assign the test cases to:

  ```go
  EncoderIndexFileNoErrTestCases = []*EncoderIndexTestCase{

  }
  ```

in [lmcrec/codec/encoder_index_file_tc_test.go](../../lmcrec/codec/encoder_index_file_tc_test.go)
