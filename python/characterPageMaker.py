#!/usr/bin/env python2.7.11
'''
This file reads the excel sheet and generates a static page for each character.
It also generates a list of linked characters.
The default settings only create an edgeList file for the canonical only characters
'''

#imports
import characterInfoExpander
#import distributions
import re
import xlrd 
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import subprocess

#global vars
book = xlrd.open_workbook("../input/characters_withLakonAndQuantitativeData.xlsx") #name of the file to open
sh = book.sheet_by_index(0)
edgeInfoCanonical = open("../gephi/input/edgeInfo/adegan_canonicalOnly.csv").read().splitlines() 
edgeInfoAmemba = open("../gephi/input/edgeInfo/adegan_canonicalAndDisguised.csv").read().splitlines() #this is the file that Gephi opens
disguisedInfo = xlrd.open_workbook("../gephi/output/nodeInfo/adegan_canonicalAndDisguised_nodeInfo.xlsx").sheet_by_index(0) 
factions = ""
origin = ""
normal = []
amemba = []

#functions
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

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

def makeHtml (header,column, linked=False):
	htmlString = ""
	column = col2num(column)
	if (sh.cell_value(rowx=num, colx=column) != ""):
		if (linked):
			htmlString = "<p><b>" + header + "</b>: "
			linkedSet = sh.cell_value(rowx=num, colx=column).split(", ")
			for x in range (0, len(linkedSet)):
				exists = os.path.isfile("../html/characterPages/%s.html" % linkedSet[x])
				if(exists):
					htmlString += "<a href='%s.html'>%s</a>" % (linkedSet[x],linkedSet[x])
				else:
					htmlString += str(linkedSet[x])
				if x < len(linkedSet)-1:
					htmlString += ", "
		else:
			htmlString = "<p><b>" + header + "</b>: " + str(sh.cell_value(rowx=num, colx=column))	
	return htmlString

def makeLakonHtml():
	lakonList = sh.cell_value(rowx=num, colx=col2num("Y")).split(",")
	lakonArray = []
	htmlString = "<p><b>Found in the follwing lakon (stories)</b>:</p><ol> "
	for lakon in lakonList:
		htmlString += '<li><a href="../lakonPages/%s.html">%s</a></li>' % (lakon,lakon)
	htmlString += "</ol>"
	return htmlString

def makeDescriptionHtml():
	htmlString = sh.cell_value(rowx=num, colx=col2num("G"))
	matchObj = re.findall(r"(\[[a-zA-Z\_]*\])",htmlString)
	for match in matchObj:
		cleanMatch = re.sub(r"(\[|\])","",match)
		exists = os.path.isfile("../html/characterPages/%s.html" % cleanMatch)
		if(exists):
			link = '<a href="%s.html">%s</a>' % (cleanMatch,cleanMatch)
			htmlString = re.sub("\[" + cleanMatch + "\]", link, htmlString)
	#htmlString = re.sub(r"\/([\w ]+)\/", r"<i>\1</i>", htmlString)
	
	matchObj = re.findall(r"\/([\w_\(\) ]+)\/",htmlString)
	for match in matchObj:
		#print match
		cleanMatch = re.sub(r"\/","",match)
		print cleanMatch
		exists = os.path.isfile("../html/lakonPages/%s.html" % cleanMatch)
		if(exists):
			link = '<a href="../lakonPages/%s.html">%s</a>' % (cleanMatch,cleanMatch)
			htmlString = re.sub("\/" + cleanMatch + "\/", link, htmlString)
		else:
			htmlString = re.sub("\/" + cleanMatch + "\/", "<i>" + cleanMatch + "</i>", htmlString)
	
	htmlString = "<p><b>Description in the Javanese version</b>: " + htmlString.decode("utf-8")
	return htmlString

def makeTable(listName,valueName,measurement,location):
	#currently the makeTable function only looks at disguised values
	disguisedValue = sh.cell_value(rowx=num, colx=col2num(location)+10)
	htmlString = "<tr><td>%s</td><td>%s</td><td><a href=\"histograms/%s_%s.png\"><img src=\"histograms/%s_%s.png\" height=\"100px\"></a></td></tr>" % (measurement,disguisedValue,name,valueName,name,valueName)
	#here we make an image with the histogram for this particular
	
	plt.figure(figsize=(15,3)) 
	n,bins,patches = plt.hist(listName, bins=12, color="blue") 
	plt.title("%s for %s (in red)" %(valueName,name))
	plt.ylabel("Number of instances")
	plt.xlabel(valueName)
	
	binNum = -1
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

def page(value):
	trueNumber = re.sub('\.0','',str(value))
	if ("-" in trueNumber):
		return "pp. %s" % trueNumber
	else:
		return "p. %s" % trueNumber

