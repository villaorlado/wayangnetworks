import re
import glob

characterList = "var availableTags = "
characterArray = []

for fileItem in sorted(glob.glob("../html/characterPages/*.html")):
	title = re.sub("(../html/characterPages/|\.html)","",fileItem)
	#html += '<li>' + '<a href="characterPages/' + title + '.html">' + title + '</a></li>'
	characterArray.append(title)

characterList += str(characterArray)
characterList += ";"
print characterList

