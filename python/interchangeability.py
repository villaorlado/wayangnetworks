'''
produce a list of characters, indicating their degree and whether they can be changed or not
'''

import xlrd
from xlsxwriter.workbook import Workbook
import xlsxwriter

#functions
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

#data

book = xlrd.open_workbook("../input/characters_withLakonAndQuantitativeData.xlsx")
data = book.sheet_by_index(0)



for a in range(1,data.nrows):	
	degree = data.cell_value(rowx=a, colx=col2num("B"))
	print degree
