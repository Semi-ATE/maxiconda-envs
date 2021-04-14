import openpyxl
import requests
import bz2
import json


def get_conda_forge_packages(OS, CPU, Python):
    platforms = {
        ('Linux', 'x86_64') : 'linux-64', 
        ('Linux', 'aarch64') : 'linux-aarch64',
        ('MacOS', 'x86_64') : 'osx-64',
        ('MacOS', 'aarch64') : 'osx-arm64',
        ('Windows', 'x86_64') : 'win-64',
    }
    if (OS, CPU) not in platforms:
        raise Exception(f"{OS}/{CPU} not supported.")

    arch_packages = f"https://conda.anaconda.org/conda-forge/{platforms[(OS, CPU)]}/repodata.json.bz2"
    noarch_packages = "https://conda.anaconda.org/conda-forge/noarch/repodata.json.bz2"
    retval = {}

    arch_json_bz2 = requests.get(arch_packages).content
    arch_json = bz2.decompress(arch_json_bz2) 
    arch = json.loads(arch_json)
    for package in arch['packages']:
        if arch['packages'][package]['build'].startswith('py'):
            if not arch['packages'][package]['build'].startswith(Python):
                continue
        if arch['packages'][package]['name'] not in retval:
            retval[arch['packages'][package]['name']] = []
        if arch['packages'][package]['version'] not in retval[arch['packages'][package]['name']]:
            retval[arch['packages'][package]['name']].append(arch['packages'][package]['version'])
        
    noarch_json_bz2 = requests.get(noarch_packages).content
    noarch_json = bz2.decompress(noarch_json_bz2) 
    noarch = json.loads(noarch_json)
    for package in arch['packages']:
        if arch['packages'][package]['name'] not in retval:
            retval[arch['packages'][package]['name']] = []
        if arch['packages'][package]['version'] not in retval[arch['packages'][package]['name']]:
            retval[arch['packages'][package]['name']].append(arch['packages'][package]['version'])

    return retval



def envs_from_xlsx(bookname):
    """ This functin returns a dictionary of environments of packages """
    retval = {}
    book = openpyxl.load_workbook(bookname)
    for sheetname in book.sheetnames:
        retval[sheetname] = {}
        sheet = book[sheetname]

        for item in sheet[4]:
            if item.value is None or item.value != "ON":
                continue
            else:
                OS = sheet[f"{item.column_letter}1"].value
                CPU = sheet[f"{item.column_letter}2"].value
                Python = sheet[f"{item.column_letter}3"].value
                column = item.column_letter
                retval[sheetname][(column, OS, CPU, Python)] = {}
        for column, OS, CPU, Python in retval[sheetname]:
            print(f"{OS}-{CPU}-{Python}")
            packages = sheet['A']
            switch = sheet['B']
            versions = sheet[column]
            for row, package in enumerate(packages):
                if switch[row].value is None or switch[row].value.upper() != "ON":
                    continue
                if versions[row].value is None:
                    continue
                else:
                    retval[sheetname][(column, OS, CPU, Python)][package.value] = versions[row].value
    return retval

def check_envs(data):
    """ This function will check if the packages/versions for the given environments exist on conda-forge """
     



if __name__ == '__main__':
    # data = get_conda_forge_packages('Linux', 'aarch64', 'py38')
    # for package in data:
    #     print(f"{package} : {data[package]}")
    data = envs_from_xlsx('maxiconda_envs.xlsx')
    for sheetname in data:
        print(sheetname)
        for column, OS, CPU, Python in data[sheetname]:
            print(f"  {OS}-{CPU}-{Python}")
            for package in data[sheetname][(column, OS, CPU, Python)]:
                print(f"    - {package} {data[sheetname][(column, OS, CPU, Python)][package]} ")
