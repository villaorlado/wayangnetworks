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
	html = open("htmlfragments/heather.txt").read()
	html += title
	html += open("htmlfragments/html1.html").read()
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
	text = re.sub(r'(\d+)', r"<p><b>\1</b>", text)
	text = re.sub(r'\*([\w ]+)\*', r"<p>&nbsp;<p><h3>\1</h3><hr>", text)
	
	text = re.sub(r'([a-zA-Z -]+):([a-zA-Z]+)', r" <span class='badge'>\1</span> <b>\2</b>", text)
	text = re.sub(r'\[(\w*)\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\{(\w*)\}', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\[(\w*)\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\[(\w*)@\w+\]', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\((\w*)\)', r"<a href='../characterPages/\1.html'>\1</a>", text)
	text = re.sub(r'\((\w*)@\w+\)', r"<a href='../characterPages/\1.html'>\1</a>", text)
	html += "<h1>" + title + "</h1>"
	html += '<div class="well" id="characters">' + characterList + '</div>' 
	html += text 
	html += open("htmlfragments/html2.html").read()
	
	with open("../html/lakonPages/" + title + ".html", "w") as file:
		file.write(html.decode('utf-8').encode('utf-8'))
		print title + " created"

	with open("../html/lakonPages/%s_characters.txt" % title, "w") as file:
		file.write(characterListText)
