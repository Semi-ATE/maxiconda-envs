import pandas as pd
import xlrd

xls = xlrd.open_workbook(r'maxiconda_envs.xlsx', on_demand=True)
print(xls.sheet_names())
