"""
LMC Playback State Cache

Given a LMC record file, the state cache class provides a method for reading a
scan and updating the cache representing the entire state.

"""

import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from codec import (
    LmcrecDecoder,
    LmcrecFileDecoder,
    LmcRecord,
    LmcrecType,
    LmcVarType,
)


class LmcrecScanRetCode(IntEnum):
    COMPLETE = 1
    ATEOR = 2
    ATEOF = 3
    CLOSED = 4
    PARTIAL = 5


InstTreeKey = Tuple[str, str]  # (name, class)
InstTree = Dict[Optional[InstTreeKey], Set[InstTreeKey]]
LmcrecClassVarInfo = Dict[
    str, Dict[str, "LmcrecVarInfo"]
]  # [class][var_name] -> var_info


@dataclass
class LmcrecVarInfo:
    name: Optional[str] = None
    var_id: Optional[int] = None
    var_type: Optional[LmcVarType] = None
    # Integer LMC variable types do not provide information whether they are
    # signed or unsigned, this has to be discovered based on their values.
    neg_vals: bool = False

    # Max size for string values:
    max_size: int = 0


@dataclass
class LmcrecClassCacheEntry:
    name: Optional[str] = None
    class_id: Optional[int] = None
    var_info_by_id: Dict[int, LmcrecVarInfo] = field(default_factory=dict)
    var_info_by_name: Dict[str, LmcrecVarInfo] = field(default_factory=dict)
    # The timestamp when this was last updated; query may use this to determine
    # if the var ID mapping has to be re-evaluated or not:
    last_update_ts: Optional[float] = None


@dataclass
class LmcrecInstCacheEntry:
    name: Optional[str] = None
    inst_id: Optional[int] = None
    class_id: Optional[int] = None
    parent_inst_id: Optional[int] = None
    vars: Dict[int, Union[int, bool, str]] = field(default_factory=dict)
    prev_vars: Optional[Dict[int, Union[int, bool, str]]] = None


