"""lmcrec query object

See https://github.com/bgp59/lmc-recorder/tree/main/docs/QueryDescription.md for query syntax.

"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml
from cache import LmcrecStateCache
from codec import LmcVarType

from .query_state_cache import LmcrecQueryIntervalStateCache

# Query suffix indicating a file name:
QUERY_FROM_FILE_SUFFIX = ".yaml"

# Instance common prefix:
QUERY_INSTANCE_PREFIX = "~"

# Query spec keys:
QUERY_NAME_KEY = "n"
QUERY_INST_KEY = "i"
QUERY_CLASS_KEY = "c"
QUERY_EXCLUDE_TYPE_KEY = "T"
QUERY_INCLUDE_TYPE_KEY = "t"
QUERY_EXCLUDE_VAR_KEY = "V"
QUERY_INCLUDE_VAR_KEY = "v"

# Variable value qualifier separator:
QUERY_VAL_QUAL_SEP = ":"

# Numerical values may be queried for any of the combinations below (ORed
# flags):
QUERY_VARIABLE_VALUE_FLAG = 1 << 0
QUERY_VARIABLE_PREV_VALUE_FLAG = 1 << 1
QUERY_VARIABLE_ADJUSTED_DELTA_FLAG = 1 << 2
QUERY_VARIABLE_UNADJUSTED_DELTA_FLAG = 1 << 3
QUERY_VARIABLE_RATE_FLAG = 1 << 4

QUERY_VARIABLE_NEEDS_DELTA_FLAGS = (
    QUERY_VARIABLE_ADJUSTED_DELTA_FLAG
    | QUERY_VARIABLE_UNADJUSTED_DELTA_FLAG
    | QUERY_VARIABLE_RATE_FLAG
)

QUERY_VARIABLE_NEEDS_PREV_FLAGS = (
    QUERY_VARIABLE_PREV_VALUE_FLAG | QUERY_VARIABLE_NEEDS_DELTA_FLAGS
)

var_val_qual_flag_map = {
    "v": QUERY_VARIABLE_VALUE_FLAG,
    "p": QUERY_VARIABLE_PREV_VALUE_FLAG,
    "d": QUERY_VARIABLE_ADJUSTED_DELTA_FLAG,
    "D": QUERY_VARIABLE_UNADJUSTED_DELTA_FLAG,
    "r": QUERY_VARIABLE_RATE_FLAG,
}

var_val_qual_flag_order = [
    QUERY_VARIABLE_VALUE_FLAG,
    QUERY_VARIABLE_PREV_VALUE_FLAG,
    QUERY_VARIABLE_ADJUSTED_DELTA_FLAG,
    QUERY_VARIABLE_UNADJUSTED_DELTA_FLAG,
    QUERY_VARIABLE_RATE_FLAG,
]

var_val_flag_qual_map = {
    f: q for q, f in var_val_qual_flag_map.items() if f != QUERY_VARIABLE_VALUE_FLAG
}

var_val_delta_adujstment_by_type = {
    LmcVarType.COUNTER: 1 << 32,
    LmcVarType.NUMERIC: 1 << 32,
    LmcVarType.LARGE_NUMERIC: 1 << 64,
}

delta_rate_types = set(
    [
        LmcVarType.COUNTER,
        LmcVarType.NUMERIC,
        LmcVarType.LARGE_NUMERIC,
    ]
)


def parse_var_val_qualifiers(var_quals: str) -> int:
    flags = 0
    for q in var_quals:
        flags |= var_val_qual_flag_map.get(q, 0)
    if flags == 0:
        flags = QUERY_VARIABLE_VALUE_FLAG
    return flags


@dataclass
class LmcrecQueryClassSelector:
    """Per class query selector.

    When a query is resolved, its actual instances may belong to different
    classes. The variable retrieval is based on var ID, which is class specific,
    so it follows that the resolved instances should be grouped by class.

    """

    # How to handle the variables; list of:
    #   (retrieval var_id, ORed QUERY_VARIABLE_...FLAG):
    var_handling_info: List[Tuple[int, int]] = field(default_factory=list)
    # The list of variable names, matching the order from above. Note that there
    # may be more entries for a given variable if value qualifiers are in use:
    # the name + a suffix as per var_name_qual_suffix:
    var_names: List[str] = field(default_factory=list)
    # Instance names:
    inst_names: Set[str] = field(default_factory=set)
    # The timestamp of the last class_info used to update the selector. It will
    # be compared against the class_info.last_update_ts to determine if the
    # current selector is valid or it needs updating:
    last_update_ts: Optional[float] = None


@dataclass
class LmcrecQueryClassResult:
    """Per class query result"""

    # var_names and vals_by_inst[inst_name] below are parallel arrays:
    var_names: List[str] = field(default_factory=list)
    vals_by_inst: Dict[str, List[Any]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert to [inst_name][var_name] = value"""

        to_dict = {}
        for inst_name, vals in self.vals_by_inst.items():
            to_dict[inst_name] = {
                var_name: vals[i] for i, var_name in enumerate(self.var_names)
            }
        return to_dict


