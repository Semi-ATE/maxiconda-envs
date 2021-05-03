# solutions directory

This directory contains a bunch of .json files, named as `platform_python.json` where `platform` and `python` come from ./../matrix.yaml and each file is the result of a run of maxiconda-bot for the given platform and python version. genre `mamba create -n env --file XXX --dry-run --json > platform_python.json`