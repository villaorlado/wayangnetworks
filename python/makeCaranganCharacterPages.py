'''
this script creates an Individual page for each disguised character with reduced information.
'''

import re
import xlrd 
import glob
from xlsxwriter.workbook import Workbook
import xlsxwriter
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json

def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1


characters = xlrd.open_workbook("../input/characters.xlsx").sheet_by_index(1) 
canonicalInfo = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalOnly_nodeInfo.xlsx").sheet_by_index(0) 
disguisedInfo = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalAndDisguised_nodeInfo.xlsx").sheet_by_index(0) 
edgeInfoAmemba = open("../gephi/input/edgeInfo/adegan_canonicalAndDisguised.csv").read().splitlines() #this is the file that Gephi opens

#make histograms
degreeList = []
weightedDegreeList = []
closenessCentralityList = []
betweennessCentralityList = []
eigenvectorCentralityList = []

for num in range(1,disguisedInfo.nrows):	
	if (disguisedInfo.cell_value(rowx=num, colx=col2num("B"))):
		degree = int(disguisedInfo.cell_value(rowx=num, colx=col2num("B")))
		weightedDegree = int(disguisedInfo.cell_value(rowx=num, colx=col2num("C")))
		closenessCentrality = float(disguisedInfo.cell_value(rowx=num, colx=col2num("D")))
		betweennessCentrality = float(disguisedInfo.cell_value(rowx=num, colx=col2num("F")))
		eigenvectorCentrality = float(disguisedInfo.cell_value(rowx=num, colx=col2num("K")))
		degreeList.append(degree)
		weightedDegreeList.append(weightedDegree)
		closenessCentralityList.append(closenessCentrality)
		betweennessCentralityList.append(betweennessCentrality)
		eigenvectorCentralityList.append(eigenvectorCentrality)
		
def findCharacterData(location):
	returnedValue = ""
	for num in range(1,disguisedInfo.nrows):
		if (name == disguisedInfo.cell_value(rowx=num, colx=col2num("A"))):
			returnedValue = disguisedInfo.cell_value(rowx=num, colx=col2num(location))
	return returnedValue

def makeTable(listName,valueName,measurement,location):
	#currently the makeTable function only looks at disguised values
	disguisedValue = findCharacterData(location)
	htmlString = "<tr><td>%s</td><td>%s</td><td><a href=\"histograms/%s_%s.png\"><img src=\"histograms/%s_%s.png\" height=\"100px\"></a></td></tr>" % (measurement,disguisedValue,name,valueName,name,valueName)
	#here we make an image with the histogram for this particular
	
	plt.figure(figsize=(15,3)) 
	n,bins,patches = plt.hist(listName, bins=15, color="blue") 
	plt.title("%s for %s (in red)" %(valueName,name))
	plt.ylabel("Number of instances")
	plt.xlabel(valueName)
	
	binNum = -1
	print valueName
	print bins
	for bin in bins:
		if disguisedValue > bin:
			binNum+=1
		else:
			break
	if binNum ==-1:
		binNum = 0
	
	if binNum == len(patches):
		binNum = binNum-1

	patches[binNum].set_fc('r')
	plt.xticks(bins)
	plt.savefig("../html/characterPages/histograms/%s_%s.png" % (name,valueName))
	plt.close()
	return htmlString

def makeHtml (header,column, linked=False):
	htmlString = ""
	column = col2num(column)
	if (characters.cell_value(rowx=num, colx=column) != ""):
		if (linked):
			htmlString = "<p><b>" + header + "</b>: "
			linkedSet = characters.cell_value(rowx=num, colx=column).split(", ")
			for x in range (0, len(linkedSet)):
				exists = os.path.isfile("../html/characterPages/%s.html" % linkedSet[x])
				if(exists):
					htmlString += "<a href='%s.html'>%s</a>" % (linkedSet[x],linkedSet[x])
				else:
					htmlString += str(linkedSet[x])
				if x < len(linkedSet)-1:
					htmlString += ", "
		else:
			htmlString = "<p><b>" + header + "</b>: " + str(characters.cell_value(rowx=num, colx=column))	
	return htmlString
	
