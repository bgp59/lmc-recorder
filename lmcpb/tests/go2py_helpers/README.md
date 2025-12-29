# Python Decoder Test Helpers

Since the recorder is written in Golang and the decoder in Python, unit tests to
verify their compatibility are required.

The helpers in this sub-directory use [lmcrec/codec](../../../lmcrec/codec/) to
encode into byte sequences and generate test cases for Python as a list of
tuples (_byte sequence_, _expected Python value_).

A specific helper is invoked via `./run.sh ..._helper` command.
