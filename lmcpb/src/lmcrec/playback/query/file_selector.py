"""lmcrec query file selector"""

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from codec import (
    GZIP_FILE_SUFFIX,
    INFO_FILE_SUFFIX,
    LMCREC_FILE_SUFFIX,
    LmcrecInfo,
    decode_lmcrec_info_from_file,
)
from misc.timeutils import format_ts

lmcrec_file_suffixes = [LMCREC_FILE_SUFFIX, LMCREC_FILE_SUFFIX + GZIP_FILE_SUFFIX]


@dataclass
class LmcrecFileEntry:
    next: Optional["LmcrecFileEntry"] = None
    file_name: Optional[str] = None
    lmcrec_info: Optional[LmcrecInfo] = None
    _has_prev: bool = False


def build_lmcrec_file_chains(
    record_files_dir: str,
    from_ts: Optional[float] = None,
    to_ts: Optional[float] = None,
) -> Optional[List[LmcrecFileEntry]]:
    """Build the list of lmcrec chains for the given dir and time window

    Args:

        record_files_dir (str):
            Either the top record files dir or one of its sub-dirs.

        from_ts (float):
            The start of the timestamp window. If None then consider files
            starting with the earliest available.

        to_ts (float):
            The start of the timestamp window. If None then consider files up to
            the most recent available.

    Returns:
        list: of LmcrecFileEntry chains, sorted chronologically. A new LmcrecStateCache
        has to be created at the beginning of each chain and the files in the
        chain can share it by replacing the decoder. In other words, the last
        scan of a file in the chain can be used for previous values for the
        first scan of the next file in the chain.

    Raises:
        RuntimeError

    """

    record_files_dir = os.path.abspath(record_files_dir)

    def yyyy_mm_dd_from_ts(ts: Optional[float]) -> Optional[str]:
        if ts is None:
            return None
        return format_ts(ts)[:10]

    from_yyyy_mm_dd = yyyy_mm_dd_from_ts(from_ts)
    to_yyyy_mm_dd = yyyy_mm_dd_from_ts(to_ts)

    # Determine whether this is top record files dir or one of its sub-dir; only
    # one list below should end up being populated.
    lmcrec_file_list = []
    subdir_list = []

    def classify_dir(subdir=""):
        dpath = os.path.join(record_files_dir, subdir) if subdir else record_files_dir
        for fname in os.listdir(dpath):
            if fname in {".", ".."}:
                continue
            if (
                not subdir
                and re.match(r"\d{4}-\d{2}-\d{2}$", fname)
                and (from_yyyy_mm_dd is None or from_yyyy_mm_dd <= fname)
                and (to_yyyy_mm_dd is None or fname <= to_yyyy_mm_dd)
                and os.path.isdir(os.path.join(dpath, fname))
            ):
                subdir_list.append(fname)
                continue
            for suffix in lmcrec_file_suffixes:
                if fname.endswith(suffix):
                    if subdir:
                        fname = os.path.join(subdir, fname)
                    lmcrec_file_list.append(fname)
                    continue

    classify_dir()

    if lmcrec_file_list and subdir_list:
        raise RuntimeError(
            f"{record_files_dir} contains both sub-dirs and lmcrec files"
        )

    if lmcrec_file_list:
        # Must have been a sub-dir, normalize top dir and the file paths
        # relative to it:
        subdir = os.path.basename(record_files_dir)
        record_files_dir = os.path.dirname(record_files_dir)
        lmcrec_file_list = [os.path.join(subdir, fname) for fname in lmcrec_file_list]
    elif subdir_list:
        for subdir in subdir_list:
            classify_dir(subdir)

    if not lmcrec_file_list:
        return None

    # At this point record_files_dir is the true top dir and lmcrec_file_list
    # holds subdir/lmcrec paths. Iterate through the list, keep only the
    # files that intersect with the time window and place them in the
    # appropriate chain.
    lmcrec_file_entry: Dict[str, LmcrecFileEntry] = dict()

    # The files are in the listdir order, which is not necessarily the
    # chronological one. Keep track of cases where a file may be processed
    # before its associated prev_file, the latter's next, when/if encountered
    # should, should be the former's entry.
    lmcrec_next_file_entry: Dict[str, LmcrecFileEntry] = dict()

    for lmcrec_file in lmcrec_file_list:
        file_name = os.path.join(record_files_dir, lmcrec_file)
        info_file_name = file_name + INFO_FILE_SUFFIX
        lmcrec_info = None
        try:
            lmcrec_info = decode_lmcrec_info_from_file(info_file_name)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
        except (ValueError, EOFError) as e:
            print(f"{info_file_name}: {e}", file=sys.stderr)
        if (
            lmcrec_info is None
            or from_ts is not None
            and lmcrec_info.most_recent_ts < from_ts
            or to_ts is not None
            and lmcrec_info.start_ts > to_ts
        ):
            continue

        entry = LmcrecFileEntry(
            file_name=file_name,
            lmcrec_info=lmcrec_info,
        )

        next_entry = lmcrec_next_file_entry.get(lmcrec_file)
        if next_entry is not None:
            # Next file already encountered, point this one to it:
            entry.next = next_entry
            next_entry._has_prev = True

        if lmcrec_info.prev_file_name:
            prev_entry = lmcrec_file_entry.get(lmcrec_info.prev_file_name)
            if prev_entry is not None:
                # Previous file already encountered, point it to this one:
                prev_entry.next = entry
                entry._has_prev = True
            else:
                # Previous file may be encountered later, remember that this
                # entry is to be its next:
                lmcrec_next_file_entry[lmcrec_info.prev_file_name] = entry
        lmcrec_file_entry[lmcrec_file] = entry

    # Build the chain list; the head of each chain is an entry without a previous:
    chain_list: List[LmcrecFileEntry] = []
    for entry in lmcrec_file_entry.values():
        if not entry._has_prev:
            chain_list.append(entry)

    # Sort the list in chronological order, based in start_ts of the chain head:
    chain_list = sorted(chain_list, key=lambda e: e.lmcrec_info.start_ts)

    # Perform sanity check: across all chains, each entry but the first follows
    # chronologically the previous one:
    prev_most_recent_ts = None
    prev_file_name = None
    for entry in chain_list:
        while entry is not None:
            file_name, start_ts = entry.file_name, entry.lmcrec_info.start_ts
            if prev_most_recent_ts is not None and prev_most_recent_ts >= start_ts:
                l = max(len(prev_file_name), len(file_name))
                raise RuntimeError(
                    f"Chronological order violation:\n"
                    f" {prev_file_name:>{l}s}:  last_ts={format_ts(prev_most_recent_ts)}\n"
                    f" {file_name:>{l}s}: start_ts={format_ts(start_ts)}"
                )
            prev_file_name = file_name
            prev_most_recent_ts = entry.lmcrec_info.most_recent_ts
            entry = entry.next

    return chain_list


def chain_to_file_list(
    chain_list: Optional[List[LmcrecFileEntry]] = None,
) -> List[str]:
    """Flatten the chain list"""

    file_list = []
    if chain_list:
        for entry in chain_list:
            while entry is not None:
                file_list.append(entry.file_name)
                entry = entry.next
    return file_list