class LmcrecStateCache:
    def __init__(self, decoder: LmcrecDecoder, have_prev: bool = False):
        """Create LMC state cache using decoder. Optionally provide previous
        variable values map too.
        """

        self._decoder = decoder
        self._have_prev = have_prev
        self.apply_next_scan = self._apply_next_scan
        self.reset()

    def reset(self):
        self.ts = None
        self.prev_ts = None
        self.duration = None
        self.scan_tally = None
        self.num_scans = 0
        self.new_inst = None
        self.deleted_inst = None
        self.new_class_def = None

        # Note: the values in ..._by_nme and ..._by_id below are references to
        # the *same* object.
        self.class_by_name: Dict[str, LmcrecClassCacheEntry] = dict()
        self.class_by_id: Dict[int, LmcrecClassCacheEntry] = dict()
        self.inst_by_name: Dict[str, LmcrecInstCacheEntry] = dict()
        self.inst_by_id: Dict[int, LmcrecInstCacheEntry] = dict()

        # Instance max size:
        self.inst_max_size = 0

        # A common query is for some of the variables in all instances of a
        # given class; keep track of instance names on a per class basis:
        self.inst_by_class_name: Dict[str, Set[str]] = defaultdict(set)

        # Set by the most recent ClassInfo:
        self._curr_class = None

        # Set by the most recent InstInfo or SetInsId:
        self._curr_inst = None

    def set_decoder(self, decoder: LmcrecDecoder):
        self._decoder = decoder

    def _apply_next_scan(self) -> LmcrecScanRetCode:
        if self._decoder is None:
            return LmcrecScanRetCode.CLOSED
        try:
            record = self._decoder.next_record()
        except EOFError:
            self._decoder = None
            return LmcrecScanRetCode.ATEOF
        if record.record_type == LmcrecType.EOR:
            self._decoder = None
            return LmcrecScanRetCode.ATEOR

        if record.record_type != LmcrecType.TIMESTAMP_USEC:
            raise RuntimeError(
                f"want: {LmcrecType.TIMESTAMP_USEC!r}, got: {record.record_type!r}"
            )
        if self._have_prev:
            self.prev_ts = self.ts
        self.ts = record.value
        self.new_inst = False
        self.deleted_inst = False
        self.new_class_def = False

        if self._have_prev:
            for inst in self.inst_by_id.values():
                if inst.prev_vars is None:
                    inst.prev_vars = dict()
                inst.prev_vars.update(inst.vars)

        while True:
            try:
                record = self._decoder.next_record(record)
            except EOFError:
                self._decoder = None
                return LmcrecScanRetCode.PARTIAL

            record_type = record.record_type
            # For performance reasons, test record type in decreasing order of
            # expected frequency:
            if record_type == LmcrecType.VAR_VALUE:
                value = record.value
                self._curr_inst.vars[record.var_id] = value
                var_info = self._curr_class.var_info_by_id[record.var_id]
                if (
                    record.file_record_type == LmcrecType.VAR_SINT_VAL
                    or isinstance(value, (int, float))
                    and value < 0
                ):
                    var_info.neg_vals = True
                elif isinstance(record.value, str):
                    var_info.max_size = max(var_info.max_size, len(record.value))
            elif record_type == LmcrecType.SET_INST_ID:
                self._curr_inst = self.inst_by_id[record.inst_id]
                self._curr_class = self.class_by_id[self._curr_inst.class_id]
            elif record_type == LmcrecType.DELETE_INST_ID:
                inst_id = record.inst_id
                inst = self.inst_by_id.get(inst_id)
                if inst is not None:
                    if self._curr_inst is inst:
                        self._curr_inst = None
                    self.inst_by_class_name[
                        self.class_by_id[inst.class_id].name
                    ].discard(inst.name)
                    del self.inst_by_name[inst.name]
                    del self.inst_by_id[inst_id]
                    self.deleted_inst = True
            elif record_type == LmcrecType.INST_INFO:
                inst = self.inst_by_id.get(record.inst_id)
                if inst is None:
                    # Sanity check: instance definition unchanged:
                    inst_by_name = self.inst_by_name.get(record.name)
                    if inst_by_name is not None:
                        raise RuntimeError(
                            f"definition change for inst {record.name!r}:\n"
                            f"  was: inst_id={inst_by_name.inst_id}, class ID: {inst_by_name.class_id}, parent inst ID: {inst_by_name.parent_inst_id}"
                            f"   is: inst_id={record.inst_id}, class ID: {record.class_id}, parent inst ID: {record.parent_inst_id}"
                        )

                    inst = LmcrecInstCacheEntry(
                        name=record.name,
                        inst_id=record.inst_id,
                        class_id=record.class_id,
                        parent_inst_id=record.parent_inst_id,
                    )
                    self.inst_by_id[inst.inst_id] = inst
                    self.inst_by_name[inst.name] = inst
                    self.inst_by_class_name[self.class_by_id[record.class_id].name].add(
                        inst.name
                    )
                    self.inst_max_size = max(self.inst_max_size, len(inst.name))
                    self.new_inst = True
                else:
                    # Sanity check: instance definition unchanged:
                    if (
                        inst.name != record.name
                        or inst.class_id != record.class_id
                        or inst.parent_inst_id != record.parent_inst_id
                    ):
                        raise RuntimeError(
                            f"definition change for inst ID {record.inst_id}\n"
                            f"  was: name={inst.name!r}, class ID: {inst.class_id}, parent inst ID: {inst.parent_inst_id}"
                            f"   is: name={record.name!r}, class ID: {record.class_id}, parent inst ID: {record.parent_inst_id}"
                        )
                self._curr_inst = inst
                self._curr_class = self.class_by_id[self._curr_inst.class_id]
            elif record_type == LmcrecType.VAR_INFO:
                class_info = self.class_by_id[record.class_id]
                var_info = class_info.var_info_by_id.get(record.var_id)
                if var_info is None:
                    # Sanity check: var definition unchanged:
                    var_info_by_name = class_info.var_info_by_name.get(record.name)
                    if var_info_by_name is not None:
                        raise RuntimeError(
                            f"var definition change for var {record.name!r} of class {class_info.name!r}, class ID {class_info.class_id}:\n"
                            f"  was: var_id={var_info_by_name.var_id}, type={var_info_by_name.var_type!r}\n"
                            f"   is: var_id={record.var_id}, type={record.lmc_var_type!r}"
                        )
                    var_info = LmcrecVarInfo(
                        record.name, record.var_id, record.lmc_var_type
                    )
                    class_info.var_info_by_id[var_info.var_id] = var_info
                    class_info.var_info_by_name[var_info.name] = var_info
                    class_info.last_update_ts = self.ts
                    self.new_class_def = True
                else:
                    # Sanity check: var definition unchanged:
                    if (
                        var_info.name != record.name
                        or var_info.var_type != record.lmc_var_type
                    ):
                        raise RuntimeError(
                            f"var definition change for var ID {var_info.var_id} of class {class_info.name!r}, class ID {class_info.class_id}:\n"
                            f"  was: name={var_info.name!r}, type={var_info.var_type!r}\n"
                            f"   is: name={record.name!r}, type={record.lmc_var_type!r}"
                        )
            elif record_type == LmcrecType.CLASS_INFO:
                class_info = self.class_by_id.get(record.class_id)
                if class_info is None:
                    # Sanity check: class definition unchanged:
                    class_info_by_name = self.class_by_name.get(record.name)
                    if class_info_by_name is not None:
                        raise RuntimeError(
                            f"class definition changed for class {record.name!r}:\n"
                            f"  was: class_id={class_info_by_name.class_id}\n"
                            f"   is: class_id={record.class_id}"
                        )
                    self._curr_class = LmcrecClassCacheEntry(
                        name=record.name,
                        class_id=record.class_id,
                        last_update_ts=self.ts,
                    )
                    self.class_by_name[record.name] = self._curr_class
                    self.class_by_id[record.class_id] = self._curr_class
                    self.new_class_def = True
                else:
                    # Sanity check: class definition unchanged:
                    if class_info.name != record.name:
                        raise RuntimeError(
                            f"class definition changed for class ID {record.class_id}:\n"
                            f"  was: name={class_info.name!r}\n"
                            f"   is: name={record.name!r}"
                        )
                    self._curr_class = class_info
            elif record_type == LmcrecType.SCAN_TALLY:
                # Make a copy in case the record is re-used:
                scan_tally = self.scan_tally
                if scan_tally is None:
                    scan_tally = LmcRecord(record_type=record_type)
                    self.scan_tally = scan_tally
                scan_tally.scan_in_byte_count = record.scan_in_byte_count
                scan_tally.scan_in_inst_count = record.scan_in_inst_count
                scan_tally.scan_in_var_count = record.scan_in_var_count
                scan_tally.scan_out_var_count = record.scan_out_var_count
            elif record_type == LmcrecType.DURATION_USEC:
                self.duration = record.value
                self.num_scans += 1
                return LmcrecScanRetCode.COMPLETE
            elif record_type == LmcrecType.EOR:
                self._decoder = None
                return LmcrecScanRetCode.PARTIAL

    def get_inst_var(self, inst_name: str, var_name: str) -> Any:
        """Retrieve value for instance variable"""

        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return None
        class_info = self.class_by_id.get(inst.class_id)
        if class_info is None:
            return None
        var_info = class_info.var_info_by_name.get(var_name)
        if var_info is None:
            return None
        return inst.vars.get(var_info.var_id)

    def get_inst_vars(self, inst_name: str, *var_name: str) -> Dict[str, Any]:
        """Retrieve values by name for instance variables"""

        vals_by_name = dict()
        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return vals_by_name
        class_info = self.class_by_id.get(inst.class_id)
        if class_info is None:
            return vals_by_name
        var_info_by_name = class_info.var_info_by_name
        vars = inst.vars
        for vn in var_name or var_info_by_name.keys():
            var_info = var_info_by_name.get(vn)
            if var_info is not None:
                val = vars.get(var_info.var_id)
                if val is not None:
                    vals_by_name[vn] = val
        return vals_by_name

    def get_inst_curr_prev_var(self, inst_name: str, var_name: str) -> Tuple[Any, Any]:
        """Retrieve current, previous values for instance variable"""

        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return None, None
        class_info = self.class_by_id.get(inst.class_id)
        if class_info is None:
            return None, None
        var_info = class_info.var_info_by_name.get(var_name)
        if var_info is None:
            return None, None
        var_id = var_info.var_id
        return (
            inst.vars.get(var_id),
            inst.prev_vars.get(var_id) if inst.prev_vars is not None else None,
        )

    def get_inst_curr_prev_vars(
        self, inst_name: str, *var_name: str
    ) -> Dict[str, Tuple[Any, Any]]:
        """Retrieve current, previous values by name for instance variables"""

        vals_by_name = dict()
        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return vals_by_name
        class_info = self.class_by_id.get(inst.class_id)
        if class_info is None:
            return vals_by_name
        var_info_by_name = class_info.var_info_by_name
        vars, prev_vars = inst.vars, inst.prev_vars
        for vn in var_name or var_info_by_name.keys():
            var_info = var_info_by_name.get(vn)
            if var_info is not None:
                var_id = var_info.var_id
                val = vars.get(var_id)
                prev_val = prev_vars.get(var_id) if prev_vars is not None else None
                if val is not None or prev_val is not None:
                    vals_by_name[vn] = (val, prev_val)
        return vals_by_name

    def get_inst_class_name(self, inst_name: str) -> Optional[str]:
        """Retrieve class name for instance"""
        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return None
        class_info = self.class_by_id.get(inst.class_id)
        return class_info.name if class_info is not None else None

    def get_inst_var_types(self, inst_name: str) -> Dict[str, LmcVarType]:
        """Retrieve LMC type for instance variables"""

        type_by_name = dict()
        inst = self.inst_by_name.get(inst_name)
        if inst is None:
            return type_by_name
        class_info = self.class_by_id.get(inst.class_id)
        if class_info is None:
            return type_by_name
        for var_name, var_info in class_info.var_info_by_name.items():
            type_by_name[var_name] = var_info.var_type
        return type_by_name

    def get_class_var_types(self, class_name: str) -> Dict[str, LmcVarType]:
        """Retrieve LMC type for class variables"""

        type_by_name = dict()
        class_info = self.class_by_name.get(class_name)
        if class_info is None:
            return type_by_name
        for var_name, var_info in class_info.var_info_by_name.items():
            type_by_name[var_name] = var_info.var_type
        return type_by_name

    def get_class_inst_names(self, class_name: str) -> Set[str]:
        """Retrieve all instance names for a given class"""

        return self.inst_by_class_name.get(class_name, set())


