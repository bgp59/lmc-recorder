# Prompt: .github/prompts/schema_normalizer_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
"""Test cases for test_schema_normalizer"""

# see commit message "manual tweak"

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
        description="Test pattern-based normalization rules without length or disambiguation constraints",
        max_len=0,
        word_expect=[
            ("SchemaNormalizer", "schema_normalizer"),
            ("ACRONYMWord", "acronym_word"),
            ("camelCase", "camel_case"),
            ("camel123Case", "camel123_case"),
            ("# of items", "no_of_items"),
            ("# records", "no_of_records"),
            ("My__Special___Variable", "my_special_variable"),
            ("_leadingUnderscore", "leading_underscore"),
            ("trailingUnderscore_", "trailing_underscore"),
            ("Multiple   Spaces", "multiple_spaces"),
            ("123StartWithDigit", "_123_start_with_digit"),
            ("special!@#chars", "special_chars"),
            ("end!!!special", "end_special"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthLimitOnly",
        description="Test length truncation without suffix or disambiguation",
        max_len=10,
        word_expect=[
            ("SchemaNormalizer", "schema_nor"),
            ("ShortName", "short_name"),
            ("VeryLongVariableName", "very_long_"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SimpleDisambiguationOnly",
        description="Test disambiguation by appending numbers without additional shortening",
        max_len=0,
        word_expect=[
            ("FirstVariable", "first_variable"),
            ("FirstVariable", "first_variable2"),
            ("FirstVariable", "first_variable3"),
            ("DifferentName", "different_name"),
            ("FirstVariable", "first_variable4"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="DisambiguationWithShortening",
        description="Test disambiguation that requires truncation to fit within max_len",
        max_len=12,
        word_expect=[
            ("VeryLongName", "very_long_na"),
            ("VeryLongName", "very_long_n2"),
            ("VeryLongName", "very_long_n3"),
            ("VeryLongName", "very_long_n4"),
            ("VeryLongName", "very_long_n5"),
            ("VeryLongName", "very_long_n6"),
            ("VeryLongName", "very_long_n7"),
            ("VeryLongName", "very_long_n8"),
            ("VeryLongName", "very_long_n9"),
            ("VeryLongName", "very_long_10"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixOnly",
        description="Test suffix addition without other constraints",
        suffix="_col",
        max_len=0,
        word_expect=[
            ("VariableName", "variable_name_col"),
            ("AnotherVar", "another_var_col"),
            ("AlreadyHasSuffix_col", "already_has_suffix_col"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ReservedNamesOnly",
        description="Test that reserved names cause disambiguation",
        max_len=0,
        reserved_names=["status", "count", "value"],
        word_expect=[
            ("status", "status2"),
            ("count", "count2"),
            ("value", "value2"),
            ("normal", "normal"),
        ]
    ),
    
    # Complex test cases - combining multiple conditions
    SchemaNormalizerTestCase(
        name="PatternAndLength",
        description="Test pattern rules combined with length limit",
        max_len=15,
        word_expect=[
            ("VeryLongCamelCaseName", "very_long_camel"),
            ("ACRONYMTest", "acronym_test"),
            ("Short", "short"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="PatternAndDisambiguation",
        description="Test pattern rules with disambiguation",
        max_len=0,
        word_expect=[
            ("CamelCaseName", "camel_case_name"),
            ("CamelCaseName", "camel_case_name2"),
            ("camelCaseName", "camel_case_name3"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="LengthAndDisambiguation",
        description="Test length limit with disambiguation",
        max_len=8,
        word_expect=[
            ("LongName", "long_nam"),
            ("LongName", "long_na2"),
            ("LongName", "long_na3"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixAndLength",
        description="Test suffix with length limit",
        suffix="_t",
        max_len=10,
        word_expect=[
            ("TableName", "table_na_t"),
            ("Short", "short_t"),
            ("VeryLongTableName", "very_lon_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixAndDisambiguation",
        description="Test suffix with disambiguation",
        suffix="_t",
        max_len=0,
        word_expect=[
            ("MyTable", "my_table_t"),
            ("MyTable", "my_table2_t"),
            ("MyTable", "my_table3_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ReservedWithSuffix",
        description="Test reserved names with suffix handling",
        suffix="_col",
        max_len=0,
        reserved_names=["special_col", "normal"],
        word_expect=[
            ("special", "special2_col"),
            ("normal", "normal2_col"),
            ("other", "other_col"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="AllConditionsCombined",
        description="Test all conditions: patterns, length, disambiguation, suffix, and reserved names",
        suffix="_t",
        max_len=15,
        reserved_names=["table", "schema"],
        word_expect=[
            ("VeryLongTableName", "very_long_tab_t"),
            ("VeryLongTableName", "very_long_ta2_t"),
            ("CamelCaseName", "camel_case_na_t"),
            ("table", "table2_t"),
            ("schema", "schema2_t"),
            ("ACRONYMName", "acronym_name_t"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="EdgeCasePatterns",
        description="Test edge cases in pattern matching",
        max_len=0,
        word_expect=[
            ("___multiple_underscores___", "multiple_underscores"),
            ("ALLCAPS", "allcaps"),
            ("lowercaseonly", "lowercaseonly"),
            ("123456", "_123456"),
            ("ABC123DEF", "abc123_def"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="ComplexDisambiguationScenario",
        description="Test complex disambiguation with varied inputs",
        max_len=18,
        word_expect=[
            ("VariableName", "variable_name"),
            ("variable_name", "variable_name2"),
            ("Variable_Name", "variable_name3"),
            ("VARIABLE_NAME", "variable_name4"),
        ]
    ),
    SchemaNormalizerTestCase(
        name="SuffixOverlapHandling",
        description="Test handling when normalized word ends with suffix pattern",
        suffix="_col",
        max_len=0,
        word_expect=[
            ("MyColumn", "my_column_col"),
            ("status_col", "status_col"),
            ("data__col", "data_col"),
        ]
    ),
]

# fmt: on
