---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_lmcrec_query_selector_update_ok'
---

# Test Cases For `test_lmcrec_query_selector_update_ok`

Generate pytest cases for `test_lmcrec_query_selector_update_ok` with the following requirements:

* use context from:

  * [lmcpb/src/lmcrec/playback/query/query_selector.py](../../lmcpb/src/lmcrec/playback/query/query_selector.py)
  * [lmcpb/tests/test_query_selector.py](../../lmcpb/tests/test_query_selector.py)
  * [lmcpb/tests/query_selector_def.py](../../lmcpb/tests/query_selector_def.py)

* base on the examples from [lmcpb/tests/prompt_examples/query_selector_update_test_cases.py](../../lmcpb/tests/prompt_examples/query_selector_update_test_cases.py)

* the variable list is sorted alphabetically, case insensitive

* cover the following scenarios:
  * single/multiple of each: instance name, prefix or regexp
  * have a regexp case with `\d*` pattern
  * class/no class
  * simple and qualified variables
  * simple and qualified types
  * no instances
  * no variables
  * new/deleted instances in `.query_state_cache` compared to `.selector_primer`
  * new class definitions in `.query_state_cache` compared to `.selector_primer`
  * a mix of the above

* save the results into [lmcpb/tests/query_selector_update_test_cases.py](../../lmcpb/tests/query_selector_update_test_cases.py)