class LmcrecQuerySelector:
    """Query Selector Object

    It maintains the following data structure:

    .selector[class_name] = LmcrecQueryClassSelector

    """

    def __init__(self, query: Dict[str, Any]):
        """Create query selector from query"""

        self.name = query.get(QUERY_NAME_KEY)

        self.needs_prev = False

        self._query_full_inst_names = set()
        self._query_prefix_inst_names = []
        self._query_inst_re = []

        inst_names = query.get(QUERY_INST_KEY)
        if isinstance(inst_names, str):
            inst_names = [inst_names]
        if inst_names:
            for inst_name in inst_names:
                if len(inst_name) > 1 and inst_name[0] == "/" and inst_name[-1] == "/":
                    self._query_inst_re.append(re.compile(inst_name[1:-1]))
                elif inst_name.startswith(QUERY_INSTANCE_PREFIX):
                    self._query_prefix_inst_names.append(inst_name[1:])
                else:
                    self._query_full_inst_names.add(inst_name)

        self._query_class_name = query.get(QUERY_CLASS_KEY)

        exclude_types = query.get(QUERY_EXCLUDE_TYPE_KEY, [])
        if isinstance(exclude_types, str):
            exclude_types = [exclude_types]
        self._exclude_types = set(LmcVarType[t.upper()] for t in exclude_types)

        exclude_vars = query.get(QUERY_EXCLUDE_VAR_KEY, [])
        if isinstance(exclude_vars, str):
            exclude_vars = [exclude_vars]
        self._exclude_vars = set(exclude_vars)

        self._include_types = dict()
        include_types = query.get(QUERY_INCLUDE_TYPE_KEY, [])
        if isinstance(include_types, str):
            include_types = [include_types]
        for t in include_types:
            i = t.rfind(QUERY_VAL_QUAL_SEP)
            if i > 0:
                qual_flags = parse_var_val_qualifiers(t[i + 1 :])
                t = t[:i]
                if qual_flags & QUERY_VARIABLE_NEEDS_PREV_FLAGS:
                    self.needs_prev = True
            else:
                qual_flags = QUERY_VARIABLE_VALUE_FLAG
            self._include_types[LmcVarType[t.upper()]] = qual_flags

        self._include_vars = dict()
        include_vars = query.get(QUERY_INCLUDE_VAR_KEY, [])
        if isinstance(include_vars, str):
            include_vars = [include_vars]
        for v in include_vars:
            i = v.rfind(QUERY_VAL_QUAL_SEP)
            if i > 0:
                qual_flags = parse_var_val_qualifiers(v[i + 1 :])
                v = v[:i]
                if qual_flags & QUERY_VARIABLE_NEEDS_PREV_FLAGS:
                    self.needs_prev = True
            else:
                qual_flags = QUERY_VARIABLE_VALUE_FLAG
            self._include_vars[v] = qual_flags

        self._reset()

    def _reset(self):
        """Invoked when the query state cache indicates a new chain"""

        self._classified_inst_names: Dict[str, str] = dict()
        self.selector: Dict[str, LmcrecQueryClassSelector] = dict()
        self._result = None

    def _selector_new_inst_class_update(self, state_cache: LmcrecStateCache):
        """Handle state cache new instance and/or class info update"""

        selector = self.selector
        want_class_name = self._query_class_name
        class_by_id = state_cache.class_by_id

        # Resolve the instance and class lists:
        for inst_name, inst in state_cache.inst_by_name.items():
            # Already classified?
            if inst_name in self._classified_inst_names:
                continue

            # Class selection?
            class_name = class_by_id[inst.class_id].name
            if want_class_name and class_name != want_class_name:
                continue

            # Instance selection?
            keep = (
                not self._query_full_inst_names
                and not self._query_prefix_inst_names
                and not self._query_inst_re
            )

            # Try by name if no match yet:
            if not keep and self._query_full_inst_names:
                keep = inst_name in self._query_full_inst_names

            # Try by prefix if no match yet:
            if not keep and self._query_prefix_inst_names:
                for suffix in self._query_prefix_inst_names:
                    if inst_name.endswith(suffix):
                        keep = True
                        break

            # Try by pattern if no match yet:
            if not keep and self._query_inst_re:
                for pat in self._query_inst_re:
                    if pat.match(inst_name):
                        keep = True
                        break

            if not keep:
                continue

            self._classified_inst_names[inst_name] = class_name
            if class_name not in selector:
                selector[class_name] = LmcrecQueryClassSelector()
            selector[class_name].inst_names.add(inst_name)

        class_by_name = state_cache.class_by_name
        for class_name, class_selector in selector.items():
            class_info = class_by_name[class_name]
            # Check if the current selector is up-to-date:
            if class_info.last_update_ts == class_selector.last_update_ts:
                continue

            # Needs updating:
            class_selector.var_handling_info = []
            selector_var_names = []
            var_info_by_name = class_info.var_info_by_name
            for var_name in sorted(var_info_by_name, key=lambda v: v.lower()):
                var_info = var_info_by_name[var_name]
                var_id, var_type = var_info.var_id, var_info.var_type
                if var_name in self._exclude_vars:
                    continue
                if var_name in self._include_vars:
                    class_selector.var_handling_info.append(
                        (var_id, self._include_vars[var_name])
                    )
                    selector_var_names.append(var_name)
                    continue
                if var_type in self._exclude_types:
                    continue
                if var_type in self._include_types:
                    class_selector.var_handling_info.append(
                        (var_id, self._include_types[var_type])
                    )
                    selector_var_names.append(var_name)
                    continue
                if not self._include_vars and not self._include_types:
                    class_selector.var_handling_info.append(
                        (var_id, QUERY_VARIABLE_VALUE_FLAG)
                    )
                    selector_var_names.append(var_name)
            class_selector.var_names = []
            for i, (_, var_quals) in enumerate(class_selector.var_handling_info):
                var_name = selector_var_names[i]
                for qual_flag in var_val_qual_flag_order:
                    if var_quals & qual_flag:
                        v_name = var_name
                        qual_suffix = var_val_flag_qual_map.get(qual_flag)
                        if qual_suffix:
                            v_name += f"{QUERY_VAL_QUAL_SEP}{qual_suffix}"
                        class_selector.var_names.append(v_name)
            class_selector.last_update_ts = class_info.last_update_ts

    def _selector_verify_del_inst_update(self, state_cache: LmcrecStateCache):
        """Handle state cache deleted instance update"""

        to_delete = [
            inst_name
            for inst_name in self._classified_inst_names
            if inst_name not in state_cache.inst_by_name
        ]
        for inst_name in to_delete:
            class_name = self._classified_inst_names[inst_name]
            del self._classified_inst_names[inst_name]
            self.selector[class_name].inst_names.discard(inst_name)

    def selector_update(self, query_state_cache: LmcrecQueryIntervalStateCache) -> bool:
        updated = False
        if query_state_cache.new_chain:
            self._reset()
            self._selector_new_inst_class_update(query_state_cache)
            updated = True
        else:
            if query_state_cache.new_inst or query_state_cache.new_class_def:
                self._selector_new_inst_class_update(query_state_cache)
                updated = True
            if query_state_cache.deleted_inst:
                self._selector_verify_del_inst_update(query_state_cache)
                updated = True
        return updated

    def run(
        self, query_state_cache: LmcrecQueryIntervalStateCache
    ) -> Dict[str, LmcrecQueryClassResult]:
        """Run query selector and return the result"""

        updated = self.selector_update(query_state_cache)
        if updated or self._result is None:
            # Cannot reuse the cached result for storage, re-initialize it:
            self._result = dict()
        ts, prev_ts = query_state_cache.ts, query_state_cache.prev_ts
        d_time = ts - prev_ts if prev_ts is not None else None
        result = self._result
        inst_by_name = query_state_cache.inst_by_name
        for class_name, class_selector in self.selector.items():
            if class_name not in result:
                result[class_name] = LmcrecQueryClassResult(
                    var_names=class_selector.var_names, vals_by_inst=dict()
                )
            vals_by_inst = result[class_name].vals_by_inst
            var_info_by_id = query_state_cache.class_by_name[class_name].var_info_by_id
            for inst_name in class_selector.inst_names:
                inst = inst_by_name[inst_name]
                vars, prev_vars = inst.vars, inst.prev_vars
                if inst_name not in vals_by_inst:
                    vals_by_inst[inst_name] = [None] * len(class_selector.var_names)
                var_vals = vals_by_inst[inst_name]
                val_i = 0
                for var_id, var_quals in class_selector.var_handling_info:
                    val = vars.get(var_id)
                    var_info = var_info_by_id.get(var_id)
                    var_type = var_info.var_type if var_info is not None else None
                    d_val, d_val_adj = None, None
                    if var_quals & QUERY_VARIABLE_NEEDS_PREV_FLAGS:
                        prev_val = (
                            prev_vars.get(var_id) if prev_vars is not None else None
                        )
                    if (
                        var_quals & QUERY_VARIABLE_NEEDS_DELTA_FLAGS
                        and var_type in delta_rate_types
                        and val is not None
                        and prev_val is not None
                    ):
                        d_val = val - prev_val
                        if d_val < 0:
                            d_val_adj = d_val + var_val_delta_adujstment_by_type.get(
                                var_type, 0
                            )
                        else:
                            d_val_adj = d_val
                    for qual_flag in var_val_qual_flag_order:
                        if not var_quals & qual_flag:
                            continue
                        if qual_flag == QUERY_VARIABLE_VALUE_FLAG:
                            var_vals[val_i] = val
                        elif qual_flag == QUERY_VARIABLE_PREV_VALUE_FLAG:
                            var_vals[val_i] = prev_val
                        elif qual_flag == QUERY_VARIABLE_ADJUSTED_DELTA_FLAG:
                            var_vals[val_i] = d_val_adj
                        elif qual_flag == QUERY_VARIABLE_UNADJUSTED_DELTA_FLAG:
                            var_vals[val_i] = d_val
                        elif qual_flag == QUERY_VARIABLE_RATE_FLAG:
                            if d_val_adj is not None and d_time is not None:
                                var_vals[val_i] = d_val_adj / d_time
                            else:
                                var_vals[val_i] = None
                        val_i += 1

        return result


def build_query_selectors(*query_or_file: str) -> List[LmcrecQuerySelector]:
    """Build list of query selectors from string or file

    Args:
        query_or_file (str):
            A string or file name with the query/queries, each query or file may
            be in fact a list of queries. A file name should end w/ .yaml

    Returns:
        List[LmcrecQuerySelector]
            The list of query selectors (there may be just one).
    """

    query_selectors = []
    for q_or_f in query_or_file:
        if q_or_f.endswith(QUERY_FROM_FILE_SUFFIX):
            with open(q_or_f) as f:
                query_or_queries = yaml.safe_load(f)
        else:
            query_or_queries = yaml.safe_load(q_or_f)

        if not isinstance(query_or_queries, list):
            query_list = [query_or_queries]
        else:
            query_list = query_or_queries

        for query in query_list:
            query_selectors.append(LmcrecQuerySelector(query))
    return query_selectors
