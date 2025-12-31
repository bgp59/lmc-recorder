# Prompt: .github/prompts/schema_normalizer_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
"""Test cases for test_schema_normalizer"""

# IMPORTANT! manually tweaked (log message)

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
    # Simple test cases - one condition at a time
    SchemaNormalizerTestCase(
        name="PatternRulesOnly",
        description="Apply pattern rules: camelCase to snake_case, ACRONYM handling, special chars",
        max_len=0,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer"),
            ("ACRONYMWord", "acronym_word"),
            ("camelCase", "camel_case"),
            ("camel123Case", "camel123_case"),
            ("# of records", "no_of_records"),
            ("# items", "no_of_items"),
            ("my-special.var!", "my_special_var"),
            ("__leading_underscores", "leading_underscores"),
            ("trailing_underscores__", "trailing_underscores"),
            ("multiple___underscores", "multiple_underscores"),
            ("123starts_with_digit", "_123starts_with_digit"),
            ("MixedCASEWord", "mixed_case_word"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthLimitOnly",
        description="Truncate words to max_len when no suffix is present",
        max_len=10,
        word_expect=[
            ("short", "short"),
            ("exactly_ten", "exactly_te"),
            ("this_is_a_very_long_variable_name", "this_is_a_"),
            ("SchemaNormalizer", "schema_nor"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SimpleDisambiguationOnly",
        description="Add numeric suffix for duplicate normalized names",
        max_len=0,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer"),
            ("SchemaNormalizer", "schema_normalizer2"),
            ("SchemaNormalizer", "schema_normalizer3"),
            ("schema_normalizer", "schema_normalizer4"),
            ("Schema-Normalizer", "schema_normalizer5"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="DisambiguationWithShortening",
        description="Shorten word when disambiguation suffix causes length overflow",
        max_len=10,
        word_expect=[
            ("verylongname", "verylongna"),
            ("verylongname", "verylongn2"),
            ("verylongname", "verylongn3"),
            ("verylongname", "verylongn4"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixOnly",
        description="Append suffix to normalized words",
        suffix="_t",
        max_len=0,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer_t"),
            ("MyTable", "my_table_t"),
            ("simple", "simple_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixWithDuplicates",
        description="Handle disambiguation when suffix is present",
        suffix="_t",
        max_len=0,
        word_expect=[
            ("MyTable", "my_table_t"),
            ("MyTable", "my_table2_t"),
            ("my_table", "my_table3_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ReservedNamesOnly",
        description="Skip reserved names in disambiguation sequence",
        max_len=0,
        reserved_names=["schema_normalizer", "schema_normalizer3"],
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer2"),
            ("SchemaNormalizer", "schema_normalizer4"),
            ("schema_normalizer", "schema_normalizer5"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ReservedNamesWithSuffix",
        description="Handle reserved names that end with the suffix",
        suffix="_col",
        reserved_names=["my_var_col", "another_var_col"],
        max_len=0,
        word_expect=[
            ("MyVar", "my_var2_col"),
            ("AnotherVar", "another_var2_col"),
            ("NewVar", "new_var_col"),
        ]
    ),
    
    # Complex test cases - combining multiple conditions
    SchemaNormalizerTestCase(
        name="PatternAndLengthLimit",
        description="Apply pattern rules then truncate to length limit",
        max_len=15,
        word_expect=[
            ("VeryLongCamelCaseVariable", "very_long_camel"),
            ("AnotherLongACRONYMWord", "another_long_ac"),
            ("# of very long items", "no_of_very_long"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthLimitAndDisambiguation",
        description="Truncate to max_len and handle disambiguation",
        max_len=12,
        word_expect=[
            ("verylongname", "verylongname"),
            ("verylongname", "verylongnam2"),
            ("verylongname", "verylongnam3"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthLimitWithSuffix",
        description="Account for suffix length when truncating",
        max_len=15,
        suffix="_col",
        word_expect=[
            ("ShortName", "short_name_col"),
            ("ExactlyTenChars", "exactly_ten_col"),
            ("VeryLongVariableName", "very_long_v_col"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="PatternLengthAndSuffix",
        description="Apply patterns, truncate, and add suffix",
        max_len=20,
        suffix="_t",
        word_expect=[
            ("MySpecialTable", "my_special_table_t"),
            ("VeryLongTableNameHere", "very_long_table_na_t"),
            ("ACRONYMTableName", "acronym_table_name_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="AllConditionsCombined",
        description="Pattern rules, length limit, disambiguation, suffix, and reserved names",
        max_len=18,
        suffix="_col",
        reserved_names=["my_var_col"],
        word_expect=[
            ("MyVar", "my_var2_col"),
            ("MyVar", "my_var3_col"),
            ("VeryLongVariableName", "very_long_vari_col"),
            ("VeryLongVariableName", "very_long_var2_col"),
            ("# of items", "no_of_items_col"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="EdgeCaseSuffixTruncation",
        description="Handle edge cases where suffix and word both need adjustment",
        max_len=12,
        suffix="_type",
        word_expect=[
            ("short", "short_type"),
            ("mediumname", "mediumn_type"),
            ("verylongname", "verylon_type"),
            ("verylongname", "verylo2_type"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ComplexPatternHandling",
        description="Test complex patterns with multiple special characters and mixed cases",
        max_len=0,
        word_expect=[
            ("HTTPSConnection", "https_connection"),
            ("XMLParser", "xml_parser"),
            ("getHTTPResponse", "get_http_response"),
            ("parseJSONData", "parse_json_data"),
            ("# of HTTP requests", "no_of_http_requests"),
            ("user-ID_123", "user_id_123"),
            ("data__with___many____underscores", "data_with_many_underscores"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="DisambiguationWithReservedAndSuffix",
        description="Complex disambiguation with reserved names and suffix",
        max_len=20,
        suffix="_t",
        reserved_names=["my_table_t", "my_table3_t"],
        word_expect=[
            ("MyTable", "my_table2_t"),
            ("MyTable", "my_table4_t"),
            ("my_table", "my_table5_t"),
            ("MY_TABLE", "my_table6_t"),
        ]
    ),
]

# fmt: on
