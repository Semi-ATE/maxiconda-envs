# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

# This script creates the recipes folder like so :
#
# ./
#  └── recipes
#      ├── maxiconda
#      │   ├── meta.yaml
#      |   └── LICENSE
#      └── _spyder_
#          ├── meta.yaml
#          └── LICENSE 
#
# The LICENSE is copied from the repo root and the meta.yaml files 
# are generated from metapackages.xlsx (where they are maintained).
# 

import os
import sys
import shutil

import requests
import pandas as pd

from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))

maxiconda_header = """# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

{% set name = "maxiconda" %}

package:
  name: {{ name|lower }}
  version: {{ environ.get('VERSION', 0.0.0)}}

source:
  git_url: https://github.com/Semi-ATE/maxiconda-meta.git
 
build:
  number: {{ environ.get('BUILD_NUMBER', 0)}}

requirements:
  run:
"""

maxiconda_footer = """about:
  home: https://github.com/Semi-ATE/maxiconda-meta
  license: MIT
  summary: 'anaconda like metapackage based solely on the conda-forge channel'
  dev_url: https://github.com/Semi-ATE/maxiconda-meta
  doc_source_url: https://github.com/Semi-ATE/maxiconda-meta/blob/master/README.md

"""

spyder_header = """# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

{% set name = "_spyder_" %}

package:
  name: {{ name|lower }}
  version: {{ environ.get('VERSION', 0.0.0)}}

source:
  git_url: https://github.com/Semi-ATE/maxiconda-meta.git
 
build:
  number: {{ environ.get('BUILD_NUMBER', 0)}}

requirements:
  run:
"""

spyder_footer= """about:
  home: https://github.com/Semi-ATE/maxiconda-meta
  license: MIT
  summary: 'metapackage to install a full spyder in an application environment'
  dev_url: https://github.com/Semi-ATE/maxiconda-meta
  doc_source_url: https://github.com/Semi-ATE/maxiconda-meta/blob/master/README.md

"""

def conda_forge_check(package, OS=None, ARCH=None, PY=None, version=None, verbose=False):
    """
    This function checks the availability on conda-forge of the supplied package. 
    It returns always a list, and if nothing is found, the list is empty. 
    """
    pass

def generate_maxiconda_metapackage(path):
    pass

def generate_spyder_metapackage(path):
    pass

def generate_recipes_structure():
    recipes_root = os.path.join(here, "recipes")
    if os.path.exists(recipes_root):
        shutil.rmtree(recipes_root)
    os.mkdir(recipes_root)

    maxiconda_recipe_root = os.path.join(recipes_root, "maxiconda")
    os.mkdir(maxiconda_recipe_root)
    shutil.copyfile(os.path.join(here, "LICENSE"), os.path.join(maxiconda_recipe_root, "LICENSE"))
    generate_maxiconda_metapackage(maxiconda_recipe_root)

    spyder_recipe_root = os.path.join(recipes_root, "_spyder_")
    os.mkdir(spyder_recipe_root)
    shutil.copyfile(os.path.join(here, "LICENSE"), os.path.join(spyder_recipe_root, "LICENSE"))
    generate_spyder_metapackage(spyder_recipe_root)

if __name__ == "__main__":
    conda_forge_check("starz")
