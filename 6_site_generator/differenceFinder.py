'''
This file reads the characters.xlsx file and creates a new file which includes lakon information and network measurements
'''

import re
import xlrd 
import glob
from xlsxwriter.workbook import Workbook
import xlsxwriter

#read workbook
book = xlrd.open_workbook("../input/characters.xlsx") #name of the file to open: charactersExpandedInfo.xlsx
sh = book.sheet_by_index(0)

#write workbook
workbook = xlsxwriter.Workbook('../input/characters_withLakonAndQuantitativeData.xlsx')
worksheet = workbook.add_worksheet()

#difference report
diffReport = ""

canonicalOnly_nodeInfo = open("../gephi/output/nodeInfo/adegan_canonicalOnly_nodeInfo.csv").read().splitlines()
canonicalAndDisguised_nodeInfo = open("../gephi/output/nodeInfo/adegan_canonicalAndDisguised_nodeInfo.csv").read().splitlines()

def findDiference(fileName):
	characterStory = []
	characterDictionary = []
	global diffReport
	lines = open("../output/adegan_" + fileName + ".csv").read().splitlines()

	for line in lines:
		character = line.split(",")
		characterStory.append(character[0])
		characterStory.append(character[1])

	characterStory = list(set(characterStory))

	for num in range(1,sh.nrows):
		characterDictionary.append(str(sh.cell_value(rowx=num, colx=0)))
		characterInXlsx = sh.cell_value(rowx=num, colx=0)
		lakonArray = []
		
		for fileItem in glob.glob("../html/lakonPages/*.html"):
			lakonName = re.sub(r'(..\/html\/lakonPages\/|\.html)','',fileItem)
			lakonText = open(fileItem).read()
			lakonText = lakonText.decode('utf-8')
			if characterInXlsx in lakonText:
				lakonArray.append(lakonName)
		
		#add quantitative information to each character row
		characterInfo = []
		for nodeInfo in canonicalOnly_nodeInfo:
			nodeInfo = nodeInfo.split(",")
			if (str(characterInXlsx) == nodeInfo[0]):
				characterInfo = nodeInfo

		characterInfo2 = []
		for nodeInfo in canonicalAndDisguised_nodeInfo:
			nodeInfo = nodeInfo.split(",")
			if (str(characterInXlsx) == nodeInfo[0]):
				characterInfo2 = nodeInfo

		worksheet.write(num, 0, str(characterInXlsx))
		worksheet.write(num, 1, str(lakonArray))
		if (len(characterInfo) > 3):
			worksheet.write(num, 2, str(characterInfo[1]))
		if (len(characterInfo2) > 3):
			worksheet.write(num, 3, str(characterInfo2[1]))
		
	diffReport += "----------------------------------------------------"
	diffReport += "\nDifferences in " + fileName
	diffReport += "\nNames in the excel file but not in the story\n\n"
	diffReport += str(diff(characterDictionary,characterStory))
	diffReport += "\nNames in the story but not in the excel file\n\n"
	diffReport += str(diff(characterStory,characterDictionary))
	diffReport += "\n\n"
	
def diff(first, second):
	second = set(second)
	return [item for item in first if item not in second]

findDiference("canonicalOnly")
#findDifference("canonicalAndDisguised")
#findDifference("canonicalAndDisguisedAndCollective")

with open("../output/difference.txt", "w") as file:
		file.write(diffReport)
		
workbook.close()
