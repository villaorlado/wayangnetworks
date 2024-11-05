'''
This file creates a list for display at the characters.html page
For this we first extract the list of relevant characters and input it into a json file
'''

#import distributions
import re
import xlrd 
import json
import os
import glob
from collections import Counter

#global variables

data = {}
tableArray = []
typeArray =  []
originArray =  []
book = xlrd.open_workbook("../input/characters_withLakonAndQuantitativeData.xlsx") #name of the file to open
sh = book.sheet_by_index(0)

#functions
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1
    
for num in range(1,sh.nrows):
	columnArray = []
	name = sh.cell_value(rowx=num, colx=0)
	characterType= sh.cell_value(rowx=num, colx=col2num("C"))
	origin= sh.cell_value(rowx=num, colx=col2num("E"))
	amountOfnames= sh.cell_value(rowx=num, colx=col2num("AA"))
	weightedDegree= sh.cell_value(rowx=num, colx=col2num("AC"))
	columnArray.append(name)
	columnArray.append(characterType)
	columnArray.append(origin)
	columnArray.append(amountOfnames)
	columnArray.append(weightedDegree)
	tableArray.append(columnArray)

	typeArray.append(characterType)
	originArray.append(origin)

data['data'] = tableArray
json_data = json.dumps(data)

#character Type
typePieDict = Counter(typeArray)
typePieJSON = []
for x,y in typePieDict.items():
	typePieJSON.append({"label":str(x),"value":y})
print typePieJSON

#origin
originPieDict = Counter(originArray)
originPieJSON = []
for x,y in originPieDict.items():
	originPieJSON.append({"label":str(x),"value":y})
print originPieJSON


'''
with open("../html/data/json/allCharacters.txt","w") as file:
		file.write(json_data)
'''
