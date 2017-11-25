'''
produce a list of characters, indicating their degree and whether they can be changed or not
'''

import xlrd
from xlsxwriter.workbook import Workbook
import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn

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
book2 = xlrd.open_workbook("../html/comparisons/data/fotoInfo_Hariyanto_permissibleChanges.xlsx")
changes = book2.sheet_by_index(0)

#write book
workbook = xlsxwriter.Workbook('../input/interchangeability.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "name")
worksheet.write(0, 1, "degree")
worksheet.write(0, 2, "weighted degree")
worksheet.write(0, 3, "changeability")

#variables
bisaDegree = []
tidakDegree = []
bisaWeight = []
tidakWeight = []

#find information
counter = 1;
for a in range(1,data.nrows):	
	name = data.cell_value(rowx=a, colx=col2num("A"))
	degree = data.cell_value(rowx=a, colx=col2num("AB"))
	wtd_degree = data.cell_value(rowx=a, colx=col2num("AK"))
	
	for b in range(1,changes.nrows):
		name2 = changes.cell_value(rowx=b, colx=col2num("A"))
		bisa = changes.cell_value(rowx=b, colx=col2num("C"))
		if (name == name2  and degree):
			if ("tidak" in bisa):
				#tidak bisa
				bisa = 0
				tidakDegree.append(degree)
				tidakWeight.append(wtd_degree)
			else:
				#bisa 
				bisa = 1
				bisaDegree.append(degree)
				bisaWeight.append(wtd_degree)
			
			worksheet.write(counter,0,name)
			worksheet.write(counter,1,degree)
			worksheet.write(counter,2,wtd_degree)
			worksheet.write(counter,3,bisa)
			counter +=1
			print name, degree, bisa

#make visualization
plt.scatter(bisaDegree,bisaWeight, color="blue")
plt.scatter(tidakDegree,tidakWeight, color="red")
plt.xlabel("Weighted Degree")
plt.ylabel("Eigenvector Centrality")
red_patch = mpatches.Patch(color='red', label='Cannot be changed')
blue_patch = mpatches.Patch(color='blue', label='Can be changed')
plt.legend(handles=[red_patch,blue_patch],loc=2,shadow=False, fancybox=True)

plt.savefig("../input/interchangeability.png",bbox_inches='tight')
plt.show()
workbook.close()
