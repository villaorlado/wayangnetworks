#this file creates lists for the future use of histograms

import xlrd 
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

book = xlrd.open_workbook("../input/characters_withLakonAndQuantitativeData.xlsx") 
sh = book.sheet_by_index(0)
degreeList = []
weightedDegreeList = []
closenessCentralityList = []
betweennessCentralityList = []
eigenvectorCentralityList = []

for num in range(1,sh.nrows):	
	if (sh.cell_value(rowx=num, colx=col2num("AK"))):
		degree = int(sh.cell_value(rowx=num, colx=col2num("AK")))
		weightedDegree = int(sh.cell_value(rowx=num, colx=col2num("AL")))
		closenessCentrality = int(sh.cell_value(rowx=num, colx=col2num("AM")))
		betweennessCentrality = int(sh.cell_value(rowx=num, colx=col2num("AO")))
		eigenvectorCentrality = int(sh.cell_value(rowx=num, colx=col2num("AT")))
		degreeList.append(degree)
		weightedDegreeList.append(weightedDegree)
		closenessCentralityList.append(closenessCentrality)
		betweennessCentralityList.append(betweennessCentrality)
		eigenvectorCentralityList.append(eigenvectorCentrality)
