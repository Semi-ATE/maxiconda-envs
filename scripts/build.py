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

    cmd = ["anaconda", "-t", os.environ.get("CONDA_UPLOAD_TOKEN", "Woops"), "upload", "-u", "semi-ate", package_path, "--force"]
    print(f"'{' '.join(cmd)}'")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    error_lines = error.decode("utf-8").split("\n")    
    #TODO: add the return value based on the error_lines
    print(error_lines)


def build(env_meta_path):

    if not os.path.exists(env_meta_path):
        raise Exception(f"'{env_meta_path}' does not exist!")

    env_meta_root = os.path.dirname(env_meta_path)
    if not os.path.exists(env_meta_root):
        raise Exception(f"'{env_meta_root}' does not exist!")

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
    p = subprocess.Popen(cmd, cwd=env_meta_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    output_lines = output.decode("utf-8").split("\n")

    for i in range(len(output_lines)):
        if output_lines[i].startswith("anaconda upload"):
            break
    if os.path.exists(output_lines[i+1].strip()):
        return output_lines[i+1].strip()
    else:
        return None

def main(and_upload=False):

    OS_CPU_recipes = RECIPES_ROOT / get_OS_CPU() 

    for root, dirs, files in os.walk(str(OS_CPU_recipes)):
        for file in files:
            if file == "meta.yaml":
                recipe_path = os.path.join(root, file)
                print(f"building : '{recipe_path}' ... ", end="", flush=True)
                package = build(recipe_path)
                if not package is None:
                    print(f"Done. ({package})")
                    if and_upload:
                        print(f"uploading : ", end="", flush=True)
                        upload(package)
                else:
                    print("Failed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--and-upload', action='store_true')
    args = parser.parse_args()
    main(args.and_upload)
