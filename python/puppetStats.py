from __future__ import division
import xlrd 
from collections import Counter
from xlsxwriter.workbook import Workbook
import xlsxwriter
import re
from collections import Counter

def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1
    
data = xlrd.open_workbook("../html/comparisons/data/fotoInfo_Hariyanto.xlsx").sheet_by_index(0) 

htmlTemplate = open("htmlfragments/puppetparts.html").read()

bibir_array = []
celana_array = []
garuda_array = []
kalung_array = []
kelat_array = []
kroncong_array = []
kumis_array = []
mata_array = []	
praba_array = []	
serban_array = []	
sumping_array = []	
topong_array = []
rai_array = []
kaki_array = []

def makeArray (arrayName, letter):
	temp_data = data.cell_value(rowx=x,colx=col2num(letter))
	try:
		int(temp_data)
		arrayName.append(int(temp_data))
	except:
		print temp_data

for x in range (0, data.nrows):
	mata = data.cell_value(rowx=x,colx=col2num("N"))
	try:
		mata_array.append(mata)
	except:
		print "not working"
	
	makeArray(bibir_array, "F")
	makeArray(garuda_array, "I")
	makeArray(celana_array, "H")
	makeArray(sumping_array, "Q")
	
print "Bibir " + str(Counter(bibir_array))
print "Mata " + str(Counter(mata_array))
print "Garuda " + str(Counter(garuda_array))
print "Celanaa " + str(Counter(celana_array))

def printArray (array,array_name,title):
	print "Working on " + str(title)
	content = "<h1>%s</h1>" % title
	content += "<p>Distributions across the collection</p>"
	c = Counter(array)
	total = sum(c.values())
	for key,value in c.items():
		if (key == 0):
			content += "<p><h3>No %s %.2f%%</h3>" % (array_name, value/total * 100)
		else:
			content += "<p><h3><img height='70px' src='elements/%s/%s.png'> %.2f%%</h3>" % (array_name, key, value/total * 100)
	
	html = htmlTemplate.replace("$title$",array_name).replace("$content$",content)
	with open("../html/comparisons/" + array_name + ".html", "w") as file:
		file.write(html.decode('utf-8').encode('utf-8'))
		print str(array_name) + " created"

printArray(bibir_array,"bibir","Mouths")
printArray(garuda_array,"garuda","Garuda")
printArray(mata_array,"mata","Eyes")
printArray(celana_array,"celana","Pants")
printArray(sumping_array,"sumping","Sumping")