def get_inventory(
    state_cache: LmcrecStateCache,
    inst_tree: Optional[InstTree] = None,
    class_var_info: Optional[LmcrecClassVarInfo] = None,
) -> Tuple[
    InstTree, LmcrecClassVarInfo, Optional[float], Optional[float], LmcrecScanRetCode
]:
    """Run inventory on lmcrec file.

    Args:
        state_cache(LmcrecStateCache)
            The state cache

        inst_tree (InstTree):
            Update already existent tree, useful when collecting the inventory
            from multiple files.

        class_var_info (LmcrecClassVarInfo):
            Update already existent info, useful when collecting the inventory
            from multiple files.

    Returns:
        The (updated) inst_tree,  class_var_info, the first_ts and
        last_ts (timestamps) and the the last scan ret_code

    Raises:
        AssertionError if the type of variable has changed from the previous one
        in class_var_info
    """

    if inst_tree is None:
        inst_tree = dict()
    if class_var_info is None:
        class_var_info = dict()
    ret_code = None

    first_ts, last_ts = None, None

    while True:
        ret_code = state_cache.apply_next_scan()
        if ret_code != LmcrecScanRetCode.COMPLETE:
            break
        if first_ts is None:
            first_ts = state_cache.ts
        if not state_cache.new_inst:
            continue
        for inst_name, inst in state_cache.inst_by_name.items():
            inst_parent = state_cache.inst_by_id.get(inst.parent_inst_id)
            if inst_parent is None:
                parent_key = None
            else:
                parent_class_name = state_cache.class_by_id[inst_parent.class_id].name
                parent_key = (inst_parent.name, parent_class_name)
            class_name = state_cache.class_by_id[inst.class_id].name
            if parent_key not in inst_tree:
                inst_tree[parent_key] = set()
            inst_tree[parent_key].add((inst_name, class_name))

    last_ts = state_cache.ts

    for class_name, class_info in state_cache.class_by_name.items():
        if class_name not in class_var_info:
            class_var_info[class_name] = dict()
        for var_name, var_info in class_info.var_info_by_name.items():
            if var_name not in class_var_info[class_name]:
                class_var_info[class_name][var_name] = var_info
            else:
                # Verify var type consistency:
                curr_var_info = class_var_info[class_name][var_name]
                assert curr_var_info.var_type == var_info.var_type, (
                    f"class: {class_name!r}, var: {var_name!r}: "
                    f"inconsistent type, prev: {curr_var_info!r}, curr: {var_info.var_type!r}"
                )
                if var_info.neg_vals:
                    curr_var_info.neg_vals = True
                if var_info.max_size > curr_var_info.max_size:
                    curr_var_info.max_size = var_info.max_size

    return inst_tree, class_var_info, first_ts, last_ts, ret_code


