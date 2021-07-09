#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
import argparse
import sys
import os
import platform
import subprocess
from pathlib import Path

# Constants
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
RECIPES_ROOT  = REPO_ROOT / "recipes"

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

def upload(package_path):
    """
    This function uploads the package pointed to by package_path to anaconda.org/Semi-ATE
    It uses the CONDA_UPLOAD_TOKEN environment variable to do so.

    Parameters
    ----------
    package_path : str that points to a valid meta.yaml file under recipes.

    Returns
    -------
    bool (True for success, False for failure)
    """

    if not os.path.exists(package_path):
        raise Exception(f"'{package_path}' does not exist!")

    package_path = os.path.normpath(package_path)
    package_file = package_path.split(os.sep)[-1]
    environment = package_file.split("-")[0]
    package_version = package_file.split("-")[1]
    PY = package_file.split("-")[2].split(".")[0]
    OS_CPU = package_path.split(os.sep)[-2] 

    print(f"Uploading : {OS_CPU}/{PY}/{environment}")
    #TODO: maybe only run if the package_version != "0.0.0" ?!?
    retval = True
    cmd = ["anaconda", "-t", os.environ.get("CONDA_UPLOAD_TOKEN", "Woops"), "upload", "-u", "semi-ate", package_path, "--force"]
    print(f"  running '{' '.join(cmd)}' ... ", end="", flush=True)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, output = p.communicate()
    output_lines = output.decode("utf-8").split("\n")  
    for output_line in output_lines:
        if "[ERROR]" in output_line:
            retval = False
    if retval == False:
        print("Failure.")
        for output_line in output_lines:
            print(f"  {output_line}")
    else:
        print("Success.")
    return retval

def build(env_meta_path):

    if not os.path.exists(env_meta_path):
        raise Exception(f"'{env_meta_path}' does not exist!")

    env_meta_root = os.path.dirname(env_meta_path)
    if not os.path.exists(env_meta_root):
        raise Exception(f"'{env_meta_root}' does not exist!")

    env_meta_path = os.path.normpath(env_meta_path)
    environment = env_meta_path.split(os.sep)[-2]
    PY = env_meta_path.split(os.sep)[-3]
    OS_CPU = env_meta_path.split(os.sep)[-4]

    print(f"Building : {OS_CPU}/{PY}/{environment}")

    NUMPY_VER = None
    PYTHON_VER = None
    with open(env_meta_path) as fd:
        for line in fd:
            if "- numpy " in line:
                NUMPY_VER = line.split("=")[1].strip()
            if "- python " in line and PYTHON_VER is None:
                PYTHON_VER = line.split("=")[1].strip()

    cmd = ["conda-build", ".", "--python",  PYTHON_VER]
    if NUMPY_VER:
        cmd.extend(["--numpy", NUMPY_VER])
    cmd.extend(["-c", "conda-forge"])

    print(f"  running '{' '.join(cmd)}' ... ", end="", flush=True)
    p = subprocess.Popen(cmd, cwd=env_meta_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    retval = None
    if b"anaconda upload" in output:
        print("success.")
        retval = output.split(b"anaconda upload")[1].split(b"\n")[1]
        retval = str(retval).replace("b'", "").replace("'", "").strip()
        print(f"  package location = '{retval}'")
    else:
        print("Failure.")
        output_lines = output.decode("utf-8").split("\n")
        error_lines = error.decode("utf-8").split("\n")
        for line in output_lines:
            print(line)
        for line in error_lines:
            print(line)
    return retval

def is_uploadable(package_path):
    if not isinstance(package_path, str):
        return False
    package_path = os.path.normpath(package_path)
    if not os.path.exists(package_path):
        return False
    retval = os.path.basename(package_path)
    retval = retval.split("-")[1]
    return not (retval == "0.0.0")

def main(testing=True):

    OS_CPU_recipes = RECIPES_ROOT / get_OS_CPU() 

    for root, dirs, files in os.walk(str(OS_CPU_recipes)):
        for file in files:
            if file == "meta.yaml":
                recipe_path = os.path.join(root, file)
                package = build(recipe_path)
                if is_uploadable(package):
                    if not testing:
                        upload(package)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    main(args.test)
