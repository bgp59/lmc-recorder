#! /usr/bin/bash --noprofile

# Common release definitions to be sourced by all release creating scripts.

# Infer project root dir from the location of this file:
project_root_dir=$(dirname $(realpath ${BASH_SOURCE}))

reference_dir="$project_root_dir/reference"
release_root_dir="$project_root_dir/releases"
relnotes_file="$project_root_dir/relnotes.txt"
semver_file="$project_root_dir/semver.txt"

# Must have semver:
semver=$(cat $semver_file)
if [[ -z "$semver" ]]; then
    echo >&2 "$(basename ${BASH_SOURCE}): Missing mandatory semver"
    exit 1
fi

release_dir=$release_root_dir/$semver

