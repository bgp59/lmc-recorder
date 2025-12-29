# Prompt: .github/prompts/merge_schema_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
"""Test cases for test_merge_lmcrec_schema"""

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
        description = "Simply load new schema when into_schema is empty",
        new_schema = """
            classes:
                Class1:
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
        name = "IncreasedInstMaxSize",
        description = "Instance max size increased from 100 to 132",
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
        name = "DecreasedInstMaxSize",
        description = "Instance max size decreased should not update",
        into_schema = """
            info:
                inst_max_size: 200
        """,
        new_schema = """
            info:
                inst_max_size: 100
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "SameInstMaxSize",
        description = "Same instance max size should not update",
        into_schema = """
            info:
                inst_max_size: 150
        """,
        new_schema = """
            info:
                inst_max_size: 150
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "NewClass",
        description = "Add a new class to existing schema",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class2:
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        expect_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                Class2:
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NewVariable",
        description = "Add a new variable to existing class",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class1:
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        expect_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "IncreasedVarMaxSize",
        description = "Variable max size increased should update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 100
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "DecreasedVarMaxSize",
        description = "Variable max size decreased should not update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 100
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "SameVarMaxSize",
        description = "Same variable max size should not update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 75
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 75
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "NegValsFalseToTrue",
        description = "neg_vals flag changed from False to True should update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
                        neg_vals: true
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NegValsTrueToFalse",
        description = "neg_vals flag changed from True to False should not update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
                        neg_vals: true
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "NegValsTrueToTrue",
        description = "neg_vals flag stays True should not update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
                        neg_vals: true
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
                        neg_vals: true
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "IncompatibleVarType",
        description = "Variable type change should raise RuntimeError",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
        """,
        expect_exception = RuntimeError,
        expect_exception_str = "inconsistent var type"
    ),
    MergeLmcrecSchemaTestCase(
        name = "UniqueClassesInBothSchemas",
        description = "Classes unique to each schema should appear in merge",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                Class2:
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class3:
                    var3:
                        type: GAUGE
                Class4:
                    var4:
                        type: STRING
                        max_size: 30
            info:
                inst_max_size: 100
        """,
        expect_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                Class2:
                    var2:
                        type: NUMERIC
                Class3:
                    var3:
                        type: GAUGE
                Class4:
                    var4:
                        type: STRING
                        max_size: 30
            info:
                inst_max_size: 100
        """,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "UniqueVariablesInBothSchemas",
        description = "Variables unique to each schema should appear in merge",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
        """,
        new_schema = """
            classes:
                Class1:
                    var3:
                        type: GAUGE
                    var4:
                        type: STRING
                        max_size: 30
        """,
        expect_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
                    var3:
                        type: GAUGE
                    var4:
                        type: STRING
                        max_size: 30
        """,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "ComplexMergeScenario",
        description = "Multiple updates: new class, new variable, increased sizes, neg_vals change",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 80
                    var2:
                        type: NUMERIC
                        neg_vals: true
                    var3:
                        type: GAUGE
                Class2:
                    var4:
                        type: STRING
                        max_size: 60
            info:
                inst_max_size: 150
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NoClassesInNewSchema",
        description = "New schema without classes should only update info if needed",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 100
        """,
        new_schema = """
            info:
                inst_max_size: 150
        """,
        expect_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 150
        """,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "NoClassesInIntoSchema",
        description = "Into schema without classes should add all from new schema",
        into_schema = """
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 100
        """,
        expect_schema = SAME_AS_NEW_SCHEMA,
        expect_updated = True
    ),
    MergeLmcrecSchemaTestCase(
        name = "EmptyNewSchema",
        description = "Empty new schema should not update anything",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
            info:
                inst_max_size: 100
        """,
        new_schema = """
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "IdenticalSchemas",
        description = "Identical schemas should not update",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
                        neg_vals: true
            info:
                inst_max_size: 100
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                        max_size: 50
                    var2:
                        type: NUMERIC
                        neg_vals: true
            info:
                inst_max_size: 100
        """,
        expect_schema = SAME_AS_INTO_SCHEMA,
        expect_updated = False
    ),
    MergeLmcrecSchemaTestCase(
        name = "MultipleIncompatibleTypes",
        description = "Should fail on first incompatible type encountered",
        into_schema = """
            classes:
                Class1:
                    var1:
                        type: STRING
                    var2:
                        type: GAUGE
        """,
        new_schema = """
            classes:
                Class1:
                    var1:
                        type: NUMERIC
                    var2:
                        type: STRING
        """,
        expect_exception = RuntimeError,
        expect_exception_str = "inconsistent var type"
    ),
]

# fmt: on
