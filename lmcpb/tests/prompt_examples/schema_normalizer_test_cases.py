"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple


@dataclass
class SchemaNormalizerTestCase:
    name: str = ""
    description: str = ""
    max_len: int = 0
    reserved_names: Optional[Iterable[str]] = None
    suffix: str = ""
    word_expect: List[Tuple[str, str]] = field(default_factory=list)

test_cases = [
    SchemaNormalizerTestCase(
        name="PatternRulesOnly",
        max_len=30,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer"),
            ("ACRONYMWord", "acronym_word"),
            ("camelCase", "camel_case"),
            ("camel123Case", "camel123_case"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthLimitOnly",
        max_len=6,
        word_expect=[
            ("SchemaNormalizer", "schema"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SimpleDisambiguationOnly",
        max_len=30,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer"),
            ("SchemaNormalizer", "schema_normalizer2"),
            ("SchemaNormalizer", "schema_normalizer3"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SimpleDisambiguationWithSuffix",
        suffix="_t",
        max_len=30,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer_t"),
            ("SchemaNormalizer", "schema_normalizer2_t"),
            ("SchemaNormalizer", "schema_normalizer3_t"),
        ]
    ),
]

# fmt: on
