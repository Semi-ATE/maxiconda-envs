#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
import sys
import os
import platform
import subprocess
from pathlib import Path
from jinja2 import Template
from yaml import safe_load

# Constants
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
RECIPES_PATH = REPO_ROOT / "recipes"
UPLOAD_SCRIPT = REPO_ROOT / "scripts" / "upload.sh"


def get_env():
    os_table = {
        "Darwin": "osx",
        "Linux": "linux",
        "Windows": "win",
    }
    return os_table.get(platform.system())


def get_py_numpy(meta_fpath):
    with open(meta_fpath, "r") as fh:
        data = fh.read()
    
    py_ver = None
    numpy_ver = None
    template = Template(data)
    data = safe_load(template.render(os=os))
    for package in data["requirements"]["build"]:
        if package.startswith("python ="):
            py_ver = package.split(" =")[-1]

    for package in data["requirements"]["run"]:
        if package.startswith("numpy ="):
            numpy_ver = package.split(" =")[-1]

    name = data["package"]["name"]
    version = data["package"]["version"]
    build = data["build"]["number"]
    return name, version, build, py_ver, numpy_ver


def upload(version, build, environment, py_ver):
    py_ver = "".join(py_ver.split(".")[:2])
    path = Path(sys.prefix) / "conda-bld" / f"{get_env()}-64" / f"{environment}-{version}-py{py_ver}_{build}.tar.bz2"
    cmd = ["anaconda", "-t", "$CONDA_UPLOAD_TOKEN", "upload", "-u", "semi-ate", str(path), "--force"]

    print("\n\nUploading packages:\n\n")
    print(f"{cmd}\n\n")

    cmd[2] = os.environ.get("CONDA_UPLOAD_TOKEN")
    if path.is_file():
        p = subprocess.Popen(cmd)
        p.communicate()


def purge():
    print("\n\nPurging packages:\n\n")
    cmd = ["conda", "build", "purge-all"]
    p = subprocess.Popen(cmd)
    p.communicate()


def build_package(meta_fpath, py_ver, numpy_ver):
    cmd = ["conda-build", ".", "--python",  py_ver]
    if numpy_ver:
        cmd.extend(["--numpy", numpy_ver])

    cmd.extend(["-c", "conda-forge"])
    path = meta_fpath.parent
    print("\n\nBuilding packages:\n\n")
    print(f"Working dir: {path}")
    print(" ".join(cmd))
    print("\n\n")
    p = subprocess.Popen(cmd, cwd=path)
    p.communicate()


def main(python_version, py_implementation):
    recipes_path = RECIPES_PATH / f"{get_env()}-64/{py_implementation}{python_version.replace('.', '')}/"
    for environment in recipes_path.iterdir():
        if environment.is_dir():
            for meta_path in environment.iterdir():
                if str(meta_path).endswith(".yaml"):
                    environment_name, version, build, py_ver, numpy_ver = get_py_numpy(meta_path)
                    # purge()
                    build_package(meta_path, py_ver, numpy_ver)
                    upload(version, build, environment_name, py_ver)


if __name__ == '__main__':
    for python_version in ["3.6", "3.7", "3.8", "3.9"]:
        for py_implementation in ["py"]:
            main(
                python_version,
                py_implementation,
            )
