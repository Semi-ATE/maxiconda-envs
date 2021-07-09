#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will consolidate all the recipes in one maxiconda-envs.xlsx file.
"""
import os
import yaml
import openpyxl
from pathlib import Path

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
    retval = {}

    print(f"Parsing: {OS_CPU}/{PY}/{environment}")

    with open(recipe_path) as fd:
        start_marker = False
        for line in fd:
            if not start_marker:
                if line.startswith("  run:"):
                    start_marker = True
                continue
            else:
                if line.startswith("about:"):
                    break
                else:
                    line = line.strip()
                    if line == "" or line.startswith("#"):
                        continue
                    line_elements = line[2:].split(" =")
                    package_name = line_elements[0]
                    package_version = "-".join(line_elements[1:])
                    retval[package_name] = package_version
    return OS_CPU, PY, environment, retval

def main():

    all_packages = {}
    for root, dirs, files in os.walk(str(RECIPES_ROOT)):
        for file in files:
            if file == "meta.yaml":
                recipe_path = os.path.join(root, file)
                OS_CPU, PY, environment, packages = parse_recipe(recipe_path)
                if environment not in all_packages:
                    all_packages[environment] = {}
                if OS_CPU not in all_packages[environment]:
                    all_packages[environment][OS_CPU] = {}
                if PY not in all_packages[environment][OS_CPU]:
                    all_packages[environment][OS_CPU][PY] = {}
                all_packages[environment][OS_CPU][PY] = packages
    print(f"Parsing: specs")
    with open(SPECS_FPATH) as fd:
        specs = yaml.load(fd, Loader=yaml.FullLoader)
    specs = specs['environments']

    print(specs)    

if __name__ == '__main__':
    main()