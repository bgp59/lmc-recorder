import pytest

from lmcrec.playback.commands.lmcrec_export import SchemaNormalizer

from .schema_normalizer_test_cases import (
    SchemaNormalizerTestCase,
    test_cases,
)


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_schema_normalizer(tc: SchemaNormalizerTestCase):
    normalizer = SchemaNormalizer(
        tc.max_len,
        reserved_names=tc.reserved_names,
        suffix=tc.suffix,
    )
    for word, expect in tc.word_expect:
        assert normalizer(word) == expect
