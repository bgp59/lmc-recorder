import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path = [root_dir] + sys.path

from .decoder import (
    GZIP_FILE_SUFFIX,
    INDEX_FILE_SUFFIX,
    INFO_FILE_SUFFIX,
    LMCREC_FILE_SUFFIX,
    LmcrecDecoder,
    LmcrecFileDecoder,
    LmcRecord,
    LmcrecType,
    LmcVarType,
)
from .index_decoder import (
    LmcrecIndexDecoder,
    LmcrecIndexFileDecoder,
    locate_checkpoint,
)
from .info_decoder import (
    LmcrecInfo,
    LmcrecInfoState,
    decode_lmcrec_info,
    decode_lmcrec_info_from_file,
)
