---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_build_lmcrec_file_chains_ok'
---

# Test Cases For `test_build_lmcrec_file_chains_ok`

Generate test cases for `test_build_lmcrec_file_chains_ok` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/query/file_selector.py](../../lmcpb/src/lmcrec/playback/query/file_selector.py)
  * [lmcpb/tests/build_file_chains_def.py](../../lmcpb/tests/build_file_chains_def.py)
  * [lmcpb/tests/test_build_file_chains.py](../../lmcpb/tests/test_build_file_chains.py)

* base on the examples from [lmcpb/tests/prompt_examples/build_file_chains_test_cases_ok.py](../../lmcpb/tests/prompt_examples/build_file_chains_test_cases_ok.py)

* all timestamps should be in ISO 8601 format

* no test case should generate an error

* cover the following scenarios at the very least:

  * multiple files resulting in a single chain
  * multiple files resulting in multiple chains
  * files outside the `from_ts` - `to_ts` window
  * `listdir` returns the files in non-chronological order

* save the results into [lmcpb/tests/build_file_chains_test_cases_ok.py](../../lmcpb/tests/build_file_chains_test_cases_ok.py)
