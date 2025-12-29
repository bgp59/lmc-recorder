# Prompt: .github/prompts/db_mapping_init_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5

"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from dataclasses import dataclass
from typing import Optional


@dataclass
class LmcrecDbMappingInitTestCase:
    name: str = ""
    description: str = ""
    lmcrec_schema: str = ""
    db_mapping: Optional[str] = None
    expect_tables: Optional[dict] = None
    expect_lmc_classes: Optional[dict] = None
    expect_exception: Optional[Exception] = None
    expect_exception_str: Optional[str] = None

test_cases = [
    LmcrecDbMappingInitTestCase(
        name="DefaultBasicDbMapping",
        description="Test default DB mapping with basic numeric, string, and boolean types",
        lmcrec_schema=r"""
        classes:
            TestClass:
                numericVar:
                    type: NUMERIC
                stringVar:
                    type: STRING
                    max_size: 17
                booleanVar:
                    type: BOOLEAN
        info:
            inst_max_size: 123
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("boolean_var_col", "tinyint", False),
                ("numeric_var_col", "int", False),               
                ("string_var_col", "varchar(32)", True),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "booleanVar": ("BOOLEAN", 2),
                    "numericVar": ("NUMERIC", 3),
                    "stringVar": ("STRING", 4),
                },
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="AllNumericTypes",
        description="Test all numeric type variants with signed and unsigned values",
        lmcrec_schema=r"""
        classes:
            NumericClass:
                counterVar:
                    type: COUNTER
                gaugeVar:
                    type: GAUGE
                gaugeConfigVar:
                    type: GAUGE_CONFIG
                numericVar:
                    type: NUMERIC
                numericConfigVar:
                    type: NUMERIC_CONFIG
                numericRangeVar:
                    type: NUMERIC_RANGE
                signedNumericVar:
                    type: NUMERIC
                    neg_vals: true
                largeNumericVar:
                    type: LARGE_NUMERIC
                signedLargeNumericVar:
                    type: LARGE_NUMERIC
                    neg_vals: true
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "numeric_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("counter_var_col", "int", False),
                ("gauge_config_var_col", "int", False),
                ("gauge_var_col", "int", False),
                ("large_numeric_var_col", "bigint", False),
                ("numeric_config_var_col", "int", False),
                ("numeric_range_var_col", "int", False),
                ("numeric_var_col", "int", False),
                ("signed_large_numeric_var_col", "bigint", False),
                ("signed_numeric_var_col", "int", False),
            ]
        },
        expect_lmc_classes={
            "NumericClass": (
                "numeric_class_t",
                {
                    "counterVar": ("COUNTER", 2),
                    "gaugeConfigVar": ("GAUGE_CONFIG", 3),
                    "gaugeVar": ("GAUGE", 4),
                    "largeNumericVar": ("LARGE_NUMERIC", 5),
                    "numericConfigVar": ("NUMERIC_CONFIG", 6),
                    "numericRangeVar": ("NUMERIC_RANGE", 7),
                    "numericVar": ("NUMERIC", 8),
                    "signedLargeNumericVar": ("LARGE_NUMERIC", 9),
                    "signedNumericVar": ("NUMERIC", 10),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="SignedUnsignedNumericMapping",
        description="Test signed and unsigned numeric types with custom DB mapping",
        lmcrec_schema=r"""
        classes:
            TestClass:
                unsignedVar:
                    type: NUMERIC
                signedVar:
                    type: NUMERIC
                    neg_vals: true
                unsignedLargeVar:
                    type: LARGE_NUMERIC
                signedLargeVar:
                    type: LARGE_NUMERIC
                    neg_vals: true
        info:
            inst_max_size: 100
        """,
        db_mapping=r"""
            data_type_mapping:
                numeric:
                    signed_col_type: int
                    unsigned_col_type: unsigned int
                large_numeric:
                    signed_col_type: bigint
                    unsigned_col_type: unsigned bigint
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("signed_large_var_col", "bigint", False),
                ("signed_var_col", "int", False),
                ("unsigned_large_var_col", "unsigned bigint", False),
                ("unsigned_var_col", "unsigned int", False),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "signedLargeVar": ("LARGE_NUMERIC", 2),
                    "signedVar": ("NUMERIC", 3),
                    "unsignedLargeVar": ("LARGE_NUMERIC", 4),
                    "unsignedVar": ("NUMERIC", 5),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="AllStringTypes",
        description="Test string and string_config types with various max_size values",
        lmcrec_schema=r"""
        classes:
            StringClass:
                stringVar:
                    type: STRING
                    max_size: 50
                stringConfigVar:
                    type: STRING_CONFIG
                    max_size: 100
                smallStringVar:
                    type: STRING
                    max_size: 10
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "string_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("small_string_var_col", "varchar(32)", True),
                ("string_config_var_col", "varchar(100)", True),
                ("string_var_col", "varchar(50)", True),
            ]
        },
        expect_lmc_classes={
            "StringClass": (
                "string_class_t",
                {
                    "smallStringVar": ("STRING", 2),
                    "stringConfigVar": ("STRING_CONFIG", 3),
                    "stringVar": ("STRING", 4),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="AllBooleanTypes",
        description="Test boolean and boolean_config types",
        lmcrec_schema=r"""
        classes:
            BooleanClass:
                booleanVar:
                    type: BOOLEAN
                booleanConfigVar:
                    type: BOOLEAN_CONFIG
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "boolean_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("boolean_config_var_col", "tinyint", False),
                ("boolean_var_col", "tinyint", False),
            ]
        },
        expect_lmc_classes={
            "BooleanClass": (
                "boolean_class_t",
                {
                    "booleanConfigVar": ("BOOLEAN_CONFIG", 2),
                    "booleanVar": ("BOOLEAN", 3),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="BooleanCharMapping",
        description="Test boolean type with char DB type and T/F values",
        lmcrec_schema=r"""
        classes:
            TestClass:
                booleanVar:
                    type: BOOLEAN
        info:
            inst_max_size: 100
        """,
        db_mapping=r"""
            data_type_mapping:
                boolean:
                    col_type: char(1)
                    true_value: T
                    false_value: F
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("boolean_var_col", "char(1)", False),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "booleanVar": ("BOOLEAN", 2),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="BooleanBitMapping",
        description="Test boolean type with bit DB type",
        lmcrec_schema=r"""
        classes:
            TestClass:
                booleanVar:
                    type: BOOLEAN
        info:
            inst_max_size: 100
        """,
        db_mapping=r"""
            data_type_mapping:
                boolean:
                    col_type: bit
                    true_value: 1
                    false_value: 0
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("boolean_var_col", "bit", False),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "booleanVar": ("BOOLEAN", 2),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="DefaultDbMappingWithOverrides",
        description="Test default DB mapping with schema overrides for inst_max_size and string max_size",
        lmcrec_schema=r"""
        classes:
            TestClass:
                numericVar:
                    type: NUMERIC
                stringVar:
                    type: STRING
                    max_size: 64
                booleanVar:
                    type: BOOLEAN
        info:
            inst_max_size: 280
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(280)", True),
                ("boolean_var_col", "tinyint", False),
                ("numeric_var_col", "int", False),
                ("string_var_col", "varchar(64)", True),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t", 
                {
                    "booleanVar": ("BOOLEAN", 2),
                    "numericVar": ("NUMERIC", 3),
                    "stringVar": ("STRING", 4),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="StringMaxSizeOverride",
        description="Test that LMC schema string max_size overrides DB mapping default when larger",
        lmcrec_schema=r"""
        classes:
            TestClass:
                largeStringVar:
                    type: STRING
                    max_size: 500
                smallStringVar:
                    type: STRING
                    max_size: 20
        info:
            inst_max_size: 100
        """,
        db_mapping=r"""
            data_type_mapping:
                string:
                    col_type: "varchar({max(max_size, 64)})"
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("large_string_var_col", "varchar(500)", True),
                ("small_string_var_col", "varchar(64)", True),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "largeStringVar": ("STRING", 2),
                    "smallStringVar": ("STRING", 3),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="InstanceMaxSizeOverride",
        description="Test that LMC schema inst_max_size overrides DB mapping default when larger",
        lmcrec_schema=r"""
        classes:
            TestClass:
                numericVar:
                    type: NUMERIC
        info:
            inst_max_size: 500
        """,
        db_mapping=r"""
            instance_col:
                col_type: "varchar({max(inst_max_size, 128)})"
        """,
        expect_tables={
            "test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(500)", True),
                ("numeric_var_col", "int", False),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class_t",
                {
                    "numericVar": ("NUMERIC", 2),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="DbMapping",
        description="Test comprehensive DB mapping with custom names, types, and suffixes",
        lmcrec_schema=r"""
        classes:
            TestClass:
                numericVar:
                    type: NUMERIC
                signedNumericVar:
                    type: NUMERIC
                    neg_vals: true
                stringVar:
                    type: STRING
                    max_size: 32
                booleanVar:
                    type: BOOLEAN
        info:
            inst_max_size: 113
        """,
        db_mapping=r"""
            table_name_max_size: 25
            col_name_max_size: 255
            table_name_suffix:
            col_name_suffix: _cl
            timestamp_col:
                name: lmc_ts_col
                col_type: datetime
                strftime: "%Y-%m-%d %H:%M:%S.{msec}"
            instance_col:
                name: lmc_inst_col
                col_type: "varchar({max(inst_max_size, 128)})"   
            data_type_mapping:
                numeric:
                    signed_col_type: int
                    unsigned_col_type: unsigned int
                large_numeric:
                    signed_col_type: bigint
                    unsigned_col_type: unsigned bigint
                string:
                    col_type: "varchar({max(max_size, 64)})"
                boolean:
                    col_type: bit
                    true_value: 1
                    false_value: 0
        """,
        expect_tables={
            "test_class": [
                ("lmc_ts_col", "datetime", False),
                ("lmc_inst_col", "varchar(128)", True),
                ("boolean_var_cl", "bit", False),
                ("numeric_var_cl", "unsigned int", False),
                ("signed_numeric_var_cl", "int", False),
                ("string_var_cl", "varchar(64)", True),
            ]
        },
        expect_lmc_classes={
            "TestClass": (
                "test_class",
                {
                    "booleanVar": ("BOOLEAN", 2),
                    "numericVar": ("NUMERIC", 3),
                    "signedNumericVar": ("NUMERIC", 4), 
                    "stringVar": ("STRING", 5),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="NormalizationSimple",
        description="Test simple name normalization with CamelCase conversion",
        lmcrec_schema=r"""
        classes:
            MyTestClass:
                myTestVar:
                    type: NUMERIC
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "my_test_class_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("my_test_var_col", "int", False),
            ]
        },
        expect_lmc_classes={
            "MyTestClass": (
                "my_test_class_t",
                {
                    "myTestVar": ("NUMERIC", 2),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="NormalizationAcronym",
        description="Test normalization with acronyms in names",
        lmcrec_schema=r"""
        classes:
            HTTPSConnection:
                TCPPort:
                    type: NUMERIC
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "https_connection_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("tcp_port_col", "int", False),
            ]
        },
        expect_lmc_classes={
            "HTTPSConnection": (
                "https_connection_t",
                {
                    "TCPPort": ("NUMERIC", 2),
                }
            )
        },
    ),
    LmcrecDbMappingInitTestCase(
        name="NormalizationWithNumbers",
        description="Test normalization with numbers in names",
        lmcrec_schema=r"""
        classes:
            Class123Test:
                var456Test:
                    type: NUMERIC
        info:
            inst_max_size: 100
        """,
        expect_tables={
            "class123_test_t": [
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                ("var456_test_col", "int", False),
            ]
        },
        expect_lmc_classes={
            "Class123Test": (
                "class123_test_t",
                {
                    "var456Test": ("NUMERIC", 2),
                }
            )
        },
    ),
]

# fmt: on
