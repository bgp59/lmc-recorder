---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for loadRecorderConfig'
---

# Test Cases For `loadRecorderConfig`

Generate test cases for `loadRecorderConfig`with the following requirements:

* use context from [lmcrec/recorder/recorder_config.go](../../lmcrec/recorder/recorder_config.go)

* for all the tests, regardless whether they have `default` or `recorders` sections, check **all** the fields for which `RECORDER_CONFIG_..._DEFAULT` are applicable.

* when checking the results run the test in 2 steps, for example:

    ```go
    if config.Field == nil {
        t.Error("field Field should not be nil")
    } else if want, got = ..., *config.Field; want != got {
        t.Errorf("field Field: want: %v, got: %v", want, got)
    }
    ```
* do not test logger config

* prefix all tests with `TestLoadRecorderConfig...`

* save the results in [lmcrec/recorder/recorder_config_test.go](../../lmcrec/recorder/recorder_config_test.go)