def get_inventory_from_files(
    lmcrec_file_or_files: Union[str, List[str]],
    inst_tree: Optional[InstTree] = None,
    class_var_info: Optional[LmcrecClassVarInfo] = None,
    verbose: bool = False,
) -> Tuple[InstTree, LmcrecClassVarInfo, int, float, float]:
    """Run inventory on lmcrec files.

    Args:
        lmcrec_file_or_files (list):
            The (list of) lmcrec file(s).

        inst_tree (InstTree):
            Update already existent tree, useful when collecting the inventory
            from multiple runs.

        class_var_info (LmcrecClassVarInfo):
            Update already existent info, useful when collecting the inventory
            from multiple runes.

        verbose (bool):
            If True print progress info to stderr.

    Returns:
        The (updated) inst_tree,  class_var_info, inst_max_size,
        and first and last timestamps (time window, that is)

    Raises:
        AssertionError if the type of variable has changed from the previous one
        in class_var_info
    """

    if inst_tree is None:
        inst_tree = dict()
    if class_var_info is None:
        class_var_info = dict()

    if isinstance(lmcrec_file_or_files, str):
        lmcrec_file_or_files = [lmcrec_file_or_files]

    global_first_ts, global_last_ts, inst_max_size = None, None, 0

    for lmcrec_file in lmcrec_file_or_files:
        start_ts = time.time()
        state_cache = LmcrecStateCache(LmcrecFileDecoder(lmcrec_file))
        inst_tree, class_var_info, first_ts, last_ts, ret_code = get_inventory(
            state_cache,
            inst_tree,
            class_var_info,
        )
        d_time = time.time() - start_ts
        inst_max_size = max(inst_max_size, state_cache.inst_max_size)
        if (
            global_first_ts is None
            or first_ts is not None
            and first_ts < global_first_ts
        ):
            global_first_ts = first_ts
        if global_last_ts is None or last_ts is not None and last_ts > global_last_ts:
            global_last_ts = last_ts
        if ret_code != LmcrecScanRetCode.ATEOR or verbose:
            print(
                f"get_inventory({lmcrec_file!r}) returned {ret_code!r} in {d_time:.06f} sec",
                file=sys.stderr,
            )
    return (
        inst_tree,
        class_var_info,
        inst_max_size,
        global_first_ts,
        global_last_ts,
    )
