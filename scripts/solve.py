#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will solve all the environments in environments.yaml
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

def get_OS_CPU():
    """
    This function will return the OS and CPU in a conda-forge compatible format.

    Parameters
    ----------
    /

    Returns
    -------
    conda-forge compatile OS_CPU, limited to:
        - linux-64   
        - linux-aarch64
        - osx-64   
        - osx-arm64
        - win-64
    """

    is_64bits = sys.maxsize > 2**32
    if not is_64bits:
        raise Exception("only 64 bit platforms are supported.")

    CPU = platform.machine()

    OS = platform.system()
    if OS == "Linux":
        if CPU in ["AMD64", "x86_64"]:
            OS_CPU = "linux-64"
        elif CPU in ["aarch64"]:
            OS_CPU = "linux-aarch64"
        else:
            raise Exception(f"'{CPU}' not supported in Linux")
    elif OS == "Windows":
        if CPU in ["AMD64", "x86_64"]:
            OS_CPU = "win-64"
        else:
            raise Exception(f"'{CPU}' not supported in Windows")
    elif OS == "Darwin":
        if CPU in ["AMD64", "x86_64"]:
            OS_CPU = "osx-64"
        elif CPU in ["aarch64"]:
            OS_CPU = "osx-arm64"
        else:
            raise Exception(f"'{CPU}' not supported in MacOS")
    else:
        raise Exception("'{OS}' not supported.")

    return OS_CPU

def get_repodata(url):
    """
    Get repodata from url poitning to anaconda.org bz2 files.

    If url has been already downloaded in a session, it will use the data from
    cache.

    Parameters
    ----------
    url : str
        URL to repodata.

    Returns
    -------
    dict
        Repodata dictionary.
    """
    global CACHE
    if url not in CACHE:
        request = requests.get(url)
        if request.status_code != 200:
            print(f"Warning: '{url}' doesn't exist!")
            return {}
        arch_json_bz2 = request.content
        arch_json = bz2.decompress(arch_json_bz2) 
        arch = json.loads(arch_json)
        CACHE[url] = arch
    else:
        arch = CACHE[url]

    return arch


def get_conda_forge_packages(designator):
    """
    This function returns all packages that exist for the given designator

    Parameters
    ----------
    designator 
        str formatted like so :linux-64_py36

    Returns
    -------
    dict
        packages and versions formatted like { package : [versions] }
    """
    OS_CPU = designator.split('_')[0]
    PY = designator.split('_')[1]

    arch_packages = f"https://conda.anaconda.org/conda-forge/{OS_CPU}/repodata.json.bz2"
    noarch_packages = "https://conda.anaconda.org/conda-forge/noarch/repodata.json.bz2"
    retval = {}

    arch = get_repodata(arch_packages)
    for package in arch['packages']:
        if arch['packages'][package]['build'].startswith('py'):
            if not arch['packages'][package]['build'].startswith(PY[-4:]):
                continue

        if arch['packages'][package]['name'] not in retval:
            retval[arch['packages'][package]['name']] = []

        if arch['packages'][package]['version'] not in retval[arch['packages'][package]['name']]:
            retval[arch['packages'][package]['name']].append(arch['packages'][package]['version'])

    noarch = get_repodata(noarch_packages)
    for package in noarch['packages']:
        if noarch['packages'][package]['name'] not in retval:
            retval[noarch['packages'][package]['name']] = []

        if noarch['packages'][package]['version'] not in retval[noarch['packages'][package]['name']]:
            retval[noarch['packages'][package]['name']].append(noarch['packages'][package]['version'])

    return retval


def reduce(packages, designator):
    """ 
    This function will return a list of packages that need to be removed from packages
    because they don't exist on conda-forge for the given designator.

    Parameters
    ----------
    packages : list of packages
    designator 
        str formatted like so :linux-64_py36

    Returns
    -------
    list of packages that do not exist for the given designator.
    """
    retval = []
    available_packages = get_conda_forge_packages(designator)
    for package in packages:
        if not package in available_packages:
            retval.append(package)

    return retval

def run_solver(pkgs, PY, channels=["conda-forge"], solver="mamba"):
    """
    Run conda solver dry run. 

    Parameters
    ----------
    pkgs : list of packages to solve for
    PY : string indicating the python version/implementation to use for solving
        py36 --> python=3.6
        pypy36 --> pypy3.6
    channels : list of channels to use
    solver : the solver to use

    Returns
    -------
    PY_IMP : string representing the python implementation
    data : The solution in (json) dictionary format.
    """
    if solver not in ["conda", "mamba"]:
        raise ValueError("Must use 'conda' or 'mamba' as solver!")

    if PY.startswith("pypy"):
        if not len(PY) == 6:
            raise ValueError(f"'{PY}' should be exactly 6 characters long")
        PY_IMP = f"pypy{PY[4]}.{PY[5]}"
    elif PY.startswith("py"):
        if not len(PY) == 4:
            raise ValueError(f"'{PY}' should be exactly 4 characters long")
        PY_IMP = f"python={PY[2]}.{PY[3]}"
    else:
        raise ValueError(f"'{PY}' should start with 'py' or 'pypy'")

    cmd = [solver, "create", "--name", "test_env", "--dry-run", "--json", "--yes", "--strict-channel-priority", PY_IMP] + pkgs
    for channel in channels:
        cmd.append("--channel")
        cmd.append(channel)

    print("  solving command: '" + " ".join(cmd))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()
    data = {}
    try:
        data = json.loads(stdout)
    except Exception as err:
        print(f"Error: {err}")

    return PY_IMP, data