def getSources():
	htmlString = ""
	array = []
	ewp = sh.cell_value(rowx=num, colx=col2num("T"))
	mt = sh.cell_value(rowx=num, colx=col2num("U"))
	swp = sh.cell_value(rowx=num, colx=col2num("V"))
	wei = sh.cell_value(rowx=num, colx=col2num("W"))
	rkwp = sh.cell_value(rowx=num, colx=col2num("X"))
	if (ewp):
		array.append("<i>Ensiklopedi Wayang Purwa</i>, %s" % page(ewp))
	if (mt):
		array.append("<i>Mengenal Gambar Tokoh Wayang Purwa</i>, %s" % page(mt))
	if (swp):
		array.append("<i>Sejarah Wayang Purwa</i>, %s" % page(swp))
	if (wei):
		array.append("<i>Ensiklopedi Wayang Indonesia</i>, %s" % page(wei))
	if (rkwp):
		array.append("<i>Rupa dan Karakter Wayang Purwa</i>, %s" % page(rkwp))
	if (not array == []):
		htmlString = "<p><b>Sources</b>: "  + "; ".join(array)
	return htmlString

def findSpouseAncestry(spouse):
	html = ""
	for num1 in range(1,sh.nrows):
		possibleName = sh.cell_value(rowx=num1, colx=0)
		if (spouse == possibleName):
			spouseParents = []
			spouseFather = sh.cell_value(rowx=num1, colx=col2num("I"))
			spouseMother = sh.cell_value(rowx=num1, colx=col2num("J"))
			if (spouseFather):
				spouseParents.append(spouseFather)
			if (spouseMother):
				spouseParents.append(spouseMother)
			html += "\n  - parents: [%s]" % ", ".join(spouseParents)
			html += "\n    children: [%s]" % possibleName
	return html
	
def getFamily():
	string = ""
	spouses = []
	offspring = []
	yaml = "families:"
	family =  sh.cell_value(rowx=num, colx=col2num("L")).decode("utf-8")
	if (family):
		family = family.split(";")
		for fam in family:
			yamlParents = [name]
			yamlChildren = []
			members = fam.split(":")
			if "x" not in members[0]:
				spouses.append(re.sub(" ","",members[0]))
				yamlParents.append(members[0])
			children = members[1].split(",")
			for child in children:
				if "x" not in child:
					offspring.append(re.sub(" ","",child))
					yamlChildren.append(child)
			yaml += "\n  - parents: [%s]" % ", ".join(yamlParents)
			yaml += "\n    children: [%s]" % ", ".join(yamlChildren)
	parents = []
	mother = sh.cell_value(rowx=num, colx=col2num("I"))
	father = sh.cell_value(rowx=num, colx=col2num("J"))
	if (father):
		parents.append(father)
	if (mother):
		parents.append(mother)
	yaml += "\n  - parents: [%s]" % ", ".join(parents)
	yaml += "\n    children: [%s]" % name
	
	for spouse in spouses:
		yaml += findSpouseAncestry(spouse)
	
	with open("../html/characterPages/yaml/" + name + ".yml", "w") as file:
		file.write(yaml)
		
	command = "kingraph ../html/characterPages/yaml/%s.yml > ../html/characterPages/trees/%s.svg" % (name,name)
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print p.communicate()[0]
	
	for x in range (0, len(spouses)):
		exists = os.path.isfile("../html/characterPages/%s.html" % spouses[x])
		if(exists):
			spouses[x] = "<a href='%s.html'>%s</a>" % (spouses[x],spouses[x])
	
	for x in range (0, len(offspring)):
		exists = os.path.isfile("../html/characterPages/%s.html" % offspring[x])
		if(exists):
			offspring[x] = "<a href='%s.html'>%s</a>" % (offspring[x],offspring[x])
	
	if (spouses): string += "<p><b>Consorts: </b> %s" % ", ".join(spouses)
	if (offspring): string += "<p><b>Offspring: </b> %s" % ", ".join(offspring)
	return string

