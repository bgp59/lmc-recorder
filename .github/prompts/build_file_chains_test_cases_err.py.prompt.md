---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_build_lmcrec_file_chains_err'
---

# Test Cases For `test_build_lmcrec_file_chains_err`

Generate test cases for `test_build_lmcrec_file_chains_err` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/query/file_selector.py](../../lmcpb/src/lmcrec/playback/query/file_selector.py)
  * [lmcpb/tests/build_file_chains_def.py](../../lmcpb/tests/build_file_chains_def.py)
  * [lmcpb/tests/test_build_file_chains.py](../../lmcpb/tests/test_build_file_chains.py)

* base on the examples from [lmcpb/tests/prompt_examples/build_file_chains_test_cases_err.py](../../lmcpb/tests/prompt_examples/build_file_chains_test_cases_err.py)

* all timestamps should be in ISO 8601 format

* all test case should generate an error

* cover the following scenarios:

  * mix of lmcrec files and sub-dirs at top level
  * chronological order violation

* save the results into [lmcpb/tests/build_file_chains_test_cases_err.py](../../lmcpb/tests/build_file_chains_test_cases_err.py)
