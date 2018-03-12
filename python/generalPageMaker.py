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
	
'''	
#For Character Pages
html = open("htmlfragments/heather.txt").read()
html += "Lakon list"
html += open("htmlfragments/html1.html").read()

html += "<h1>List of Characters</h1>"
html += "<ul>"

for fileItem in sorted(glob.glob("../html/characterPages/*.html")):
	title = re.sub("(../html/characterPages/|\.html)","",fileItem)
	html += '<li>' + '<a href="characterPages/' + title + '.html">' + title + '</a></li>'
	
html += "</ul>"
html += open("htmlfragments/html2.html").read()
html = re.sub("\.\.\/","",html)

with open("../html/characters.html", "w") as file:
		file.write(html)
		print "characterss.html created"
'''
