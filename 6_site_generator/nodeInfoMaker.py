#!/usr/bin/env python2.7.11
'''
This file extracts information relevant for the gephi visualization on the nodes
'''

#imports
import re
import xlrd 

#global vars
book = xlrd.open_workbook("../input/characters22.xlsx") 
sh = book.sheet_by_index(0)
sh2 = book.sheet_by_index(1)

#functions
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

#Canonical Only
nodeInfo = "Label,ID,origin,type"
for num in range(1,sh.nrows):
	nodeInfo += "\n" + sh.cell_value(rowx=num, colx=col2num("A")) + "," + sh.cell_value(rowx=num, colx=col2num("A")) + "," + sh.cell_value(rowx=num, colx=col2num("E")) + "," + sh.cell_value(rowx=num, colx=col2num("C")) 
		
with open("../gephi/input/nodeInfo/nodeInfo_canonicalOnly.csv","w") as file:
		file.write(nodeInfo)

#Canonical And Disguised
nodeInfo = "Label,ID,type"
for num in range(1,sh.nrows):
	nodeInfo += "\n" + sh.cell_value(rowx=num, colx=col2num("A")) + "," + sh.cell_value(rowx=num, colx=col2num("A")) + ",canonical"
	
for num in range(1,sh2.nrows):
	if ("#" not in sh2.cell_value(rowx=num, colx=col2num("A"))):
		nodeInfo += "\n" + sh2.cell_value(rowx=num, colx=col2num("A")) + "," + sh2.cell_value(rowx=num, colx=col2num("A")) + ",disguised"
		
with open("../gephi/input/nodeInfo/nodeInfo_canonicalAndDisguised.csv","w") as file:
		file.write(nodeInfo)
