#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will consolidate all the recipes in one maxiconda-envs.xlsx file.
"""
import sys
import os
import platform
import yaml
import requests
import bz2
import json
import subprocess
from pathlib import Path
from typing import Tuple

# Constants
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SPECS_FPATH = REPO_ROOT / "specs.yaml"
RECIPES_ROOT  = REPO_ROOT / "recipes"
CACHE = {}

def parse_recipe(recipe_path):
    recipe_path = os.path.normpath(recipe_path)
    if not os.path.exists(recipe_path):
        raise Exception(f"'{recipe_path}' does not exist!")
    environment = recipe_path.split(os.sep)[-2]
    PY = recipe_path.split(os.sep)[-3]
    OS_CPU = recipe_path.split(os.sep)[-4]
    print(f"Parsing: {OS_CPU}/{PY}/{environment}")

    # with open(parse_recipe) as fd:
    #     start_marker = False
    #     end_marker = False
    #     for line in fd:
    #         if start_marker markernot "  run:" in line:
    #             continue
    #         marker = True

def main():

    for root, dirs, files in os.walk(str(RECIPES_ROOT)):
        for file in files:
            if file == "meta.yaml":
                recipe_path = os.path.join(root, file)
                parse_recipe(recipe_path)

if __name__ == '__main__':
    main()