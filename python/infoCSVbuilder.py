#!/usr/bin/env python2.7.11

'''
This script reads an annotated copy of the lakon file and produces three lists:
All characters by lakon
All characters by adegan
All amemba(disguised) characters by lakon
All amemba(disguised) characters by adegan
The same with information about the place of the link

'''
import re
import itertools

#input variables
inputFile = "../input/lakonFull.txt"
narratives = open(inputFile).read()
listOfPlaces = []

#character types
regex = {"normal":r'\[(\w*)\]', "realAmemba":r'\[\w*@(\w*)\]', "amemba":r'\[(\w*)@\w*\]', "collective":r'\{(\w*)\}'}
canonicalOnly = ["normal","realAmemba"]
#canonicalAndCollective = ["normal","realAmemba","collective"]
canonicalAndDisguised = ["normal","amemba"]
#canonicalAndDisguisedAndCollective = ["normal","amemba","collective"]

#network types
networkTypes = {}
networkTypes["canonicalOnly"] = {"charactersIncluded":canonicalOnly,"dictionary":{},"fileName":"canonicalOnly"}
#networkTypes["canonicalAndCollective"] = {"charactersIncluded":canonicalAndCollective,"dictionary":{},"fileName":"canonicalAndCollective"}
networkTypes["canonicalAndDisguised"] = {"charactersIncluded":canonicalAndDisguised,"dictionary":{},"fileName":"canonicalAndDisguised"}
#networkTypes["canonicalAndDisguisedAndCollective"] = {"charactersIncluded":canonicalAndDisguisedAndCollective,"dictionary":{},"fileName":"canonicalAndDisguisedAndCollective"}

#window types
windowTypes = {}
windowTypes["lakon"] = {"pattern":r"[//]+\d+","name":r"#([a-zA-Z ,\.\:\(\)]*)#"}
windowTypes["adegan"] = {"pattern":r"\n\d+\.","name":r"\<([a-zA-Z -:]*)\>"}

#lakons and adegans
lakons = re.split(r"[//]\d",narratives);
adegans = re.split(r"\d*\.",narratives);

#extract given character types from given windows
def characterList(characterTypes, where):
	result = []
	for characterType in characterTypes:
		matches = re.findall(regex[characterType], where)
		for match in matches:
			result.append(match)
	return list(set(result))

'''
For Andy's analysis
csv file with adegan name and characters = 
01.01 = Puntadewa, Werkudara, Sadewa
designations file: character,desgination
Abimanyu,Pandawa
'''

def beautifyArray(receivedArray):
	returnedString = ""
	for element in receivedArray:
		returnedString += element + ","
	return returnedString[:-1]
	
#iterate for each window type
for k,v in windowTypes.iteritems():	

	windowGroups = re.split(v["pattern"],narratives);

	for key,value in networkTypes.iteritems():
		#here key is the name of the networkType and value is the related information
		
		windowList = ""
		n = 1
		for windowGroup in windowGroups: #lakon in lakons, adegan in adegans
			characters = characterList(value["charactersIncluded"],windowGroup)
			#name = 	re.findall(r'\<([a-zA-Z :]*)\>', windowGroup)
			name = 	re.findall(v["name"], windowGroup)
			
			if (len(characters)>1):
				windowList += str(n) + " " + ''.join(name) + " = " + beautifyArray(characters) + "\n"
				n+=1
				if (str(":") in str(name)):
					listOfPlaces.append(''.join(name))
		with open("../output/csvAnalysis/" + key + "_" + k + "_csvAnalysis.txt", "w") as file:
			file.write(windowList)

uniquePlaces = list(set(listOfPlaces))
uniquePlacesText = ""
for uniquePlace in uniquePlaces:
	uniquePlacesText += uniquePlace + "\n"

with open("../output/csvAnalysis/uniquePlaces.csv", "w") as file:
	file.write(uniquePlacesText)
