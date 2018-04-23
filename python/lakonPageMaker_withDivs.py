#!/usr/bin/env python2.7.11
'''
This file reads the excel sheet and generates a static page for each character.
'''
import re

inputFile = "../input/stories.txt"
narratives = open(inputFile).read()

lakons = re.split(r"\/\/\d+ ",narratives);

for x in range (1, len(lakons)):
	lines = lakons[x].splitlines()
	title = re.sub("#","",lines[0])
	fullHTML = open("htmlfragments/lakon_div_template.html").read()
	fullHTML = fullHTML.replace("@@@title@@@",title)
	html = ""
	text = ""
	matches = re.findall(r'\[(\w*)\]', lakons[x])
	characters = list(set(matches))
	characterList = "<p>This lakon has " + str(len(characters)) + " characters: " 
	characterListText = ",".join(characters)
	
	for character in characters:
		characterList += " <a href='../characterPages/" + character + ".html'>" + character + "</a>,"
	
	for i in range(1, len(lines)):
		text += lines[i]
	text = re.sub(r'(<|>)', "", text)
	text = re.sub(r'(\d+)', r"<p class='adegan' id='adegan\1'><b>\1</b>", text)
	text = re.sub(r'\*([\w ]+)\*', r"<p>&nbsp;<p id='\1'><h3>\1</h3><br/>", text)
	
	text = re.sub(r'([a-zA-Z -]+):([a-zA-Z\-]+)', r" <span class='badge'>\1</span> <b>\2</b>", text)
	text = re.sub(r'\[(\w*)\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\{(\w*)\}', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\[(\w*)\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	#text = re.sub(r'\[(\w*)@\w+\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\[(\*\w*)@\w+\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\((\w*)\)', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\((\w*)@\w+\)', r"<a href='../characterPages/\1.html'>\1</a>", text)
	html += "<h1>" + title + "</h1>"
	html += '<div class="datum" id="CharacterList">' + characterList + '</div>' 
	html += '<div class="datum">' + text + '</div>' 
	fullHTML = fullHTML.replace("@@@content@@@",html)	
	fullHTML = fullHTML.replace("@@@csv@@@",title)
		
	
	with open("../html/lakonPages/" + title + ".html", "w") as file:
		file.write(fullHTML.decode('utf-8').encode('utf-8'))
		print title + " created"

	with open("../html/lakonPages/%s_characters.txt" % title, "w") as file:
		file.write(characterListText)
