'''
This file reads the characters.xlsx file and creates a new file which includes lakon information and network measurements
For this purpose, the program does as follows:
- It reads the excel file and begins to copy it to the new destination
- It finds all lakons that contain this character
- It adds all network measurement data
- It calculates differences between the measurements
'''

import re
import xlrd 
import glob
from xlsxwriter.workbook import Workbook
import xlsxwriter

def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

#read workbooks
characters = xlrd.open_workbook("../input/characters22.xlsx").sheet_by_index(0) 
canonicalInfo = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalOnly_nodeInfo.xlsx").sheet_by_index(0) 
disguisedInfo = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalAndDisguised_nodeInfo.xlsx").sheet_by_index(0) 

#write workbook
workbook = xlsxwriter.Workbook('../input/characters_withLakonAndQuantitativeData.xlsx')
worksheet = workbook.add_worksheet()

characterLength = characters.ncols
canonicalInfoLength = canonicalInfo.ncols
disguisedInfoLength = disguisedInfo.ncols

#add proper row names
worksheet.write(0, characterLength, "Lakons")
worksheet.write(0, characterLength+1, "Amount of names")

for a in range (1, canonicalInfo.ncols):
	rowname = "Canonical %s" % canonicalInfo.cell_value(rowx=0, colx=a)
	worksheet.write(0, a+characterLength+1, rowname)

for a in range (1, disguisedInfo.ncols):
	rowname = "Disguised %s" % disguisedInfo.cell_value(rowx=0, colx=a)
	worksheet.write(0, a+characterLength+disguisedInfoLength, rowname)

#add information
for x in range (0, characters.nrows):
	
	character = characters.cell_value(rowx=x,colx=0)
	lakonArray = []

	#excel file with character descriptive info
	for y in range (0, characterLength):
		worksheet.write(x, y, characters.cell_value(rowx=x,colx=y).encode("utf-8").decode("utf-8"))
	
	#canoncial info
	for a in range (1, canonicalInfo.nrows):
		characterName = canonicalInfo.cell_value(rowx=a, colx=0)
		if ( character == characterName):
			for a1 in range(1,canonicalInfoLength):
				worksheet.write(x, a1+characterLength+1, canonicalInfo.cell_value(rowx=a, colx=a1))
	
	#disguised info
	for a in range (1, disguisedInfo.nrows):
		characterName = disguisedInfo.cell_value(rowx=a, colx=0)
		if (character == characterName):
			for a1 in range(1,disguisedInfoLength):
				worksheet.write(x, a1+characterLength+disguisedInfoLength, disguisedInfo.cell_value(rowx=a, colx=a1))
	
	#lakon info
	for fileItem in glob.glob("../html/lakonPages/*_characters.txt"):
		lakonName = re.sub(r'(..\/html\/lakonPages\/|\_characters.txt)','',fileItem)
		lakonCharacterList = open(fileItem).read().split(",")
		if (character in lakonCharacterList):
			lakonArray.append(lakonName)
			
	lakonList = (",").join(lakonArray)
		
	#find amount of names
	alternativeNames = characters.cell_value(rowx=x,colx=col2num("H"))
	if (alternativeNames == ""):
		amountOfNames = 1
	elif ("," in alternativeNames):
		amountOfNames = len(alternativeNames.split(","))+1
	else:
		amountOfNames = 2
	
	#print lakon info and amount of names
	if (x>0):
		worksheet.write(x,characterLength,lakonList)
		worksheet.write(x,characterLength+1,amountOfNames)
		
workbook.close()
