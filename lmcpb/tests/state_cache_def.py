"""
Testcase definitions for state_cache unit tests
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from lmcrec.playback.cache.state_cache import (
    LmcrecClassCacheEntry,
    LmcrecInstCacheEntry,
)
from lmcrec.playback.codec.decoder import LmcRecord


@dataclass
class LmcrecStateCacheTestCase:
    name: str = ""
    description: str = ""
    # Return values for decoder next_record:
    next_records: List[LmcRecord] = field(default_factory=list)
    # Return values for decoder next_record used to prime the state:
    prime_next_records: Optional[List[LmcRecord]] = None
    # Whether to maintain a previous value or not:
    have_prev: bool = False
    # Expected state:
    expect_class_cache: List[LmcrecClassCacheEntry] = field(default_factory=list)
    expect_inst_cache: List[LmcrecInstCacheEntry] = field(default_factory=list)
    expect_inst_by_class_name: Dict[str, Set[str]] = field(default_factory=dict)
    expect_new_inst: bool = False
    expect_deleted_inst: bool = False
    expect_new_class_def: bool = False
    # Exception condition:
    expect_exception: Optional[Exception] = None
    expect_exception_str: Optional[str] = None
