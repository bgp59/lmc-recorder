"""Examples for test case generation via Copilot prompt"""

# noqa
# fmt: off

from .build_file_chains_def import BuildLmcrecFileChainsTestCase

test_cases_err = [
    BuildLmcrecFileChainsTestCase(
        name="MixedLmcrecFilesAndSubdirs",
        record_files_dir="/lmcrec/rec",
        listdir_ret_vals = {
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
]

# fmt: on
