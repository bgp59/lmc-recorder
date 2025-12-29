"""Common definitions for testcase and unittest files"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from lmcrec.playback.cache.state_cache import (
    LmcrecClassCacheEntry,
    LmcrecInstCacheEntry,
    LmcrecVarInfo,
)
from lmcrec.playback.codec.decoder import LmcVarType
from lmcrec.playback.query.query_selector import (
    LmcrecQueryClassResult,
    LmcrecQueryClassSelector,
)
from lmcrec.playback.query.query_state_cache import LmcrecQueryIntervalStateCache

q_v = 1 << 0
q_p = 1 << 1
q_d = 1 << 2
q_D = 1 << 3
q_r = 1 << 4


@dataclass
class LmcrecQuerySelectorInitTestCase:
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    expect_needs_prev: bool = False
    expect_query_full_inst_names: List[str] = field(default_factory=list)
    expect_query_prefix_inst_names: List[str] = field(default_factory=list)
    expect_query_inst_re: List[str] = field(default_factory=list)
    expect_query_class_name: Optional[str] = None
    expect_query_include_types: Dict[str, int] = field(default_factory=dict)
    expect_query_exclude_types: Set[str] = field(default_factory=set)
    expect_query_include_vars: Dict[str, int] = field(default_factory=dict)
    expect_query_exclude_vars: Set[str] = field(default_factory=set)


@dataclass
class LmcrecQueryIntervalStateCacheBuilder:
    #   instances: [
    #       (inst_name, class_name),
    #       (inst_name, class_name, {
    #           var: val,
    #           var: (val, prev_val),
    #       }),
    #   ]
    instances: List[Union[Tuple[str, str], Tuple[str, str, Dict[str, Any]]]] = field(
        default_factory=list
    )

    #   classes: {
    #       class_name: (
    #           last_update_ts,
    #           [
    #               (var_name, var_type),
    #               (var_name, var_type),
    #           ]
    #       )
    #   }
    classes: Dict[str, Tuple[float, List[Tuple[str, LmcVarType]]]] = field(
        default_factory=dict
    )

    # Time delta, for rates:
    d_time: Optional[float] = None

    # State cache attributes:
    ts: float = 0
    new_chain: bool = False
    new_inst: bool = False
    deleted_inst: bool = False
    new_class_def: bool = False

    def __call__(self, is_primer: bool = False) -> LmcrecQueryIntervalStateCache:
        query_state_cache = LmcrecQueryIntervalStateCache(_no_chain_list=True)

        class_id = 1
        for class_name, (last_update_ts, class_vars) in self.classes.items():
            class_entry = LmcrecClassCacheEntry(
                name=class_name,
                class_id=class_id,
                last_update_ts=last_update_ts,
            )
            for var_id, (var_name, var_type) in enumerate(class_vars):
                var_info = LmcrecVarInfo(
                    name=var_name,
                    var_id=var_id,
                    var_type=var_type,
                )
                class_entry.var_info_by_id[var_id] = var_info
                class_entry.var_info_by_name[var_name] = var_info
            query_state_cache.class_by_name[class_name] = class_entry
            query_state_cache.class_by_id[class_id] = class_entry
            class_id += 1

        inst_id = 1
        for inst_info in self.instances:
            inst_name, class_name = inst_info[0:2]
            class_entry = query_state_cache.class_by_name.get(class_name)
            if class_entry is None:
                class_entry = LmcrecClassCacheEntry(
                    name=class_name,
                    class_id=class_id,
                    last_update_ts=self.ts,
                )
                query_state_cache.class_by_name[class_name] = class_entry
                query_state_cache.class_by_id[class_id] = class_entry
                class_id += 1

            vars, prev_vars = dict(), None
            if len(inst_info) > 2:
                var_values = inst_info[2]
                var_info_by_name = class_entry.var_info_by_name
                var_info_by_id = class_entry.var_info_by_id
                for var_name, val in var_values.items():
                    if isinstance(val, tuple):
                        val, prev_val = val
                    else:
                        prev_val = None
                    var_info = var_info_by_name.get(var_name)
                    if var_info is None:
                        var_id = len(var_info_by_id)
                        var_info = LmcrecVarInfo(
                            name=var_name,
                            var_id=var_id,
                            var_type=(
                                LmcVarType.NUMERIC
                                if isinstance(val, int)
                                else (
                                    LmcVarType.BOOLEAN
                                    if isinstance(val, bool)
                                    else LmcVarType.STRING
                                )
                            ),
                        )
                        var_info_by_id[var_id] = var_info
                        var_info_by_name[var_name] = var_info
                    var_id = var_info.var_id
                    vars[var_id] = val
                    if prev_val is not None:
                        if prev_vars is None:
                            prev_vars = dict()
                        prev_vars[var_id] = prev_val

            inst_entry = LmcrecInstCacheEntry(
                name=inst_name,
                inst_id=inst_id,
                class_id=query_state_cache.class_by_name[class_name].class_id,
                vars=vars,
                prev_vars=prev_vars,
            )
            query_state_cache.inst_by_name[inst_name] = inst_entry
            query_state_cache.inst_by_id[inst_id] = inst_entry
            inst_id += 1

        query_state_cache.ts = self.ts
        query_state_cache.prev_ts = (
            query_state_cache.ts - self.d_time if self.d_time is not None else None
        )
        if is_primer:
            query_state_cache.new_chain = True
        else:
            query_state_cache.new_chain = self.new_chain
            query_state_cache.new_inst = self.new_inst
            query_state_cache.deleted_inst = self.deleted_inst
            query_state_cache.new_class_def = self.new_class_def
        return query_state_cache


@dataclass
class LmcrecQuerySelectorUpdateTestCase:
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    query_state_cache: Optional[LmcrecQueryIntervalStateCacheBuilder] = None
    selector_primer: Optional[LmcrecQueryIntervalStateCacheBuilder] = None
    expect_selector: Optional[Dict[str, LmcrecQueryClassSelector]] = None
    expect_exception: Optional[Exception] = None
    expect_exception_str: Optional[str] = None


@dataclass
class LmcrecQuerySelectorRunTestCase:
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    query_state_cache: Optional[LmcrecQueryIntervalStateCacheBuilder] = None
    expect_result: Dict[str, LmcrecQueryClassResult] = field(default_factory=dict)
