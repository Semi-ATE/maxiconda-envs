# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

#
# This little script will take the list of the packages currently included in the 
# anaconda installers and weed out the packages that are not available on conda-forge
# for the following operating systems:
#   - linux-64
#   - linux-ppc64le
#   - linux-aarch64
#   - osx-64
#   - osx-arm64
#   - win-64'
# thus removing win-32, and adding linux-aarch64 and osx-arm64 😍

import os
import sys

import requests

from bs4 import BeautifulSoup








def collect_anaconda_packages(verbose=True):
    def scrape_anaconda(url):
        retval = []
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')
        table = soup.find_all('table')[0]
        for row in table.find_all('tr'):
            package = row.text.split('\n')[1].strip()
            if row.find_all(class_='fa fa-check'):
                retval.append(package)
            else:
                retval.append('')
        return retval

    urls = {
        "Windows_x86_64_py36" : "https://docs.anaconda.com/anaconda/packages/py3.6_win-64/",
        "Windows_x86_64_py37" : "https://docs.anaconda.com/anaconda/packages/py3.7_win-64/",
        "Windows_x86_64_py38" : "https://docs.anaconda.com/anaconda/packages/py3.8_win-64/",

        "Linux_x86_64_py36" : "https://docs.anaconda.com/anaconda/packages/py3.6_linux-64/",
        "Linux_x86_64_py37" : "https://docs.anaconda.com/anaconda/packages/py3.7_linux-64/",
        "Linux_x86_64_py38" : "https://docs.anaconda.com/anaconda/packages/py3.8_linux-64/",

        "Linux_ppc64le_py36" : "https://docs.anaconda.com/anaconda/packages/py3.6_linux-ppc64le/",
        "Linux_ppc64le_py37" : "https://docs.anaconda.com/anaconda/packages/py3.7_linux-ppc64le/",
        "Linux_ppc64le_py38" : "https://docs.anaconda.com/anaconda/packages/py3.8_linux-ppc64le/",

        "MacOS_x86_64_py36" : "https://docs.anaconda.com/anaconda/packages/py3.6_osx-64/",
        "MacOS_x86_64_py37" : "https://docs.anaconda.com/anaconda/packages/py3.7_osx-64/",
        "MacOS_x86_64_py38" : "https://docs.anaconda.com/anaconda/packages/py3.8_osx-64/",
    }

    retval = {}
    for url in urls:
        if verbose:
            print(f"{url} ... ", end="")
        url_packages = scrape_anaconda(urls[url])
        url_installer_packages = [pkg for pkg in url_packages if pkg != '']       
        if verbose:
            print(f"{len(url_installer_packages)}/{len(url_packages)-1}")
        for package in url_installer_packages:
            if package not in retval:
                retval[package] = ""
    return retval


def conda_forge_support(packages, verbose=True):
    def scrape_conda_forge(package):
        retval = []
        page = requests.get(f"https://anaconda.org/conda-forge/{package}")
        soup = BeautifulSoup(page.content, 'lxml')
        if not soup.find('input', id="username"):
            support = soup.find('ul', class_='list-inline no-bullet')
            for entry in support.find_all('li'):
                arch = entry.text.strip().split()[0]
                retval.append(arch)
        return sorted(retval)

    retval = {}
    for package in packages:
        if verbose:
            print(f"{package} ... ", end="")
        retval[package] = scrape_conda_forge(package)
        if verbose:
            print(retval[package])
    return retval

def write_packages_txt(packages):
    def is_interesting(catalog, interest):
        if 'noarch' in catalog:
            return True
        for item in catalog:
            if item in interest:
                return True
        return False

    tags_of_interest = ['linux-64', 'linux-ppc64le', 'linux-aarch64', 'osx-64', 'osx-arm64', 'win-64']
    header = """# Copyright (c) Semi-ATE
# Distributed under the terms of the MIT License

#
# This file lists the packages included in maxiconda, and the
# OS/Architecture(s) that are supported.
#
# The available OS/Architectures are:
#    linux-64
#    linux-ppc64le
#    linux-aarch64
#    osx-64
#    osx-arm64
#    win-64
#

maxiconda_packages = {
"""
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "packages.txt")
    if os.path.exists(target):
        response = input("overwrite 'packages.txt' ? [Y/n] > ")
        if response.upper().startswith('Y'):
            os.remove(target)
        else:
            return
    with open(target, 'w') as fd:
        fd.write(header)
        for package in packages:
            if is_interesting(packages[package], tags_of_interest):
                fd.write(f'    "{package}" : ["')
                if 'noarch' in packages[package]:
                    fd.write(", ".join(tags_of_interest))
                else:
                    supported_tags = []
                    for tag in tags_of_interest:
                        if tag in packages[package]:
                            supported_tags.append(tag)
                    fd.write('", "'.join(supported_tags))
                fd.write('"],\n')
        fd.write("}")

if __name__ == "__main__":
    packages = collect_anaconda_packages()
    print(f"\n➜ {len(packages)} distinct installer packages :\n")
    packages = conda_forge_support(packages)
    write_packages_txt(packages)
