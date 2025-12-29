"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from .build_file_chains_def import BuildLmcrecFileChainsTestCase

test_cases_ok = [
    BuildLmcrecFileChainsTestCase(
        name="EmptyDir",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals = {
            "/lmcrec/rec": [],
        },
    ),
    BuildLmcrecFileChainsTestCase(
        name="OneFileTopDir",
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
]

# fmt: on
