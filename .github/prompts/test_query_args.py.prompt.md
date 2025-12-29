---
agent: edit
model: Claude Sonnet 4.5
description: 'Test cases for query.args'
---

# Test Cases For `query.args`

Generate test cases for `query.args` with the following requirements:

* use context from:
  * [lmcpb/src/lmcrec/playback/query/args.py](../../lmcpb/src/lmcrec/playback/query/args.py)

* for `parse_duration` not in range error, the string to match is `UNIT not in \\[0, 60\\) range` where `UNIT` is `min` or `sec`

* save the results into [lmcpb/tests/test_query_args.py](../../lmcpb/tests/test_query_args.py)
