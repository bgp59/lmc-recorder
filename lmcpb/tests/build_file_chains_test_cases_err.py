# Prompt: .github/prompts/build_file_chains_test_cases_err.py.prompt.md
# Model: Claude Sonnet 4.5

"""Test cases for test_build_lmcrec_file_chains_err"""

# noqa
# fmt: off

from .build_file_chains_def import BuildLmcrecFileChainsTestCase

test_cases_err = [
    BuildLmcrecFileChainsTestCase(
        name="MixedLmcrecFilesAndSubdirs",
        description="Top directory contains both lmcrec files and yyyy-mm-dd subdirectories",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                ".lck",
                "2000-01-01",
                "file.lmcrec",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        expect_exception=RuntimeError,
        expect_exception_str="contains both sub-dirs and lmcrec files",
    ),
    BuildLmcrecFileChainsTestCase(
        name="ChronologicalOrderViolationWithinChain",
        description="Files in a chain have overlapping timestamps causing chronological violation",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec",
                "file2.lmcrec",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "",
                "2000-01-01T10:00:00",
                "2000-01-01T12:00:00",
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec",
                "2000-01-01T11:30:00",
                "2000-01-01T13:00:00",
            ),
        },
        expect_exception=RuntimeError,
        expect_exception_str="Chronological order violation",
    ),
    BuildLmcrecFileChainsTestCase(
        name="ChronologicalOrderViolationAcrossChains",
        description="Multiple chains where a later chain starts before an earlier chain ends",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec",
                "file2.lmcrec",
                "file3.lmcrec",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "",
                "2000-01-01T10:00:00",
                "2000-01-01T11:00:00",
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec",
                "2000-01-01T12:00:00",
                "2000-01-01T13:00:00",
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "",
                "2000-01-01T10:30:00",
                "2000-01-01T14:00:00",
            ),
        },
        expect_exception=RuntimeError,
        expect_exception_str="Chronological order violation",
    ),
    BuildLmcrecFileChainsTestCase(
        name="ChronologicalOrderViolationIdenticalStartTimes",
        description="Two chains with identical start times causing chronological violation",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec",
                "file2.lmcrec",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "",
                "2000-01-01T10:00:00",
                "2000-01-01T11:00:00",
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "",
                "2000-01-01T10:00:00",
                "2000-01-01T12:00:00",
            ),
        },
        expect_exception=RuntimeError,
        expect_exception_str="Chronological order violation",
    ),
]

# fmt: on
