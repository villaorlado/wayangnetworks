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
inputFile = "../input/stories.txt"
narratives = open(inputFile).read()

#character types
regex = {"normal":r'\[(\w*)\]', "realAmemba":r'\[\w*@(\w*)\]', "amemba":r'\[(\w*)@\w*\]', "collective":r'\{(\w*)\}'}
canonicalOnly = ["normal","realAmemba"]
canonicalAndCollective = ["normal","realAmemba","collective"]
canonicalAndDisguised = ["normal","amemba"]
canonicalAndDisguisedAndCollective = ["normal","amemba","collective"]

#network types
networkTypes = {}
networkTypes["canonicalOnly"] = {"charactersIncluded":canonicalOnly,"dictionary":{},"fileName":"canonicalOnly"}
networkTypes["canonicalAndCollective"] = {"charactersIncluded":canonicalAndCollective,"dictionary":{},"fileName":"canonicalAndCollective"}
networkTypes["canonicalAndDisguised"] = {"charactersIncluded":canonicalAndDisguised,"dictionary":{},"fileName":"canonicalAndDisguised"}
networkTypes["canonicalAndDisguisedAndCollective"] = {"charactersIncluded":canonicalAndDisguisedAndCollective,"dictionary":{},"fileName":"canonicalAndDisguisedAndCollective"}

#window types
windowTypes = {}
windowTypes["lakon"] = {"pattern":r"[//]+\d+"}
windowTypes["adegan"] = {"pattern":r"\n\d+\."}

#lakons and adegans

#lakons = narratives.split("//");
lakons = re.split(r"[//]\d+",narratives);

for x in range (1, len(lakons)):
	lines = lakons[x].splitlines()
	title = re.sub("#","",lines[0]).replace(" ","")
	csv = "characters,names"
	characterDict = {}
	for y in range(1,len(lines)):
		if re.search(r"^\d",lines[y]): #this means we have a scene
			
			matches1 = re.findall(r'\[(\w*)\]', lines[y])
			matches2 = re.findall(r'\[\w*@(\w*)\]', lines[y])
			matches3 = re.findall(r'\[(\w*)@\w*\]', lines[y])
			matches =  matches1 + matches2 + matches3
			
			characters = list(set(matches))
			characterNames = "&".join(characters)
			csv += "\n" + str(len(characters)) + "," + characterNames
			
			#populate character dict
			for subset in itertools.combinations(characters, 2): #iterate trhough each pair and name it
				name = subset[0] + "_" + subset[1]
				altName = subset[1] + "_" + subset[0]
			
				#if already in dict, increase the degree, otherwise add new item to edgelist
				if (name in characterDict):
					characterDict[name]["degree"] = characterDict[name]["degree"]+1
			
				#make sure a->b is not duplicated as b->a	
				elif (altName in characterDict): 
					characterDict[altName]["degree"] = characterDict[altName]["degree"]+1
		
				#if not in list, give it degree of 1		
				else:
					characterDict[name] = {}
					characterDict[name]["from"] = subset[0]
					characterDict[name]["to"] = subset[1]
					characterDict[name]["degree"] = 1
			
	#print character dict to csv file
	csvFile = "Source,Target,Type,Weight\n"
	for k,v in characterDict.iteritems():
		csvFile += str(v["from"]) + "," + str(v["to"]) + ",Undirected," + str(v["degree"]) + "\n"
	with open("../html/lakonPages/networkData/" + title + ".csv", "w") as file:
		file.write(csvFile)
	
	with open("../html/lakonPages/data/" + title + ".csv", "w") as file:
		file.write(csv.decode('utf-8').encode('utf-8'))
		print title + " created"

'''
#extract given character types from given windows
def characterList(characterTypes, where):
	result = []
	for characterType in characterTypes:
		matches = re.findall(regex[characterType], where)
		for match in matches:
			result.append(match)
	return list(set(result))

#populate a given dictionary with a given character array
def populateEdgeDict (characterArray, dictName):
	for subset in itertools.combinations(characterArray, 2): #iterate trhough each pair and name it
		name = subset[0] + "_" + subset[1]
		altName = subset[1] + "_" + subset[0]
			
		#if already in dict, increase the degree, otherwise add new item to edgelist
		if (name in dictName):
			dictName[name]["degree"] = dictName[name]["degree"]+1
			
		#make sure a->b is not duplicated as b->a	
		elif (altName in dictName): 
			dictName[altName]["degree"] = dictName[altName]["degree"]+1
		
		#if not in list, give it degree of 1		
		else:
			dictName[name] = {}
			dictName[name]["from"] = subset[0]
			dictName[name]["to"] = subset[1]
			dictName[name]["degree"] = 1

#convert character Dictionary to CSV:
def makeCSV(characterDict,csvName):
	csvFile = "Source,Target,Type,Weight\n"
	for k,v in characterDict.iteritems():
		csvFile += str(v["from"]) + "," + str(v["to"]) + ",Undirected," + str(v["degree"]) + "\n"
	with open("../gephi/input/edgeInfo/" + csvName + ".csv", "w") as file:
		file.write(csvFile)

#iterate for each window type
for k,v in windowTypes.iteritems():
	n = 1
	windowGroups = re.split(v["pattern"],narratives);
	for windowGroup in windowGroups: #lakon in lakons, adegan in adegans
		for key,value in networkTypes.iteritems():
			populateEdgeDict(characterList(value["charactersIncluded"],windowGroup),value["dictionary"])
	for key2,value2 in networkTypes.iteritems():
		makeCSV(value2["dictionary"],str(k)+"_"+value2["fileName"])
'''