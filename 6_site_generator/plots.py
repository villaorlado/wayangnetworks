import matplotlib.pyplot as plt


import re
import xlrd # this is for reading the exisitng file

book = xlrd.open_workbook("../input/charactersExpandedInfo.xlsx") #name of the file to open: charactersExpandedInfo.xlsx
sh = book.sheet_by_index(0)

normal = []
amemba = []

for num in range(1,sh.nrows):
	normal.append(int(sh.cell_value(rowx=num, colx=17)))
	amemba.append(int(sh.cell_value(rowx=num, colx=18)))
	
plt.plot([0, 160], [0, 160], "b--")
plt.plot(normal, amemba, 'ko', alpha=0.4, markersize=7)

plt.ylabel('Canonical only')
plt.xlabel('Disguised')
plt.title('Canonical Only Degree vs. Disguised Degree')
plt.grid(True)

#plt.text(5, 17, 'gato')
plt.show()

#plt.savefig('plt.png')


