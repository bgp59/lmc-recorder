"""Utilities for parsing lmcrec config"""

import os
from functools import lru_cache
from typing import Any, Dict, Optional

import yaml

# The following definitions should match the lmcrec/**/*.go ones:
LMCREC_RUNTIME_ENV_VAR = "LMCREC_RUNTIME"
LMCREC_RUNTIME_DEFAULT = "$HOME/runtime/lmcrec"
LMCREC_CONFIG_FILE_ENV_VAR = "LMCREC_CONFIG"
LMCREC_CONFIG_FILE_DEFAULT = "lmcrec-config.yaml"

LMCREC_CONFIG_RECORDER_INST_PLACEHOLDER = "<INST>"

LMCREC_CONFIG_DEFAULT_SECTION = "default"
LMCREC_CONFIG_RECORDERS_SECTION = "recorders"
LMCREC_CONFIG_RECORDERS_INST_KEY = "inst"
LMCREC_CONFIG_RECORDERS_BY_INST_KEY = "recorders_by_inst"


if not os.environ.get(LMCREC_RUNTIME_ENV_VAR):
    os.environ[LMCREC_RUNTIME_ENV_VAR] = os.path.expandvars(LMCREC_RUNTIME_DEFAULT)


def get_lmcrec_runtime():
    return os.environ.get(LMCREC_RUNTIME_ENV_VAR) or os.path.expandvars(
        LMCREC_RUNTIME_DEFAULT
    )


def get_lmcrec_config_file(config_file: Optional[str] = None) -> str:
    return (
        config_file  # typically arg.config
        or os.environ.get(LMCREC_CONFIG_FILE_ENV_VAR)
        or LMCREC_CONFIG_FILE_DEFAULT
    )


@lru_cache
def load_lmcrec_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    with open(get_lmcrec_config_file(config_file)) as f:
        lmcrec_config = yaml.safe_load(f)

    # Add instance config by inst section to avoid sequential lookup multiple
    # times:
    lmcrec_config[LMCREC_CONFIG_RECORDERS_BY_INST_KEY] = {
        inst_config.get(LMCREC_CONFIG_RECORDERS_INST_KEY): inst_config
        for inst_config in lmcrec_config.get(LMCREC_CONFIG_RECORDERS_SECTION, [])
    }
    return lmcrec_config


def lookup_lmcrec_config(
    lmcrec_config: Dict[str, Any],
    inst: Optional[str] = None,
    param: Optional[str] = None,
    expand: bool = False,
) -> Any:
    """Lookup config param in default and recorders section"""
    inst_config = lmcrec_config[LMCREC_CONFIG_RECORDERS_BY_INST_KEY].get(inst)
    val = inst_config.get(param) if inst_config is not None else None
    if val is None:
        default_section = lmcrec_config.get(LMCREC_CONFIG_DEFAULT_SECTION)
        val = default_section.get(param) if default_section is not None else None
    if expand and isinstance(val, str) and isinstance(inst, str):
        val = os.path.expandvars(
            val.replace(LMCREC_CONFIG_RECORDER_INST_PLACEHOLDER, inst)
        )
    return val


def lookup_lmcrec_config_file(
    inst: str,
    config_file: Optional[str] = None,
    param: Optional[str] = None,
    expand: bool = False,
) -> Any:
    return lookup_lmcrec_config(
        load_lmcrec_config(config_file), inst, param, expand=expand
    )


def get_record_files_dir(
    inst: str,
    config_file: Optional[str] = None,
) -> str:
    return lookup_lmcrec_config_file(inst, config_file, "record_files_dir", expand=True)
