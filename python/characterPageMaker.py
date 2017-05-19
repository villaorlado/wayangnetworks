#!/usr/bin/env python2.7.11
'''
This file reads the excel sheet and generates a static page for each character.
It also generates a list of linked characters.
'''

import re
import xlrd # this is for reading the exisitng file
import matplotlib.pyplot as plt
import seaborn as sns
import json

book = xlrd.open_workbook("../input/charactersExpandedInfo.xlsx") #name of the file to open: charactersExpandedInfo.xlsx
sh = book.sheet_by_index(0)

edgeInfo = xlrd.open_workbook("../output/processedData/adegan_canonicalOnly_edgeInfo.xlsx").sheet_by_index(0)

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
	
	array = []
	data = {}
	matchedNum = 0
	name = sh.cell_value(rowx=num, colx=0)
	
	print "Working on " + name
	
	html = open("htmlfragments/heather.txt").read()
	html += name 
	html += open("htmlfragments/html1.html").read()
	
	html += "<p><h1>" + name + "</h1></p>"
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
	html += makeLakonHtml()
	html += makeHtml("Degree in canoncial only network", 17)
	html += makeHtml("Degree in canonical and disguised network", 18)
	html += makeHtml("Difference in degree ", 19)
	html += "<p><img src=images/" + name + ".png>"
	
	
	html += "<h3>Characters linked to %s</h3><hr>" %name
	
	html += open("htmlfragments/table.html").read()
	
	html += '<script src="http://localhost/datatables/jquery-1.12.4.js"></script>'

	html += '<script src="../js/jquery.dataTables.min.js"></script>'
	html += '<script>$(document).ready(function() {$("#linktable").DataTable({"ajax":"../data/json/%s.txt"});});</script>' % name
	
	html += open("htmlfragments/html2.html").read()

	#text file for network display
	text = ""
	text += "<p><h1>" + name + "</h1></p>"
	text += makeHtml("Alternative names", 7)
	text += makeHtml("Terms of address", 3)
	text += makeHtml("Kalangan", 2)
	text += makeHtml("Description", 6)
	text += makeLakonHtml2()

	#this is for the factions file
	factions += name + "," + sh.cell_value(rowx=num, colx=2) + "," + sh.cell_value(rowx=num, colx=4) + "," + sh.cell_value(rowx=num, colx=1) + "\n"
	
	with open("../html/characterPages/" + name + ".html", "w") as file:
		file.write(html)
	with open("../html/characterPages/" + name + ".txt", "w") as file:
		file.write(text)
	
	'''	
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
	'''
	for x in range(1,edgeInfo.nrows):
		
		if(edgeInfo.cell_value(rowx=x, colx=0) == name):
			array.append([])
			array[matchedNum].append(edgeInfo.cell_value(rowx=x, colx=1))
			array[matchedNum].append(str(int(edgeInfo.cell_value(rowx=x, colx=2))))
			matchedNum += 1
		if(edgeInfo.cell_value(rowx=x, colx=1) == name):
			array.append([])
			array[matchedNum].append(edgeInfo.cell_value(rowx=x, colx=0))
			array[matchedNum].append(str(int(edgeInfo.cell_value(rowx=x, colx=2))))
			matchedNum += 1
			
	data['data'] = array
	json_data = json.dumps(data)
	with open("../html/data/json/%s.txt" % name,"w") as file:
		file.write(json_data)
	
with open("../output/processedData/factions.txt","w") as file:
		file.write(factions)

