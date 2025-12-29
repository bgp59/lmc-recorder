---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_lmcrec_query_selector_init'
---

# Test Cases For `test_lmcrec_query_selector_init`

Generate test cases for `test_lmcrec_query_selector_init` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/query/query_selector.py](../../lmcpb/src/lmcrec/playback/query/query_selector.py)
  * [lmcpb/tests/test_query_selector.py](../../lmcpb/tests/test_query_selector.py)
  * [lmcpb/tests/query_selector_def.py](../../lmcpb/tests/query_selector_def.py)

* base on the examples from [lmcpb/tests/prompt_examples/query_selector_init_test_cases.py](../../lmcpb/tests/prompt_examples/query_selector_init_test_cases.py)

* query `n` field value should match the testcase `name`, with non-word characters removed and case insensitive

* for JSON format:
    * regexp's should be enclosed in `"`: `"/~\\.part5/"`
    * `\` should be doubled: `"/host\\.1\\.ads\\.\\S+\\.part3/"`
    * a space is required after `':'` for `key: value`

* cover the following scenarios:
  * prefix/no prefix
  * instance name/instance regexp
  * class/no class
  * simple and qualified variables
  * include/exclude types
  * include/exclude variables
  * no instances
  * no variables
  * a mix of the above

* save the results into [lmcpb/tests/query_selector_init_test_cases.py](../../lmcpb/tests/query_selector_init_test_cases.py)
