"""Utilities for handling LMC Schema"""

from copy import deepcopy
from typing import Any, Dict, Literal, Union

from cache import LmcrecClassVarInfo

"""
lmcrec_schema = {
    "info": {
        "inst_max_size: 100
    },
    "classes": {
        "CLASS_NAME": {
            "VAR_NAME": {
                "type": LMC_TYPE,
                "neg_vals": true, # False is default
                "inst_max_size": N,
            }
        }
    }
}
"""


LMCREC_SCHEMA_INFO_KEY = "info"
LMCREC_SCHEMA_INFO_INST_MAX_SIZE_KEY = "inst_max_size"

LMCREC_SCHEMA_CLASSES_KEY = "classes"
LMCREC_SCHEMA_CLASS_VAR_TYPE_KEY = "type"
LMCREC_SCHEMA_CLASS_VAR_NEG_VALS_KEY = "neg_vals"
LMCREC_SCHEMA_CLASS_VAR_MAX_SIZE_KEY = "max_size"


LmcrecInfoSchema = Dict[str, Any]

LmcrecVarSchema = Dict[str, Any]
LmcrecVarName = str
LmcrecClassSchema = Dict[LmcrecVarName, LmcrecVarSchema]
LmcrecClassName = str
LmcrecClassesSchema = Dict[LmcrecClassName, LmcrecClassSchema]

LmcrecSchema = Dict[
    Union[Literal[LMCREC_SCHEMA_INFO_KEY], Literal[LMCREC_SCHEMA_CLASSES_KEY]],
    Union[LmcrecInfoSchema, LmcrecClassesSchema],
]


def generate_lmcrec_schema(
    class_var_info: LmcrecClassVarInfo,
    inst_max_size: int = 0,
) -> LmcrecSchema:
    """Generate LMC schema"""

    schema = {
        LMCREC_SCHEMA_INFO_KEY: {LMCREC_SCHEMA_INFO_INST_MAX_SIZE_KEY: inst_max_size}
    }

    class_schema_by_name = dict()
    for class_name in sorted(class_var_info, key=lambda c: c.lower()):
        var_info_by_name = class_var_info[class_name]
        class_schema = dict()
        for var_name in sorted(var_info_by_name, key=lambda v: v.lower()):
            var_info = var_info_by_name[var_name]
            var_schema = {LMCREC_SCHEMA_CLASS_VAR_TYPE_KEY: var_info.var_type.name}
            if var_info.neg_vals:
                var_schema[LMCREC_SCHEMA_CLASS_VAR_NEG_VALS_KEY] = True
            if var_info.max_size > 0:
                var_schema[LMCREC_SCHEMA_CLASS_VAR_MAX_SIZE_KEY] = var_info.max_size
            class_schema[var_name] = var_schema
        class_schema_by_name[class_name] = class_schema
    schema[LMCREC_SCHEMA_CLASSES_KEY] = class_schema_by_name
    return schema


def merge_lmcrec_schema(into_schema: LmcrecSchema, new_schema: LmcrecSchema) -> bool:
    """Merge 2 schemas while checking for compatibility

    Args:
        into_schema (LmcrecSchema):
            Destination for the merge
        new_schema (LmcrecSchema):
            The new schema to merge from
    Returns:
        True if there was any update
    """

    updated = False

    if not new_schema:
        return updated

    new_info_schema = new_schema.get(LMCREC_SCHEMA_INFO_KEY)
    if new_info_schema:
        into_info_schema = into_schema.get(LMCREC_SCHEMA_INFO_KEY)
        if into_info_schema is None:
            into_schema[LMCREC_SCHEMA_INFO_KEY] = deepcopy(new_info_schema)
            updated = True
        else:
            new_max_inst_size = new_info_schema.get(
                LMCREC_SCHEMA_INFO_INST_MAX_SIZE_KEY, 0
            )
            if new_max_inst_size > into_info_schema.get(
                LMCREC_SCHEMA_INFO_INST_MAX_SIZE_KEY, 0
            ):
                into_info_schema[LMCREC_SCHEMA_INFO_INST_MAX_SIZE_KEY] = (
                    new_max_inst_size
                )
                updated = True

    # Classes edge case(s):
    new_class_schema_by_name = new_schema.get(LMCREC_SCHEMA_CLASSES_KEY)
    if not new_class_schema_by_name:
        return updated

    into_class_schema_by_name = into_schema.get(LMCREC_SCHEMA_CLASSES_KEY)
    if into_class_schema_by_name is None:
        into_schema[LMCREC_SCHEMA_CLASSES_KEY] = deepcopy(new_class_schema_by_name)
        return True

    # Compare classes:
    for class_name, new_class_schema in new_class_schema_by_name.items():
        # Class edge case(s):
        into_class_schema = into_class_schema_by_name.get(class_name)
        if into_class_schema is None:
            into_class_schema_by_name[class_name] = deepcopy(new_class_schema)
            updated = True
            continue
        # Compare variables:
        for var_name, new_var_schema in new_class_schema.items():
            # Variable edge case(s):
            into_var_schema = into_class_schema.get(var_name)
            if into_var_schema is None:
                into_class_schema[var_name] = deepcopy(new_var_schema)
                updated = True
                continue
            # Compatibility:
            new_var_type = new_var_schema.get(LMCREC_SCHEMA_CLASS_VAR_TYPE_KEY)
            into_var_type = into_var_schema.get(LMCREC_SCHEMA_CLASS_VAR_TYPE_KEY)
            if new_var_type != into_var_type:
                raise RuntimeError(
                    f"inconsistent var type for class: {class_name!r}, var: {var_name!r}: "
                    f"old: {into_var_type!r}, new: {new_var_type!r}"
                )
            if new_var_schema.get(
                LMCREC_SCHEMA_CLASS_VAR_NEG_VALS_KEY, False
            ) and not into_var_schema.get(LMCREC_SCHEMA_CLASS_VAR_NEG_VALS_KEY, False):
                into_var_schema[LMCREC_SCHEMA_CLASS_VAR_NEG_VALS_KEY] = True
                updated = True
            new_max_size = new_var_schema.get(LMCREC_SCHEMA_CLASS_VAR_MAX_SIZE_KEY, 0)
            if new_max_size > into_var_schema.get(
                LMCREC_SCHEMA_CLASS_VAR_MAX_SIZE_KEY, 0
            ):
                into_var_schema[LMCREC_SCHEMA_CLASS_VAR_MAX_SIZE_KEY] = new_max_size
                updated = True

    return updated
