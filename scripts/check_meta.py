import os
import sys

import requests
import pandas as pd
import openpyxl as xl

from bs4 import BeautifulSoup

class CheckMeta:

    source_name = "meta.xlsx"

    def __init__(self, path=None):
        if path is None:
            path = os.getcwd()
        self.source_path = os.path.join(os.path.abspath(path), self.source_name)
        if not os.path.exists(self.source_path):
            raise Exception(f"couldn't find '{self.source_path}'")
        self.get_conda_forge_versions("spyder")

    def get_conda_forge_versions(self, package):
        def parse(package, filename):
            if package not in filename:
                raise Exception(f"'{package}' not to be found in '{filename}'")
            OS_ARCH, REST = filename.split(f"/{package}-")
            VER, PY = filename.split("-")
            PY = PY.split(".")[0]

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
                    label = elements[14]
                    if label in ['main', 'alpha', 'beta']:
                        package = elements[5]
                        


                        # print(package)


if __name__ == "__main__":
    CheckMeta()

        


