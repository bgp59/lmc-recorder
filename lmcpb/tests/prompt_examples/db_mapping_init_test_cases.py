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
                # Timestamp and instance should always be the 1st and 2nd
                # columns:
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(255)", True),
                # The rest of the columns should be sorted in ascending order by
                # name, case insensitive:
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
        name="DefaultDbMappingWithOverrides",
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
                # Timestamp and instance should always be the 1st and 2nd
                # columns:
                ("__ts__", "datetime", False),
                ("__inst__", "varchar(280)", True),
                # The rest of the columns should be sorted in ascending order by
                # name, case insensitive:
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
        name="DbMapping",
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
                # Timestamp and instance should always be the 1st and 2nd
                # columns:
                ("lmc_ts_col", "datetime", False),
                ("lmc_inst_col", "varchar(128)", True),
                # The rest of the columns should be sorted in ascending order by
                # name, case insensitive:
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
]

# fmt: on
