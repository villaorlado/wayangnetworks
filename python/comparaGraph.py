import numpy as np
import matplotlib.pyplot as plt
import xlrd 
import seaborn
import matplotlib.patches as mpatches

def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

book = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalOnly_completeInfo.xlsx") #name of the file to open
java = book.sheet_by_index(3)
india = book.sheet_by_index(2)

javaDegree = []
javaWeight = []
punoDegree = []
punoWeight = []
indiaDegree = []
indiaWeight = []

for num in range(5,71):
	javaDegree.append(java.cell_value(rowx=num, colx=col2num("D")))
	javaWeight.append(java.cell_value(rowx=num, colx=col2num("E")))
	
for num in range(1,4):
	punoDegree.append(java.cell_value(rowx=num, colx=col2num("D")))
	punoWeight.append(java.cell_value(rowx=num, colx=col2num("E")))
	
for num in range(1,78):
	indiaDegree.append(india.cell_value(rowx=num, colx=col2num("D")))
	indiaWeight.append(india.cell_value(rowx=num, colx=col2num("E")))
	
plt.scatter(javaDegree,javaWeight, color="blue")
plt.scatter(indiaDegree,indiaWeight, color="red")
plt.scatter(punoDegree,punoWeight, color="green")
plt.ylabel("Weighted Degree")
plt.xlabel("Topological Degree")

red_patch = mpatches.Patch(color='red', label='India')
blue_patch = mpatches.Patch(color='blue', label='Java')
green_patch = mpatches.Patch(color='green', label='Punokawan')
plt.legend(handles=[red_patch,blue_patch,green_patch], loc=2)
plt.savefig("../input/JavaAndIndia.png",bbox_inches='tight')
plt.show()
