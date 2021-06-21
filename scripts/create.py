#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This will create meta.yaml recipes for each spec found.
"""

import os
from pathlib import Path
from jinja2 import Template

# Constants
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SOLUTIONS_PATH = REPO_ROOT / "specs/solutions"
TEMPLATE = """# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

# /{{ data["OS"] }}/{{ data["PY_VERSION"] }}/{{ data["environment"] }}

{% raw -%}
{% set version = os.environ.get("MAXICONDA_ENV_RELEASE", "") %}
{%- endraw %}

package:
  name: {{ data["environment"] }}
  version: {% raw %}{{ version }}{% endraw %}

source: 
  path: .

build:
  number: 0  # fixed to 0

requirements:
  build:
    # python
    - {{ data["python"] }}

  run:
    # python
    - python

    # primary packages:
    {% for item in data["primary"] -%}
    - {{ item }}
    {% endfor %}
    # secondary packages:
    {% for item in data["secondary"] -%}
    - {{ item }}
    {% endfor %}
about:
  home: https://github.com/Semi-ATE/maxiconda-envs
  license: MIT
  license_file: ../../../../LICENSE
  summary: '{{ data["environment"] }} meta package'
  dev_url: https://github.com/Semi-ATE/maxiconda-envs/blob/main/specs/primary_packages.yaml
extra:
  recipe-maintainers:
    - nerohmot

"""


def parse_file(fpath):
    # Only build spyder and maxiconda packages
    if fpath.endswith(("_spyder_.txt", "maxiconda.txt")):
        with open(fpath) as fh:
            content = fh.read()

        data = {}
        key = None
        environment = None
        python = None
        primary = []
        secondary = []
        for line in content.split("\n"):
            if line:
                if line.startswith("#"):
                    if key is None:
                        key = "python"
                        environment = line.replace("#", "").strip()
                    elif "primary" in line:
                        key = "primary"
                    elif "secondary" in line:
                        key = "secondary"

                    continue

                if key == "python":
                    python = line.replace(" ", "").strip().split("=")
                    python = " =".join(python[:2])
                elif key == "primary":
                    clean_line = line.replace(" ", "").strip().split("=")
                    primary.append(" =".join(clean_line[:2]))
                elif key == "secondary":
                    clean_line = line.replace(" ", "").strip().split("=")
                    secondary.append(" =".join(clean_line[:2]))
                else:
                    pass

        PY, OS, ENV = environment.split("/")
        data["environment"] = ENV
        data["PY_VERSION"] = PY
        data["OS"] = OS
        data["primary"] = primary
        data["secondary"] = secondary
        data["python"] = python
        data["path"] = fpath

        new_path = fpath.replace("/specs/solutions/", "/recipes/")
        new_path = new_path.replace(".txt", "")
        meta_path = Path(new_path) / "meta.yaml"
        data["meta_path"] = meta_path
        return data


def create_meta_file(data):
    meta_path = data["meta_path"]
    os.makedirs(Path(meta_path).parent, exist_ok=True)
    template = Template(TEMPLATE)
    text = template.render(data=data)
    with open(meta_path, "w") as fh:
        fh.write(text)


def create_meta_files():
    for os_path in SOLUTIONS_PATH.iterdir():
        if os_path.is_dir():
            for py_path in os_path.iterdir():
                if py_path.is_dir():
                    for txt_file in py_path.iterdir():
                        if txt_file.is_file() and str(txt_file).endswith(".txt"):
                            data = parse_file(str(txt_file))
                            if data:
                                create_meta_file(data)


if __name__ == '__main__':
    create_meta_files()
