"""Standard arguments used for queries"""

import argparse
import re
import time
from typing import Optional, Tuple

from config import (
    LMCREC_CONFIG_FILE_DEFAULT,
    LMCREC_CONFIG_FILE_ENV_VAR,
    get_record_files_dir,
)
from misc.timeutils import parse_ts


def parse_duration(spec: str) -> float:
    """Parse duration specifier

    Args:
        spec (str):
            [Hh][Mm][S[s]] H hours, M min, S sec. Some of them may be missing,
            e.g. Mm for M minutes of HhSs for H hours and S sec.

            M and S, unless they are in the first position of the spec, should
            be within the [0, 60) range. For instance '78m' is valid but '1h78m'
            is not, the latter should be '2h18m'.

            S may be a float in decimal point format. 's' suffix may be omitted,
            e.g. '5' stands for 5 sec.

    Returns
        float: the duration, in seconds

    Raises:
        ValueError for invalid spec
    """

    m_obj = re.match(r"(\d+h)?(\d+m)?(\d+(?:\.\d*)?s?)?$", spec.strip())
    if m_obj is None:
        raise ValueError(f"invalid duration specifier {spec!r}")
    h_spec, m_spec, s_spec = m_obj.groups()
    if h_spec is None and m_spec is None and s_spec is None:
        raise ValueError(f"invalid duration specifier {spec!r}")
    h, m, s = 0, 0, 0
    if h_spec is not None:
        h = int(h_spec[:-1])
    if m_spec is not None:
        m = int(m_spec[:-1])
    if s_spec is not None:
        if s_spec.endswith("s"):
            s_spec = s_spec[:-1]
        s = float(s_spec)
    if h_spec is not None and m >= 60:
        raise ValueError(
            f"invalid duration specifier {spec!r}, {m} min not in [0, 60) range"
        )
    if (h_spec is not None or m_spec is not None) and s >= 60:
        raise ValueError(
            f"invalid duration specifier {spec!r}, {s} sec not in [0, 60) range"
        )
    return h * 3600 + m * 60 + s


def parse_from_to_ts(
    from_spec: Optional[str] = None,
    to_spec: Optional[str] = None,
) -> Tuple[Optional[float], Optional[float]]:
    """Parse (from, to) timestamp specifiers

    Args:
        from_spec (str):
            ISO 8601 date spec or -HhMmSs duration. A negative duration stands
            for time back from to_spec. If None then start from the oldest
            available data.

        to_spec (str):
            ISO 8601 date spec or +HhMmSs duration.  A positive duration stands
            for time after from_spec. If None then use up to the most recent
            available data.

    Returns:
        (float, float): (from, to) timestamps. If either is None then use from
        the oldest and/or up to the newest available data.

    Raises:
        ValueError for invalid spec or combinations
    """

    if (
        from_spec is not None
        and from_spec.startswith("-")
        and to_spec is not None
        and to_spec.startswith("+")
    ):
        raise RuntimeError(
            f"cannot have both from={from_spec!r} and to={to_spec!r} as duration"
        )

    from_ts, to_ts = None, None
    before, after = None, None
    if from_spec is not None:
        if from_spec.startswith("-"):
            before = parse_duration(from_spec[1:])
        else:
            from_ts = parse_ts(from_spec)
    if to_spec is not None:
        if to_spec.startswith("+"):
            after = parse_duration(to_spec[1:])
        else:
            to_ts = parse_ts(to_spec)
    if before is not None:
        if to_ts is None:
            to_ts = time.time()
        from_ts = to_ts - before
    elif after is not None:
        to_ts = from_ts + after

    return from_ts, to_ts


def get_file_selection_arg_parser() -> argparse.ArgumentParser:
    """Return the argument parser with the standard args used for file selection

    To be used as a parent to a specific tool parser (see parents arg of
    ArgumentParser).
    """

    parser = argparse.ArgumentParser(
        add_help=False,
    )
    parser.add_argument(
        "-f",
        "--from-ts",
        help="""
        Starting timestamp for a query, either in ISO 8601 date spec or -HhMmSs
        duration. A negative duration stands for time back from --to-ts arg. If
        not specified then start from the oldest available data. Note that a
        negative value has to be specified using '=' rather that ' ', (space),
        e.g. --from-ts=-30m or -f=-30m.
        """,
    )
    parser.add_argument(
        "-t",
        "--to-ts",
        help="""
        Ending timestamp for a query, either in ISO 8601 date spec or +HhMmSs
        duration. A positive duration stands for time after --from-ts arg. If
        not specified then end at the newest available data. 
        """,
    )
    parser.add_argument(
        "-c",
        "--config",
        help=f"""
        Config file used in conjunction with INST to determine record files dir.
        It defaults to env var ${LMCREC_CONFIG_FILE_ENV_VAR}, or if the latter is not
        set, to {LMCREC_CONFIG_FILE_DEFAULT!r}.
        """,
    )
    parser.add_argument(
        "-i",
        "--inst",
        help=f"""
        lmcrec inst(ance), used to locate the record files dir based on the
        config. It is mandatory if  --record-files-dir is not specified.
        """,
    )
    parser.add_argument(
        "-d",
        "--record-files-dir",
        help="""
        Use RECORD_FILES_DIR instead of the one inferred using --inst. lmcrec
        stores record files under date based sub-dirs:
        RECORD_FILES_DIR/yyyy-mm-dd. The argument value may be either the top
        dir RECORD_FILES_DIR or a sub-dir RECORD_FILES_DIR/yyyy-mm-dd.
        """,
    )
    return parser


def process_file_selection_args(
    args: argparse.Namespace,
) -> Tuple[Optional[float], Optional[float], str]:
    """Extract query file selection args from the parsed set

    Args:
        args (argparse.Namespace): returned by parse_args()

    Returns:
        str, float, float: record_files_dir, from_ts, to_ts

    Raises:
        RuntimeError
    """

    record_files_dir = args.record_files_dir
    if not record_files_dir:
        inst = args.inst
        if not inst:
            raise RuntimeError(
                "--inst is mandatory when --record-files-dir is not used"
            )
        record_files_dir = get_record_files_dir(inst, args.config)
        if not record_files_dir:
            raise RuntimeError("record_files_dir cannot be determined")
    from_ts, to_ts = parse_from_to_ts(args.from_ts, args.to_ts)
    return record_files_dir, from_ts, to_ts
