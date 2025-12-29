import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path = [root_dir] + sys.path

from .config import (
    LMCREC_CONFIG_FILE_DEFAULT,
    LMCREC_CONFIG_FILE_ENV_VAR,
    LMCREC_CONFIG_RECORDER_INST_PLACEHOLDER,
    LMCREC_CONFIG_RECORDERS_BY_INST_KEY,
    LMCREC_RUNTIME_DEFAULT,
    LMCREC_RUNTIME_ENV_VAR,
    get_lmcrec_config_file,
    get_lmcrec_runtime,
    get_record_files_dir,
    load_lmcrec_config,
    lookup_lmcrec_config,
    lookup_lmcrec_config_file,
)
