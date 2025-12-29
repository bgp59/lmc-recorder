---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for test_schema_normalizer'
---

# Test Cases For `test_schema_normalizer`

Generate pytest cases for `test_schema_normalizer` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/commands/lmcrec_export.py](../../lmcpb/src/lmcrec/playback/commands/lmcrec_export.py)
  * [lmcpb/tests/test_schema_normalizer.py](../../lmcpb/tests/test_schema_normalizer.py)

* follow the examples from [lmcpb/tests/prompt_examples/schema_normalizer_test_cases.py](../../lmcpb/tests/prompt_examples/schema_normalizer_test_cases.py)

* the second member of each pair (tuple) in `.word_expect` list of a test case should be unique within the case

* length limit truncation occurs as follows:
  * for empty suffix:`word[:max_len]`
  * for non empty suffix: `word[:-len(suffix)][:max_len-len(suffix)]`

* create a set of simple test cases for only one condition at a time:
    * Pattern rules
    * Length limit
    * Disambiguation without additional shortening
    * Disambiguation with additional shortening
    * Suffix

* create a set of complex test cases that combine some of the test cases from above

* save the results into [lmcpb/tests/schema_normalizer_test_cases.py](../../lmcpb/tests/schema_normalizer_test_cases.py)
