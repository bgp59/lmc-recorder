"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from dataclasses import dataclass
from typing import Optional


@dataclass
class MergeLmcrecSchemaTestCase:
    name: str = ""
    description: str = ""
    into_schema: Optional[str] = None
    new_schema: Optional[str] = None
    expect_schema: Optional[str] = None
    expect_updated: bool = False
    expect_exception: Optional[Exception] = None
    expect_exception_str: Optional[str] = None

SAME_AS_INTO_SCHEMA = object()
SAME_AS_NEW_SCHEMA = object()

test_cases = [
    MergeLmcrecSchemaTestCase(
        name = "NoPriorIntoSchema",
        description = "Simply load new schema",
        new_schema = """
        classes:
            Class:
                gauge:
                    type: GAUGE
                signed_numeric:
                    type: NUMERIC
                    neg_vals: true
                string:
                    type: STRING
                    max_size: 83
        info:
            inst_max_size: 132
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NewMaxSize",
        description = "instance max size increased",
        into_schema = """
        info:
            inst_max_size: 100
        """,
        new_schema = """
        info:
            inst_max_size: 132
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NewClass",
        description = "instance max size increased",
        into_schema = """
        info:
            inst_max_size: 100
        """,
        new_schema = """
        info:
            inst_max_size: 132
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
]

# fmt: on
