#!/usr/bin/env python2.7.11

''' 
This file creates a list of characters and a list of lakons for the web interface 
'''

import glob
import re

#For Lakon Pages
html = open("htmlfragments/lakons_template.html").read()
html = html.replace("$title$","Lakon list")

content = "<h1>List of stories (lakon)</h1>"
content += "Lakon list"
content += "<ul>"

x =1
for fileItem in sorted(glob.glob("../html/lakonPages/*.html")):
	title = re.sub("(../html/lakonPages/|\.html)","",fileItem)
	content += '<li class="titles" id="title%s">'%x + '<a href="lakonPages/' + title + '.html">' + title + '</a></li>'
	x+=1
	
html =html.replace("$content$",content)

with open("../html/lakons.html", "w") as file:
		file.write(html)
		print "lakons.html created"
	

#For Character Pages
html = open("htmlfragments/characters_template.html").read()
characterArray = []
characterList = "<ul>"

for fileItem in sorted(glob.glob("../html/characterPages/*.html")):
	title = re.sub("(../html/characterPages/|\.html)","",fileItem)
	characterList += '<li>' + '<a href="characterPages/' + title + '.html">' + title + '</a></li>'
	characterArray.append(title)
	
characterList += "</ul>"

html = html.replace("@@@",str(characterArray))
html = html.replace("$$$",characterList)

with open("../html/characters.html", "w") as file:
		file.write(html)
		print "characters.html created"

