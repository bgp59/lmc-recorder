"""Lmcrec Query Object"""

from typing import Callable, Dict, Optional, Tuple

from .query_selector import LmcrecQueryClassResult, build_query_selectors
from .query_state_cache import LmcrecQueryIntervalStateCache, LmcrecScanRetCode

# The query result is indexed by query name:
LmcrecQueryResult = Dict[str, LmcrecQueryClassResult]

# The callable for run w/ callback:
LmcrecQueryCallback = Callable[[LmcrecQueryResult, LmcrecQueryIntervalStateCache], bool]


class LmcrecQuery:
    """Lmcrec Query Object"""

    def __init__(
        self,
        record_files_dir,
        *query_or_file,
        from_ts: Optional[float] = None,
        to_ts: Optional[float] = None,
        force_prev: bool = False,
    ):
        """Build Lmcrec Query Object

        Args:

            record_files_dir (str):
                Either the top record files dir or one of its sub-dirs.

            from_ts (float):
                The start of the timestamp window. If None then consider files
                starting with the earliest available.

            to_ts (float):
                The start of the timestamp window. If None then consider files
                up to the most recent available.

            force_prev (bool):
                Force maintaining the previous value in state cache; normally
                the queries are inspected to decide if it is needed or not,
                based on whether any query specified delta or rate.

            query_or_file (str):
                Queries to execute. If a query starts w/ '@' then it is the name
                of the file containing the actual query. If query does not have
                a name, it will be assigned 'query#N', where N is order number,
                starting from 1. Whether explicit of implicit, all query names
                must be unique.

                See: query_selector.py for actual query syntax.
        """

        selectors = build_query_selectors(*query_or_file)

        # Auto-assign names as needed:
        for i, selector in enumerate(selectors):
            if not selector.name:
                selector.name = f"query#{i + 1}"

        # Verify name uniqueness and whether previous state is needed or not:
        used_names = set()
        have_prev = force_prev
        for selector in selectors:
            if selector.name in used_names:
                raise RuntimeError(f"duplicate query name: {selector.name!r}")
            used_names.add(selector.name)
            if selector.needs_prev:
                have_prev = True
        self._selectors = selectors

        # Build the query state cache:
        self.query_state_cache = LmcrecQueryIntervalStateCache(
            record_files_dir,
            from_ts=from_ts,
            to_ts=to_ts,
            have_prev=have_prev,
        )

        chain_list = self.query_state_cache._chain_list
        if chain_list:
            c_from_ts, c_to_ts = chain_list[0].lmcrec_info.start_ts, None
            entry = chain_list[-1]
            while entry is not None:
                c_to_ts = entry.lmcrec_info.most_recent_ts
                entry = entry.next
        self.from_ts = from_ts if from_ts is not None else c_from_ts
        self.to_ts = to_ts if to_ts is not None else c_to_ts

    def get_next_results(self) -> Tuple[LmcrecScanRetCode, float, LmcrecQueryResult]:
        """Apply next scan to the cache, run the queries and return the results

        Return: ret_code, ts, results

            ret_code:
                LmcrecScanRetCode.COMPLETE: valid  ts, results
                anything else: ts is None, results is None

            ts:
                Timestamp when the scan was recorded

            results:
                The results, indexed by query name and class name:
                    [query_name][class_name] = LmcrecQueryClassResult(
                            var_names=List[str],
                            vals_by_inst=Dict[str, List[Any]]
                    )
        """

        query_state_cache = self.query_state_cache
        ret_code = query_state_cache.apply_next_scan()
        if ret_code != LmcrecScanRetCode.COMPLETE:
            return ret_code, None, None

        result = {
            selector.name: selector.run(query_state_cache)
            for selector in self._selectors
        }
        return ret_code, query_state_cache.ts, result

    def run_with_callback(
        self,
        cb: Optional[
            Callable[[LmcrecQueryResult, LmcrecQueryIntervalStateCache], bool]
        ],
    ) -> LmcrecScanRetCode:
        """Invoke callback in a loop after each next results

        Args:
            cb (Callable[[LmcrecQueryResult, LmcrecQueryIntervalStateCache], bool):

            A callable to invoke with the query results and the state cache
            passed as args until either the callback returns False or
            get_next_results returns something different than
            LmcrecScanRetCode.COMPLETE

        Returns:
            Most recent LmcrecScanRetCode
        """

        ret_code = None
        while True:
            ret_code, _, result = self.get_next_results()
            if ret_code != LmcrecScanRetCode.COMPLETE:
                break
            if cb is not None and not cb(result, self.query_state_cache):
                break
        return ret_code

    @property
    def first_ts(self):
        return self.query_state_cache.first_ts

    @property
    def last_ts(self):
        return self.query_state_cache.last_ts
