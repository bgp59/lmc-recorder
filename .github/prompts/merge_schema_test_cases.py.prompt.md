---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_merge_lmcrec_schema'
---

# Test Cases For `test_merge_lmcrec_schema`

Generate test cases for `test_merge_lmcrec_schema` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/commands/lmcrec_schema.py](../../lmcpb/src/lmcrec/playback/commands/lmcrec_schema.py)
  * [lmcpb/tests/test_merge_schema.py](../../lmcpb/tests/test_merge_schema.py)

* base on the examples from [lmcpb/tests/prompt_examples/merge_schema_test_cases.py](../../lmcpb/tests/prompt_examples/merge_schema_test_cases.py)

* cover all scenarios such as:
  * new classes
  * new class variables
  * unique classes and variablies in either `into_schema` or `new_schema` should appear in merge
  * change in `inst_max_size`, `max_size`: increase should be reflected in merge, decrease or same should not
  * change in `neg_val_flag`: only `False` -> `True` should be reflected in merge
  * error conditions

* save the results into [lmcpb/tests/merge_schema_test_cases.py](../../lmcpb/tests/merge_schema_test_cases.py)
