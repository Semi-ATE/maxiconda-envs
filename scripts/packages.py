import os
import sys

import requests
import pandas as pd

from bs4 import BeautifulSoup


class CondaPackages:

    # fmt: off
    urls = {
        # OS         ARCH       PY 
        ("Windows", "x86_64",  "py36") : "https://docs.anaconda.com/anaconda/packages/py3.6_win-64/",
        ("Windows", "x86_64",  "py37") : "https://docs.anaconda.com/anaconda/packages/py3.7_win-64/",
        ("Windows", "x86_64",  "py38") : "https://docs.anaconda.com/anaconda/packages/py3.8_win-64/",

        ("Linux",   "x86_64",  "py36") : "https://docs.anaconda.com/anaconda/packages/py3.6_linux-64/",
        ("Linux",   "x86_64",  "py37") : "https://docs.anaconda.com/anaconda/packages/py3.7_linux-64/",
        ("Linux",   "x86_64",  "py38") : "https://docs.anaconda.com/anaconda/packages/py3.8_linux-64/",

        ("Linux",   "ppc64le", "py36") : "https://docs.anaconda.com/anaconda/packages/py3.6_linux-ppc64le/",
        ("Linux",   "ppc64le", "py37") : "https://docs.anaconda.com/anaconda/packages/py3.7_linux-ppc64le/",
        ("Linux",   "ppc64le", "py38") : "https://docs.anaconda.com/anaconda/packages/py3.8_linux-ppc64le/",

        ("MacOS",   "x86_64",  "py36") : "https://docs.anaconda.com/anaconda/packages/py3.6_osx-64/",
        ("MacOS",   "x86_64",  "py37") : "https://docs.anaconda.com/anaconda/packages/py3.7_osx-64/",
        ("MacOS",   "x86_64",  "py38") : "https://docs.anaconda.com/anaconda/packages/py3.8_osx-64/",
    }
    # fmt: on

    def __init__(self, verbose=True):
        self.get_conda_forge_versions("autopep8")

        return 
        self.packages = {}
        for config in self.urls:
            pkgs = self.scrape_anaconda(self.urls[config])
            for pkg in pkgs:
                if pkg not in self.packages:
                    self.packages[pkg] = {}
                self.packages[pkg][config] = pkgs[pkg]
        self.to_xlsx("analysis")

    def to_xlsx(self, name):
        df = self.to_pandas()
        writer = pd.ExcelWriter(f"{name}.xlsx")
        df.to_excel(writer, "Anaconda")
        writer.save()
        writer.close()

    def to_pandas(self):
        data = []
        headers = [[], [], []]
        for config in self.urls:
            OS, ARCH, PY = config 
            headers[0].append(OS)
            headers[1].append(ARCH)
            headers[2].append(PY)
        index = []
        for package in self.packages:
            index.append(package)
            row = []
            for config in self.urls:
                if config in self.packages[package]:
                    row.append(self.packages[package][config])
                else:
                    row.append("")
            data.append(row)
        df = pd.DataFrame(data, index=index, columns=headers)
        return df

    def prettyprint(self):
        for package in self.packages:
            print(f"{package}:")
            for config in self.packages[package]:
                print(f"   {config} : {self.packages[package][config]}")

    def scrape_anaconda(self, url):
        retval = {}
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')
        table = soup.find_all('table')[0]
        for row in table.find_all('tr'):
            elements = [element for element in row.text.split("\n") if element != ""]
            if "In Installer" in elements:  # header
                continue
            package = elements[0]
            version = elements[1]
            if row.find_all(class_='fa fa-check'):
                retval[package] = version
        return retval

    def get_conda_forge_versions(self, package):
        retval = {}
        base_url = f"https://anaconda.org/conda-forge/{package}/files"
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, 'lxml')
        if soup.find(class_="pagination"):
            number_of_pages = int(soup.find(class_="pagination").text.split("\n")[2].split("of")[-1].strip())
            for page in range(1, number_of_pages + 1):
                url = f"{base_url}?page={page}"
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'lxml')
                table = soup.find("table", class_="full-width")
                table = table.find("tbody")
                for row in table.find_all("tr"):
                    elements = [element.strip() for element in row.text.split("\n") if element!=""]
                    print(elements)
                    package = elements[5]
                    # print(package)







if __name__ == "__main__":
    conda_packages = CondaPackages()