def write_recipe(designator, primary_packages, environment, build_string=False):
    """
    Run conda solver dry run. 

    Parameters
    ----------
    designator :
        str formatted like so :linux-64_py36
    primary_packages :
        list of package names to solve for
    environment :
        the name of the environment to write the recipe for
    build_string :
        boolean that indicates if the build_string will be written to the recipe.

    Returns
    -------
    /
    """
    OS_CPU, PY = designator.split('_')
    print(f"Solving : {OS_CPU}/{PY}/{environment}")

    print(f"  primary packages : {primary_packages}")

    packages_to_remove = reduce(primary_packages, designator)
    if packages_to_remove:
        print(f"  excluding packages : {packages_to_remove}")
        for package_to_remove in packages_to_remove:
            primary_packages.remove(package_to_remove)

    PY_IMP, data = run_solver(primary_packages, PY)
    if not data:
        return
    packages = {}
    for element in data['actions']['LINK']:
        packages[element['name']] = {"version": element['version'], "build_string": element['build_string']}
    if PY_IMP.startswith("pypy"):
        PYTHON = f"{PY_IMP} ={packages[PY_IMP]['version']}"
        if build_string:
            PYTHON += f" ={packages[PY_IMP]['build_string']}"
        del packages[PY_IMP]  
    else:
        PYTHON = f"python ={packages['python']['version']}"
        if build_string:
            PYTHON += f" ={packages['python']['build_string']}"
        del packages['python']

    secondary_packages = list(packages)
    for primary_package in primary_packages:
        secondary_packages.remove(primary_package)
    print(f"  primary packages : {len(primary_packages)} ")
    print(f"  secondary packages : {len(secondary_packages)}")

    recipe_fpath = RECIPES_ROOT / OS_CPU / PY / environment / "meta.yaml"
    if not recipe_fpath.is_file():
        os.makedirs(recipe_fpath.parent, exist_ok=True)
    print(f"  writing : '{recipe_fpath}'")

    with open(recipe_fpath, 'w') as fh:
        fh.write("#\n# Copyright (c) Semi-ATE\n")
        fh.write("# Distributed under the terms of the MIT License\n")
        fh.write("#\n")
        fh.write(f"# {OS_CPU}/{PY}/{environment}\n")
        fh.write("#\n\n")
        fh.write('{% set version = os.environ.get("MAXICONDA_ENV_RELEASE", "0.0.0") %}\n')
        fh.write("\n")
        fh.write("package:\n")
        fh.write(f"  name: {environment}\n")
        fh.write("  version: {{ version }}\n")
        fh.write("\n")
        fh.write("source:\n") 
        fh.write(f"  path: .\n")
        fh.write("\n")
        fh.write("build:\n")
        fh.write("  number: 0\n")
        fh.write("\n")
        fh.write("requirements:\n")
        fh.write("  build:\n")
        fh.write("    # python\n")
        fh.write(f"    - {PYTHON}\n")
        fh.write("  run:\n")
        fh.write("    # python\n")
        fh.write(f"    - {PYTHON}\n")
        fh.write("\n")
        fh.write(f"    # {len(primary_packages)-1} primary packages :\n")
        for primary_package in sorted(primary_packages):
            fh.write(f"    - {primary_package} ={packages[primary_package]['version']}")
            if build_string:
                fh.write(f" ={packages[primary_package]['build_string']}")
            fh.write("\n")
        fh.write("\n")
        fh.write(f"    # {len(secondary_packages)} secondary packages :\n")
        for secondary_package in sorted(secondary_packages):
            fh.write(f"    - {secondary_package} ={packages[secondary_package]['version']}")
            if build_string:
                fh.write(f" ={packages[secondary_package]['build_string']}")
            fh.write("\n")
        fh.write("about:\n")
        fh.write("  home: https://github.com/Semi-ATE/maxiconda-envs\n")
        fh.write("  license: MIT\n")
        fh.write("  license_file: ../../../../LICENSE\n")
        fh.write(f"  summary: '{environment} meta package'\n")
        fh.write("  dev_url: https://github.com/Semi-ATE/maxiconda-envs\n\n")
        fh.write("extra:\n")
        fh.write("  recipe-maintainers:\n")
        fh.write("    - nerohmot\n")

def main(build_string=False):
    OS_CPU = get_OS_CPU()

    with open(SPECS_FPATH) as fd:
        specs = yaml.load(fd, Loader=yaml.FullLoader)

    archs = specs['matrix'][OS_CPU]
    environments = specs['environments']

    for arch in archs:
        for environment in archs[arch]:
            if environment not in environments:
                print(f"ERROR in 'specs.yaml' : {arch} specifies the {environment} environment, but this is not defined.")
            write_recipe(arch, environments[environment], environment, build_string)

if __name__ == '__main__':
    main(True)
