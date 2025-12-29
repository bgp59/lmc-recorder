---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_lmcrec_query_selector_run'
---

# Test Cases For `test_lmcrec_query_selector_run`

Generate test cases for `test_lmcrec_query_selector_run` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/query/query_selector.py](../../lmcpb/src/lmcrec/playback/query/query_selector.py)
  * [lmcpb/tests/test_query_selector.py](../../lmcpb/tests/test_query_selector.py)
  * [lmcpb/tests/query_selector_def.py](../../lmcpb/tests/query_selector_def.py)

* base on the examples from [lmcpb/tests/prompt_examples/query_selector_run_test_cases.py](../../lmcpb/tests/prompt_examples/query_selector_run_test_cases.py)

* observe the following rules for `var_names` in `LmcrecQueryClassResult`

  * the list is sorted alphabetically by name, case insensitive
  * for a given name, the qualifier suffixes order is given by `var_val_qual_flag_order`

* cover the following scenarios:
  * prefix/no prefix
  * instance name/instance regexp
  * simple and qualified variables
  * adjusted delta `d` for variable types in `delta_rate_types`
  * the correction is not applied for negative deltas for unadjusted delta `D` for variable types in `delta_rate_types` 
  * `d`, `D`, and `r` yield `None` for variable types not in `delta_rate_types`
  * a mix of variable value types
  * a mix of the above

* save the results into [lmcpb/tests/query_selector_run_test_cases.py](../../lmcpb/tests/query_selector_run_test_cases.py)
