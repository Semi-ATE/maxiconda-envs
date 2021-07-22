#!/usr/bin/env bash

set -xe

if [[ "$(uname)" != "Linux" ]]; then
    echo "Not running a Linux OS ... aborting!"
    exit 1
fi

if [[ "$(uname -m)" != "aarch64" ]]; then
    echo "Not running on an ARM64 processor ... aborting!"
    exit 1
fi

conda install --file /maxiconda-envs/environment.txt
python -u /maxiconda-envs/scripts/maxiconda.py $MAXICONDA_ARGS
