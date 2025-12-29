---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_db_mapping_init'
---

# Test Cases For `test_db_mapping_init`

Generate pytest cases for `test_db_mapping_init` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/commands/lmcrec_export.py](../../lmcpb/src/lmcrec/playback/commands/lmcrec_export.py)
  * [lmcpb/tests/test_db_mapping_init.py](../../lmcpb/tests/test_db_mapping_init.py)

* follow the examples from [lmcpb/tests/prompt_examples/db_mapping_init_test_cases.py](../../lmcpb/tests/prompt_examples/db_mapping_init_test_cases.py)

* use raw strings `r"""..."""` for YAML content

* follow [lmcpb/tests/prompt_examples/schema_normalizer_test_cases.py](../../lmcpb/tests/prompt_examples/schema_normalizer_test_cases.py) for normalization examples; use only simple cases

* cover all scenarios such as:
  * all LMC data types; for numeric types consider both `neg_vals` `true` and `false`
  * boolean types with different `db_type` and `true_value` and `default_value`, such: `char`, `T`, `F`
  * LMC schema string var or instance max size overrides the one in DB mapping
  * unsupported category LMC data type error condition

* save the results into [lmcpb/tests/db_mapping_init_test_cases.py](../../lmcpb/tests/db_mapping_init_test_cases.py)
