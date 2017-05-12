#!/usr/bin/env python2.7.11

import glob
import re

#For Lakon Pages
html = open("htmlfragments/heather.txt").read()
html += "Lakon list"
html += open("htmlfragments/html1.html").read()

html += "<h1>List of Lakons</h1>"
html += "<ul>"

for fileItem in glob.glob("../html/lakonPages/*.html"):
	title = re.sub("(../html/lakonPages/|\.html)","",fileItem)
	html += '<li>' + '<a href="lakonPages/' + title + '.html">' + title + '</a></li>'
	
html += "</ul>"
html += open("htmlfragments/html2.html").read()
html = re.sub("\.\.\/","",html)

with open("../html/lakons.html", "w") as file:
		file.write(html)
		print "lakons.html created"
	
	
#For Character Pages
html = open("htmlfragments/heather.txt").read()
html += "Lakon list"
html += open("htmlfragments/html1.html").read()

html += "<h1>List of Characters</h1>"
html += "<ul>"

for fileItem in glob.glob("../html/characterPages/*.html"):
	title = re.sub("(../html/characterPages/|\.html)","",fileItem)
	html += '<li>' + '<a href="characterPages/' + title + '.html">' + title + '</a></li>'
	
html += "</ul>"
html += open("htmlfragments/html2.html").read()
html = re.sub("\.\.\/","",html)

with open("../html/characters.html", "w") as file:
		file.write(html)
		print "characterss.html created"
