import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path = [root_dir] + sys.path

from .args import (
    get_file_selection_arg_parser,
    process_file_selection_args,
)
from .file_selector import build_lmcrec_file_chains, chain_to_file_list
from .lmcrec_query import (
    LmcrecQuery,
    LmcrecQueryResult,
)
from .query_selector import (
    QUERY_FROM_FILE_SUFFIX,
    LmcrecQueryClassResult,
    LmcrecQuerySelector,
    build_query_selectors,
)
from .query_state_cache import LmcrecQueryIntervalStateCache
