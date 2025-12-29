"""Common definitions for testcase and unittest files"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class BuildLmcrecFileChainsTestCase:
    name: Optional[str] = None
    description: Optional[str] = None
    record_files_dir: str = ""
    from_ts: Optional[str] = None  # ISO 8601
    to_ts: Optional[str] = None  # ISO 8601
    abspath_ret_vals: Optional[Dict[str, str]] = None
    listdir_ret_vals: Optional[Dict[str, List[str]]] = None
    isdir_list: Optional[List[str]] = None
    decode_lmcrec_info_from_file_ret_vals: Optional[
        Dict[
            str,  # info file_name
            Tuple[
                str,  # prev_file_name
                str,  # start_ts, ISO 8601
                str,  # most_recent_ts, ISO 8601
            ],
        ]
    ] = None
    expect_file_chains: Optional[List[List[str]]] = None
    expect_exception: Optional[Exception] = None
    expect_exception_str: Optional[str] = None
