#!/usr/bin/env python2.7.11
'''
This file reads the excel sheet and generates a static page for each character.
'''

import re
import xlrd # this is for reading the exisitng file
import matplotlib.pyplot as plt
import seaborn as sns

book = xlrd.open_workbook("../input/charactersExpandedInfo.xlsx") #name of the file to open: charactersExpandedInfo.xlsx
sh = book.sheet_by_index(0)

def makeHtml (header,column):
	htmlString = ""
	if (sh.cell_value(rowx=num, colx=column) != ""):
		htmlString = "<p><b>" + header + "</b>: " + str(sh.cell_value(rowx=num, colx=column))	
	return htmlString

def makeLakonHtml():
	lakonList = re.sub(r'([\w \(\) ,]*)',r'<a href="../lakonPages/\1.html">\1</a>',sh.cell_value(rowx=num, colx=15))
	htmlString = "<p><b>Found in the follwing lakon </b>: " + lakonList
	return htmlString
	
def makeLakonHtml2():
	lakonList = re.sub(r'([\w \(\) ,]*)',r'<a target="_blank" href="../html/lakonPages/\1.html">\1</a>',sh.cell_value(rowx=num, colx=15))
	htmlString = "<p><b>Found in the follwing lakon </b>: " + lakonList
	return htmlString

factions = ""
origin = ""
normal = []
amemba = []

#this populates the arrays we need for the scatterplots
for num in range(1,sh.nrows):
	normal.append(int(sh.cell_value(rowx=num, colx=17)))
	amemba.append(int(sh.cell_value(rowx=num, colx=18)))

for num in range(1,sh.nrows):
	
	name = sh.cell_value(rowx=num, colx=0)
	html = "<html><head><title>" + name + "</title></head>"
	html += "<br/><h1>" + name + "</h1></p>"
	html += makeHtml("Alternative names", 7)
	html += makeHtml("Terms of address", 3)
	html += makeHtml("Kalangan", 2)
	html += makeHtml("Description", 6)
	#html += makeHtml("Allegiance", 1)
	html += makeHtml("Mother", 9)
	html += makeHtml("Father", 10)
	html += makeHtml("Siblings", 11)
	html += makeHtml("Spouses", 12)
	html += makeHtml("Ruler of", 14)
	
	#text file for network display
	text = ""
	text += html
	text += makeLakonHtml2()
	html += makeLakonHtml()
	html += makeHtml("Degree in canoncial only network", 17)
	html += makeHtml("Degree in canonical and disguised network", 18)
	html += makeHtml("Difference in degree ", 19)
	html += "<p><img src=images/" + name + ".png>"
	
	#this is for the factions file
	factions += name + "," + sh.cell_value(rowx=num, colx=2) + "," + sh.cell_value(rowx=num, colx=4) + "," + sh.cell_value(rowx=num, colx=1) + "\n"
	
	with open("../html/characterPages/" + name + ".html", "w") as file:
		file.write(html)
	with open("../html/characterPages/" + name + ".txt", "w") as file:
		file.write(text)
		
	#making scatterplot image
	plt.plot([0, 160], [0, 160], "b--")
	plt.plot(normal, amemba, 'ko', alpha=0.4, markersize=7)

	plt.ylabel('Canonical only')
	plt.xlabel('Disguised')
	plt.title(name + ' Canonical Only Degree vs. Disguised Degree')
	plt.grid(True)

	xval = int(sh.cell_value(rowx=num, colx=17))
	yval = int(sh.cell_value(rowx=num, colx=18))
	plt.plot(xval,yval, 'bo', markersize=8)
	plt.annotate(name, xy=(xval, yval), xytext=(120, 40),
            arrowprops=dict(facecolor='blue', shrink=0.05),
            )
	#plt.text(10, 140, name, color="blue")
	#plt.show()

	plt.savefig("../html/characterPages/images/" + name + ".png")
	plt.clf()	
	
	sns.distplot(normal, hist=False, rug=False);
	plt.savefig("../html/characterPages/images/" + name + "normal.png")

with open("../output/processedData/factions.txt","w") as file:
		file.write(factions)
