#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
import json
import bz2
#import networkx as nx
import yaml
import time
import datetime
import subprocess
import platform
import tempfile
import shutil
import jinja2
import tarfile
import argparse

supported_subdirs = ['linux-64', 'linux-aarch64', 'win-64', 'osx-64', 'osx-arm64']

class Maxiconda:

    def __init__(self, subdir):
        self.saved_subdir = os.getenv('CONDA_SUBDIR', None)
        self.subdir = subdir
        os.environ['CONDA_SUBDIR'] = subdir
        self.build_version = os.getenv('MAXICONDA_ENV_RELEASE', "0.0.0")

        print(f"Initializing : {subdir} (v{self.build_version}) .", end="", flush=True)

        self.repo_root = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
        self.specs_fpath = os.path.join(self.repo_root, "specs.yaml")
        self.recipe_root = os.path.join(self.repo_root, "recipes")
        self.license_fpath = os.path.join(self.repo_root, "LICENSE")
        self.build_root = os.path.join(self.repo_root, "build", self.subdir)

        if os.path.exists(self.build_root):
            shutil.rmtree(self.build_root)
        os.makedirs(self.build_root)

        with open(self.specs_fpath) as fd:
            self.specs = yaml.load(fd, Loader=yaml.FullLoader)
        self.targets = {}
        for target in self.specs['matrix'][self.subdir]:
            subdir, PY = target.split("_")
            if subdir != self.subdir:
                raise ValueError(f"Target '{target}' under 'matrix/{self.subdir}' doesn't start with '{self.subdir}'")
            self.targets[PY] = self.specs['matrix'][self.subdir][target]
        self.environments = {}
        for environment in self.specs['environments']:
            self.environments[environment] = self.specs['environments'][environment]
        print(".", end="", flush=True)

        self.get_conda_packages_from('conda-forge', subdir)
        
        print(" Done.")

    def __del__(self):
        if self.saved_subdir is None:
            del os.environ["CONDA_SUBDIR"]
        else:
            os.environ["CONDA_SUBDIR"] = self.saved_subdir

    def log(self, PY, environment, message, prefix=None):
        if not prefix is None:
            print(f"{prefix}{message}") 
        logfile = os.path.join(self.repo_root, "recipes", self.subdir, PY, environment, "meta.log")
        with open(logfile, "a") as fd:
            fd.write(f"{datetime.datetime.now().strftime('%Y/%m/%d@%H:%M:%S')} >> {message.strip()}\n")

    def get_platform_subdir(self):
        
        if not sys.maxsize > 2**32:
            raise Exception("only 64 bit platforms are supported.")
        
        CPU = platform.machine()
        OS = platform.system()
        if OS == "Linux":
            if CPU in ["AMD64", "x86_64"]:
                retval = "linux-64"
            elif CPU in ["aarch64"]:
                retval = "linux-aarch64"
            else:
                raise Exception(f"'{CPU}' not supported in Linux")
        elif OS == "Windows":
            if CPU in ["AMD64", "x86_64"]:
                retval = "win-64"
            else:
                raise Exception(f"'{CPU}' not supported in Windows")
        elif OS == "Darwin":
            if CPU in ["AMD64", "x86_64"]:
                retval = "osx-64"
            elif CPU in ["aarch64"]:
                retval = "osx-arm64"
            else:
                raise Exception(f"'{CPU}' not supported in MacOS")
        else:
            raise Exception("'{OS}' not supported.")
            
        return retval

    def get_conda_packages_from(self, channel, subdir):
        def get_repo_data(url):
            request = requests.get(url)
            if request.status_code == 200:
                data_json_bz2 = request.content
                data_json = bz2.decompress(data_json_bz2) 
                data = json.loads(data_json)["packages"]
            else:
                data = {}
            return data  

        # self.graph = nx.Graph()
        self.packages = {}
        self.packages['noarch'] = get_repo_data(f"https://conda.anaconda.org/{channel}/noarch/repodata.json.bz2")
        print(".", end="", flush=True)
        self.packages['arch'] = get_repo_data(f"https://conda.anaconda.org/{channel}/{subdir}/repodata.json.bz2")
        print(".", end="", flush=True)
        self.available_packages = []
        for arch in self.packages:
            for package in self.packages[arch]:
                package_name = self.packages[arch][package]['name']
                if package_name not in self.available_packages:
                    self.available_packages.append(package_name)
        print(".", end="", flush=True)

        # self.graph.clear()
        # for arch in self.packages:
        #     for package in self.packages[arch]:
        #         package_name = self.packages[arch][package]["name"]
        #         package_depends = self.packages[arch][package]["depends"]
        #         for dependency in package_depends:
        #             self.graph.add_edge(package_name, dependency)


    def solve(self, PY, environment):

        recipe_path = os.path.join(self.recipe_root, self.subdir, PY, environment)
        if not os.path.isdir(recipe_path):
            os.makedirs(recipe_path)
        recipe_fpath = os.path.join(recipe_path, "meta.yaml")
        made_logging = False
        
        print(f"Solving : {self.subdir}/{PY}/{environment}")
        cleaned_primary_packages = self.environments[environment]
        print(f"  Primary packages : {cleaned_primary_packages}")
        for package in cleaned_primary_packages:
            if package not in self.available_packages:
                cleaned_primary_packages.remove(package)
                self.log(PY, environment, f"Removing primary package : '{package}' (does not exist for {self.subdir}/{PY})", "  ")
                made_logging = True
            if package.startswith("python"):
                cleaned_primary_packages.remove(package)
                self.log(PY, environment, f"Removing primary package : '{package}' (python can't be a primary package)", "  ")
                made_logging = True
            if package.startswith("pypy"):
                cleaned_primary_packages.remove(package)
                self.log(PY, environment, f"Removing primary package : '{package}' (pypy can't be a primary package)", " ")
                made_logging = True
        
        data, feedback = self._run_solver(PY, environment, cleaned_primary_packages)
        
        if feedback is None:
            all_packages = {}
            for element in data['actions']['LINK']:
                all_packages[element['name']] = {"version": element['version'], "build_string": element['build_string']}
            
            PYPY = None
            primary_packages = {}
            secondary_packages = {}
            for package in all_packages:
                if package == "python":
                    PYTHON = f"{package} ={all_packages[package]['version']} ={all_packages[package]['build_string']}"
                elif package.startswith("pypy"):
                    PYPY = f"{package} ={all_packages[package]['version']} ={all_packages[package]['build_string']}"
                elif package in cleaned_primary_packages:
                    primary_packages[package] = all_packages[package]
                else:
                    secondary_packages[package] = all_packages[package]

            print(f"  writing : '{recipe_fpath}' ... ", end="", flush=True)
            
            with open(recipe_fpath, 'w') as fh:
                fh.write("#\n# Copyright (c) Semi-ATE\n")
                fh.write("# Distributed under the terms of the MIT License\n")
                fh.write("#\n")
                fh.write(f"# {self.subdir}/{PY}/{environment}\n")
                fh.write("#\n\n")
                fh.write('{% set version = os.environ.get("MAXICONDA_ENV_RELEASE", "0.0.0") %}\n')
                fh.write("\n")
                fh.write("package:\n")
                fh.write(f"  name: {environment}\n")
                fh.write("  version: {{ version }}\n")
                fh.write("\n")
                fh.write("source:\n") 
                fh.write("  path: .\n")
                fh.write("\n")
                fh.write("build:\n")
                fh.write("  number: 0\n")
                fh.write(f"  string: {PY}\n")
                fh.write("\n")
                fh.write("requirements:\n")
                fh.write("  build:\n")
                fh.write(f"    - {PYTHON}\n")
                fh.write("  run:\n")
                fh.write(f"    - {PYTHON}\n")
                if PYPY:
                    fh.write(f"    - {PYPY}\n")
                fh.write("\n")
                fh.write(f"    # {len(primary_packages)} primary packages :\n")
                for primary_package in sorted(primary_packages):
                    fh.write(f"    - {primary_package} ={primary_packages[primary_package]['version']} ={primary_packages[primary_package]['build_string']}\n")
                fh.write("\n")
                fh.write(f"    # {len(secondary_packages)} secondary packages :\n")
                for secondary_package in sorted(secondary_packages):
                    fh.write(f"    - {secondary_package} ={secondary_packages[secondary_package]['version']} ={secondary_packages[secondary_package]['build_string']}\n")
                fh.write("\nabout:\n")
                fh.write("  home: https://github.com/Semi-ATE/maxiconda-envs\n")
                fh.write("  license: MIT\n")
                fh.write("  license_file: ../../../../LICENSE\n")
                fh.write(f"  summary: '{environment} meta package'\n")
                fh.write("  dev_url: https://github.com/Semi-ATE/maxiconda-envs\n\n")
                fh.write("extra:\n")
                fh.write("  recipe-maintainers:\n")
                fh.write("    - nerohmot\n")
            retval = recipe_fpath
            print("Done.")
        else:
            self.log(PY, environment, feedback)
            made_logging = True
            print(f"  Problem: {feedback}")
            retval = None
        if not made_logging:
            log_fpath = os.path.join(recipe_path, "meta.log")
            if os.path.isfile(log_fpath):
                print(f"  Removed un-necessary loggin : {log_fpath} ... ", end="", flush=True)
                os.remove(log_fpath)
                print("Done.")
                
        return retval

    def _run_solver(self, PY, environment, packages, channels=['conda-forge', 'semi-ate']):
        solver = "mamba"  # conda is much slower
        
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
        
        cmd = [solver, "create", "--name", "test_env", "--dry-run", "--json", "--yes", "--strict-channel-priority", PY_IMP] + packages
        for channel in channels:
            cmd.append("--channel")
            cmd.append(channel)
            
        print(f">>> {' '.join(cmd)}")
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()
        data = {}
        if stdout.decode("utf-8").startswith("Encountered problems while solving"):
            feedback = stdout.decode("utf-8").split(":")[1].strip().replace("-", "").strip()
        else:
            try:
                data = json.loads(stdout)
                feedback = None
            except:
                feedback = stdout.decode("utf-8").replace('\n', '').split('-')[1].strip()
                
        return data, feedback

    def build(self, PY:str, environment:str) -> str:
        print(f"Building : {self.subdir}/{PY}/{environment}")
        
        recipe_fpath = os.path.join(self.recipe_root, self.subdir, PY, environment, "meta.yaml")
        if not os.path.exists(recipe_fpath):
            self.log(PY, environment, f"'{recipe_fpath}' does not exist!", prefix="  Aborting : ")
            return ""

        archive_name = os.path.join(self.build_root, f"{environment}-{self.build_version}-{PY}.tar.bz2") 
        if os.path.exists(archive_name):
            raise Exception(f"'{archive_name}' already exists")
            
        print(f"  Analyzing : '{recipe_fpath}' ... ", end="", flush=True)
        OS, CPU = self.subdir.split("-")
        if CPU == "64":
            CPU = "x86_64"
        NUMPY_VER = "1.21.2"
        PYTHON_VER = None
        DEPENDS = []
        deps = False
        MAINTAINERS = []
        maintainers = False
        with open(recipe_fpath) as fd:
            for line in fd:
                line = line.lstrip()
                if line.startswith("number:"):
                    BUILD_NUMBER = int(line.split(":")[-1].strip())
                    deps = False
                    maintainers = False
                if line.startswith("string:"):
                    BUILD_STRING = line.split(":")[-1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("home:"):
                    HOME_URL = line.split(":")[1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("license:"):
                    LICENSE = line.split(":")[1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("license_file:"):
                    LICENSE_FILE = line.split(":")[1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("summary:"):
                    SUMMARY = line.split(":")[1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("dev_url:"):
                    DEV_URL = line.split(":")[1].strip()
                    deps = False
                    maintainers = False
                if line.startswith("about:"):
                    deps = False
                    maintainers = False
                if line.startswith("run:"):
                    deps = True
                    maintainers = False
                if line.startswith("maintainers:"):
                    deps = False
                    maintainers = True
                if deps: 
                    if line.startswith("- "):
                        DEPENDS.append(line[1:].strip())
                    if line.startswith("- numpy"):
                        NUMPY_VER = line.split("=")[1].strip()
                    if line.startswith("- python"):
                        PYTHON_VER = line.split("=")[1].strip()
                if maintainers:
                    if line.startswitn("- "):
                        MAINTAINERS.append(line[1:].strip())

        index = {
            "arch" : CPU,
            "build" : BUILD_STRING,
            "build_number" : BUILD_NUMBER,
            "depends" : DEPENDS,
            "license": "MIT",
            "name": environment,
            "platform": OS,
            "subdir": self.subdir,
            "timestamp": int(time.time()*1000),
            "version": self.build_version
        }

        about = {
            "channels": [
                "https://conda.anaconda.org/Semi-ATE",
                "https://conda.anaconda.org/conda-forge"
             ],
            "conda_build_version": "3.21.4",
            "conda_private": False,
            "conda_version": "4.10.3",
            "dev_url": DEV_URL,
            "env_vars": {
                "CIO_TEST": "<not set>"
            },
            "extra": {
                "copy_test_source_files": True,
                "final": True,
                "recipe-maintainers": MAINTAINERS,
            },
            "home": HOME_URL,
            "identifiers": [],
            "keywords": [],
            "license": LICENSE,
            "license_file": LICENSE_FILE,
            "root_pkgs": DEPENDS,
            "summary": SUMMARY,
            "tags": []
        }

        PATHS = {
            "paths": [],
            "paths_version": 1
        }

        CONDA_BUILD_CONFIG = f"""c_compiler: gcc
cpu_optimization_target: nocona
cran_mirror: https://cran.r-project.org
cxx_compiler: gxx
extend_keys:
- ignore_version
- pin_run_as_build
- ignore_build_only_deps
- extend_keys
fortran_compiler: gfortran
ignore_build_only_deps:
- numpy
- python
lua: '5'
numpy: {NUMPY_VER}
perl: 5.26.2
pin_run_as_build:
  python:
    min_pin: x.x
    max_pin: x.x
  r-base:
    min_pin: x.x
    max_pin: x.x
python: {PYTHON_VER}
r_base: '3.5'
target_platform: {self.subdir}
"""
        print("Done.")

        print(f"  Writing : '{archive_name}' ... ", end="", flush=True)
        
        tmpdirname = tempfile.mkdtemp(f"{self.subdir}_{PY}", f"{environment}_")
        
        licenses_directory = os.path.join(tmpdirname, "licenses")
        os.makedirs(licenses_directory, mode=0o777, exist_ok=True)
        shutil.copyfile(self.license_fpath, os.path.join(tmpdirname, "licenses", "LICENSE0.txt"))

        recipe_directory = os.path.join(tmpdirname, "recipe")
        os.makedirs(recipe_directory, mode=0o777, exist_ok=True)
        shutil.copyfile(recipe_fpath, os.path.join(tmpdirname, "recipe", "meta.yaml.template"))

        with open(os.path.join(tmpdirname, "recipe", "conda_build_config.yaml"), "w", encoding="utf-8") as file:
            file.write(CONDA_BUILD_CONFIG)

        file_loader = jinja2.FileSystemLoader(os.path.dirname(recipe_fpath))
        env = jinja2.Environment(loader=file_loader)
        template = env.get_template('meta.yaml')
        env.globals.update(os=os)
        output = '\n'.join(template.render().split('\n')[9:])
        LOCATION = os.path.sep.join(os.path.dirname(recipe_fpath).split(os.path.sep)[-5:])
        DATE = datetime.datetime.now().strftime("%A %B %d %Y @ %H:%M:%S")
        with open(os.path.join(tmpdirname, "recipe", "meta.yaml"), "w") as fd:
            fd.write("# This file is created by maxiconda-env/build\n")
            fd.write(f"# meta.yaml template originally from 'https://github.com/Semi-ATE/{LOCATION}'\n")
            fd.write(f"# Created on {DATE}\n")
            fd.write("# ------------------------------------------------\n\n")
            fd.write(output)

        with open(os.path.join(tmpdirname, "about.json"), "w", encoding="utf-8") as file:
            json.dump(about, file, indent=2)
        with open(os.path.join(tmpdirname, "files"), "w"):
            pass
        with open(os.path.join(tmpdirname, "git"), "w"):
            pass
        with open(os.path.join(tmpdirname, "hash_input.json"), "w", encoding="utf-8") as file:
            json.dump({}, file, indent=2)
        with open(os.path.join(tmpdirname, "index.json"), "w", encoding="utf-8") as file:
            json.dump(index, file, indent=2)
        with open(os.path.join(tmpdirname, "paths.json"), "w", encoding="utf-8") as file:
            json.dump(PATHS, file, indent=2)

        with tarfile.open(archive_name, mode='w:bz2') as archive:
            archive.add(tmpdirname, recursive=True, arcname="info")

        shutil.rmtree(tmpdirname)

        print("Done.")

        return archive_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('SUBDIR', type=str, default="*", help=f"The SUBDIR to work with. {supported_subdirs}")
    parser.add_argument('--solve', action='store_true')
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    
    if args.solve == args.build == False:
        print("Error: At least one action needs to be given (--solve --build)")
        parser.print_help()
        sys.exit(1)
    
    if args.SUBDIR not in supported_subdirs:
        print(f"Error: '{args.SUBDIR}' is not supported, should be one of {supported_subdirs}")
        parser.print_help()
        sys.exit(1)
                
    maxiconda = Maxiconda(args.SUBDIR)
    for PY in maxiconda.targets:
        for environment in maxiconda.targets[PY]:
            if args.solve:
                recipe_fpath = maxiconda.solve(PY, environment)
            if args.build:
                archive_fpath = maxiconda.build(PY, environment)