for num in range(1,sh.nrows):
	
	array = []
	data = {}
	matchedNum = 0
	name = sh.cell_value(rowx=num, colx=0)
	
	print "Working on " + name
	
	html = open("htmlfragments/heather.txt").read()
	html += name 
	html += open("htmlfragments/html1.html").read()
	
	#HTML Character Page
	html += "<p><h1>" + name + "</h1></p>"
	html += "<img src='Yogyakarta/" + name + ".png' height='300px'></img>"
	html += makeHtml("Terms of address", "D")
	html += makeHtml("Type", "C")
	html += makeHtml("Origin", "E")
	html += makeHtml("Notes on the Sanskrit version", "F")
	html += makeHtml("Alternative names", "H")
	html += makeDescriptionHtml()
	html += makeLakonHtml()
	
	if (sh.cell_value(rowx=num, colx=col2num("L")) or sh.cell_value(rowx=num, colx=col2num("I")) or sh.cell_value(rowx=num, colx=col2num("J")) or sh.cell_value(rowx=num, colx=col2num("K"))):	
		html += "<hr><h3>Family relationships</h3>"
	
		html += makeHtml("Mother", "I", True)
		html += makeHtml("Father", "J", True)
		html += makeHtml("Siblings", "K", True)
		html += getFamily()
	
		#exists = os.path.isfile("../html/characterPages/trees/%s.svg" % name)
		#if(exists):
		svg = open("../html/characterPages/trees/%s.svg" %name).read()
		svg = re.sub('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"',"",svg)
		svg = re.sub('"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',"",svg)
		svg = re.sub('width\=".*" height\=".*"','width="100%"',svg)
		svg = re.sub(r'\<title\>' + name + '\<\/title\>[ \n]*\<polygon fill\="white"', '<title>'+name+'</title>\n<polygon fill="#ADD8E6"', svg)  
		matchObj = re.findall(r"\>([a-zA-Z_]*)\<\/text\>",svg)
		for match in matchObj:
			nodeExists = os.path.isfile("../html/characterPages/%s.html" % match)
			if(nodeExists):
				svg = re.sub(match, "<a href='%s.html'>%s</a>" % (match,match), svg)
		html += "<p>" + svg
	
	html += "<hr><h3>More information</h3>"
	html += makeHtml("Ruler of", "N")
	html += makeHtml("Killed by", "O", True)
	html += makeHtml("Aji / Wahyu / Pusaka", "P")
	html += makeHtml("Takes the shape of", "Q", True)
	html += makeHtml("Impersonated by", "R", True)
	html += makeHtml("Wanda", "S", True)
	html += getSources()
	
	html += "<p>&nbsp;<hr><p><h3>Network measurements for %s</h3>" %name
	html += open("htmlfragments/table2.html").read()
	html += makeTable(degreeList,"Degree",'Degree <a href="#" data-toggle="tooltip" title="The amount of connections of the given node."><i class="glyphicon glyphicon-question-sign"></i></a>',"AA")
	html += makeTable(weightedDegreeList,"Weigted Degree",'Weighted Degree <a href="#" data-toggle="tooltip" title="The amount of connections a node has, taking into account the weight of those connections"><i class="glyphicon glyphicon-question-sign"></i></a>',"AB")
	html += makeTable(closenessCentralityList,"Closeness Centrality",'Closeness Centrality <a href="#" data-toggle="tooltip" title="The average length of the shortest path between the node and all other nodes in the graph"><i class="glyphicon glyphicon-question-sign"></i></a>',"AC")
	html += makeTable(betweennessCentralityList,"Betweenness Centrality",'Betweeness Centrality <a href="#" data-toggle="tooltip" title="Inidcates how often a node acts as a bridge along the shortest path between two other nodes"><i class="glyphicon glyphicon-question-sign"></i></a>',"AE")
	html += makeTable(eigenvectorCentralityList,"Eigenvector Centrality",'Eigenvector Centrality <a href="#" data-toggle="tooltip" title="A measurement of the influence of the node in the graph, that takes into account how connected it is to higher-degree nodes"><i class="glyphicon glyphicon-question-sign"></i></a>',"AJ")
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
	html += open("htmlfragments/html2.html").read()

	#text file for network display
	text = ""
	text += "<p><h1>" + name + "</h1></p>"
	text += makeHtml("Terms of address", "D")
	text += makeHtml("Type", "C")
	text += makeHtml("Origin", "E")
	text += makeHtml("Alternative names", "H")
	text += makeHtml("Mother", "I")
	text += makeHtml("Father", "J")
	#text += makeLakonHtml()

	#this is for the factions file
	factions += name + "," + sh.cell_value(rowx=num, colx=col2num("C")) + "," + sh.cell_value(rowx=num, colx=col2num("E")) + "," + sh.cell_value(rowx=num, colx=col2num("B")) + "\n"
	
	with open("../html/characterPages/" + name + ".html", "w") as file:
		file.write(html)
	with open("../html/characterPages/" + name + ".txt", "w") as file:
		file.write(text)
	
	for edge in edgeInfoCanonical:
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
	with open("../html/data/json/%s_canonical.txt" % name,"w") as file:
		file.write(json_data)
	
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
	
with open("../inputForAnalysis/factions.txt","w") as file:
		file.write(factions)

