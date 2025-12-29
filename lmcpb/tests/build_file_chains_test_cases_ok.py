# Prompt: .github/prompts/build_file_chains_test_cases_ok.py.prompt.md
# Model: Claude Sonnet 4.5
"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from .build_file_chains_def import BuildLmcrecFileChainsTestCase

test_cases_ok = [
    BuildLmcrecFileChainsTestCase(
        name="EmptyDir",
        description="Empty directory returns no chains",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals = {
            "/lmcrec/rec": [],
        },
    ),
    BuildLmcrecFileChainsTestCase(
        name="OneFileTopDir",
        description="Single file in a dated subdirectory under top dir",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                ".lck",
                "2000-01-01"
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info", "file1.lmcrec.index",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:07:08", "2000-01-01T09:10:11"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file1.lmcrec"]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="OneFileSubDir",
        description="Single file when pointing directly to a dated subdirectory",
        record_files_dir="/lmcrec/rec/2000-01-01",
        listdir_ret_vals={
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info", "file1.lmcrec.index",
            ],
        },
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:07:08", "2000-01-01T09:10:11"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file1.lmcrec"]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="SingleChainThreeFiles",
        description="Three files linked via prev_file_name forming a single chain",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info", "file1.lmcrec.index",
                "file2.lmcrec", "file2.lmcrec.info", "file2.lmcrec.index",
                "file3.lmcrec", "file3.lmcrec.info", "file3.lmcrec.index",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec", "2000-01-01T08:00:01", "2000-01-01T10:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "2000-01-01/file2.lmcrec", "2000-01-01T10:00:01", "2000-01-01T12:00:00"
            ),
        },
        expect_file_chains = [
            [
                "/lmcrec/rec/2000-01-01/file1.lmcrec",
                "/lmcrec/rec/2000-01-01/file2.lmcrec",
                "/lmcrec/rec/2000-01-01/file3.lmcrec",
            ]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="MultipleChainsInSameDir",
        description="Two independent chains in the same directory",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
                "file3.lmcrec", "file3.lmcrec.info",
                "file4.lmcrec", "file4.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec", "2000-01-01T08:00:01", "2000-01-01T10:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "", "2000-01-01T14:00:00", "2000-01-01T16:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file4.lmcrec.info": (
                "2000-01-01/file3.lmcrec", "2000-01-01T16:00:01", "2000-01-01T18:00:00"
            ),
        },
        expect_file_chains = [
            [
                "/lmcrec/rec/2000-01-01/file1.lmcrec",
                "/lmcrec/rec/2000-01-01/file2.lmcrec",
            ],
            [
                "/lmcrec/rec/2000-01-01/file3.lmcrec",
                "/lmcrec/rec/2000-01-01/file4.lmcrec",
            ]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="MultipleChainsAcrossDirs",
        description="Multiple chains spanning different dated directories",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
                "2000-01-02",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
            ],
            "/lmcrec/rec/2000-01-02": [
                ".", "..",
                "file3.lmcrec", "file3.lmcrec.info",
                "file4.lmcrec", "file4.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01", "/lmcrec/rec/2000-01-02"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T12:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "", "2000-01-01T14:00:00", "2000-01-01T20:00:00"
            ),
            "/lmcrec/rec/2000-01-02/file3.lmcrec.info": (
                "", "2000-01-02T06:00:00", "2000-01-02T12:00:00"
            ),
            "/lmcrec/rec/2000-01-02/file4.lmcrec.info": (
                "", "2000-01-02T14:00:00", "2000-01-02T20:00:00"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file1.lmcrec"],
            ["/lmcrec/rec/2000-01-01/file2.lmcrec"],
            ["/lmcrec/rec/2000-01-02/file3.lmcrec"],
            ["/lmcrec/rec/2000-01-02/file4.lmcrec"],
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="TimeWindowFromTs",
        description="Filter files by from_ts, excluding earlier files",
        record_files_dir="/lmcrec/rec",
        from_ts="2000-01-01T10:00:00",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
                "file3.lmcrec", "file3.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "", "2000-01-01T09:00:00", "2000-01-01T11:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "", "2000-01-01T12:00:00", "2000-01-01T14:00:00"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file2.lmcrec"],
            ["/lmcrec/rec/2000-01-01/file3.lmcrec"],
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="TimeWindowToTs",
        description="Filter files by to_ts, excluding later files",
        record_files_dir="/lmcrec/rec",
        to_ts="2000-01-01T11:00:00",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
                "file3.lmcrec", "file3.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "", "2000-01-01T09:00:00", "2000-01-01T11:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "", "2000-01-01T12:00:00", "2000-01-01T14:00:00"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file1.lmcrec"],
            ["/lmcrec/rec/2000-01-01/file2.lmcrec"],
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="TimeWindowFromToTs",
        description="Filter files by both from_ts and to_ts",
        record_files_dir="/lmcrec/rec",
        from_ts="2000-01-01T08:30:00",
        to_ts="2000-01-01T12:30:00",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
                "file3.lmcrec", "file3.lmcrec.info",
                "file4.lmcrec", "file4.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "", "2000-01-01T09:00:00", "2000-01-01T10:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "", "2000-01-01T11:00:00", "2000-01-01T12:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file4.lmcrec.info": (
                "", "2000-01-01T13:00:00", "2000-01-01T14:00:00"
            ),
        },
        expect_file_chains = [
            ["/lmcrec/rec/2000-01-01/file2.lmcrec"],
            ["/lmcrec/rec/2000-01-01/file3.lmcrec"],
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="NonChronologicalListdir",
        description="Files returned by listdir in non-chronological order are correctly chained",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file3.lmcrec", "file3.lmcrec.info",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec", "2000-01-01T08:00:01", "2000-01-01T10:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "2000-01-01/file2.lmcrec", "2000-01-01T10:00:01", "2000-01-01T12:00:00"
            ),
        },
        expect_file_chains = [
            [
                "/lmcrec/rec/2000-01-01/file1.lmcrec",
                "/lmcrec/rec/2000-01-01/file2.lmcrec",
                "/lmcrec/rec/2000-01-01/file3.lmcrec",
            ]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="NonChronologicalMultipleChains",
        description="Multiple chains with files in non-chronological listdir order",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file4.lmcrec", "file4.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
                "file1.lmcrec", "file1.lmcrec.info",
                "file3.lmcrec", "file3.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec", "2000-01-01T08:00:01", "2000-01-01T10:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file3.lmcrec.info": (
                "", "2000-01-01T14:00:00", "2000-01-01T16:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file4.lmcrec.info": (
                "2000-01-01/file3.lmcrec", "2000-01-01T16:00:01", "2000-01-01T18:00:00"
            ),
        },
        expect_file_chains = [
            [
                "/lmcrec/rec/2000-01-01/file1.lmcrec",
                "/lmcrec/rec/2000-01-01/file2.lmcrec",
            ],
            [
                "/lmcrec/rec/2000-01-01/file3.lmcrec",
                "/lmcrec/rec/2000-01-01/file4.lmcrec",
            ]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="ChainAcrossDatedDirs",
        description="Single chain spanning multiple dated directories",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
                "2000-01-02",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
                "file2.lmcrec", "file2.lmcrec.info",
            ],
            "/lmcrec/rec/2000-01-02": [
                ".", "..",
                "file3.lmcrec", "file3.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01", "/lmcrec/rec/2000-01-02"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T12:00:00"
            ),
            "/lmcrec/rec/2000-01-01/file2.lmcrec.info": (
                "2000-01-01/file1.lmcrec", "2000-01-01T12:00:01", "2000-01-01T18:00:00"
            ),
            "/lmcrec/rec/2000-01-02/file3.lmcrec.info": (
                "2000-01-01/file2.lmcrec", "2000-01-02T00:00:00", "2000-01-02T06:00:00"
            ),
        },
        expect_file_chains = [
            [
                "/lmcrec/rec/2000-01-01/file1.lmcrec",
                "/lmcrec/rec/2000-01-01/file2.lmcrec",
                "/lmcrec/rec/2000-01-02/file3.lmcrec",
            ]
        ],
    ),
    BuildLmcrecFileChainsTestCase(
        name="TimeWindowExcludesAllFiles",
        description="Time window that excludes all available files",
        record_files_dir="/lmcrec/rec",
        from_ts="2000-01-02T00:00:00",
        to_ts="2000-01-02T23:59:59",
        listdir_ret_vals={
            "/lmcrec/rec": [
                ".", "..",
                "2000-01-01",
            ],
            "/lmcrec/rec/2000-01-01": [
                ".", "..",
                "file1.lmcrec", "file1.lmcrec.info",
            ],
        },
        isdir_list=["/lmcrec/rec/2000-01-01"],
        decode_lmcrec_info_from_file_ret_vals={
            "/lmcrec/rec/2000-01-01/file1.lmcrec.info": (
                "", "2000-01-01T06:00:00", "2000-01-01T08:00:00"
            ),
        },
        expect_file_chains = None,
    ),
]

# fmt: on
