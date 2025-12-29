"""lmcrec query state cache object"""

import inspect
import sys
from typing import Callable, Optional

from cache import LmcrecScanRetCode, LmcrecStateCache
from codec import (
    LmcrecFileDecoder,
    locate_checkpoint,
)
from misc.timeutils import format_ts

from .file_selector import build_lmcrec_file_chains


class LmcrecQueryIntervalStateCache(LmcrecStateCache):

    def __init__(
        self,
        record_files_dir: str = "",
        from_ts: Optional[float] = None,
        to_ts: Optional[float] = None,
        have_prev: bool = False,
        _verbose: bool = False,
        _no_chain_list: bool = False,  # used for testing
    ):
        """LmcrecStateCache across multiple files

        Args:

            record_files_dir (str):
                Either the top record files dir or one of its sub-dirs.

            from_ts (float):
                The start of the timestamp window. If None then consider files
                starting with the earliest available.

            to_ts (float):
                The start of the timestamp window. If None then consider files up to
                the most recent available.

            have_prev (bool):
                Whether to maintain previous variable values or not.

            _verbose (bool):
                Used for troubleshooting, create stderr trace.

            _no_chain_list: bool:
                Used for testing, do not actually access files
        """

        self._from_ts = from_ts
        self._to_ts = to_ts
        self._have_prev = have_prev
        self._verbose = _verbose
        self._chain_list_index = 0
        self._chain_entry = None
        self._decoder = None
        self._check_from_ts = self._from_ts is not None
        self._closed = False
        self.first_ts = None
        self.last_ts = None
        if _no_chain_list:
            self._chain_list = None
        else:
            self._chain_list = build_lmcrec_file_chains(
                record_files_dir, from_ts=from_ts, to_ts=to_ts
            )
        self.reset()

    def _trace(self, *msg):
        co_name = inspect.currentframe().f_back.f_code.co_name
        print(f"{co_name}():", *msg, file=sys.stderr)

    def apply_next_scan(self) -> LmcrecScanRetCode:
        """Create/update encoder to state cache and apply the next scan"""

        if self._closed:
            return LmcrecScanRetCode.CLOSED

        self.new_chain = False
        if self._decoder is None:
            if self._chain_entry is None:
                if self._chain_list_index >= len(self._chain_list):
                    self._closed = True
                    return LmcrecScanRetCode.ATEOR
                self._chain_entry = self._chain_list[self._chain_list_index]
                self._chain_list_index += 1
                self.new_chain = True
                if self._verbose:
                    self._trace("new chain, invalidate the cache")
                self.reset()
            self.lmcrec_file = self._chain_entry.file_name
            if self._verbose:
                self._trace(f"new decoder from {self.lmcrec_file!r}")
            self._decoder = LmcrecFileDecoder(self.lmcrec_file)
            if self._check_from_ts:
                from_ts = self._from_ts
                if self._verbose:
                    self._trace(
                        f"locate checkpoint before {format_ts(from_ts)}, if any"
                    )
                try:
                    chkpt_ts, chkpt_off = locate_checkpoint(self.lmcrec_file, from_ts)
                except FileNotFoundError as e:
                    chkpt_ts, chkpt_off = None, None
                    if self._verbose:
                        self._trace(e)
                if chkpt_off is not None:
                    if self._verbose:
                        self._trace(
                            f"found checkpoint: ts={format_ts(chkpt_ts)}, off=+{chkpt_off}",
                        )
                    self._decoder.goto(chkpt_off)
        # The state cache is now ready:
        ret_code = None
        if self._check_from_ts:
            # Locate the 1st scan after or at from_ts:
            if self._verbose:
                self._trace(
                    f"locate first scan at or after ts={format_ts(from_ts)}",
                )
            while self.ts is None or self.ts < from_ts:
                ret_code = self._apply_next_scan()
                if chkpt_ts is not None:
                    # Sanity check:
                    if chkpt_ts != self.ts:
                        raise RuntimeError(
                            f"checkpoint ts: want: {format_ts(chkpt_ts)}, got: {format_ts(self.ts)}"
                        )
                    chkpt_ts = None
                if ret_code != LmcrecScanRetCode.COMPLETE:
                    break
            if self._verbose and ret_code == LmcrecScanRetCode.COMPLETE:
                self._trace(f"start ts={format_ts(self.ts)}")
            self._check_from_ts = False
        else:
            ret_code = self._apply_next_scan()

        if ret_code == LmcrecScanRetCode.ATEOR:
            # Move to the next file in the chain and re-invoke:
            self._decoder = None
            self._chain_entry = self._chain_entry.next
            ret_code = self.apply_next_scan()
        elif ret_code == LmcrecScanRetCode.COMPLETE:
            if self.first_ts is None:
                self.first_ts = self.ts
            # Check for time window end, if any:
            if self._to_ts is not None and self._to_ts < self.ts:
                if self._verbose:
                    self._trace(
                        f"scan ts={format_ts(self.ts)} after to_ts={format_ts(self._to_ts)}, force close everything",
                    )
                self.close()
                ret_code = LmcrecScanRetCode.ATEOR
            else:
                self.last_ts = self.ts
        else:
            self._trace(
                f"{self.lmcrec_file!r}: ret_code={ret_code!r}, force close everything"
            )
            self.close()

        return ret_code

    def run_with_cb(
        self, cb: Optional[Callable[["LmcrecQueryIntervalStateCache"], bool]]
    ) -> LmcrecScanRetCode:
        """Invoke callback in a loop after each scan

        Args:
            cb (Callable[[mcQueryStateCache], bool]):

            A callable to invoke with the state cache passed as arg until either
            the callback returns False or get_next_results returns something
            different than LmcrecScanRetCode.COMPLETE

        Returns:
            Most recent LmcrecScanRetCode
        """

        ret_code = None
        while True:
            ret_code = self.apply_next_scan()
            if ret_code != LmcrecScanRetCode.COMPLETE:
                break
            if cb is not None and not cb(self):
                break
        return ret_code

    def close(self):
        if not self._closed:
            if self._decoder is not None:
                self._decoder.close()
                self._decoder = None
            self._closed = True

    def __del__(self):
        self.close()
