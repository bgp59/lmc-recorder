#! /bin/bash

# Apply Python code formatting tools:

this_script=${0##*/}

case "$1" in
    -h|--h*)
        echo >&2 "Usage: $this_script DIR ..."
        exit 1
    ;;
esac

case "$0" in
    /*|*/*) this_dir=$(dirname $(realpath $0));;
    *) this_dir=$(dirname $(realpath $(which $0)));;
esac

lmcpb_project_root=$(realpath $this_dir/..)


for d in ${@:-$lmcpb_project_root}; do
    real_d=$(realpath $d) || continue
    if [[ "$real_d" != "$lmcpb_project_root" && "$real_d" != "$lmcpb_project_root/"* ]]; then
        echo >&2 "$this_script: '$d' ignored, its real path '$real_d' is outside the project root '$lmcpb_project_root'"
        continue
    fi
    (
        set -x
        autoflake --config $lmcpb_project_root/pyproject.toml $real_d
        isort --settings-path $lmcpb_project_root $real_d
        black --config=$lmcpb_project_root/pyproject.toml $real_d
    )
done