def makeLakonHtml():
	lakonList = characters.cell_value(rowx=num, colx=col2num("D")).split(",")
	lakonArray = []
	htmlString = "<p><b>Found in the follwing lakon (stories)</b>:</p><ol> "
	for lakon in lakonList:
		htmlString += '<li><a href="../lakonPages/%s.html">%s</a></li>' % (lakon,lakon)
	htmlString += "</ol>"
	return htmlString

for num in range (1, characters.nrows):
	
	name = characters.cell_value(rowx=num,colx=0)
	print "Working on " + name
	
	html = open("htmlfragments/heather.txt").read()
	html += name 
	html += open("htmlfragments/html1.html").read()
	
	#HTML Character Page
	html += "<p><h1>" + name + "</h1></p>"
	html += "<div class='well'><i>This is not a real character, but a disguise for another character</i></div>";
	html += makeHtml("Real character", "B",True)
	html += makeHtml("Type", "C")
	html += makeLakonHtml()
	
	html += "<p>&nbsp;<hr><p><h3>Network measurements for %s</h3>" %name
	html += open("htmlfragments/table2.html").read()
	html += makeTable(degreeList,"Degree",'Degree <a href="#" data-toggle="tooltip" title="The amount of connections of the given node."><i class="glyphicon glyphicon-question-sign"></i></a>',"B")
	html += makeTable(weightedDegreeList,"Weigted Degree",'Weighted Degree <a href="#" data-toggle="tooltip" title="The amount of connections a node has, taking into account the weight of those connections"><i class="glyphicon glyphicon-question-sign"></i></a>',"C")
	html += makeTable(closenessCentralityList,"Closeness Centrality",'Closeness Centrality <a href="#" data-toggle="tooltip" title="The average length of the shortest path between the node and all other nodes in the graph"><i class="glyphicon glyphicon-question-sign"></i></a>',"D")
	html += makeTable(betweennessCentralityList,"Betweenness Centrality",'Betweeness Centrality <a href="#" data-toggle="tooltip" title="Inidcates how often a node acts as a bridge along the shortest path between two other nodes"><i class="glyphicon glyphicon-question-sign"></i></a>',"F")
	html += makeTable(eigenvectorCentralityList,"Eigenvector Centrality",'Eigenvector Centrality <a href="#" data-toggle="tooltip" title="A measurement of the influence of the node in the graph, that takes into account how connected it is to higher-degree nodes"><i class="glyphicon glyphicon-question-sign"></i></a>',"K")
	html += open("htmlfragments/table3.html").read()
	html += "<p>&nbsp;<p>&nbsp;<p><h3>Characters in the same adegan as %s</h3><hr>" %name	
	html += open("htmlfragments/table4.html").read()
	
	html += '<script src="../js/jquery.js"></script>'
	html += '<script src="../js/jquery.dataTables.min.js"></script>'
	html += '<script>$(document).ready(function(){'
	html += 'table = $("#linktableDisguised").DataTable({"ajax":"../data/json/%s_disguised.txt","order": [[ 1, "desc" ]]});' % name
	html += "$('#linktableDisguised tbody').on('click', 'tr', function () {"
	html += "\n var data = table.row(this).data();"
	html += "\n window.location = data[0] + '.html';"
	html+= "});"
	html += "$('#linktableDisguised tbody').mouseover(function(){$(this).css('cursor','pointer');});"
	html += "});"
	html += "$(document).ready(function(){"
	html += "$('[data-toggle="  +'"tooltip"]' + "').tooltip();"
	html += '\n });</script>' 
	#ending
	html += open("htmlfragments/html2.html").read()
	
	with open("../html/characterPages/" + name + ".html", "w") as file:
		file.write(html)

	#Linked characters amemba
	array = []
	data = {}
	matchedNum = 0
	
	for edge in edgeInfoAmemba:
		datum = edge.split(",")
		if (datum[0] == name):
			array.append([])
			array[matchedNum].append(datum[1])
			array[matchedNum].append(str(datum[3]))
			matchedNum += 1
			
		if (datum[1] == name):
			array.append([])
			array[matchedNum].append(datum[0])
			array[matchedNum].append(str(datum[3]))
			matchedNum += 1
			
	data['data'] = array
	json_data = json.dumps(data)
	with open("../html/data/json/%s_disguised.txt" % name,"w") as file:
		file.write(json_data)
