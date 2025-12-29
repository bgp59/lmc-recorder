# Prompt: .github/prompts/test_query_args.py.prompt.md
# Model: Claude Sonnet 4.5

"""Test cases for query.args module"""

import time
from datetime import datetime

import pytest

from lmcrec.playback.query.args import parse_duration, parse_from_to_ts


class TestParseDuration:
    """Test cases for parse_duration function"""

    @pytest.mark.parametrize(
        "spec,expected",
        [
            ("5", 5.0),
            ("5s", 5.0),
            ("5.5", 5.5),
            ("5.5s", 5.5),
            ("30m", 1800.0),
            ("2h", 7200.0),
            ("1h30m", 5400.0),
            ("1h30m45s", 5445.0),
            ("1h45s", 3645.0),
            ("30m45s", 1845.0),
            ("0h0m0s", 0.0),
            ("78m", 4680.0),
            ("2h18m", 8280.0),
            ("1h0m0s", 3600.0),
            ("0m30s", 30.0),
            ("1h30m45.5s", 5445.5),
            ("90s", 90.0),
        ],
    )
    def test_ValidFormats(self, spec, expected):
        """
        Test parse_duration with valid duration formats including hours,
        minutes, seconds, and combinations. Validates both integer and
        decimal values.
        """
        assert parse_duration(spec) == expected

    @pytest.mark.parametrize(
        "spec",
        [
            "1h78m",
            "2h60m",
            "1h59m60s",
            "30m60s",
            "1h60s",
        ],
    )
    def test_OutOfRangeValues(self, spec):
        """
        Test parse_duration with out-of-range values where minutes or
        seconds exceed 60 when hours or minutes are specified.
        """
        with pytest.raises(ValueError, match=r"(min|sec) not in \[0, 60\) range"):
            parse_duration(spec)

    @pytest.mark.parametrize(
        "spec",
        [
            "",
            "abc",
            "1x",
            "1h2x",
            "1.5h",
            "1.5m",
            "-5s",
            "5 s",
            "1h 30m",
            "h",
            "m",
            "s",
            "1hh",
            "1mm",
            "1ss",
        ],
    )
    def test_InvalidFormats(self, spec):
        """
        Test parse_duration with invalid format strings that don't match
        the expected HhMmSs pattern or contain invalid characters.
        """
        with pytest.raises(ValueError, match="invalid duration specifier"):
            parse_duration(spec)


class TestParseFromToTs:
    """Test cases for parse_from_to_ts function"""

    def test_BothNone(self):
        """
        Test parse_from_to_ts when both from_spec and to_spec are None,
        expecting both timestamps to be None (use all available data).
        """
        from_ts, to_ts = parse_from_to_ts(None, None)
        assert from_ts is None
        assert to_ts is None

    def test_IsoDateFormats(self):
        """
        Test parse_from_to_ts with ISO 8601 date specifications for both
        from and to timestamps.
        """
        from_ts, to_ts = parse_from_to_ts("2024-01-01T10:00:00", "2024-01-01T12:00:00")
        expected_from = datetime.fromisoformat("2024-01-01T10:00:00").timestamp()
        expected_to = datetime.fromisoformat("2024-01-01T12:00:00").timestamp()
        assert from_ts == expected_from
        assert to_ts == expected_to

    def test_FromIsoToNone(self):
        """
        Test parse_from_to_ts with ISO date for from_spec and None for
        to_spec (query from specific time to newest data).
        """
        from_ts, to_ts = parse_from_to_ts("2024-01-01T10:00:00", None)
        expected_from = datetime.fromisoformat("2024-01-01T10:00:00").timestamp()
        assert from_ts == expected_from
        assert to_ts is None

    def test_FromNoneToIso(self):
        """
        Test parse_from_to_ts with None for from_spec and ISO date for
        to_spec (query from oldest data to specific time).
        """
        from_ts, to_ts = parse_from_to_ts(None, "2024-01-01T12:00:00")
        expected_to = datetime.fromisoformat("2024-01-01T12:00:00").timestamp()
        assert from_ts is None
        assert to_ts == expected_to

    def test_NegativeDurationFromTo(self):
        """
        Test parse_from_to_ts with negative duration for from_spec (time
        back from to_spec). Validates calculation of from_ts based on to_ts.
        """
        to_spec = "2024-01-01T12:00:00"
        from_ts, to_ts = parse_from_to_ts("-30m", to_spec)
        expected_to = datetime.fromisoformat(to_spec).timestamp()
        expected_from = expected_to - 1800.0
        assert from_ts == expected_from
        assert to_ts == expected_to

    def test_NegativeDurationFromCurrentTime(self):
        """
        Test parse_from_to_ts with negative duration and no to_spec,
        expecting to_ts to default to current time and from_ts calculated
        from it.
        """
        current_time = time.time()
        from_ts, to_ts = parse_from_to_ts("-1h", None)
        assert to_ts is not None
        assert from_ts is not None
        assert abs(to_ts - current_time) < 1.0  # within 1 second
        assert abs(from_ts - (to_ts - 3600.0)) < 0.01

    def test_PositiveDurationAfterFrom(self):
        """
        Test parse_from_to_ts with positive duration for to_spec (time
        after from_spec). Validates calculation of to_ts based on from_ts.
        """
        from_spec = "2024-01-01T10:00:00"
        from_ts, to_ts = parse_from_to_ts(from_spec, "+2h")
        expected_from = datetime.fromisoformat(from_spec).timestamp()
        expected_to = expected_from + 7200.0
        assert from_ts == expected_from
        assert to_ts == expected_to

    def test_BothDurationsError(self):
        """
        Test parse_from_to_ts with both from_spec and to_spec as durations,
        expecting a RuntimeError since this combination is invalid.
        """
        with pytest.raises(RuntimeError, match="cannot have both"):
            parse_from_to_ts("-30m", "+1h")

    def test_ComplexDurations(self):
        """
        Test parse_from_to_ts with complex duration formats like 1h30m45s
        to ensure proper parsing and calculation.
        """
        to_spec = "2024-01-01T12:00:00"
        from_ts, to_ts = parse_from_to_ts("-1h30m45s", to_spec)
        expected_to = datetime.fromisoformat(to_spec).timestamp()
        expected_from = expected_to - 5445.0
        assert from_ts == expected_from
        assert to_ts == expected_to

    def test_InvalidIsoFormat(self):
        """
        Test parse_from_to_ts with invalid ISO date format, expecting
        ValueError from datetime parsing.
        """
        with pytest.raises(ValueError):
            parse_from_to_ts("invalid-date", None)

    def test_InvalidDurationFormat(self):
        """
        Test parse_from_to_ts with invalid duration format in from_spec,
        expecting ValueError from parse_duration.
        """
        with pytest.raises(ValueError, match="invalid duration specifier"):
            parse_from_to_ts("-invalid", "2024-01-01T12:00:00")
