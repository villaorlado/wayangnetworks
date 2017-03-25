import os, sys
import pickle as pk
import errno
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy import interpolate

###########################################################################

def CharacterListTxt(datasettag):

	CharacterNodes = LoadGraphs(datasettag)[1]
	characterlist = open("../Outputs/" + datasettag + "/" + datasettag + "_CharacterList.csv" , 'w')
	for character in sorted(set(CharacterNodes)):
		characterlist.write(character + "," + "\n")
	characterlist.close()


###########################################################################

def CoarseGrainer(datasettag, newdatasettag):

# requires episodes to be named like "1.1" etc.
# will group together by episodes sharing the first number
# output will be a new input file

	episodelist = open("../Inputs/CharacterListsByEpisode" + datasettag + ".txt").read().splitlines()
	characters = []
	episodes = dict()
	episodesub = dict()

	B=nx.Graph()
	for episode in episodelist:
		episodesub[episode.split('=')[0].strip(' ').split(".")[0]] = []
		episodes[episode.split('=')[0].strip(' ').split(".")[0]] = []
	for episode in episodelist:	
		print(episode.split('=')[0].strip(' '))
		episodesub[episode.split('=')[0].strip(' ').split(".")[0]].append(episode.split('=')[0].strip(' '))
		episodes[episode.split('=')[0].strip(' ').split(".")[0]].extend([char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")])

		#characters.extend([char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")])#extend(episode.split(':')[1].split(','))
	EpisodeNodes = sorted(set(episodes.keys()))#sorted(set([episode.strip(" ") for episode in episodes]))#[(i+1) for i in episodeind]
	#CharacterNodes = sorted(set([character.strip(" ") for character in characters]))

	episodescoarse = dict()
	coarselist = open("../Inputs/" + newdatasettag + "CharacterListsByEpisode.txt" , 'w')
	for episode in EpisodeNodes:
		episodescoarse[episode] = sorted(set(episodes[episode]))
		coarselist.write(episode + " = ")
		for character in episodescoarse[episode]:
			coarselist.write(character + ", ")
		coarselist.write("\n")
	coarselist.close()

	return episodescoarse, episodesub

###########################################################################

def MacroEpisodeSubGraphs(datasettag, newdatasettag):

	episodelist = open("../Inputs/CharacterListsByEpisode" + datasettag + ".txt").read().splitlines()
	characters = []
	episodes = dict()
	#episodeind=range(0,len(episodes))

	# Construct bipartite character-episode occurrence network
	B=nx.Graph()
	for episode in episodelist:
		episodes[episode.split('=')[0].strip(' ')] = [char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")]
#		characters.extend([char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")])#extend(episode.split(':')[1].split(','))

	episodescoarse, episodesub = CoarseGrainer(datasettag, newdatasettag)

	for coarseepisode in episodescoarse.keys():
		coarselist = open("../Inputs/CharacterListsByEpisode" + newdatasettag + "_" + str(coarseepisode) + ".txt" , 'w')
		for episodename in episodesub[coarseepisode]:
			coarselist.write(episodename + " = ")
			for character in episodes[episodename]:
				coarselist.write(character + ", ")
			coarselist.write("\n")
		coarselist.close()

###########################################################################

def NumberedEdgeList(datasettag):

	CharacterNodes, B, G = LoadGraphs(datasettag)[1:4]

	charindexlist = open("../Outputs/" + datasettag + "/" + datasettag + "_CharacterIndexList.txt" , 'w')	
	CharacterIndices = dict()
	for count, character in enumerate(sorted(set(CharacterNodes))):
		CharacterIndices[character] = count
		charindexlist.write(str(count) + "," + str(character) + "\n")
	charindexlist.close()

	edgeindexlist = open("../Outputs/" + datasettag + "/" + datasettag + "_EdgeIndexList.txt" , 'w')	
	for edge in G.edges():
		edgeindexlist.write(str(CharacterIndices[edge[0]]) + "\t" + str(CharacterIndices[edge[1]]) + "\n")
	edgeindexlist.close()
		
###########################################################################

def ThresholdDataSet(datasettag, threshold):

	EpisodeNodes, CharacterNodes, B = LoadGraphs(datasettag)[0:3]

	Remove = []

	Degree = B.degree(CharacterNodes)
	for character in CharacterNodes:
		if (Degree[character] < threshold):
			Remove.append(character)

	episodelist = open("../Inputs/CharacterListsByEpisode" + datasettag + ".txt").read().splitlines()
	newtxt = open("../Inputs/CharacterListsByEpisode" + datasettag + "Threshold" + str(threshold) + ".txt" , 'w')
	characters = []
	episodes = dict()
	for episode in episodelist:
		ep = episode.split('=')[0].strip(' ')
		ls = episode.split('=')[1].split(',')
		episodes[ep] = [char.strip(" ") for char in ls if char.strip(" ")]
		for character in Remove:
			if character in episodes[ep]:
				episodes[ep].remove(character)
		if episodes[ep]:
			newtxt.write(ep + " =")
			for character in ls:
				if character.strip(" "):
					newtxt.write(character + ",")
			newtxt.write("\n")
	newtxt.close()

###########################################################################

def ConstructBipartite(datasettag):
	# CHARACTER-EPISODE OCCURRENCE NETWORK:
	# Load lists of characters by episode
	# (store input files in the folder "./Inputs/")
	episodelist = open("../Inputs/CharacterListsByEpisode" + datasettag + ".txt").read().splitlines()
	characters = []
	episodes = dict()
	#episodeind=range(0,len(episodes))

	# Construct bipartite character-episode occurrence network
	B=nx.Graph()
	for episode in episodelist:
		episodes[episode.split('=')[0].strip(' ')] = [char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")]
		characters.extend([char.strip(" ") for char in episode.split('=')[1].split(',') if char.strip(" ")])#extend(episode.split(':')[1].split(','))
	EpisodeNodes = sorted(set(episodes.keys()))#sorted(set([episode.strip(" ") for episode in episodes]))#[(i+1) for i in episodeind]
	CharacterNodes = sorted(set([character.strip(" ") for character in characters]))

	B.add_nodes_from(EpisodeNodes)#,bipartite=0)
	B.add_nodes_from(CharacterNodes)#,bipartite=1)
	#print(EpisodeNodes)
	#print(CharacterNodes)
	for ep in EpisodeNodes:
		for char in episodes[ep]:
			B.add_edge(ep,char)
	# Compute degree in bipartite network 
	# (# of episodes for character nodes; # of characters for episode nodes)
	#Occurrences = nx.degree(B)

	# #---------------------------------------------------

	# if ( threshold > 0 ):
	# 	Degree = nx.degree(B)
	# 	for character in CharacterNodes:
	# 		if ( Degree[character] < threshold ):
	# 			B.remove_node(character)
	# 			CharacterNodes.remove(character)
	# 	for episode in EpisodeNodes:
	# 		if ( Degree[episode] == 0 ):
	# 			B.remove_node(episode)
	# 			EpisodeNodes.remove(episode)

	# #---------------------------------------------------

	return EpisodeNodes, CharacterNodes, B

###########################################################################

def CharacterCooccurrenceNetwork(B, EpisodeNodes, CharacterNodes):

	# CHARACTER CO-OCCURRENCE NETWORK

	# Project bipartite graph onto set of character nodes to construct the
	# CHARACTER CO-OCCURENCE NETWORK:
	G=nx.Graph()
	G.add_nodes_from(CharacterNodes)
	for c1 in CharacterNodes:
		for c2 in CharacterNodes:
			for L in EpisodeNodes:
				if (B.has_edge(L,c1)) and (B.has_edge(L,c2)) and (c1 is not c2):
					if G.has_edge(c1,c2):
						G[c1][c2]['weight'] += 1./2 # because of double-counting
					else:
						G.add_edge(c1,c2, weight=1./2)
	return G

###########################################################################

def EpisodeIntersectionNetwork(B, EpisodeNodes, CharacterNodes):


	# CHARACTER CO-OCCURRENCE NETWORK

	# Project bipartite graph onto set of episode nodes to construct the
	# CHARACTER CO-OCCURENCE NETWORK:
	E=nx.Graph()
	E.add_nodes_from(EpisodeNodes)
	for e1 in EpisodeNodes:
		counter = 0
		for e2 in EpisodeNodes:
			for C in CharacterNodes:
				if (B.has_edge(C,e1)) and (B.has_edge(C,e2)) and (e1 is not e2):
					counter += 1
					if E.has_edge(e1,e2):
						E[e1][e2]['weight'] += 1./2 # because of double-counting
					else:
						E.add_edge(e1,e2, weight=1./2)
	return E

###########################################################################
###########################################################################

def InverseWeightCooccurrenceNetwork(G):
	# Now construct a second version with link weights replaced by their inverses
	# (for use in betweenness centrality computations, since shortest-path-finding
	# algorithms consider weights as "distances")
	GI=nx.Graph()
	GI.add_nodes_from(G.nodes())
	for edge in G.edges():
		GI.add_edge(edge[0],edge[1],weight = 1./float(G[edge[0]][edge[1]]['weight']))

	return GI

###########################################################################
###############################################################

def LoadGraphs(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl"):
		EpisodeNodes = pk.load(open("../Outputs/" + datasettag + "/Objects/EpisodeNodes" + datasettag + ".pkl","rb"))
		CharacterNodes = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterNodes" + datasettag + ".pkl","rb"))
		B = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl","rb"))
		G = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterCooccurrence" + datasettag + ".pkl","rb"))
		GI = pk.load(open("../Outputs/" + datasettag + "/Objects/InverseWeightCharacterCooccurrence" + datasettag + ".pkl","rb"))
		E = pk.load(open("../Outputs/" + datasettag + "/Objects/EpisodeIntersection" + datasettag + ".pkl","rb"))
		EI = pk.load(open("../Outputs/" + datasettag + "/Objects/InverseWeightEpisodeIntersection" + datasettag + ".pkl","rb"))
	else:
		EpisodeNodes, CharacterNodes, B = ConstructBipartite(datasettag)
		G = CharacterCooccurrenceNetwork(B, EpisodeNodes, CharacterNodes)
		GI = InverseWeightCooccurrenceNetwork(G)
		E = EpisodeIntersectionNetwork(B, EpisodeNodes, CharacterNodes)
		EI = InverseWeightCooccurrenceNetwork(E)
		pk.dump(EpisodeNodes, open( "../Outputs/" + datasettag + "/Objects/EpisodeNodes" + datasettag + ".pkl", "wb" ))
		pk.dump(CharacterNodes, open( "../Outputs/" + datasettag + "/Objects/CharacterNodes" + datasettag + ".pkl", "wb" ))
		pk.dump(B, open( "../Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl", "wb" ))
		pk.dump(G, open( "../Outputs/" + datasettag + "/Objects/CharacterCooccurrence" + datasettag + ".pkl", "wb" ))
		pk.dump(GI, open( "../Outputs/" + datasettag + "/Objects/InverseWeightCharacterCooccurrence" + datasettag + ".pkl", "wb" ))
		pk.dump(E, open( "../Outputs/" + datasettag + "/Objects/EpisodeIntersection" + datasettag + ".pkl", "wb" ))
		pk.dump(EI, open( "../Outputs/" + datasettag + "/Objects/InverseWeightEpisodeIntersection" + datasettag + ".pkl", "wb" ))

	return EpisodeNodes, CharacterNodes, B, G, GI, E, EI

###########################################################

def LoadFactions(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/CharacterFactions" + datasettag + ".pkl"):
		CharacterFactions = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterFactions" + datasettag + ".pkl","rb"))
		FactionCharacters = pk.load(open("../Outputs/" + datasettag + "/Objects/FactionCharacters" + datasettag + ".pkl","rb"))
	else:
		CharacterFactions = CharacterFactionAffiliations(datasettag)
		FactionCharacters = FactionCharacterLists(CharacterFactions)
		pk.dump(CharacterFactions, open( "../Outputs/" + datasettag + "/Objects/CharacterFactions" + datasettag + ".pkl", "wb" ))
		pk.dump(FactionCharacters, open( "../Outputs/" + datasettag + "/Objects/FactionCharacters" + datasettag + ".pkl", "wb" ))

	return CharacterFactions, FactionCharacters

###########################################################################

def FactionNodeMetricStats(datasettag):

	CharacterDegrees, CharacterStrengths, CharacterBetweenness = LoadCharacterNodeMetrics(datasettag)

	CharacterFactions, FactionCharacters = LoadFactions(datasettag)


	CharacterNodes, B, G = LoadGraphs(datasettag)[1:4]

	IG = FactionCooccurrenceNetwork(G, CharacterFactions)

	StrengthByFaction = dict()
	for character in CharacterNodes:
		StrengthByFaction[character] = dict()
		for faction in sorted(FactionCharacters.keys()):
			StrengthByFaction[character][faction] = 0
			for characterf in FactionCharacters[faction]:
				if G.has_edge(character,characterf):
					StrengthByFaction[character][faction] += G[character][characterf]['weight']

	FactionMeanStrengthByFaction = dict()
	for faction in sorted(FactionCharacters.keys()):
		FactionMeanStrengthByFaction[faction] = dict()
		for faction1 in sorted(FactionCharacters.keys()):
			FactionMeanStrengthByFaction[faction][faction1] = np.mean([StrengthByFaction[character][faction] for character in FactionCharacters[faction1]])

	FactionMeanDegrees = dict()
	FactionMeanStrength = dict()
	FactionMeanBetweenness = dict()
	ibs = open("../Outputs/" + datasettag + "/NodeMetricsByFactionsMean" + datasettag + ".csv" , 'w')
	ibt = open("../Outputs/" + datasettag + "/NodeMetricsByFactionsAbsolute" + datasettag + ".csv" , 'w')
	ibs.write("Faction,Number of characters,Mean Degree,Mean Node Strength,Mean Betweenness Centrality")
	ibt.write("Faction,Number of characters,Total Degree,Total Node Strength,Total Betweenness Centrality")
	for faction in sorted(FactionCharacters.keys()):
		ibs.write(", Mean " + faction + " Node Strength")
		ibt.write(", Total " + faction + " Node Strength")
	ibs.write("\n")
	ibt.write("\n")
	for faction in sorted(FactionCharacters.keys()):
		FactionMeanDegrees[faction] = np.mean([CharacterDegrees[character] for character in FactionCharacters[faction]])
		FactionMeanStrength[faction] = np.mean([CharacterStrengths[character] for character in FactionCharacters[faction]])
		FactionMeanBetweenness[faction] = np.mean([CharacterBetweenness[character] for character in FactionCharacters[faction]])
		ibs.write(faction + "," + str(len(FactionCharacters[faction])) + "," + str(FactionMeanDegrees[faction]) + "," + str(FactionMeanStrength[faction]) + "," + str(FactionMeanBetweenness[faction]))
		ibt.write(faction + "," + str(len(FactionCharacters[faction])) + "," + str(len(FactionCharacters[faction])*FactionMeanDegrees[faction]) + "," + str(len(FactionCharacters[faction])*FactionMeanStrength[faction]) + "," + str(len(FactionCharacters[faction])*FactionMeanBetweenness[faction]))
		for factiond in sorted(FactionCharacters.keys()):
			if IG.has_edge(faction,factiond):
				print(faction + factiond)
				print(str(FactionMeanStrengthByFaction[factiond][faction]) + " vs " + str(IG[faction][factiond]['weight']))
			ibs.write("," + str(FactionMeanStrengthByFaction[factiond][faction]))
			ibt.write("," + str(len(FactionCharacters[faction])*FactionMeanStrengthByFaction[factiond][faction]))
			#ibs.write("," + str(np.mean([StrengthByFaction[character][faction] for character in FactionCharacters[faction1]])))
		ibs.write("\n")
		ibt.write("\n")
	ibs.close()

	PercentagesOverall = dict()
	for faction in sorted(FactionCharacters.keys()):
		print(faction)
		print(len(FactionCharacters[faction]))
		#PercentagesOverall[faction] = np.divide(len(FactionCharacters[faction]), len(G.nodes()))

		PercentagesOverall[faction] = np.divide(FactionMeanStrength[faction]*len(FactionCharacters[faction]), np.sum(list(CharacterStrengths.values())))

	print(PercentagesOverall)

	DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	barwidth = 0.25
	OverallPercentagesPie = [PercentagesOverall[p] for p in sorted(FactionCharacters.keys())]
	factions = [f for f in sorted(FactionCharacters.keys())]
	for faction in PercentagesOverall:
		totes0 += np.power(PercentagesOverall[faction],2)
	totes0 = np.sqrt(totes0)
	for faction in sorted(FactionCharacters.keys()):
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		figurecounter = 0
		for factiond in sorted(FactionCharacters.keys()):
			#sumofsquares += np.power(DifferenceFromOverall[faction][factiond], 2)
			dotproduct += np.dot(FactionMeanStrengthByFaction[factiond][faction], PercentagesOverall[factiond])
			totes += np.power(FactionMeanStrengthByFaction[factiond][faction], 2)
		print(faction)
		print(totes)
		print(totes0)
		DistanceFromOverall[faction] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[faction] = np.divide(dotproduct, np.dot(totes0, totes))

		#-------------------

		Persum = np.sum([FactionMeanStrengthByFaction[f][faction] for f in factions])
		PercentagesPie = [np.divide(FactionMeanStrengthByFaction[faction1][faction], Persum) for faction1 in factions]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth, len(factions)-barwidth, len(factions)), OverallPercentagesPie, width = barwidth)
		plt.bar(np.linspace(1, len(factions), len(factions)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		#, autopct='%1.1f%%', shadow = False, startangle = 90)
		
		#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
		ax = fig.gca()
		ax.set_xlabel('Faction')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(factions), len(factions)))
		ax.set_xticklabels(factions, fontsize = 6)
		ax.set_title(faction + ' node strength allocation')
		ax.set_xlim([0, len(factions)+1])
		ax.set_ylim([0, 1])
		ax.legend(['Overall faction abundance', faction + ' node strength allocation'], fontsize = 6, loc = 'best')
		#ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/" + faction + "_NodeStrengthAllocation.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1


	ibs = open("../Outputs/" + datasettag + "/FactionNodeStrengthDistSimilarity.csv" , 'w')
	#for pair in sorted(DistanceFromOverall.keys(), key = lambda x: DistanceFromOverall[x], reverse = True):
	for faction in sorted(ProductOverall.keys(), key = lambda x: ProductOverall[x], reverse = False):
		ibs.write(faction + "," + str(ProductOverall[faction]) + "\n")
	ibs.close()	


	return FactionMeanDegrees, FactionMeanStrength, FactionMeanBetweenness, FactionMeanStrengthByFaction

###########################################################################

def FactionNodeMetricStatsProcess(datasettag):
	[]


###########################################################################

def LoadCharacterNodeMetrics(datasettag):

	EpisodeNodes, CharacterNodes, B, G, GI, E, EI = LoadGraphs(datasettag)

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/CharacterDegrees" + datasettag + ".pkl"):
		CharacterDegrees = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterDegrees" + datasettag + ".pkl","rb"))
		CharacterStrengths = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterStrengths" + datasettag + ".pkl","rb"))
		CharacterBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterBetweenness" + datasettag + ".pkl","rb"))
	else:
		CharacterDegrees = B.degree(CharacterNodes)
		CharacterStrengths = nx.degree(G, weight = 'weight')
		CharacterBetweenness = nx.betweenness_centrality(GI, weight = 'weight')
		pk.dump(CharacterDegrees, open("../Outputs/" + datasettag + "/Objects/CharacterDegrees" + datasettag + ".pkl", "wb"))
		pk.dump(CharacterStrengths, open("../Outputs/" + datasettag + "/Objects/CharacterStrengths" + datasettag + ".pkl", "wb"))
		pk.dump(CharacterBetweenness, open("../Outputs/" + datasettag + "/Objects/CharacterBetweenness" + datasettag + ".pkl", "wb"))

	return CharacterDegrees, CharacterStrengths, CharacterBetweenness

###########################################################################

def LoadLinkMetrics(datasettag):

	EpisodeNodes, CharacterNodes, B, G, GI, E, EI = LoadGraphs(datasettag)
	CharacterDegrees = LoadCharacterNodeMetrics(datasettag)[1]

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/LinkWeights" + datasettag + ".pkl"):
		LinkWeights = pk.load(open("../Outputs/" + datasettag + "/Objects/LinkWeights" + datasettag + ".pkl","rb"))
		LinkDegreeProduct = pk.load(open("../Outputs/" + datasettag + "/Objects/LinkDegreeProduct" + datasettag + ".pkl","rb"))
		LinkBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/LinkBetweenness" + datasettag + ".pkl","rb"))
	else:
		LinkBetweenness = nx.edge_betweenness_centrality(GI, weight = 'weight', normalized = True)
		LinkWeights = dict()#nx.edge_weight(G)
		LinkDegreeProduct = dict()
		for edge in LinkBetweenness.keys(): #G.edges():
			LinkWeights[edge] = G[edge[0]][edge[1]]['weight']
			LinkDegreeProduct[edge] = np.dot(CharacterDegrees[edge[0]], CharacterDegrees[edge[1]])
		pk.dump(LinkWeights, open("../Outputs/" + datasettag + "/Objects/LinkWeights" + datasettag + ".pkl", "wb"))
		pk.dump(LinkDegreeProduct, open("../Outputs/" + datasettag + "/Objects/LinkDegreeProduct" + datasettag + ".pkl", "wb"))
		pk.dump(LinkBetweenness, open("../Outputs/" + datasettag + "/Objects/LinkBetweenness" + datasettag + ".pkl", "wb"))

	return LinkWeights, LinkDegreeProduct, LinkBetweenness

###########################################################################
###########################################################################

def LoadInterfactionBetweenness(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/InterfactionBetweenness" + datasettag + ".pkl"):
		InterfactionBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/InterfactionBetweenness" + datasettag + ".pkl","rb"))
	else:
		GI = LoadGraphs(datasettag)[4] #
		FactionCharacters = LoadFactions(datasettag)[1]
		InterfactionBetweenness = InterfactionBetweennessCentrality(GI, FactionCharacters)
		pk.dump(InterfactionBetweenness, open( "../Outputs/" + datasettag + "/Objects/InterfactionBetweenness" + datasettag + ".pkl", "wb" ))

	return InterfactionBetweenness

###########################################################################

def LoadInterfactionLinkBetweenness(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/InterfactionLinkBetweenness" + datasettag + ".pkl"):
		InterfactionLinkBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/InterfactionLinkBetweenness" + datasettag + ".pkl","rb"))
	else:
		GI = LoadGraphs(datasettag)[4] #
		FactionCharacters = LoadFactions(datasettag)[1]
		InterfactionLinkBetweenness = InterfactionLinkBetweennessCentrality(GI, FactionCharacters)
		pk.dump(InterfactionLinkBetweenness, open( "../Outputs/" + datasettag + "/Objects/InterfactionLinkBetweenness" + datasettag + ".pkl", "wb" ))

	return InterfactionLinkBetweenness

###########################################################################

def LoadFactionWorldLinkBetweenness(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/FactionWorldLinkBetweenness" + datasettag + ".pkl"):
		FactionWorldLinkBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/FactionWorldLinkBetweenness" + datasettag + ".pkl","rb"))
	else:
		GI = LoadGraphs(datasettag)[4] #
		FactionCharacters = LoadFactions(datasettag)[1]
		FactionWorldLinkBetweenness = FactionWorldLinkBetweennessCentrality(GI, FactionCharacters)
		pk.dump(FactionWorldLinkBetweenness, open( "../Outputs/" + datasettag + "/Objects/FactionWorldLinkBetweenness" + datasettag + ".pkl", "wb" ))

	return FactionWorldLinkBetweenness

###########################################################################
###########################################################################

def LoadFactionWorldBetweenness(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/FactionWorldBetweenness" + datasettag + ".pkl"):
		FactionWorldBetweenness = pk.load(open("../Outputs/" + datasettag + "/Objects/FactionWorldBetweenness" + datasettag + ".pkl","rb"))
	else:
		GI = LoadGraphs(datasettag)[4] #EpisodeNodes, CharacterNodes, B, G, GI, E, EI
		FactionCharacters = LoadFactions(datasettag)[1]
		FactionWorldBetweenness = FactionWorldBetweennessCentrality(GI, FactionCharacters)
		pk.dump(FactionWorldBetweenness, open( "../Outputs/" + datasettag + "/Objects/FactionWorldBetweenness" + datasettag + ".pkl", "wb" ))

	return FactionWorldBetweenness

###########################################################################



###########################################################################

def WeightedNetworkThreshold(G, threshold):

	H = nx.Graph()
	H.add_nodes_from(G)

	for edge in G.edges():
		if (G[edge[0]][edge[1]]['weight'] >= threshold):
			H.add_edge(edge[0], edge[1], weight = G[edge[0]][edge[1]]['weight'])

	TruncatedDegree = nx.degree(H)
	for node in H.nodes():
		if (TruncatedDegree[node] == 0):
			H.remove_node(node)

	Hs = list(nx.connected_component_subgraphs(H))
	for h in Hs:
		if threshold == 2:
			print("comp")
			print(h.nodes())


	return H

###########################################################################

def CharacterFactionAffiliations(datasettag):
	 
	CharacterFactions = dict()
	for line in open("../Inputs/CharacterAffiliations" + datasettag + ".csv").read().splitlines()[0:]:
		CharacterFactions[line.split(",")[0].strip(" ")] = line.split(",")[1].strip(" ")

	return CharacterFactions
	
###########################################################################

def FactionCharacterLists(CharacterFactions):

	FactionCharacters = dict()
	for faction in sorted(set(CharacterFactions.values())):
		FactionCharacters[faction] = []

	for character in CharacterFactions.keys():
		FactionCharacters[CharacterFactions[character]].append(character)

	return FactionCharacters

###########################################################################

def RemoveFaction(G, FactionCharacters, faction):

	H = G.copy()
	for character in FactionCharacters[faction]:
		H.remove_node(character)

	return H

###########################################################################
###########################################################################

def FactionCooccurrenceNetwork(G, CharacterFactions):

	# FACTION CO-OCCURRENCE NETWORK
	# (Coarse-graining of the cooccurrence network where 
	# nodes represent factions, link weights represent the sum of all 
	# co-occurrence network link weights between characters in the corresponding
	# faction pairs)

	factions = sorted(set(CharacterFactions.values()))

	IG = nx.Graph()
	IG.add_nodes_from(factions)
	for edge in G.edges():
		c1 = edge[0]
		c2 = edge[1]
		f1 = CharacterFactions[c1]
		f2 = CharacterFactions[c2]
		if IG.has_edge(f1,f2):
			IG[f1][f2]['weight'] += G[c1][c2]['weight']
		else:
			IG.add_edge(f1,f2, weight = G[c1][c2]['weight'])

	return IG

###########################################################################
###########################################################################

def InterfactionBetweennessCentrality(GI, FactionCharacters):

	########################

	CharacterNodes = GI.nodes()

	factions = sorted(set(FactionCharacters.keys()))
	FactionPairsList = []
	for faction1 in factions:
		for faction2 in factions:
			if (not (faction1, faction2) in FactionPairsList) and (not (faction2, faction1) in FactionPairsList):
				FactionPairsList.append((faction1, faction2))

	InterfactionBetweenness = dict()
	for pair in FactionPairsList:
		IFB = nx.betweenness_centrality_subset(GI, FactionCharacters[pair[0]], FactionCharacters[pair[1]], normalized = True, weight = 'weight')
		InterfactionBetweenness[pair] = IFB

	############################

	return InterfactionBetweenness

###########################################################################
###########################################################################

def InterfactionLinkBetweennessCentrality(GI, FactionCharacters):

	########################

	CharacterNodes = GI.nodes()

	factions = sorted(set(FactionCharacters.keys()))
	FactionPairsList = []
	for faction1 in factions:
		for faction2 in factions:
			if (not (faction1, faction2) in FactionPairsList) and (not (faction2, faction1) in FactionPairsList):
				FactionPairsList.append((faction1, faction2))

	InterfactionLinkBetweenness = dict()
	for pair in FactionPairsList:
		IFB = nx.edge_betweenness_centrality_subset(GI, FactionCharacters[pair[0]], FactionCharacters[pair[1]], normalized = True, weight = 'weight')
		InterfactionLinkBetweenness[pair] = IFB

	############################

	return InterfactionLinkBetweenness

###########################################################################
###########################################################################

def FactionWorldLinkBetweennessCentrality(GI, FactionCharacters):

	########################

	CharacterNodes = GI.nodes()

	factions = sorted(set(FactionCharacters.keys()))

	FactionWorldLinkBetweenness = dict()
	for faction in factions:
		IFB = nx.edge_betweenness_centrality_subset(GI, FactionCharacters[faction], ( set(CharacterNodes) - set(FactionCharacters[faction]) ), normalized = True, weight = 'weight')
		FactionWorldLinkBetweenness[faction] = IFB

	############################

	return FactionWorldLinkBetweenness

###########################################################################

def InterfactionBetweennessBreakdownByFaction(datasettag, FactionCharacters, Betweenness, InterfactionBetweenness):

	factions = sorted(set(FactionCharacters.keys()))
	FactionPairsList = []
	for faction1 in factions:
		for faction2 in factions:
			if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
				FactionPairsList.append((faction1, faction2))

# Overall Betweenness pie chart for comparison

	figurecounter = 0
	TotalBetweenness = 0
	FactionTotals = dict()
	PercentagesOverall = dict()
	factionlist = [faction for faction in factions]
	for faction1 in factions:
		FactionTotals[faction1] = 0
		for character in FactionCharacters[faction1]:
			FactionTotals[faction1] += Betweenness[character]
			TotalBetweenness += Betweenness[character]
	for faction1 in factions:
		PercentagesOverall[faction1] = np.divide(FactionTotals[faction1],TotalBetweenness)

	try:
	    os.makedirs("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByFactionPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	OverallPercentagesPie = [PercentagesOverall[faction1] for faction1 in factions]
	fig = plt.figure(figurecounter)
	barwidth = 0.25
	plt.bar(np.linspace(1-barwidth/2, len(factions)-barwidth/2, len(factions)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
	#plt.pie(PercentagesPie, labels = factionlist, autopct='%1.1f%%', shadow = False, startangle = 90)
	ax = fig.gca()
	ax.set_xlabel('Faction')
	ax.set_ylabel('Fraction of total betweenness centrality')
	ax.set_xticks(np.linspace(1, len(factions), len(factions)))
	ax.set_xticklabels(factionlist, fontsize = 6)
	ax.set_title('Total betweenness centrality by faction')
	ax.set_xlim([0, len(factions)+1])
	plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByFactionPlots/OverallBetweenness.png", bbox_inches='tight')
	plt.close()
	figurecounter += 1

#########################################################

	DifferenceFromOverall = dict()

	# Interfaction Betweenness pie charts
	FactionTotals = dict()
	Percentages = dict()
	betweennesstypecounter = 1
	for pair in FactionPairsList:
		TotalBetweenness = 0
		FactionTotals[pair] = dict()
		Percentages[pair] = dict()
		DifferenceFromOverall[pair] = dict()
		for faction1 in factions:
			FactionTotals[pair][faction1] = 0
			for character in FactionCharacters[faction1]:
				FactionTotals[pair][faction1] += InterfactionBetweenness[pair][character]
				TotalBetweenness += InterfactionBetweenness[pair][character]
		factioncounter = 1
		for faction1 in factions:
			Percentages[pair][faction1] = np.divide(FactionTotals[pair][faction1],TotalBetweenness)
			if PercentagesOverall[faction1] != 0:
				DifferenceFromOverall[pair][faction1] = np.divide( Percentages[pair][faction1] - PercentagesOverall[faction1] , PercentagesOverall[faction1])
			else:
				DifferenceFromOverall[pair][faction1] = 0
	#		if TotalBetweenness > 0:
	#			ifbcsheet4.write(factioncounter,betweennesstypecounter+1,Percentages[pair][faction1])
			factioncounter += 1
#		if (piecharts is True) and (TotalBetweenness > 0):
		PercentagesPie = [Percentages[pair][faction1] for faction1 in factions]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth, len(factions)-barwidth, len(factions)), OverallPercentagesPie, width = barwidth)
		plt.bar(np.linspace(1, len(factions), len(factions)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		#, autopct='%1.1f%%', shadow = False, startangle = 90)
		
		#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
		ax = fig.gca()
		ax.set_xlabel('Faction')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(factions), len(factions)))
		ax.set_xticklabels(factionlist, fontsize = 6)
		ax.set_title("Total " + pair[0] + "-" + pair[1] + ' betweenness centrality fractions by faction')
		ax.set_xlim([0, len(factions)+1])
		ax.set_ylim([0, 1])
		ax.legend(['Overall betweenness centrality', pair[0] + "-" + pair[1] + ' betweenness centrality'], fontsize = 6, loc = 'best')
		#ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByFactionPlots/" + pair[0] + pair[1] + "BetweennessByFaction.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1
		betweennesstypecounter += 1
	#ifbcbook4.close()

	DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	for faction in factions:
		totes0 += np.power(PercentagesOverall[faction],2)
	totes0 = np.sqrt(totes0)
	for pair in FactionPairsList:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for faction in factions:
			sumofsquares += np.power(DifferenceFromOverall[pair][faction], 2)
			dotproduct += np.dot(Percentages[pair][faction], PercentagesOverall[faction])
			totes += np.power(Percentages[pair][faction], 2)
		DistanceFromOverall[pair] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[pair] = np.divide(dotproduct, np.dot(totes0, totes))

	ibs = open("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessSimilarity.csv" , 'w')
	#for pair in sorted(DistanceFromOverall.keys(), key = lambda x: DistanceFromOverall[x], reverse = True):
	for pair in sorted(ProductOverall.keys(), key = lambda x: ProductOverall[x], reverse = False):
		ibs.write(pair[0] + "-" + pair[1] + "," + str(ProductOverall[pair]) + "\n")
	ibs.close()	

	return PercentagesOverall, ProductOverall, Percentages

###########################################################################
###########################################################################

def InterfactionBetweennessBreakdownByCharacter(datasettag, FactionCharacters, Betweenness, InterfactionBetweenness):

	factions = sorted(set(FactionCharacters.keys()))
	FactionPairsList = []
	for faction1 in factions:
		for faction2 in factions:
			if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
				FactionPairsList.append((faction1, faction2))

	CharacterNodes = sorted(set(Betweenness.keys()))
	characters = [character for character in CharacterNodes]

# Overall Betweenness pie chart for comparison

	figurecounter = 0
	TotalBetweenness = 0
	PairTotals = dict()
	PercentagesOverall = dict()
	factionlist = [faction for faction in factions]
	#for pair in FactionPairsList:
		#CharacterTotals[faction1] = 0
		#for character in FactionCharacters[faction1]:

	for pair in FactionPairsList:
		PairTotals[pair] = 0
		for character in CharacterNodes:
			PairTotals[pair] += InterfactionBetweenness[pair][character]
		#CharacterTotals[faction1] += Betweenness[character]
	PairB = dict()
	for pair in FactionPairsList:
		PairB[pair] = dict()
		for character in CharacterNodes:
			PairB[pair][character] = np.divide(InterfactionBetweenness[pair][character], PairTotals[pair])
	#for faction1 in factions:
	#	PercentagesOverall[character] = np.divide(FactionTotals[character],TotalBetweenness)

	###
	TotalBetweenness = np.sum(list(Betweenness.values()))
	NormBetweenness = dict()
	for character in CharacterNodes:
		NormBetweenness[character] = np.divide(Betweenness[character], TotalBetweenness)

	###

	try:
	    os.makedirs("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByCharacterPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	OverallPercentagesPie = [NormBetweenness[character] for character in CharacterNodes]
	fig = plt.figure(figurecounter)
	barwidth = 0.25
	plt.bar(np.linspace(1-barwidth/2, len(characters)-barwidth/2, len(characters)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
	#plt.pie(PercentagesPie, labels = factionlist, autopct='%1.1f%%', shadow = False, startangle = 90)
	ax = fig.gca()
	ax.set_xlabel('Faction')
	ax.set_ylabel('Fraction of total betweenness centrality')
	ax.set_xticks(np.linspace(1, len(characters), len(characters)))
	ax.set_xticklabels(characters, fontsize = 4, rotation = 'vertical')
	ax.set_title('Total betweenness centrality by faction')
	ax.set_xlim([0, len(characters)+1])
	plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByCharacterPlots/OverallBetweenness.png", bbox_inches='tight')
	plt.close()
	figurecounter += 1

#########################################################

	DifferenceFromOverall = dict()

	# Interfaction Betweenness pie charts
	FactionTotals = dict()
	Percentages = dict()
	betweennesstypecounter = 1
	for pair in FactionPairsList:
	# 	TotalBetweenness = 0
	# 	FactionTotals[pair] = dict()
	# 	Percentages[pair] = dict()
	# 	DifferenceFromOverall[pair] = dict()
	# 	for faction1 in factions:
	# 		FactionTotals[pair][faction1] = 0
	# 		for character in FactionCharacters[faction1]:
	# 			FactionTotals[pair][faction1] += InterfactionBetweenness[pair][character]
	# 			TotalBetweenness += InterfactionBetweenness[pair][character]
	# 	factioncounter = 1
	# 	for faction1 in factions:
	# 		Percentages[pair][faction1] = np.divide(FactionTotals[pair][faction1],TotalBetweenness)
	# 		if PercentagesOverall[faction1] != 0:
	# 			DifferenceFromOverall[pair][faction1] = np.divide( Percentages[pair][faction1] - PercentagesOverall[faction1] , PercentagesOverall[faction1])
	# 		else:
	# 			DifferenceFromOverall[pair][faction1] = 0
	# #		if TotalBetweenness > 0:
	# #			ifbcsheet4.write(factioncounter,betweennesstypecounter+1,Percentages[pair][faction1])
	# 		factioncounter += 1
#		if (piecharts is True) and (TotalBetweenness > 0):
		PercentagesPie = [PairB[pair][character] for character in characters]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth, len(characters)-barwidth, len(characters)), OverallPercentagesPie, width = barwidth)
		plt.bar(np.linspace(1, len(characters), len(characters)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		#, autopct='%1.1f%%', shadow = False, startangle = 90)
		
		#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
		ax = fig.gca()
		ax.set_xlabel('Faction')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(characters), len(characters)))
		ax.set_xticklabels(characters, fontsize = 4, rotation = 'vertical')
		ax.set_title("Total " + pair[0] + "-" + pair[1] + ' betweenness centrality fractions by faction')
		ax.set_xlim([0, len(characters)+1])
		ax.set_ylim([0, 1])
		ax.legend(['Overall betweenness centrality', pair[0] + "-" + pair[1] + ' betweenness centrality'], fontsize = 6, loc = 'best')
		#ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessByCharacterPlots/" + pair[0] + pair[1] + "BetweennessByCharacter.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1
		betweennesstypecounter += 1
	#ifbcbook4.close()

	#DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	for character in CharacterNodes:
		totes0 += np.power(NormBetweenness[character],2)
	totes0 = np.sqrt(totes0)
	for pair in FactionPairsList:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for character in CharacterNodes:
			#sumofsquares += np.power(DifferenceFromOverall[pair][character], 2)
			dotproduct += np.dot(PairB[pair][character], NormBetweenness[character])
			totes += np.power(PairB[pair][character], 2)
		#DistanceFromOverall[pair] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[pair] = np.divide(dotproduct, np.dot(totes0, totes))

	ibs = open("../Outputs/" + datasettag + "/InterfactionBetweenness/InterfactionBetweennessCharacterSimilarity.csv" , 'w')
	#for pair in sorted(DistanceFromOverall.keys(), key = lambda x: DistanceFromOverall[x], reverse = True):
	for pair in sorted(ProductOverall.keys(), key = lambda x: ProductOverall[x], reverse = False):
		ibs.write(pair[0] + "-" + pair[1] + "," + str(ProductOverall[pair]) + "\n")
	ibs.close()	

	return PercentagesOverall, ProductOverall

###########################################################################
###########################################################################

def FactionWorldBetweennessBreakdownByCharacter(datasettag, FactionCharacters, Betweenness, FactionWorldBetweenness):


	factions = sorted(set(FactionCharacters.keys()))

	# FactionPairsList = []
	# for faction1 in factions:
	# 	for faction2 in factions:
	# 		if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
	# 			FactionPairsList.append((faction1, faction2))

	CharacterNodes = sorted(set(Betweenness.keys()))
	characters = [character for character in CharacterNodes]

# Overall Betweenness pie chart for comparison

	figurecounter = 0
	TotalBetweenness = 0
	FactionTotals = dict()
	PercentagesOverall = dict()
	factionlist = [faction for faction in factions]
	#for pair in FactionPairsList:
		#CharacterTotals[faction1] = 0
		#for character in FactionCharacters[faction1]:

	for faction in factions:
		FactionTotals[faction] = 0
		for character in CharacterNodes:
			FactionTotals[faction] += FactionWorldBetweenness[faction][character]
		#CharacterTotals[faction1] += Betweenness[character]
	FactB = dict()
	for faction in factions:
		FactB[faction] = dict()
		for character in CharacterNodes:
			FactB[faction][character] = np.divide(FactionWorldBetweenness[faction][character], FactionTotals[faction])
	#for faction1 in factions:
	#	PercentagesOverall[character] = np.divide(FactionTotals[character],TotalBetweenness)

	###
	TotalBetweenness = np.sum(list(Betweenness.values()))
	NormBetweenness = dict()
	for character in CharacterNodes:
		NormBetweenness[character] = np.divide(Betweenness[character], TotalBetweenness)

	###

	try:
	    os.makedirs("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByCharacterPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	OverallPercentagesPie = [NormBetweenness[character] for character in CharacterNodes]
	fig = plt.figure(figurecounter)
	barwidth = 0.25
	plt.bar(np.linspace(1-barwidth/2, len(characters)-barwidth/2, len(characters)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
	#plt.pie(PercentagesPie, labels = factionlist, autopct='%1.1f%%', shadow = False, startangle = 90)
	ax = fig.gca()
	ax.set_xlabel('Faction')
	ax.set_ylabel('Fraction of total betweenness centrality')
	ax.set_xticks(np.linspace(1, len(characters), len(characters)))
	ax.set_xticklabels(characters, fontsize = 4, rotation = 'vertical')
	ax.set_title('Total betweenness centrality by faction')
	ax.set_xlim([0, len(characters)+1])
	plt.savefig("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByCharacterPlots/OverallBetweenness.png", bbox_inches='tight')
	plt.close()
	figurecounter += 1

#########################################################

	DifferenceFromOverall = dict()

	# Interfaction Betweenness pie charts
	FactionTotals = dict()
	Percentages = dict()
	betweennesstypecounter = 1
	for faction in factions:
	# 	TotalBetweenness = 0
	# 	FactionTotals[pair] = dict()
	# 	Percentages[pair] = dict()
	# 	DifferenceFromOverall[pair] = dict()
	# 	for faction1 in factions:
	# 		FactionTotals[pair][faction1] = 0
	# 		for character in FactionCharacters[faction1]:
	# 			FactionTotals[pair][faction1] += InterfactionBetweenness[pair][character]
	# 			TotalBetweenness += InterfactionBetweenness[pair][character]
	# 	factioncounter = 1
	# 	for faction1 in factions:
	# 		Percentages[pair][faction1] = np.divide(FactionTotals[pair][faction1],TotalBetweenness)
	# 		if PercentagesOverall[faction1] != 0:
	# 			DifferenceFromOverall[pair][faction1] = np.divide( Percentages[pair][faction1] - PercentagesOverall[faction1] , PercentagesOverall[faction1])
	# 		else:
	# 			DifferenceFromOverall[pair][faction1] = 0
	# #		if TotalBetweenness > 0:
	# #			ifbcsheet4.write(factioncounter,betweennesstypecounter+1,Percentages[pair][faction1])
	# 		factioncounter += 1
#		if (piecharts is True) and (TotalBetweenness > 0):
		PercentagesPie = [FactB[faction][character] for character in characters]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth, len(characters)-barwidth, len(characters)), OverallPercentagesPie, width = barwidth)
		plt.bar(np.linspace(1, len(characters), len(characters)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		#, autopct='%1.1f%%', shadow = False, startangle = 90)
		
		#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
		ax = fig.gca()
		ax.set_xlabel('Faction')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(characters), len(characters)))
		ax.set_xticklabels(characters, fontsize = 4, rotation = 'vertical')
		ax.set_title("Total " + faction + '-World betweenness centrality fractions by faction')
		ax.set_xlim([0, len(characters)+1])
		ax.set_ylim([0, 1])
		ax.legend(['Overall betweenness centrality', faction + '-World betweenness centrality'], fontsize = 6, loc = 'best')
		#ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByCharacterPlots/" + faction + "BetweennessByCharacter.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1
		betweennesstypecounter += 1
	#ifbcbook4.close()

	#DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	for character in CharacterNodes:
		totes0 += np.power(NormBetweenness[character],2)
	totes0 = np.sqrt(totes0)
	for faction in factions:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for character in CharacterNodes:
			#sumofsquares += np.power(DifferenceFromOverall[pair][character], 2)
			dotproduct += np.dot(FactB[faction][character], NormBetweenness[character])
			totes += np.power(FactB[faction][character], 2)
		#DistanceFromOverall[pair] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[faction] = np.divide(dotproduct, np.dot(totes0, totes))

	ibs = open("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessCharacterSimilarity.csv" , 'w')
	#for pair in sorted(DistanceFromOverall.keys(), key = lambda x: DistanceFromOverall[x], reverse = True):
	for faction in sorted(ProductOverall.keys(), key = lambda x: ProductOverall[x], reverse = False):
		ibs.write(faction + "," + str(ProductOverall[faction]) + "\n")
	ibs.close()	

	return PercentagesOverall, ProductOverall, FactB

###########################################################################

def FactionWorldBetweennessBreakdownByFaction(datasettag, FactionCharacters, Betweenness, FactionWorldBetweenness):


	factions = sorted(set(FactionCharacters.keys()))
	# FactionPairsList = []
	# for faction1 in factions:
	# 	for faction2 in factions:
	# 		if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
	# 			FactionPairsList.append((faction1, faction2))

# Overall Betweenness pie chart for comparison

	figurecounter = 0
	TotalBetweenness = 0
	FactionTotals = dict()
	PercentagesOverall = dict()
	factionlist = [faction for faction in factions]
	for faction1 in factions:
		FactionTotals[faction1] = 0
		for character in FactionCharacters[faction1]:
			FactionTotals[faction1] += Betweenness[character]
			TotalBetweenness += Betweenness[character]
	for faction1 in factions:
		PercentagesOverall[faction1] = np.divide(FactionTotals[faction1],TotalBetweenness)

	try:
	    os.makedirs("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByFactionPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	OverallPercentagesPie = [PercentagesOverall[faction1] for faction1 in factions]
	fig = plt.figure(figurecounter)
	barwidth = 0.25
	plt.bar(np.linspace(1-barwidth/2, len(factions)-barwidth/2, len(factions)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
	#plt.pie(PercentagesPie, labels = factionlist, autopct='%1.1f%%', shadow = False, startangle = 90)
	ax = fig.gca()
	ax.set_xlabel('Faction')
	ax.set_ylabel('Fraction of total betweenness centrality')
	ax.set_xticks(np.linspace(1, len(factions), len(factions)))
	ax.set_xticklabels(factionlist, fontsize = 6)
	ax.set_title('Total betweenness centrality by faction')
	ax.set_xlim([0, len(factions)+1])
	plt.savefig("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByFactionPlots/OverallBetweenness.png", bbox_inches='tight')
	plt.close()
	figurecounter += 1

#########################################################

	DifferenceFromOverall = dict()

	# Interfaction Betweenness pie charts
	FactionTotals = dict()
	Percentages = dict()
	betweennesstypecounter = 1
	for faction in factions:
		TotalBetweenness = 0
		FactionTotals[faction] = dict()
		Percentages[faction] = dict()
		DifferenceFromOverall[faction] = dict()
		for faction1 in factions:
			FactionTotals[faction][faction1] = 0
			for character in FactionCharacters[faction1]:
				FactionTotals[faction][faction1] += FactionWorldBetweenness[faction][character]
				TotalBetweenness += FactionWorldBetweenness[faction][character]
		factioncounter = 1
		for faction1 in factions:
			Percentages[faction][faction1] = np.divide(FactionTotals[faction][faction1],TotalBetweenness)
			if PercentagesOverall[faction1] != 0:
				DifferenceFromOverall[faction][faction1] = np.divide( Percentages[faction][faction1] - PercentagesOverall[faction1] , PercentagesOverall[faction1])
			else:
				DifferenceFromOverall[faction][faction1] = 0
	#		if TotalBetweenness > 0:
	#			ifbcsheet4.write(factioncounter,betweennesstypecounter+1,Percentages[pair][faction1])
			factioncounter += 1
#		if (piecharts is True) and (TotalBetweenness > 0):
		PercentagesPie = [Percentages[faction][faction1] for faction1 in factions]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth, len(factions)-barwidth, len(factions)), OverallPercentagesPie, width = barwidth)
		plt.bar(np.linspace(1, len(factions), len(factions)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		#, autopct='%1.1f%%', shadow = False, startangle = 90)
		
		#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
		ax = fig.gca()
		ax.set_xlabel('Faction')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(factions), len(factions)))
		ax.set_xticklabels(factionlist, fontsize = 6)
		ax.set_title("Total " + faction + '-World betweenness centrality fractions by faction')
		ax.set_xlim([0, len(factions)+1])
		ax.set_ylim([0, 1])
		ax.legend(['Overall betweenness centrality', faction + '-World betweenness centrality'], fontsize = 6, loc = 'best')
		#ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessByFactionPlots/" + faction + "WorldBetweennessByFaction.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1
		betweennesstypecounter += 1
	#ifbcbook4.close()

	DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	for faction in factions:
		totes0 += np.power(PercentagesOverall[faction],2)
	totes0 = np.sqrt(totes0)
	for faction in factions:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for faction1 in factions:
			sumofsquares += np.power(DifferenceFromOverall[faction][faction1], 2)
			dotproduct += np.dot(Percentages[faction][faction1], PercentagesOverall[faction1])
			totes += np.power(Percentages[faction][faction1], 2)
		DistanceFromOverall[faction] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[faction] = np.divide(dotproduct, np.dot(totes0, totes))

	ibs = open("../Outputs/" + datasettag + "/FactionWorldBetweenness/FactionWorldBetweennessFactionSimilarity.csv" , 'w')
	#for pair in sorted(DistanceFromOverall.keys(), key = lambda x: DistanceFromOverall[x], reverse = True):
	for faction in sorted(ProductOverall.keys(), key = lambda x: ProductOverall[x], reverse = False):
		ibs.write(faction + "," + str(ProductOverall[faction]) + "\n")
	ibs.close()	

	return PercentagesOverall, ProductOverall, Percentages

###########################################################################
###########################################################################

def CharacterBetweennessBreakdown(datasettag, FactionCharacters, Betweenness, InterfactionBetweenness, GI):

	# since dealing with faction pairs, think of doing heat maps instead of bar charts

	CharacterNodes = sorted(set(Betweenness.keys()))

	factions = sorted(set(FactionCharacters.keys()))
	FactionPairsList = []
	for faction1 in factions:
		for faction2 in factions:
			if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
				FactionPairsList.append((faction1, faction2))


	InterfactionBetweennessFractions = dict()
	for pair in FactionPairsList:
		BetweennessSTsum = sum(InterfactionBetweenness[pair].values())
		InterfactionBetweennessFractions[pair] = dict() 
		if BetweennessSTsum > 0:
			for c in CharacterNodes:
				InterfactionBetweennessFractions[pair][c] = np.divide(InterfactionBetweenness[pair][c], BetweennessSTsum)

	# Interfaction Betweenness pie charts

	TotalInterfactionBetweenness = dict()
	for pair in FactionPairsList:
		if pair[0] == pair[1]:
			TotalInterfactionBetweenness[pair] = np.sum(list(InterfactionBetweenness[pair].values()))
		else:
			TotalInterfactionBetweenness[pair] = 2*np.sum(list(InterfactionBetweenness[pair].values()))
	TotalBetweenness = np.sum(list(Betweenness.values()))

	TotalInterfactionBetweennessNormalized = dict()
	for pair in FactionPairsList:
		TotalInterfactionBetweennessNormalized[pair] = np.divide(TotalInterfactionBetweenness[pair], np.sum(list(TotalInterfactionBetweenness.values())))

	try:
	    os.makedirs("../Outputs/" + datasettag + "/InterfactionBetweenness/CharacterBetweennessInterfactionBreakdownPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	figurecounter = 0
	OverallPercentagesPie = [TotalInterfactionBetweennessNormalized[pair] for pair in FactionPairsList]
	factionpairs = [(pair[0] + "-" + pair[1]) for pair in FactionPairsList]
	fig = plt.figure(figurecounter)
	barwidth = 0.25
	plt.bar(np.linspace(1-barwidth/2, len(factionpairs)-barwidth/2, len(factionpairs)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
	#plt.pie(PercentagesPie, labels = factionlist, autopct='%1.1f%%', shadow = False, startangle = 90)
	ax = fig.gca()
	ax.set_xlabel('Faction')
	ax.set_ylabel('Fraction of total betweenness centrality')
	ax.set_xticks(np.linspace(1, len(factionpairs), len(factionpairs)))
	ax.set_xticklabels(factionpairs, fontsize = 5, rotation = 'vertical')
	ax.set_title('Total betweenness centrality by faction')
	ax.set_xlim([0, len(factionpairs)+1])
	plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/CharacterBetweennessInterfactionBreakdownPlots/OverallBetweennessBreakdown.png", bbox_inches='tight')
	plt.close()
	figurecounter += 1

	##################################

	CharacterTotals = dict()
	Percentages = dict()
	betweennesstypecounter = 1
	for character in CharacterNodes:
		TotalBetweenness = 0
		CharacterTotals[character] = dict()
		Percentages[character] = dict()
		for pair in FactionPairsList:
			CharacterTotals[character][pair] = InterfactionBetweenness[pair][character]
			if pair[0] == pair[1]:
				Percentages[character][pair] = np.divide(InterfactionBetweenness[pair][character], Betweenness[character])
				TotalBetweenness += InterfactionBetweenness[pair][character]
			else:
				Percentages[character][pair] = np.divide(2*InterfactionBetweenness[pair][character], Betweenness[character])
				TotalBetweenness += 2*InterfactionBetweenness[pair][character]
		factioncounter = 1
		if (TotalBetweenness > 0):
			PercentagesPie = [Percentages[character][pair] for pair in FactionPairsList]
			fig = plt.figure(figurecounter)
			#plt.pie(PercentagesPie, labels=FactionPairsList,autopct='%1.1f%%', shadow=False, startangle=90)

			plt.bar(np.linspace(1-barwidth, len(factionpairs)-barwidth, len(factionpairs)), OverallPercentagesPie, width = barwidth)
			plt.bar(np.linspace(1, len(factionpairs), len(factionpairs)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
			#, autopct='%1.1f%%', shadow = False, startangle = 90)

			#plt.pie(PercentagesPie, labels=factionlist,autopct='%1.1f%%', shadow=False, startangle=90)
			ax = fig.gca()
			ax.set_xlabel('Interfaction pair')
			ax.set_ylabel('Fraction of total betweenness centrality')
			ax.set_xticks(np.linspace(1, len(factionpairs), len(factionpairs)))
			ax.set_xticklabels(factionpairs, fontsize = 5, rotation = 'vertical')
			ax.set_title(character + " betweenness centrality breakdown")
			ax.set_xlim([0, len(factionpairs)+1])
			#ax.set_ylim([0, 1])
			ax.legend(['Overall betweenness centrality breakdown', character + ' betweenness centrality breakdown'], fontsize = 6, loc = 'best')
			#ax.set_aspect('equal')
			plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/CharacterBetweennessInterfactionBreakdownPlots/" + character + "BetweennessByFaction.png", bbox_inches='tight')
			plt.close()
			#ax.set_aspect('equal')
			#plt.title('Total betweenness centrality : ' + str(Betweenness0[character]))
			#plt.savefig("../Outputs/" + window + "/PieCharts/InterfactionByCharacter/" + character + "Betweenness" + window + '.png', bbox_inches='tight')
			#plt.close()
			figurecounter += 1
		betweennesstypecounter +=1

	DistanceFromOverall = dict()
	ProductOverall = dict()
	totallength = dict()
	totes0 = 0
	for pair in FactionPairsList:
		totes0 += np.power(TotalInterfactionBetweennessNormalized[pair], 2)
	totes0 = np.sqrt(totes0)
	for character in CharacterNodes:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for pair in FactionPairsList:
			#sumofsquares += np.power(DifferenceFromOverall[pair][faction], 2)
			dotproduct += np.dot(Percentages[character][pair], TotalInterfactionBetweennessNormalized[pair])
			totes += np.power(Percentages[character][pair], 2)
		#DistanceFromOverall[character] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[character] = np.divide(dotproduct, np.dot(totes0, totes))

	ProductOverall0 = {k: ProductOverall[k] for k in ProductOverall if not np.isnan(ProductOverall[k])}

	#CharacterEccentricity = nx.eccentricity(GI)
	CharacterCloseness = nx.closeness_centrality(GI, normalized = True)

	ibs = open("../Outputs/" + datasettag + "/InterfactionBetweenness/CharacterBetweennessBreakdownSimilarity.csv" , 'w')
	for character in sorted(ProductOverall0.keys(), key = lambda x: ProductOverall0[x], reverse = False):
		if ( Betweenness[character] > 0 ):
			#print(character  + " : " + str(ProductOverall[character]) + " ; " + str(Betweenness[character]))
			ibs.write(character + "," + str(ProductOverall0[character]) + "," + str(Betweenness[character]) + "\n" )#+ "," + str(CharacterEccentricity[character]) + "," + str(CharacterCloseness[character]) + "\n")
	ibs.close()	

	###############################

	#FactionBreakdown
	InterfactionBetweennessFaction = dict()
	for faction in factions:
		InterfactionBetweennessFaction[faction] = dict()
		for pair in FactionPairsList:
			InterfactionBetweennessFaction[faction][pair] = 0
			for character in FactionCharacters[faction]:
				InterfactionBetweennessFaction[faction][pair] += InterfactionBetweenness[pair][character]

	InterfactionBetweennessFactionNormalized = dict()
	for faction in factions:
		InterfactionBetweennessFactionNormalized[faction] = dict()
		for pair in FactionPairsList:
			InterfactionBetweennessFactionNormalized[faction][pair] = np.divide( InterfactionBetweennessFaction[faction][pair], np.sum(list(InterfactionBetweennessFaction[faction].values())) )

	try:
	    os.makedirs("../Outputs/" + datasettag + "/InterfactionBetweenness/FactionTotalsBetweennessInterfactionBreakdownPlots/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	for faction in factions:
		PercentagesPie = [InterfactionBetweennessFactionNormalized[faction][pair] for pair in FactionPairsList]
		fig = plt.figure(figurecounter)
		plt.bar(np.linspace(1-barwidth/2, len(factionpairs)-barwidth/2, len(factionpairs)), OverallPercentagesPie, width = barwidth)#, autopct='%1.1f%%', shadow = False, startangle = 90)
		plt.bar(np.linspace(1, len(factionpairs), len(factionpairs)), PercentagesPie, width = barwidth, color = 'red')#, autopct='%1.1f%%', shadow = False, startangle = 90)
		ax = fig.gca()
		ax.set_xlabel('Interfaction pair')
		ax.set_ylabel('Fraction of total betweenness centrality')
		ax.set_xticks(np.linspace(1, len(factionpairs), len(factionpairs)))
		ax.set_xticklabels(factionpairs, fontsize = 5, rotation = 'vertical')
		ax.set_title('Total interfaction betweenness centrality of faction ' + faction)
		ax.set_xlim([0, len(factionpairs)+1])
		ax.legend(['Betweenness centrality breakdown by faction', faction + ' betweenness centrality breakdown'], fontsize = 6, loc = 'best')
		plt.savefig("../Outputs/" + datasettag + "/InterfactionBetweenness/FactionTotalsBetweennessInterfactionBreakdownPlots/" + faction + "BetweennessBreakdown.png", bbox_inches='tight')
		plt.close()
		figurecounter += 1


	ProductOverall = dict()
	totallength = dict()
	#totes0 = 0
	#for faction in factions:
	#	totes0 += np.power(TotalInterfactionBetweennessFactionNormalized[faction][pair], 2)
	#totes0 = np.sqrt(totes0)
	for faction in factions:
		sumofsquares = 0
		dotproduct = 0
		totes = 0
		for pair in FactionPairsList:
			#sumofsquares += np.power(DifferenceFromOverall[pair][faction], 2)
			dotproduct += np.dot(InterfactionBetweennessFactionNormalized[faction][pair], TotalInterfactionBetweennessNormalized[pair])
			totes += np.power(InterfactionBetweennessFactionNormalized[faction][pair], 2)
		#DistanceFromOverall[character] = np.abs(sumofsquares) #np.sqrt(sumofsquares)
		totes = np.sqrt(totes)
		ProductOverall[faction] = np.divide(dotproduct, np.dot(totes0, totes))

	ProductOverall0 = {k: ProductOverall[k] for k in ProductOverall if not np.isnan(ProductOverall[k])}

	# factioneccentricity = dict()
	# factioncloseness = dict()
	# for faction in factions:
	# 	ecc = 0
	# 	clo = 0
	# 	for character in FactionCharacters[faction]:
	# 		ecc += CharacterEccentricity[character]
	# 		clo += CharacterCloseness[character]
		#factioneccentricity[faction] = np.divide(ecc, len(list(FactionCharacters[faction])))
		#factioncloseness[faction] = np.divide(clo, len(list(FactionCharacters[faction])))

	ibs = open("../Outputs/" + datasettag + "/InterfactionBetweenness/FactionBetweennessBreakdownSimilarity.csv" , 'w')
	for faction in sorted(ProductOverall0.keys(), key = lambda x: ProductOverall0[x], reverse = False):
		#if ( Betweenness[character] > 0 ):
			#print(character  + " : " + str(ProductOverall[character]) + " ; " + str(Betweenness[character]))
		ibs.write(faction + "," + str(ProductOverall0[faction]) + "\n")#," + str(factioneccentricity[faction]) + "," + str(factioncloseness[faction]) + "\n")
	ibs.close()	


	#return Percentages

###########################################################################


def FactionWorldBetweennessCentrality(GI, FactionCharacters):

	CharacterNodes = GI.nodes()

	factions = sorted(set(FactionCharacters.keys()))
	FactionWorldBetweenness = dict()
	for faction in factions:
		factioncharacters = [str(x) for x in FactionCharacters[faction]]
		worldcharacters = [str(x) for x in (set(CharacterNodes) - set(factioncharacters))] 
		FWB = nx.betweenness_centrality_subset(GI, factioncharacters, worldcharacters, normalized = True, weight = 'weight')
		FactionWorldBetweenness[faction] = FWB

	return FactionWorldBetweenness

###########################################################################

###########################################################################
# Null model
###########################################################################
###########################################################################

def BipartiteConfigurationModelGenerate(EpisodeDegrees, CharacterDegrees):

	EpisodeNodes = EpisodeDegrees.keys()
	CharacterNodes = CharacterDegrees.keys()

	C = nx.Graph()
	C.add_nodes_from(CharacterDegrees.keys())
	C.add_nodes_from(EpisodeDegrees.keys())

	NumberOfLinks = sum(CharacterDegrees.values())

	# Consider each character-episode pair and realize a link with probability
	# according to configuration model:

	for character in CharacterNodes:
		for episode in EpisodeNodes: 
			if (np.random.random() < np.divide(np.multiply(float(CharacterDegrees[character]), float(EpisodeDegrees[episode])), float(NumberOfLinks))):
				C.add_edge(character, episode)

	return C

###########################################################################

def BipartiteConfigurationModelRealization(EpisodeDegreesTarget, CharacterDegreesTarget, FactionCharacters = 0, links = 0, episodes = 0):

	EpisodeNodes = EpisodeDegreesTarget.keys()
	CharacterNodes = CharacterDegreesTarget.keys()

	B = BipartiteConfigurationModelGenerate(EpisodeDegreesTarget, CharacterDegreesTarget)
	G = CharacterCooccurrenceNetwork(B, EpisodeNodes, CharacterNodes)
	GI = InverseWeightCooccurrenceNetwork(G)
	if (episodes != 0):
		E = EpisodeIntersectionNetwork(B, EpisodeNodes, CharacterNodes)
		EI = InverseWeightCooccurrenceNetwork(E)

	EpisodeStrength = []
	EpisodeBetweenness = []

	Degrees = nx.degree(B)
	CharacterDegrees = dict()
	for character in CharacterNodes:
		CharacterDegrees[character] = Degrees[character]
	EpisodeDegrees = dict()
	for episode in EpisodeNodes:
		EpisodeDegrees[episode] = Degrees[episode]

	LinkWeights = []
	LinkBetweenness = []
	LinkDegreeProduct = []
	CharacterStrength = nx.degree(G, weight = 'weight')
	CharacterBetweenness = nx.betweenness_centrality(GI, weight = 'weight', normalized = True)
	if (episodes != 0):
		EpisodeStrength = nx.degree(E, weight = 'weight')
		EpisodeBetweenness = nx.betweenness_centrality(EI, weight = 'weight', normalized = True)

	#oooooooooooooooooooooooooooooooooooo
	if (links != 0):
		LinkBetweenness = nx.edge_betweenness_centrality(GI, weight = 'weight', normalized = True)
		LinkWeights = dict()#nx.edge_weight(G)
		LinkDegreeProduct = dict()
		for edge in LinkBetweenness.keys(): #G.edges():
			LinkWeights[edge] = G[edge[0]][edge[1]]['weight']
			LinkDegreeProduct[edge] = np.dot(CharacterDegrees[edge[0]], CharacterDegrees[edge[1]])
		
	#oooooooooooooooooooooooooooooooooooo

	NumberOfLinks = len(B.edges())

	InterfactionBetweenness = []
	FactionWorldBetweenness = []

	################################# if factions are specified:

	if (FactionCharacters != 0):

		InterfactionBetweenness = InterfactionBetweennessCentrality(GI, FactionCharacters)

		FactionWorldBetweenness = FactionWorldBetweennessCentrality(GI, FactionCharacters)

		# factions = sorted(set(FactionCharacters.keys()))
		# FactionPairsList = []
		# for faction1 in factions:
		# 	for faction2 in factions:
		# 		if (not (faction1, faction2) in FactionPairsList) and (not (faction2, faction1) in FactionPairsList):
		# 			FactionPairsList.append((faction1, faction2))

		# InterfactionBetweenness = dict()
		# for pair in FactionPairsList:
		# 	factionScharacters = [str(x) for x in FactionCharacters[pair[0]]]
		# 	factionTcharacters = [str(x) for x in FactionCharacters[pair[1]]]
		# 	IFB = nx.betweenness_centrality_subset(GI, factionScharacters, factionTcharacters, normalized = True, weight = 'weight')
		# 	InterfactionBetweenness[pair] = IFB
		# FactionWorldBetweenness = dict()
		# for faction in factions:
		# 	factioncharacters = [str(x) for x in FactionCharacters[faction]]
		# 	worldcharacters = [str(x) for x in (set(CharacterNodes) - set(factioncharacters))] 
		# 	FWB = nx.betweenness_centrality_subset(GI, factioncharacters, worldcharacters, normalized = True, weight = 'weight')
		# 	FactionWorldBetweenness[faction] = FWB

	#################################

	return CharacterDegrees, CharacterStrength, CharacterBetweenness, NumberOfLinks, InterfactionBetweenness, FactionWorldBetweenness, LinkWeights, LinkDegreeProduct, LinkBetweenness, EpisodeDegrees, EpisodeStrength, EpisodeBetweenness

###########################################################################

def NullModelEnsemble(datasettag, ensembletag, EpisodeDegreesTarget, CharacterDegreesTarget, NumberOfRealizations, FactionCharacters = 0, LinkWeightsTarget = [], episodes = 0):

	if LinkWeightsTarget:
		links = 1
	else:
		links = 0

	EpisodeNodes = EpisodeDegreesTarget.keys()
	CharacterNodes = CharacterDegreesTarget.keys()

	try:
		os.makedirs("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/")
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
	# allow for appending to existing dataset for separate sessions

	CharacterDegreeEnsemble = dict()
	CharacterStrengthEnsemble = dict()
	CharacterBetweennessEnsemble = dict()
	NumberOfLinksEnsemble = [] 

	for character in CharacterNodes:
		CharacterDegreeEnsemble[character] = []
		CharacterStrengthEnsemble[character] = []
		CharacterBetweennessEnsemble[character] = []

	EpisodeDegreeEnsemble = []
	EpisodeStrengthEnsemble = []
	EpisodeBetweennessEnsemble = []
	if (episodes != 0):
		EpisodeDegreeEnsemble = dict()
		EpisodeStrengthEnsemble = dict()
		EpisodeBetweennessEnsemble = dict()
		for episode in EpisodeNodes:
			EpisodeDegreeEnsemble[episode] = []
			EpisodeStrengthEnsemble[episode] = []
			EpisodeBetweennessEnsemble[episode] = []


	#ooooooooooooooooooooooooooooooooooooooo
	LinkWeightsEnsemble = []
	LinkDegreeProductEnsemble = []
	LinkBetweennessEnsemble = []
	if LinkWeightsTarget:
		LinkWeightsEnsemble = dict()
		LinkDegreeProductEnsemble = dict()
		LinkBetweennessEnsemble = dict()	
		for edge in LinkWeightsTarget.keys():
			LinkWeightsEnsemble[edge] = []
			LinkDegreeProductEnsemble[edge] = []
			LinkBetweennessEnsemble[edge] = []			
	#ooooooooooooooooooooooooooooooooooooooo

	InterfactionBetweennessEnsemble = []
	FactionWorldBetweennessEnsemble = []

	########################

	if (FactionCharacters != 0):
		factions = sorted(set(FactionCharacters.keys()))
		FactionPairsList = []
		for faction1 in factions:
			for faction2 in factions:
				if ((faction1, faction2) not in FactionPairsList) and ((faction2, faction1) not in FactionPairsList):
					FactionPairsList.append((faction1, faction2))
		InterfactionBetweennessEnsemble = dict()
		for pair in FactionPairsList:
			InterfactionBetweennessEnsemble[pair] = dict()
			for character in CharacterNodes:
				InterfactionBetweennessEnsemble[pair][character] = []
		FactionWorldBetweennessEnsemble = dict()
		for faction in FactionCharacters.keys():
			FactionWorldBetweennessEnsemble[faction] = dict()
			for character in CharacterNodes:
				FactionWorldBetweennessEnsemble[faction][character] = []

	############################

	for r in range(int(NumberOfRealizations)):
		
		print("Processing realization " + str(r+1) + " of " + str(NumberOfRealizations))
		
		CharacterDegrees, CharacterStrength, CharacterBetweenness, NumberOfLinks, InterfactionBetweenness, FactionWorldBetweenness, LinkWeights, LinkDegreeProduct, LinkBetweenness, EpisodeDegrees, EpisodeStrength, EpisodeBetweenness = BipartiteConfigurationModelRealization(EpisodeDegreesTarget, CharacterDegreesTarget, FactionCharacters, links, episodes)
		
		NumberOfLinksEnsemble.extend([NumberOfLinks])
		for character in CharacterNodes:
			CharacterDegreeEnsemble[character].extend([CharacterDegrees[character]])
			CharacterStrengthEnsemble[character].extend([CharacterStrength[character]])
			CharacterBetweennessEnsemble[character].extend([CharacterBetweenness[character]])

		if EpisodeBetweenness:
			for episode in EpisodeNodes:
				EpisodeDegreeEnsemble[episode].extend([EpisodeDegrees[episode]])
				EpisodeStrengthEnsemble[episode].extend([EpisodeStrength[episode]])
				EpisodeBetweennessEnsemble[episode].extend([EpisodeBetweenness[episode]])

		#######################################################################################

		if InterfactionBetweenness:
			for pair in InterfactionBetweenness.keys():
				for character in CharacterDegrees.keys():
					InterfactionBetweennessEnsemble[pair][character].extend([InterfactionBetweenness[pair][character]])
		if FactionWorldBetweenness:
			for faction in FactionCharacters.keys():
				for character in CharacterDegrees:
					FactionWorldBetweennessEnsemble[faction][character].extend([FactionWorldBetweenness[faction][character]])

		#######################################################################################

		#ooooooooooooooooooooooooooooooooooooo
		if LinkWeightsTarget:
			for edge in LinkWeightsTarget.keys():
				if (edge in LinkWeights.keys()):
					LinkWeightsEnsemble[edge].extend([LinkWeights[edge]])
					LinkDegreeProductEnsemble[edge].extend([LinkDegreeProduct[edge]])
					LinkBetweennessEnsemble[edge].extend([LinkBetweenness[edge]])
				else:
					LinkWeightsEnsemble[edge].extend([0])
					LinkDegreeProductEnsemble[edge].extend([np.dot(CharacterDegrees[edge[0]], CharacterDegrees[edge[0]])])
					LinkBetweennessEnsemble[edge].extend([0])
		#ooooooooooooooooooooooooooooooooooooo

	if os.path.exists("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Degrees.pkl"):

		CharacterDegreeEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Degrees.pkl","rb"))
		CharacterStrengthEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Strengths.pkl","rb"))
		CharacterBetweennessEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Betweenness.pkl","rb"))	
		NumberOfLinksEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","rb"))
		for character in CharacterNodes:
			CharacterDegreeEnsemble[character].extend(CharacterDegreeEnsemble0[character])
			CharacterStrengthEnsemble[character].extend(CharacterStrengthEnsemble0[character])
			CharacterBetweennessEnsemble[character].extend(CharacterBetweennessEnsemble0[character])
	pk.dump( CharacterDegreeEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Degrees.pkl","wb"))
	pk.dump( CharacterStrengthEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Strengths.pkl","wb"))
	pk.dump( CharacterBetweennessEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Betweenness.pkl","wb"))
	pk.dump( NumberOfLinksEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","wb"))

	if EpisodeBetweennessEnsemble:
		if os.path.exists("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeDegrees.pkl"):
			EpisodeDegreeEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeDegrees.pkl","rb"))
			EpisodeStrengthEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeStrengths.pkl","rb"))
			EpisodeBetweennessEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeBetweenness.pkl","rb"))	
			for episode in EpisodeNodes:
				EpisodeDegreeEnsemble[episode].extend(EpisodeDegreeEnsemble0[episode])
				EpisodeStrengthEnsemble[episode].extend(EpisodeStrengthEnsemble0[episode])
				EpisodeBetweennessEnsemble[episode].extend(EpisodeBetweennessEnsemble0[episode])
		pk.dump( EpisodeDegreeEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeDegrees.pkl","wb"))
		pk.dump( EpisodeStrengthEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeStrengths.pkl","wb"))
		pk.dump( EpisodeBetweennessEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeBetweenness.pkl","wb"))


	######################################

	if InterfactionBetweennessEnsemble:
		if os.path.exists("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_InterfactionBetweenness.pkl"):
			InterfactionBetweennessEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_InterfactionBetweenness.pkl","rb"))
			for pair in InterfactionBetweennessEnsemble.keys():
				for character in CharacterNodes:
					InterfactionBetweennessEnsemble[pair][character].extend(InterfactionBetweennessEnsemble0[pair][character])
		pk.dump( InterfactionBetweennessEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_InterfactionBetweenness.pkl","wb"))
	if FactionWorldBetweennessEnsemble:
		if os.path.exists("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_FactionWorldBetweenness.pkl"):
			FactionWorldBetweennessEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_FactionWorldBetweenness.pkl","rb"))
			for faction in FactionWorldBetweennessEnsemble.keys():
				for character in CharacterNodes:
					FactionWorldBetweennessEnsemble[faction][character].extend(FactionWorldBetweennessEnsemble0[faction][character])
		pk.dump( FactionWorldBetweennessEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_FactionWorldBetweenness.pkl","wb"))

	#######################################
	#
	if LinkWeightsTarget:
		if os.path.exists("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl"):
			LinkWeightsEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl","rb"))
			LinkDegreeProductEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkDegreeProduct.pkl","rb"))
			LinkBetweennessEnsemble0 = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkBetweenness.pkl","rb"))
			for edge in LinkWeightsTarget.keys():
				if edge in LinkWeightsEnsemble0.keys():
					LinkWeightsEnsemble[edge].extend(LinkWeightsEnsemble0[edge])
					LinkDegreeProductEnsemble[edge].extend(LinkDegreeProductEnsemble0[edge])
					LinkBetweennessEnsemble[edge].extend(LinkBetweennessEnsemble0[edge])
				else:
					redge = (edge[1], edge[0])
					LinkWeightsEnsemble[edge].extend(LinkWeightsEnsemble0[redge])
					LinkDegreeProductEnsemble[edge].extend(LinkDegreeProductEnsemble0[redge])
					LinkBetweennessEnsemble[edge].extend(LinkBetweennessEnsemble0[redge])
		pk.dump( LinkWeightsEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl","wb"))
		pk.dump( LinkDegreeProductEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkDegreeProduct.pkl","wb"))
		pk.dump( LinkBetweennessEnsemble, open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkBetweenness.pkl","wb"))
	#ooooooooooooooooooooooooooooooooooooo

	return CharacterDegreeEnsemble, CharacterStrengthEnsemble, CharacterBetweennessEnsemble, NumberOfLinksEnsemble, InterfactionBetweennessEnsemble, FactionWorldBetweennessEnsemble, LinkWeightsEnsemble, LinkDegreeProductEnsemble, LinkBetweennessEnsemble, EpisodeDegreeEnsemble, EpisodeStrengthEnsemble, EpisodeBetweennessEnsemble # write direct to file instead?

###########################################################################

def NullModelEnsembleProcess(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness, InterfactionBetweenness = [], FactionWorldBetweenness = [], LinkWeights = [], LinkDegreeProduct = [], LinkBetweenness = [], EpisodeDegrees = [], EpisodeStrengths = [], EpisodeBetweenness = []): # consider using pickle to retrieve target degrees, link weights etc.

	CharacterDegreeEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Degrees.pkl","rb"))
	CharacterStrengthEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Strengths.pkl","rb"))
	CharacterBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Betweenness.pkl","rb"))	
	NumberOfLinksEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","rb"))

	CharacterNodes = CharacterDegreeEnsemble.keys()

	EnsembleSize = len(CharacterDegreeEnsemble[list(CharacterNodes)[0]])

	if EpisodeStrengths:
		EpisodeDegreeEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeDegrees.pkl","rb"))
		EpisodeStrengthEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeStrengths.pkl","rb"))
		EpisodeBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeBetweenness.pkl","rb"))	
		EpisodeNodes = EpisodeDegreeEnsemble.keys()

	CharacterDegreeEnsembleMeans = dict()
	CharacterDegreeEnsembleSTD = dict()
	NodeStrengthEnsembleMeans = dict()
	NodeStrengthEnsembleSTD = dict()
	NodeStrengthSigma = dict()
	BetweennessEnsembleMeans = dict()
	BetweennessEnsembleSTD = dict()
	BetweennessEnsembleSigma = dict()

	EpisodeDegreeEnsembleMeans = []
	EpisodeDegreeEnsembleSTD = []
	EpisodeDegreeEnsembleSigma = []
	EpisodeStrengthEnsembleMeans = []
	EpisodeStrengthEnsembleSTD = []
	EpisodeStrengthEnsembleSigma = []
	EpisodeBetweennessEnsembleMeans = []
	EpisodeBetweennessEnsembleSTD = []
	EpisodeBetweennessEnsembleSigma = [] 

	InterfactionEnsembleMeans = []
	InterfactionEnsembleSTD = []
	InterfactionEnsembleSigma = []
	FactionWorldEnsembleMeans = []
	FactionWorldEnsembleSTD = []
	FactionWorldEnsembleSigma = []

	LinkWeightEnsembleMeans = []
	LinkWeightEnsembleSTD = []
	LinkWeightEnsembleSigma = []
	LinkDegreeProductEnsembleMeans = []
	LinkDegreeProductEnsembleSTD = []
	LinkDegreeProductEnsembleSigma = []
	LinkBetweennessEnsembleMeans = []
	LinkBetweennessEnsembleSTD = []
	LinkBetweennessEnsembleSigma = []


	if EpisodeStrengths:
		EpisodeDegreeEnsembleMeans = dict()
		EpisodeDegreeEnsembleSTD = dict()
		EpisodeDegreeEnsembleSigma = dict()
		EpisodeStrengthEnsembleMeans = dict()
		EpisodeStrengthEnsembleSTD = dict()
		EpisodeStrengthEnsembleSigma = dict()
		EpisodeBetweennessEnsembleMeans = dict()
		EpisodeBetweennessEnsembleSTD = dict()
		EpisodeBetweennessEnsembleSigma = dict()

		Pvalues = dict()
		for episode in EpisodeNodes:
			EpisodeDegreeEnsembleMeans[episode] = np.mean(EpisodeDegreeEnsemble[episode])
			EpisodeDegreeEnsembleSTD[episode] = np.std(EpisodeDegreeEnsemble[episode])
			EpisodeStrengthEnsembleMeans[episode] = np.mean(EpisodeStrengthEnsemble[episode])
			EpisodeStrengthEnsembleSTD[episode] = np.std(EpisodeStrengthEnsemble[episode])
			EpisodeBetweennessEnsembleMeans[episode] = np.mean(EpisodeBetweennessEnsemble[episode])
			EpisodeBetweennessEnsembleSTD[episode] = np.std(EpisodeBetweennessEnsemble[episode])
			if (EpisodeDegreeEnsembleSTD[episode] > 0):
				EpisodeDegreeEnsembleSigma[episode] = np.divide(EpisodeDegrees[episode] - EpisodeDegreeEnsembleMeans[episode],EpisodeDegreeEnsembleSTD[episode])
			else:
				EpisodeDegreeEnsembleSigma[episode] = 0
			if (EpisodeStrengthEnsembleSTD[episode] > 0):
				EpisodeStrengthEnsembleSigma[episode] = np.divide(EpisodeStrengths[episode] - EpisodeStrengthEnsembleMeans[episode],EpisodeStrengthEnsembleSTD[episode])
			else:
				EpisodeStrengthEnsembleSigma[episode] = 0
			if (EpisodeBetweennessEnsembleSTD[episode] > 0):
				EpisodeBetweennessEnsembleSigma[episode] = np.divide(EpisodeBetweenness[episode] - EpisodeBetweennessEnsembleMeans[episode],EpisodeBetweennessEnsembleSTD[episode])
			else:
				EpisodeBetweennessEnsembleSigma[episode] = 0


			if (np.max(np.max(EpisodeBetweennessEnsemble[episode]),2*EpisodeBetweenness[episode]) > 0):
				bins = np.linspace(0,np.max(np.max(EpisodeBetweennessEnsemble[episode]),2*EpisodeBetweenness[episode]),30, endpoint = True)
				freaq= plt.hist(EpisodeBetweennessEnsemble[episode], bins)
				plt.close()
				plt.figure(14)
				#bincenters = 0.5*(bins[1:]+bins[:-1])
				#totalfreq = np.sum(freaq[0])
				cumsumkasar = np.concatenate(([0],list(np.cumsum(freaq[0]))))
				#plt.plot(bins, cumsumkasar)
				binshalus = np.linspace(np.min(0),np.max(bins),1000, endpoint = True)
				cumsumhalus = interpolate.pchip_interpolate(bins, cumsumkasar, binshalus)
				cumsumhalusn = [np.divide(c, np.max(cumsumhalus)) for c in cumsumhalus]
				aindec = list(binshalus).index(min(binshalus, key=lambda x:abs(x-EpisodeBetweenness[episode])))
				pval = (cumsumhalusn[aindec])
				plt.plot(binshalus, cumsumhalusn)
				plt.plot([EpisodeBetweenness[episode], EpisodeBetweenness[episode]],[0, 1],'r-')
				plt.plot([binshalus[aindec], binshalus[aindec]],[0, 1],'g-')
				#plt.pause(0.1)
				plt.close()
				#plt.plot([EpisodeBetweenness[episode]],[.5],'ro')
				Pvalues[episode] = pval
				#print(pval)
			else:
				Pvalues[episode] = -1.0		

		er = open("../Outputs/" + datasettag + "/EpisodeBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
		er.write("Episode, Number of Characters, Ensemble mean number of Characters, Ensemble characters standard deviation, Episode Node Strength, Ensemble episode mean node strength, Ensemble episode node strength standard deviation, Betweenness centrality, Ensemble Mean Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean\n")
		for episode in sorted(EpisodeBetweennessEnsembleSigma.keys(), key = lambda x: EpisodeBetweennessEnsembleSigma[x], reverse = True):
			er.write(str(episode) + "," + str(EpisodeDegrees[episode]) + "," + str(EpisodeDegreeEnsembleMeans[episode]) + "," + str(EpisodeDegreeEnsembleSTD[episode]) + "," + str(EpisodeStrengths[episode]) + "," + str(EpisodeStrengthEnsembleMeans[episode]) + "," +  str(EpisodeStrengthEnsembleSTD[episode]) + "," + str(EpisodeBetweenness[episode]) + "," + str(EpisodeBetweennessEnsembleMeans[episode]) + "," + str(EpisodeBetweennessEnsembleSTD[episode]) + "," + str(EpisodeBetweennessEnsembleSigma[episode]) + "\n")
		er.close()

		er = open("../Outputs/" + datasettag + "/NEWEpisodeBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
		er.write("Episode, Number of Characters, Ensemble mean number of Characters, Ensemble characters standard deviation, Episode Node Strength, Ensemble episode mean node strength, Ensemble episode node strength standard deviation, Betweenness centrality, Ensemble Mean Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean, P-value\n")
		for episode in sorted(EpisodeBetweennessEnsembleSigma.keys(), key = lambda x: (Pvalues[x], EpisodeBetweennessEnsembleSigma[x]), reverse = True):
			er.write(str(episode) + "," + str(EpisodeDegrees[episode]) + "," + str(EpisodeDegreeEnsembleMeans[episode]) + "," + str(EpisodeDegreeEnsembleSTD[episode]) + "," + str(EpisodeStrengths[episode]) + "," + str(EpisodeStrengthEnsembleMeans[episode]) + "," +  str(EpisodeStrengthEnsembleSTD[episode]) + "," + str(EpisodeBetweenness[episode]) + "," + str(EpisodeBetweennessEnsembleMeans[episode]) + "," + str(EpisodeBetweennessEnsembleSTD[episode]) + "," + str(EpisodeBetweennessEnsembleSigma[episode]) + "," + str(Pvalues[episode]) + "\n")
		er.close()


	###################

	if InterfactionBetweenness:
		InterfactionBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_InterfactionBetweenness.pkl","rb"))
		InterfactionEnsembleMeans = dict()
		InterfactionEnsembleSTD = dict()
		InterfactionEnsembleSigma = dict()
		for pair in InterfactionBetweenness.keys():
			InterfactionEnsembleMeans[pair] = dict()
			InterfactionEnsembleSTD[pair] = dict()
			InterfactionEnsembleSigma[pair] = dict()
			for character in CharacterNodes:
				InterfactionEnsembleMeans[pair][character] = np.mean(InterfactionBetweennessEnsemble[pair][character])
				InterfactionEnsembleSTD[pair][character] = np.std(InterfactionBetweennessEnsemble[pair][character])
				if (InterfactionEnsembleSTD[pair][character] > 0 ):
					InterfactionEnsembleSigma[pair][character] = np.divide(InterfactionBetweenness[pair][character] - InterfactionEnsembleMeans[pair][character],InterfactionEnsembleSTD[pair][character])
				else:
					InterfactionEnsembleSigma[pair][character] = 0
		
	if FactionWorldBetweenness:
		FactionWorldBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_FactionWorldBetweenness.pkl","rb"))
		FactionWorldEnsembleMeans = dict()
		FactionWorldEnsembleSTD = dict()
		FactionWorldEnsembleSigma = dict()
		for faction in FactionWorldBetweenness.keys():
			FactionWorldEnsembleMeans[faction] = dict()
			FactionWorldEnsembleSTD[faction] = dict()
			FactionWorldEnsembleSigma[faction] = dict()
			for character in CharacterNodes:
				FactionWorldEnsembleMeans[faction][character] = np.mean(FactionWorldBetweennessEnsemble[faction][character])
				FactionWorldEnsembleSTD[faction][character] = np.std(FactionWorldBetweennessEnsemble[faction][character])
				if (FactionWorldEnsembleSTD[faction][character] > 0 ):
					FactionWorldEnsembleSigma[faction][character] = np.divide(FactionWorldBetweenness[faction][character] - FactionWorldEnsembleMeans[faction][character],FactionWorldEnsembleSTD[faction][character])
				else:
					FactionWorldEnsembleSigma[faction][character] = 0

	###################
	#oooooooooooooooooo
	if LinkBetweenness:
		LinkWeightsEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl","rb"))
		LinkDegreeProductEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl","rb"))
		LinkBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkBetweenness.pkl","rb"))

		LinkWeightsEnsembleMeans = dict()
		LinkWeightsEnsembleSTD = dict()
		LinkWeightsEnsembleSigma = dict()

		LinkDegreeProductEnsembleMeans = dict()
		LinkDegreeProductEnsembleSTD = dict()
		LinkDegreeProductEnsembleSigma = dict()

		LinkBetweennessEnsembleMeans = dict()
		LinkBetweennessEnsembleSTD = dict()
		LinkBetweennessEnsembleSigma = dict()
		for edge in LinkBetweenness.keys():
			LinkWeightsEnsembleMeans[edge] = np.mean(LinkWeightsEnsemble[edge])
			LinkWeightsEnsembleSTD[edge] = np.std(LinkWeightsEnsemble[edge])
			if (LinkWeightsEnsembleSTD[edge] > 0 ):
				LinkWeightsEnsembleSigma[edge] = np.divide(LinkWeights[edge] - LinkWeightsEnsembleMeans[edge], LinkWeightsEnsembleSTD[edge])
			else:
				LinkBetweennessEnsembleSigma[edge] = 0
			LinkDegreeProductEnsembleMeans[edge] = np.mean(LinkDegreeProductEnsemble[edge])
			LinkDegreeProductEnsembleSTD[edge] = np.std(LinkDegreeProductEnsemble[edge])
			if (LinkDegreeProductEnsembleSTD[edge] > 0 ):
				LinkDegreeProductEnsembleSigma[edge] = np.divide(LinkDegreeProduct[edge] - LinkDegreeProductEnsembleMeans[edge], LinkDegreeProductEnsembleSTD[edge])
			else:
				LinkDegreeProductEnsembleSigma[edge] = 0

			LinkBetweennessEnsembleMeans[edge] = np.mean(LinkBetweennessEnsemble[edge])
			LinkBetweennessEnsembleSTD[edge] = np.std(LinkBetweennessEnsemble[edge])
			if (LinkBetweennessEnsembleSTD[edge] > 0 ):
				LinkBetweennessEnsembleSigma[edge] = np.divide(LinkBetweenness[edge] - LinkBetweennessEnsembleMeans[edge], LinkBetweennessEnsembleSTD[edge])
			else:
				LinkBetweennessEnsembleSigma[edge] = 0
	#oooooooooooooooooo
	Pvalues = dict()
	for character in CharacterNodes:
		CharacterDegreeEnsembleMeans[character] = np.mean(CharacterDegreeEnsemble[character])
		CharacterDegreeEnsembleSTD[character] = np.std(CharacterDegreeEnsemble[character])
		NodeStrengthEnsembleMeans[character] = np.mean(CharacterStrengthEnsemble[character])
		NodeStrengthEnsembleSTD[character] = np.std(CharacterStrengthEnsemble[character])
		BetweennessEnsembleMeans[character] = np.mean(CharacterBetweennessEnsemble[character])
		BetweennessEnsembleSTD[character] = np.std(CharacterBetweennessEnsemble[character])
		if (np.max([np.max(CharacterBetweennessEnsemble[character]), 2*CharacterBetweenness[character]]) > 0):
			bins = np.linspace(0,np.max([np.max(CharacterBetweennessEnsemble[character]), 2*CharacterBetweenness[character]]),30, endpoint = True)
			freaq= plt.hist(CharacterBetweennessEnsemble[character], bins)
			#plt.close()
			#plt.figure(14)
			cumsumkasar = np.concatenate(([0],list(np.cumsum(freaq[0]))))
			#plt.plot(bins, cumsumkasar)
			binshalus = np.linspace(np.min(0),np.max(bins),1000, endpoint = True)
			cumsumhalus = interpolate.pchip_interpolate(bins, cumsumkasar, binshalus)
			cumsumhalusn = [np.divide(c, np.max(cumsumhalus)) for c in cumsumhalus]
			aindec = list(binshalus).index(min(binshalus, key=lambda x:abs(x-CharacterBetweenness[character])))
			pval = (cumsumhalusn[aindec])
			#plt.plot(binshalus, cumsumhalusn)
			#plt.plot([CharacterBetweenness[character], CharacterBetweenness[character]],[0, 1],'r-')
			#plt.plot([binshalus[aindec], binshalus[aindec]],[0, 1],'g-')

			#plt.close()
			#plt.plot([CharacterBetweenness[character]],[.5],'ro')
			Pvalues[character] = pval
			#print(pval)
		else:
			Pvalues[character] = -1.0
		#plt.show()


		# binshalus = np.linspace(np.min(bincenters),np.max(bincenters),200, endpoint = True)
		# freaqhalus = interpolate.pchip_interpolate(bincenters, freaq[0], binshalus)
		# totalfreqhalus = np.trapz(freaqhalus, binshalus)
		# freaqhalusnormal = [np.divide(f,totalfreqhalus) for f in freaqhalus]
		# freqhalusnormalcumsum = np.cumtrapz(freaqhalusnormal)
		# print(freqhalusnormalcumsum[0])
		# binshalus1 = np.concatenate(([0], list(binshalus)))
		# freqhalusnormalcumsum1 = np.concatenate(([0], list(freqhalusnormalcumsum)))
		# aindec = list(binshalus1).index(min(binshalus1, key=lambda x:abs(x-CharacterBetweenness[character])))
		# pval = (1 - list(freqhalusnormalcumsum)[aindec])

		# plt.plot(np.concatenate(([0], list(binshalus))),np.concatenate(([0], list(freqhalusnormalcumsum))), 'go-')
		# plt.plot(CharacterBetweenness[character], 0 , 'ko')
		# plt.plot(binshalus[aindec], 0 , 'go')
		# plt.show()
		# plt.close()
		if NodeStrengthEnsembleSTD[character] > 0:
			NodeStrengthSigma[character] = np.divide(CharacterStrengths[character]-NodeStrengthEnsembleMeans[character],NodeStrengthEnsembleSTD[character])
		else:
			NodeStrengthSigma[character] = 0
		BetweennessEnsembleMeans[character] = np.mean(CharacterBetweennessEnsemble[character])
		BetweennessEnsembleSTD[character] = np.std(CharacterBetweennessEnsemble[character])
		if BetweennessEnsembleSTD[character] > 0:
			BetweennessEnsembleSigma[character] = np.divide(CharacterBetweenness[character]-BetweennessEnsembleMeans[character],BetweennessEnsembleSTD[character])
		else:
			BetweennessEnsembleSigma[character] = 0

	br = open("../Outputs/" + datasettag + "/OverallBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
	br.write("Character, Number of Occurrences, Ensemble mean number of occurrences, Ensemble occurrences standard deviation, Node Strength, Ensemble mean node strength, Ensemble node strength standard deviation, Betweenness centrality, Ensemble Mean Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean\n")
	for character in sorted(BetweennessEnsembleSigma.keys(), key = lambda x: BetweennessEnsembleSigma[x], reverse = True):
		br.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterDegreeEnsembleMeans[character]) + "," + str(CharacterDegreeEnsembleSTD[character]) + "," + str(CharacterStrengths[character]) + "," + str(NodeStrengthEnsembleMeans[character]) + "," +  str(NodeStrengthEnsembleSTD[character]) + "," + str(CharacterBetweenness[character]) + "," + str(BetweennessEnsembleMeans[character]) + "," + str(BetweennessEnsembleSTD[character]) + "," + str(BetweennessEnsembleSigma[character]) + "\n")
	br.close()

	br = open("../Outputs/" + datasettag + "/NEWOverallBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
	br.write("Character, Number of Occurrences, Ensemble mean number of occurrences, Ensemble occurrences standard deviation, Node Strength, Ensemble mean node strength, Ensemble node strength standard deviation, Betweenness centrality, Ensemble Mean Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean, Approx dist p-value\n")
	for character in sorted(Pvalues.keys(), key = lambda x: (Pvalues[x], BetweennessEnsembleSigma[x]), reverse = True):
		br.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterDegreeEnsembleMeans[character]) + "," + str(CharacterDegreeEnsembleSTD[character]) + "," + str(CharacterStrengths[character]) + "," + str(NodeStrengthEnsembleMeans[character]) + "," +  str(NodeStrengthEnsembleSTD[character]) + "," + str(CharacterBetweenness[character]) + "," + str(BetweennessEnsembleMeans[character]) + "," + str(BetweennessEnsembleSTD[character]) + "," + str(BetweennessEnsembleSigma[character]) + "," + str(Pvalues[character]) + "\n")
	br.close()

	############################

	if InterfactionBetweenness:

		try:
			os.makedirs("../Outputs/" + datasettag + "/InterfactionBetweenness/")
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		for pair in InterfactionBetweenness.keys():

			Pvalues = dict()
			for character in CharacterNodes:

				if (np.max(np.max(InterfactionBetweennessEnsemble[pair][character]),2*InterfactionBetweenness[pair][character]) > 0):
					bins = np.linspace(0,np.max(np.max(InterfactionBetweennessEnsemble[pair][character]),2*InterfactionBetweenness[pair][character]),30, endpoint = True)
					freaq= plt.hist(InterfactionBetweennessEnsemble[pair][character], bins)
					#plt.close()
					#plt.figure(14)
					#bincenters = 0.5*(bins[1:]+bins[:-1])
					#totalfreq = np.sum(freaq[0])
					cumsumkasar = np.concatenate(([0],list(np.cumsum(freaq[0]))))
					#plt.plot(bins, cumsumkasar)
					binshalus = np.linspace(np.min(0),np.max(bins),1000, endpoint = True)
					cumsumhalus = interpolate.pchip_interpolate(bins, cumsumkasar, binshalus)
					cumsumhalusn = [np.divide(c, np.max(cumsumhalus)) for c in cumsumhalus]
					aindec = list(binshalus).index(min(binshalus, key=lambda x:abs(x-InterfactionBetweenness[pair][character])))
					pval = (cumsumhalusn[aindec])
					#plt.plot(binshalus, cumsumhalusn)
					#plt.plot([InterfactionBetweenness[pair][character], InterfactionBetweenness[pair][character]],[0, 1],'r-')
					#plt.plot([binshalus[aindec], binshalus[aindec]],[0, 1],'g-')
					#plt.pause(0.1)
					plt.close()
					#plt.plot([CharacterBetweenness[character]],[.5],'ro')
					Pvalues[character] = pval
					#print(pval)
				else:
					Pvalues[character] = -1.0
				#plt.show()

			ifbr = open("../Outputs/" + datasettag + "/InterfactionBetweenness/" + pair[0] + pair[1] + "InterfactionBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
			ifbr.write("Character,Number of occurrences,Node strength," + pair[0] + "-" + pair[1] + " Betweenness centrality,Ensemble Mean " + pair[0] + "-" + pair[1] + " Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean, P-value\n")
			for character in sorted(InterfactionEnsembleSigma[pair].keys(), key=lambda x: InterfactionEnsembleSigma[pair][x], reverse = True):
				ifbr.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterStrengths[character]) + "," + str(InterfactionBetweenness[pair][character]) + "," + str(InterfactionEnsembleMeans[pair][character]) + "," + str(InterfactionEnsembleSTD[pair][character]) + "," + str(InterfactionEnsembleSigma[pair][character]) + "\n")
			ifbr.close()

			ifbr = open("../Outputs/" + datasettag + "/InterfactionBetweenness/" + pair[0] + pair[1] + "NEWInterfactionBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
			ifbr.write("Character,Number of occurrences,Node strength," + pair[0] + "-" + pair[1] + " Betweenness centrality,Ensemble Mean " + pair[0] + "-" + pair[1] + " Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean\n")
			for character in sorted(InterfactionEnsembleSigma[pair].keys(), key=lambda x: (Pvalues[x], InterfactionEnsembleSigma[pair][x]), reverse = True):
				ifbr.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterStrengths[character]) + "," + str(InterfactionBetweenness[pair][character]) + "," + str(InterfactionEnsembleMeans[pair][character]) + "," + str(InterfactionEnsembleSTD[pair][character]) + "," + str(InterfactionEnsembleSigma[pair][character]) + "," + str(Pvalues[character]) + "\n")
			ifbr.close()

	if FactionWorldBetweenness:
		try:
			os.makedirs("../Outputs/" + datasettag + "/FactionWorldBetweenness/")
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		for faction in FactionWorldBetweenness.keys():
			Pvalues = dict()
			for character in CharacterNodes:
				if (np.max(np.max(FactionWorldBetweennessEnsemble[faction][character]),2*FactionWorldBetweenness[faction][character]) > 0):
					bins = np.linspace(0,np.max(np.max(FactionWorldBetweennessEnsemble[faction][character]),2*FactionWorldBetweenness[faction][character]),30, endpoint = True)
					freaq= plt.hist(FactionWorldBetweennessEnsemble[faction][character], bins)
					#plt.close()
					#plt.figure(14)
					#bincenters = 0.5*(bins[1:]+bins[:-1])
					#totalfreq = np.sum(freaq[0])
					cumsumkasar = np.concatenate(([0],list(np.cumsum(freaq[0]))))
					#plt.plot(bins, cumsumkasar)
					binshalus = np.linspace(np.min(0),np.max(bins),1000, endpoint = True)
					cumsumhalus = interpolate.pchip_interpolate(bins, cumsumkasar, binshalus)
					cumsumhalusn = [np.divide(c, np.max(cumsumhalus)) for c in cumsumhalus]
					aindec = list(binshalus).index(min(binshalus, key=lambda x:abs(x-FactionWorldBetweenness[faction][character])))
					pval = (cumsumhalusn[aindec])
					#plt.plot(binshalus, cumsumhalusn)
					#plt.plot([FactionWorldBetweenness[faction][character], FactionWorldBetweenness[faction][character]],[0, 1],'r-')
					#plt.plot([binshalus[aindec], binshalus[aindec]],[0, 1],'g-')
					#plt.pause(0.1)
					#plt.close()
					#plt.plot([CharacterBetweenness[character]],[.5],'ro')
					Pvalues[character] = pval
					#print(pval)
				else:
					Pvalues[character] = -1.0
				#plt.show()

			fwbr = open("../Outputs/" + datasettag + "/FactionWorldBetweenness/" + faction + "FactionWorldBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
			fwbr.write("Characters,Number of occurrences,Node strength," + faction + "-World Betweenness centrality,Ensemble Mean " + faction + "-World Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean\n")
			for character in sorted(FactionWorldEnsembleSigma[faction].keys(), key=lambda x: FactionWorldEnsembleSigma[faction][x], reverse = True):
				fwbr.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterStrengths[character]) + "," + str(FactionWorldBetweenness[faction][character]) + "," + str(FactionWorldEnsembleMeans[faction][character]) + "," + str(FactionWorldEnsembleSTD[faction][character]) + "," + str(FactionWorldEnsembleSigma[faction][character]) + "\n")
			fwbr.close

			fwbr = open("../Outputs/" + datasettag + "/FactionWorldBetweenness/" + faction + "FactionWorldNEWBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
			fwbr.write("Characters,Number of occurrences,Node strength," + faction + "-World Betweenness centrality,Ensemble Mean " + faction + "-World Betweenness centrality, Ensemble Mean Standard Deviation, Sigmas from mean, P-value\n")
			for character in sorted(FactionWorldEnsembleSigma[faction].keys(), key=lambda x: (Pvalues[x], FactionWorldEnsembleSigma[faction][x]), reverse = True):
				fwbr.write(character + "," + str(CharacterDegrees[character]) + "," + str(CharacterStrengths[character]) + "," + str(FactionWorldBetweenness[faction][character]) + "," + str(FactionWorldEnsembleMeans[faction][character]) + "," + str(FactionWorldEnsembleSTD[faction][character]) + "," + str(FactionWorldEnsembleSigma[faction][character]) + "," + str(Pvalues[character]) + "\n")
			fwbr.close

	#############################
	#oooooooooooooooooooooooooooo
	if LinkBetweenness:
		Pvalues = dict()
		for edge in LinkBetweenness.keys():
			if (np.max(np.max(LinkBetweennessEnsemble[edge]),2*LinkBetweenness[edge]) > 0):
				bins = np.linspace(0,np.max(np.max(LinkBetweennessEnsemble[edge]),2*LinkBetweenness[edge]),30, endpoint = True)
				freaq= plt.hist(LinkBetweennessEnsemble[edge], bins)
				#plt.close()
				#plt.figure(14)
				#bincenters = 0.5*(bins[1:]+bins[:-1])
				#totalfreq = np.sum(freaq[0])
				cumsumkasar = np.concatenate(([0],list(np.cumsum(freaq[0]))))
				#plt.plot(bins, cumsumkasar)
				binshalus = np.linspace(np.min(0),np.max(bins),1000, endpoint = True)
				cumsumhalus = interpolate.pchip_interpolate(bins, cumsumkasar, binshalus)
				cumsumhalusn = [np.divide(c, np.max(cumsumhalus)) for c in cumsumhalus]
				aindec = list(binshalus).index(min(binshalus, key=lambda x:abs(x-LinkBetweenness[edge])))
				pval = (cumsumhalusn[aindec])
				#plt.plot(binshalus, cumsumhalusn)
				#plt.plot([LinkBetweenness[edge], LinkBetweenness[edge]],[0, 1],'r-')
				#plt.plot([binshalus[aindec], binshalus[aindec]],[0, 1],'g-')
				#plt.pause(0.1)
				#plt.close()
				#plt.plot([CharacterBetweenness[edge]],[.5],'ro')
				Pvalues[edge] = pval
				#print(pval)
			else:
				Pvalues[edge] = -1.0
		#plt.show()

		ebr = open("../Outputs/" + datasettag + "/OverallLinkBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
		ebr.write("Source, Target, Link weight, Ensemble mean link weight, Product of node degrees, Ensemble mean product of node degrees, Link betweenness centrality,  Ensemble mean link betweenness centrality, Sigmas from mean\n")
		for edge in sorted(LinkBetweennessEnsembleSigma.keys(), key = lambda x: LinkBetweennessEnsembleSigma[x], reverse = True):
			ebr.write(edge[0] + "," + edge[1] + "," + str(LinkWeights[edge]) + "," + str(LinkWeightsEnsembleMeans[edge]) + "," + str(LinkDegreeProduct[edge]) + "," + str(LinkDegreeProductEnsembleMeans[edge]) + "," + str(LinkBetweenness[edge]) + "," + str(LinkBetweennessEnsembleMeans[edge]) + "," + str(LinkBetweennessEnsembleSigma[edge]) + "\n")
		ebr.close()

		ebr = open("../Outputs/" + datasettag + "/NEWOverallLinkBetweennessRankings" + ensembletag + str(EnsembleSize) + ".csv" , 'w')
		ebr.write("Source, Target, Link weight, Ensemble mean link weight, Product of node degrees, Ensemble mean product of node degrees, Link betweenness centrality,  Ensemble mean link betweenness centrality, Sigmas from mean, P-value\n")
		for edge in sorted(LinkBetweennessEnsembleSigma.keys(), key = lambda x: (Pvalues[x], LinkBetweennessEnsembleSigma[x]), reverse = True):
			ebr.write(edge[0] + "," + edge[1] + "," + str(LinkWeights[edge]) + "," + str(LinkWeightsEnsembleMeans[edge]) + "," + str(LinkDegreeProduct[edge]) + "," + str(LinkDegreeProductEnsembleMeans[edge]) + "," + str(LinkBetweenness[edge]) + "," + str(LinkBetweennessEnsembleMeans[edge]) + "," + str(LinkBetweennessEnsembleSigma[edge]) + "," + str(Pvalues[edge]) + "\n")
		ebr.close()
	#oooooooooooooooooooooooooooo

	return BetweennessEnsembleMeans, BetweennessEnsembleSTD, BetweennessEnsembleSigma, InterfactionEnsembleMeans, InterfactionEnsembleSTD, InterfactionEnsembleSigma, FactionWorldEnsembleMeans, FactionWorldEnsembleSTD, FactionWorldEnsembleSigma, LinkBetweennessEnsembleMeans, LinkBetweennessEnsembleSTD, LinkBetweennessEnsembleSigma

###########################################################################

def NullModelEnsembleBetweennessVsDegree(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness):

	CharacterDegreeEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Degrees.pkl","rb"))
	CharacterStrengthEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Strengths.pkl","rb"))
	CharacterBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_Betweenness.pkl","rb"))	
	NumberOfLinksEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","rb"))

	CharacterNodes = CharacterDegreeEnsemble.keys()

	EnsembleSize = len(CharacterDegreeEnsemble[list(CharacterNodes)[0]])

	OSE = []
	NSE = []
	BCE = []
	for character in CharacterNodes:
		OSE.extend(CharacterDegreeEnsemble[character])
		NSE.extend(CharacterStrengthEnsemble[character])
		BCE.extend(CharacterBetweennessEnsemble[character])

	occurrencelist = [CharacterDegrees[character] for character in CharacterNodes]
	nodestrengthlist = [CharacterStrengths[character] for character in CharacterNodes]
	betweennesslist = [CharacterBetweenness[character] for character in CharacterNodes]
	characterlist = [character for character in CharacterNodes]


	Bbins = np.linspace(0,np.max(BCE),50)
	Nbins = np.linspace(0,np.max(NSE),50)
	plt.figure(10)
	plt.plot(OSE,NSE,'k.')
	bincenters = 0.5*(Bbins[1:]+Bbins[:-1])
	bincentersN = 0.5*(Nbins[1:]+Nbins[:-1])

	Bmean = []
	Bstd = []
	Nmean = []
	Nstd = []
	Xz, Yz = np.meshgrid(range(1,np.max(OSE)),bincenters)
	XzN, YzN = np.meshgrid(range(1,np.max(OSE)),bincentersN)
	Zz = np.array([], dtype=np.int64).reshape(len(bincenters),0)
	Zz2 = np.array([], dtype=np.int64).reshape(len(bincentersN),0)

	for o in range(0,np.max(OSE)-1):
		io = [i for i, x in enumerate(OSE) if x == o]
		OSEo = [OSE[i] for i in io]
		NSEo = [NSE[i] for i in io]
		BCEo = [BCE[i] for i in io]
		BH,bbins = np.histogram(BCEo,bins = Bbins)
		NH,bbinsN = np.histogram(NSEo,bins = Nbins)
		BHN = BH
		Bmean.extend([np.mean(BCEo)]) 
		Bstd.extend([np.std(BCEo)])
		Nmean.extend([np.mean(NSEo)])
		Nstd.extend([np.std(NSEo)])
		NHN = NH
		if np.sum(BH) > 0:
			BHN = np.array([np.divide(b,np.sum(BH)) for b in BH])
			NHN = np.array([np.divide(b,np.sum(NH)) for b in NH])
		BHN = BHN.reshape(len(bincenters),1)
		NHN = NHN.reshape(len(bincenters),1)
		Zz = np.concatenate([Zz,BHN],axis=1)
		Zz2 = np.concatenate([Zz2,NHN],axis=1)

	# Save results in a csv:
	# First row: number of episode occurrences
	# Second row: Mean betweenness centrality for all nodes having that number of occurrences in all ensemble realizations
	# Third row: Standard deviation
	# Fourth row: 6 times the standard deviation (arbitrary, but maybe we can identify characters above this as significant
	#    outliers)

	try:
		os.makedirs("../Outputs/" + datasettag + "/")
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

	bmstd = open("../Outputs/" + datasettag + "/EnsembleMeanSTD.csv" , 'w')
	bmstd.write("Occurrences,Ensemble mean betweenness centrality,Ensemble STD betweenness centrality,6 sigmas\n")
	for i in range(1,np.max(OSE)):
		bmstd.write(str(i) + "," + str(Bmean[i-1]) + "," + str(Bstd[i-1]) + "," + str(6*Bstd[i-1]) +"\n")
	bmstd.close()

	###################################################################

	# Plots: 
	#			(interfaction betweenness plots not yet up and running)

	plt.figure(0)
	#plt.plot(OSE,NSE,'k.')
	sixsigN = [(Nmean[i]+6*Nstd[i]) for i in range(len(Nmean))]
	plt.plot(range(1,np.max(OSE)),Nmean,'k',linewidth = 2.0)
	plt.plot(range(1,np.max(OSE)),sixsigN,'r',linewidth = 1.0)
	CS1 = plt.contour(XzN, YzN, Zz2, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.clabel(CS1, inline=1, fontsize=10)
	plt.scatter(occurrencelist,nodestrengthlist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(occurrencelist[i],nodestrengthlist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(occurrencelist),np.max(OSE)]), 0, 1.05*np.max([np.max(nodestrengthlist),np.max(NSE)])])
	plt.xlabel('Number of episode appearances')
	plt.ylabel('Co-occurrence network node strength')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag)
	plt.savefig("../Outputs/" + datasettag + '/NodeStrengthVsOccurrences' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.close(0)


	plt.figure(1)
	#plt.plot(OSE,BCE,'k.')
	sixsigB = [(Bmean[i]+6*Bstd[i]) for i in range(len(Bmean))]
	CS = plt.contour(Xz, Yz, Zz, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.plot(range(1,np.max(OSE)),Bmean,'k',linewidth = 2.0)
	plt.plot(range(1,np.max(OSE)),sixsigB,'r',linewidth = 1.0)
	plt.clabel(CS, inline=1, fontsize=10)
	plt.scatter(occurrencelist,betweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(occurrencelist[i],betweennesslist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(occurrencelist),np.max(OSE)]), 0, 1.05*np.max([np.max(betweennesslist),np.max(BCE)])])
	plt.xlabel('Number of episode appearances')
	plt.ylabel('Co-occurrence network betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/BetweennessVsOccurrences' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.close(1)

	plt.figure(2)
	plt.plot(NSE,BCE,'k.')
	plt.scatter(nodestrengthlist,betweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(nodestrengthlist[i],betweennesslist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(nodestrengthlist),np.max(OSE)]), 0, 1.05*np.max([np.max(betweennesslist),np.max(BCE)])])
	plt.xlabel('Co-occurrence network node strength')
	plt.ylabel('Co-occurrence network betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble:' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/BetweennessVsNodeStrength' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.close(2)

###########################################################################
###########################################################################

def NullModelEnsembleBetweennessVsDegreeEpisodes(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness):

	CharacterDegreeEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeDegrees.pkl","rb"))
	CharacterStrengthEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeStrengths.pkl","rb"))
	CharacterBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_EpisodeBetweenness.pkl","rb"))	
	NumberOfLinksEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","rb"))

	CharacterNodes = CharacterDegreeEnsemble.keys()

	EnsembleSize = len(CharacterDegreeEnsemble[list(CharacterNodes)[0]])

	OSE = []
	NSE = []
	BCE = []
	for character in CharacterNodes:
		OSE.extend(CharacterDegreeEnsemble[character])
		NSE.extend(CharacterStrengthEnsemble[character])
		BCE.extend(CharacterBetweennessEnsemble[character])

	occurrencelist = [CharacterDegrees[character] for character in CharacterNodes]
	nodestrengthlist = [CharacterStrengths[character] for character in CharacterNodes]
	betweennesslist = [CharacterBetweenness[character] for character in CharacterNodes]
	characterlist = [character for character in CharacterNodes]


	Bbins = np.linspace(0,np.max(BCE),50)
	Nbins = np.linspace(0,np.max(NSE),50)
	plt.figure(10)
	plt.plot(OSE,NSE,'k.')
	bincenters = 0.5*(Bbins[1:]+Bbins[:-1])
	bincentersN = 0.5*(Nbins[1:]+Nbins[:-1])

	Bmean = []
	Bstd = []
	Nmean = []
	Nstd = []
	Xz, Yz = np.meshgrid(range(1,np.max(OSE)),bincenters)
	XzN, YzN = np.meshgrid(range(1,np.max(OSE)),bincentersN)
	Zz = np.array([], dtype=np.int64).reshape(len(bincenters),0)
	Zz2 = np.array([], dtype=np.int64).reshape(len(bincentersN),0)

	for o in range(0,np.max(OSE)-1):
		io = [i for i, x in enumerate(OSE) if x == o]
		OSEo = [OSE[i] for i in io]
		NSEo = [NSE[i] for i in io]
		BCEo = [BCE[i] for i in io]
		BH,bbins = np.histogram(BCEo,bins = Bbins)
		NH,bbinsN = np.histogram(NSEo,bins = Nbins)
		BHN = BH
		Bmean.extend([np.mean(BCEo)]) 
		Bstd.extend([np.std(BCEo)])
		Nmean.extend([np.mean(NSEo)])
		Nstd.extend([np.std(NSEo)])
		NHN = NH
		if np.sum(BH) > 0:
			BHN = np.array([np.divide(b,np.sum(BH)) for b in BH])
			NHN = np.array([np.divide(b,np.sum(NH)) for b in NH])
		BHN = BHN.reshape(len(bincenters),1)
		NHN = NHN.reshape(len(bincenters),1)
		Zz = np.concatenate([Zz,BHN],axis=1)
		Zz2 = np.concatenate([Zz2,NHN],axis=1)

	# Save results in a csv:
	# First row: number of episode occurrences
	# Second row: Mean betweenness centrality for all nodes having that number of occurrences in all ensemble realizations
	# Third row: Standard deviation
	# Fourth row: 6 times the standard deviation (arbitrary, but maybe we can identify characters above this as significant
	#    outliers)

	try:
		os.makedirs("../Outputs/" + datasettag + "/")
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

	bmstd = open("../Outputs/" + datasettag + "/EpisodeEnsembleMeanSTD.csv" , 'w')
	bmstd.write("Occurrences,Ensemble mean betweenness centrality,Ensemble STD betweenness centrality,6 sigmas\n")
	for i in range(1,np.max(OSE)):
		bmstd.write(str(i) + "," + str(Bmean[i-1]) + "," + str(Bstd[i-1]) + "," + str(6*Bstd[i-1]) +"\n")
	bmstd.close()

	###################################################################

	# Plots: 
	#			(interfaction betweenness plots not yet up and running)

	plt.figure(0)
	#plt.plot(OSE,NSE,'k.')
	sixsigN = [(Nmean[i]+6*Nstd[i]) for i in range(len(Nmean))]
	plt.plot(range(1,np.max(OSE)),Nmean,'k',linewidth = 2.0)
	plt.plot(range(1,np.max(OSE)),sixsigN,'r',linewidth = 1.0)
	CS1 = plt.contour(XzN, YzN, Zz2, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.clabel(CS1, inline=1, fontsize=10)
	plt.scatter(occurrencelist,nodestrengthlist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(occurrencelist[i],nodestrengthlist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(occurrencelist),np.max(OSE)]), 0, 1.05*np.max([np.max(nodestrengthlist),np.max(NSE)])])
	plt.xlabel('Number of characters')
	plt.ylabel('Episode intersection network node strength')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag)
	plt.savefig("../Outputs/" + datasettag + '/EpisodeNodeStrengthVsOccurrences' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.close(0)

	plt.figure(1)
	#plt.plot(OSE,BCE,'k.')
	sixsigB = [(Bmean[i]+6*Bstd[i]) for i in range(len(Bmean))]
	CS = plt.contour(Xz, Yz, Zz, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.plot(range(1,np.max(OSE)),Bmean,'k',linewidth = 2.0)
	plt.plot(range(1,np.max(OSE)),sixsigB,'r',linewidth = 1.0)
	plt.clabel(CS, inline=1, fontsize=10)
	plt.scatter(occurrencelist,betweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(occurrencelist[i],betweennesslist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(occurrencelist),np.max(OSE)]), 0, 1.05*np.max([np.max(betweennesslist),np.max(BCE)])])
	plt.xlabel('Number of characters')
	plt.ylabel('Episode intersection network betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/EpisodeBetweennessVsOccurrences' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.figure(1)

	plt.figure(2)
	plt.plot(NSE,BCE,'k.')
	plt.scatter(nodestrengthlist,betweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(characterlist)):
		plt.annotate(characterlist[i],(nodestrengthlist[i],betweennesslist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(nodestrengthlist),np.max(OSE)]), 0, 1.05*np.max([np.max(betweennesslist),np.max(BCE)])])
	plt.xlabel('Episode intersection network node strength')
	plt.ylabel('Episode intersection network betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble:' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/EpisodeBetweennessVsNodeStrength' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')
	plt.figure(2)

###########################################################################
###########################################################################

def NullModelEnsembleLinkBetweennessVs(datasettag, ensembletag, LinkWeights, LinkDegreeProduct, LinkBetweenness):

	LinkWeightsEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkWeights.pkl","rb"))
	LinkDegreeProductEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkDegreeProduct.pkl","rb"))
	LinkBetweennessEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_LinkBetweenness.pkl","rb"))	
	#NumberOfLinksEnsemble = pk.load(open("../Outputs/" + datasettag + "/Objects/NullModelEnsembles/" + datasettag + "_" + ensembletag + "_Ensemble_NumberOfLinks.pkl","rb"))

	################################3

	#occurrencelist = [Occurrences[character] for character in CharacterNodes]
	#nodestrengthlist = [NodeStrength0[character] for character in CharacterNodes]
	#betweennesslist = [Betweenness0[character] for character in CharacterNodes]
	#characterlist = [character for character in CharacterNodes]

	EnsembleSize = len(LinkWeightsEnsemble[list(LinkWeightsEnsemble.keys())[0]])

	edgelist = [edge for edge in LinkWeights.keys()]
	weightlist = [LinkWeights[edge] for edge in LinkWeights.keys()]
	edgebetweennesslist = [LinkBetweenness[edge] for edge in LinkWeights.keys()]
	productlist = [LinkDegreeProduct[edge] for edge in LinkWeights.keys()]

	################################3

	LWE = []
	#s = open("Outputs" + window + "/EnsembleScatterplots/LinkWeightEnsemble" + window + ".csv" , 'w')
	for edge in LinkBetweenness.keys():
#		s.write(edge[0] + "," + edge[1])
		LWE.extend(LinkWeightsEnsemble[edge])
	# 	for r in range(NumberOfRealizations):
	# 		s.write("," + str(LinkWeightData[edge][r]))
	# 	s.write("\n")
	# s.close()

	EBE = []
	#s = open("Outputs" + window + "/EnsembleScatterplots/EdgeBetweennessEnsemble" + window + ".csv" , 'w')
	for edge in LinkBetweenness.keys():
	#	s.write(edge[0] + "," + edge[1])
		EBE.extend(LinkBetweennessEnsemble[edge])
	#	for r in range(NumberOfRealizations):
	#		print(EdgeBetweennessData[edge])
	#		s.write("," + str(EdgeBetweennessData[edge][r]))
	#	s.write("\n")
	#s.close()
	# product of linked character occurrences
	POE = []
	#s = open("Outputs" + window + "/EnsembleScatterplots/EdgeOccurrenceProductEnsemble" + window + ".csv" , 'w')
	for edge in LinkBetweenness.keys():
	#	s.write(edge[0] + "," + edge[1])
		POE.extend(LinkDegreeProductEnsemble[edge])
	#	for r in range(NumberOfRealizations):
	#		s.write("," + str(EdgeOccurProductData[edge][r]))
	#	s.write("\n")
	#s.close()

	# Bbins = np.linspace(0,np.max(BCE),50)
	# Nbins = np.linspace(0,np.max(NSE),50)
	# plt.figure(10)
	# plt.plot(OSE,NSE,'k.')
	# bincenters = 0.5*(Bbins[1:]+Bbins[:-1])
	# bincentersN = 0.5*(Nbins[1:]+Nbins[:-1])

	# Bmean = []
	# Bstd = []
	# Nmean = []
	# Nstd = []
	# Xz, Yz = np.meshgrid(range(1,np.max(OSE)),bincenters)
	# XzN, YzN = np.meshgrid(range(1,np.max(OSE)),bincentersN)
	# Zz = np.array([], dtype=np.int64).reshape(len(bincenters),0)
	# Zz2 = np.array([], dtype=np.int64).reshape(len(bincentersN),0)


	Cbins = np.linspace(0,np.max(EBE),50)
	Mbins = np.linspace(0,np.max(POE),50)
	#plt.figure(10)
	#plt.plot(LWE,NSE,'k.')
	cincenters = 0.5*(Cbins[1:]+Cbins[:-1])
	cincentersN = 0.5*(Mbins[1:]+Mbins[:-1])
	Emean = []
	Estd = []
	Emean2 = []
	Estd2 = []
	Pmean = []
	Pstd = []
	Pmean2 = []
	Pstd2 = []
	Qz, Pz = np.meshgrid(range(1,int(np.max(LWE))),cincenters)
	Qz3, Pz3 = np.meshgrid(range(1,int(np.max(POE))),cincenters)
	QzN, PzN = np.meshgrid(range(1,int(np.max(LWE))),cincentersN)
	Sz = np.array([], dtype=np.int64).reshape(len(cincenters),0)
	Hz = np.array([], dtype=np.int64).reshape(len(cincenters),0)
	Sz2 = np.array([], dtype=np.int64).reshape(len(cincentersN),0)
	Hz2 = np.array([], dtype=np.int64).reshape(len(cincentersN),0)

	# for o in range(0,np.max(OSE)-1):
	# 	io = [i for i, x in enumerate(OSE) if x == o]
	# 	OSEo = [OSE[i] for i in io]
	# 	NSEo = [NSE[i] for i in io]
	# 	BCEo = [BCE[i] for i in io]
	# 	BH,bbins = np.histogram(BCEo,bins = Bbins)
	# 	NH,bbinsN = np.histogram(NSEo,bins = Nbins)
	# 	BHN = BH
	# 	Bmean.extend([np.mean(BCEo)]) 
	# 	Bstd.extend([np.std(BCEo)])
	# 	Nmean.extend([np.mean(NSEo)])
	# 	Nstd.extend([np.std(NSEo)])
	# 	NHN = NH
	# 	if np.sum(BH) > 0:
	# 		BHN = np.array([np.divide(b,np.sum(BH)) for b in BH])
	# 		NHN = np.array([np.divide(b,np.sum(NH)) for b in NH])
	# 	BHN = BHN.reshape(len(bincenters),1)
	# 	NHN = NHN.reshape(len(bincenters),1)
	# 	Zz = np.concatenate([Zz,BHN],axis=1)
	# 	Zz2 = np.concatenate([Zz2,NHN],axis=1)

	for o in range(0,int(np.max(LWE))-1):
		io = [i for i, x in enumerate(LWE) if x == o]
		LWEo = [LWE[i] for i in io]
		POEo = [POE[i] for i in io]
		EBEo = [EBE[i] for i in io]
		EH,cbins = np.histogram(EBEo,bins = Cbins)
		PH,cbinsN = np.histogram(POEo,bins = Mbins)
		EHN = EH
		Emean.extend([np.mean(EBEo)]) 
		Estd.extend([np.std(EBEo)])
		Pmean.extend([np.mean(POEo)])
		Pstd.extend([np.std(POEo)])
		PHN = PH
		if np.sum(EH) > 0:
			EHN = np.array([np.divide(b,np.sum(EH)) for b in EH])
			PHN = np.array([np.divide(b,np.sum(PH)) for b in PH])
		EHN = EHN.reshape(len(cincenters),1)
		PHN = PHN.reshape(len(cincenters),1)
		Sz = np.concatenate([Sz,EHN],axis=1)
		Sz2 = np.concatenate([Sz2,PHN],axis=1)

	for o in range(0,int(np.max(POE))-1):
		io = [i for i, x in enumerate(POE) if x == o]
		POEo2 = [POE[i] for i in io]
		EBEo2 = [EBE[i] for i in io]
		FH,dbins = np.histogram(EBEo2,bins = Cbins)
		WH,dbinsN = np.histogram(POEo2,bins = Mbins)
		FHN = FH
		Emean2.extend([np.mean(EBEo2)]) 
		Estd2.extend([np.std(EBEo2)])
		Pmean2.extend([np.mean(POEo2)])
		Pstd2.extend([np.std(POEo2)])
		WHN = WH
		if np.sum(FH) > 0:
			FHN = np.array([np.divide(b,np.sum(FH)) for b in FH])
			WHN = np.array([np.divide(b,np.sum(WH)) for b in WH])
		FHN = FHN.reshape(len(cincenters),1)
		WHN = PHN.reshape(len(cincenters),1)
		Hz = np.concatenate([Hz,FHN],axis=1)
		Hz2 = np.concatenate([Hz2,WHN],axis=1)

	# Save results in a csv:
	# First row: number of episode occurrences
	# Second row: Mean betweenness centrality for all nodes having that number of occurrences in all ensemble realizations
	# Third row: Standard deviation
	# Fourth row: 6 times the standard deviation (arbitrary, but maybe we can identify characters above this as significant
	#    outliers)

	# bmstd = open("../Outputs/" + datasettag + "/EnsembleMeanSTD.csv" , 'w')
	# bmstd.write("Occurrences,Ensemble mean betweenness centrality,Ensemble STD betweenness centrality,6 sigmas\n")
	# for i in range(1,np.max(OSE)):
	# 	bmstd.write(str(i) + "," + str(Bmean[i-1]) + "," + str(Bstd[i-1]) + "," + str(6*Bstd[i-1]) +"\n")
	# bmstd.close()

	###################################################################

	# Plots: 
	#			(interfaction betweenness plots not yet up and running)

	plt.figure(4)
	#plt.plot(OSE,BCE,'k.')
	sixsigE = [(Emean[i]+6*Estd[i]) for i in range(len(Emean))]
	CS = plt.contour(Qz, Pz, Sz, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.plot(range(1,int(np.max(LWE))),Emean,'k',linewidth = 2.0)
	plt.plot(range(1,int(np.max(LWE))),sixsigE,'r',linewidth = 1.0)
	plt.clabel(CS, inline=1, fontsize=10)
	plt.scatter(weightlist,edgebetweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(edgelist)):
		plt.annotate(edgelist[i],(weightlist[i],edgebetweennesslist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(weightlist),int(np.max(LWE))]), 0, 1.05*np.max([np.max(edgebetweennesslist),np.max(EBE)])])
	plt.xlabel('Link weight')
	plt.ylabel('Co-occurrence network link betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/LinkBetweennessVsWeight' + datasettag + '.png', bbox_inches='tight')

	plt.figure(5)
	#plt.plot(OSE,BCE,'k.')
	sixsigP = [(Pmean[i]+6*Pstd[i]) for i in range(len(Pmean))]
	CS = plt.contour(QzN, PzN, Sz2, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.plot(range(1,int(np.max(LWE))),Pmean,'k',linewidth = 2.0)
	plt.plot(range(1,int(np.max(LWE))),sixsigP,'r',linewidth = 1.0)
	plt.clabel(CS, inline=1, fontsize=10)
	plt.scatter(weightlist,productlist,s=30,zorder=100,color='orange')
	for i in range(len(edgelist)):
		plt.annotate(edgelist[i],(weightlist[i],productlist[i]),zorder=200,color='green',fontsize = 6)
	plt.axis([0, 1.05*np.max([np.max(weightlist),int(np.max(LWE))]), 0, 1.05*np.max([np.max(productlist),np.max(POE)])])
	plt.xlabel('Link weight')
	plt.ylabel('Product of linked node occurrences')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag )
	plt.savefig("../Outputs/" + datasettag + '/OccurrencesProductVsWeight' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')

	plt.figure(6)
	plt.plot(POE,EBE,'k.')
	sixsigB2 = [(Emean2[i]+6*Estd2[i]) for i in range(len(Emean2))]
	CS = plt.contour(Qz3, Pz3, Hz, levels = [.0001, .001, .01, 0.1, 0.5])
	plt.plot(range(1,int(np.max(POE))),Emean2,'k',linewidth = 2.0)
	plt.plot(range(1,int(np.max(POE))),sixsigB2,'r',linewidth = 1.0)
	plt.clabel(CS, inline=1, fontsize=10)
	plt.scatter(productlist,edgebetweennesslist,s=30,zorder=100,color='orange')
	for i in range(len(edgelist)):
		plt.annotate(edgelist[i],(productlist[i],edgebetweennesslist[i]),zorder=200,color='green',fontsize = 4)
	plt.axis([0, 1.05*np.max([np.max(productlist),int(np.max(POE))]), 0, 1.05*np.max([np.max(edgebetweennesslist),np.max(EBE)])])
	plt.xlabel('Product of linked character occurrences')
	plt.ylabel('Link betweenness centrality')
	plt.title(str(EnsembleSize) + '-network ensemble: ' + datasettag)
	plt.savefig("../Outputs/" + datasettag + '/EdgeBetweennessVsProduct' + datasettag + ensembletag + str(EnsembleSize) + '.png', bbox_inches='tight')


	###########################################################################

def CooccurrenceNetworkNodesForGephi(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/ForGephi/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	EpisodeNodes, CharacterNodes, B, G, GI, E, EI = LoadGraphs(datasettag)
	CharacterDegrees, CharacterStrengths, CharacterBetweenness = LoadCharacterNodeMetrics(datasettag)

	CharacterFactions = []
	if os.path.isfile("../Inputs/CharacterAffiliations" + datasettag + ".csv"):
		CharacterFactions = LoadFactions(datasettag)[0]
		InterfactionBetweenness = LoadInterfactionBetweenness(datasettag)
		FactionPairsList = sorted(list(InterfactionBetweenness.keys()))
		FactionWorldBetweenness = LoadFactionWorldBetweenness(datasettag)
		FactionsList = sorted(list(FactionWorldBetweenness.keys()))

	#-------------------------------------

	# Character (node) list and attributes
	ibs = open("../Outputs/" + datasettag + "/ForGephi/" + datasettag + "CharacterNodesList.csv" , 'w')
	ibs.write("Id,Label,Number of episode appearances,Node strength (weighted degree),Betweenness centrality")
	if not CharacterFactions:
		[]
	else:
		ibs.write(",Faction")
		for faction in FactionsList:
			ibs.write("," + faction + "-World Betweenness centrality")
		for pair in FactionPairsList:
			ibs.write("," + pair[0] + "-" + pair[1] + " Betweenness centrality")
	ibs.write("\n")
	for character in CharacterNodes:
		ibs.write(character + "," + character + "," + str(CharacterDegrees[character]) + "," + str(CharacterStrengths[character]) + "," + str(CharacterBetweenness[character]))
		if not CharacterFactions:
			[]
		else:
			ibs.write("," + CharacterFactions[character])
			for faction in FactionsList:				
				ibs.write("," + str(FactionWorldBetweenness[faction][character]))
			for pair in FactionPairsList:
				ibs.write("," + str(InterfactionBetweenness[pair][character]))
		ibs.write("\n")
	ibs.close()

	#------------------------------------

###########################################################################

def CooccurrenceNetworkEdgesForGephi(datasettag):

	# Prepare directory for output files (spreadsheets, plots, etc.):
	try:
	    os.makedirs("../Outputs/" + datasettag + "/ForGephi/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	EpisodeNodes, CharacterNodes, B, G, GI, E, EI = LoadGraphs(datasettag)
	LinkWeights, LinkDegreeProduct, LinkBetweenness = LoadLinkMetrics(datasettag)

	InterfactionLinkBetweenness = []
	if os.path.isfile("../Inputs/CharacterAffiliations" + datasettag + ".csv"):
		InterfactionLinkBetweenness = LoadInterfactionLinkBetweenness(datasettag)
		FactionPairsList = sorted(list(InterfactionLinkBetweenness.keys()))
		FactionWorldLinkBetweenness = LoadFactionWorldLinkBetweenness(datasettag)
		FactionsList = sorted(list(FactionWorldLinkBetweenness.keys()))

	ibs = open("../Outputs/" + datasettag + "/ForGephi/" + datasettag + "EdgeList.csv" , 'w')
	ibs.write("Source,Target,Weight,Link Product Degree,Link betweenness centrality")
	if not InterfactionLinkBetweenness:
		[]
	else:
		for faction in FactionsList:
			ibs.write("," + faction + "-World Link Betweenness centrality")
		for pair in FactionPairsList:
			ibs.write("," + pair[0] + "-" + pair[1] + " Link Betweenness centrality")
	ibs.write("\n")

	for edge in sorted(list(LinkBetweenness.keys())):
		ibs.write(edge[0] + "," + edge[1] + "," + str(LinkWeights[edge]) + "," + str(LinkDegreeProduct[edge]) + "," + str(LinkBetweenness[edge]) )
		if not InterfactionLinkBetweenness:
			[]
		else:
			for faction in FactionsList:
				if edge in FactionWorldLinkBetweenness[faction].keys():
					ibs.write("," + str(FactionWorldLinkBetweenness[faction][edge]))
				else:
					ibs.write("," + str(FactionWorldLinkBetweenness[faction][(edge[1], edge[0])]))
			for pair in FactionPairsList:
				if edge in InterfactionLinkBetweenness[pair].keys():
					ibs.write("," + str(InterfactionLinkBetweenness[pair][edge]))
				else:
					ibs.write("," + str(InterfactionLinkBetweenness[pair][(edge[1], edge[0])]))
		ibs.write("\n")
	ibs.close()

	#------------------------------------

###########################################################################
#	Structural communities versus 
####################################################################################

def VariationOfInformation(datasettag, clusteringtag):

	FactionCharacters = LoadFactions(datasettag)[1]
	CommunityCharacters = LoadCommunities(datasettag, clusteringtag)[1]
	CommunityFactionCharacters, CommunityFactionSize, characters, communities, factions = CommunityFactionIntersections(datasettag, clusteringtag)

	NumberOfCharacters = len(characters)
#	CharacterFactions, FactionCharacters = LoadFactions(datasettag)

	# characters = sorted(set(CharacterFactions.keys()))
	# NumberOfCharacters = len(characters)
	# communities = sorted(set(CharacterCommunities.values()))
	# factions = sorted(set(FactionCharacters.keys()))

	# CharacterCommunities, CommunityCharacters = LoadCommunities(datasettag, clusteringtag)

	# CommunityFactionCharacters = dict()
	# for community in communities:
	# 	CommunityFactionCharacters[community] = dict()
	# 	for faction in factions:
	# 		CommunityFactionCharacters[community][faction] = []
	# for character in characters:
	# 	CommunityFactionCharacters[Community[character]][Faction[character]].append(character)

	# CommunityFactionSize = dict()
	# for community in communities:
	# 	CommunityFactionSize[community] = dict()
	# 	for faction in factions:
	# 		if ( len(CommunityFactionCharacters[community][factions]) != 0 ):
	# 			CommunityFactionSize[community][faction] = len(CommunityFactionCharacters[community][faction])

	# CommunityFactionSize = [len(CommunityFactionCharacters[character][faction]) for community in communities for faction in factions]

	VariationOfInformation = 0
	for faction in factions:
		for community in communities:
			rij = np.divide(len(CommunityFactionCharacters[community][faction]), NumberOfCharacters)
			pi = np.divide(len(FactionCharacters[faction]), NumberOfCharacters)
			qj = np.divide(len(CommunityCharacters[community]), NumberOfCharacters)
			if ( rij != 0 ):
				VariationOfInformation += - rij*(np.log2(np.divide(rij,pi)) + np.log2(np.divide(rij,qj)))
				
	NormalizedVariationOfInformation = np.divide(VariationOfInformation,np.log2(NumberOfCharacters))

	return NormalizedVariationOfInformation

####################################################################################

def LoadCommunities(datasettag, clusteringtag):

	try:
	    os.makedirs("../Outputs/" + datasettag + "/Objects/")
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	    	raise

	if os.path.isfile("../Outputs/" + datasettag + "/Objects/CharacterCommunities" + datasettag + "_" + clusteringtag + ".pkl"):
		CharacterCommunities = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterCommunities" + datasettag + "_" + clusteringtag + ".pkl","rb"))
		CommunityCharacters = pk.load(open("../Outputs/" + datasettag + "/Objects/CommunityCharacters" + datasettag + "_" + clusteringtag + ".pkl","rb"))
	else:
		CharacterCommunities = dict()
		for line in open("../Inputs/CharacterCommunities" + datasettag + "_" + clusteringtag + ".csv").read().splitlines()[0:]:
			CharacterCommunities[line.split(",")[0].strip(" ")] = line.split(",")[1].strip(" ")
		CommunityCharacters = FactionCharacterLists(CharacterCommunities)
		pk.dump(CharacterCommunities, open( "../Outputs/" + datasettag + "/Objects/CharacterCommunities" + datasettag + "_" + clusteringtag + ".pkl", "wb" ))
		pk.dump(CommunityCharacters, open( "../Outputs/" + datasettag + "/Objects/CommunityCharacters" + datasettag + "_" + clusteringtag + ".pkl", "wb" ))

	return CharacterCommunities, CommunityCharacters

###########################################################################

def CommunityFactionIntersections(datasettag, clusteringtag, reverse = False):
	
	if reverse:
		CharacterCommunities, CommunityCharacters = LoadFactions(datasettag)
		CharacterFactions, FactionCharacters = LoadCommunities(datasettag, clusteringtag)
	else:
		CharacterFactions, FactionCharacters = LoadFactions(datasettag)
		CharacterCommunities, CommunityCharacters = LoadCommunities(datasettag, clusteringtag)

	communities = sorted(set(CharacterCommunities.values()))
	factions = sorted(set(FactionCharacters.keys()))
	characters = sorted(set(CharacterFactions.keys()))

	CommunityFactionCharacters = dict()
	for community in communities:
		CommunityFactionCharacters[community] = dict()
		for faction in factions:
			CommunityFactionCharacters[community][faction] = []
	for character in characters:
		CommunityFactionCharacters[CharacterCommunities[character]][CharacterFactions[character]].append(character)

	CommunityFactionSize = dict()
	for community in communities:
		CommunityFactionSize[community] = dict()
		for faction in factions:
			if not CommunityFactionCharacters[community][faction]:
				[]
			else:
				CommunityFactionSize[community][faction] = len(CommunityFactionCharacters[community][faction])

	return CommunityFactionCharacters, CommunityFactionSize, characters, communities, factions

###########################################################################

def CommunityFactionPiecharts(datasettag, clusteringtag, reverse = False):

	if reverse:
		CommunityFactionCharacters, CommunityFactionSize, characters, communities, factions = CommunityFactionIntersections(datasettag, clusteringtag, reverse=True)
	else:	
		CommunityFactionCharacters, CommunityFactionSize, characters, communities, factions = CommunityFactionIntersections(datasettag, clusteringtag)

			##################################################################

	if reverse:
		folder = 'FactionsByCommunity'
	else:
		folder = 'CommunitiesByFaction'

	try:
	    os.makedirs("../Outputs/" + datasettag + "/FactionsAndCommunities/" + clusteringtag + "/" + folder)
	except OSError as exception:
	    if exception.errno != errno.EEXIST:
	        raise
	
	commlist = open("../Outputs/" + datasettag + "/FactionsAndCommunities/" + clusteringtag + "/" + folder + "/" + datasettag + "_" + clusteringtag + ".txt" , 'w')
	colores = ['Maroon','Red','Yellow','Olive','Lime','Green','Aqua','Teal','Blue','Navy','Fuchsia','Purple','Silver']
	factionslist = [faction for faction in factions]

	counterc = 0
	for c in communities:
		commlist.write("Community " + c + ": \n")
		labels = [L for L in CommunityFactionSize[c].keys()]
		values = [V for V in CommunityFactionSize[c].values()]
		for la in labels:
			commlist.write("  " + la + ":\n")
			for c2 in CommunityFactionCharacters[c][la]:
				commlist.write("     " + c2 + "\n")
			#commlist.write("\n\n")
		commlist.write("\n")
		sumvalues = np.sum(values)
		normvalues = [np.divide(V,sumvalues) for V in values]
		colorz = [colores[factionslist.index(chra)] for chra in labels]
		fig = plt.figure(counterc)
		plt.pie(normvalues, labels=labels,colors=colorz,autopct='%1.1f%%', shadow=False, startangle=90)
		plt.title("Community " + c)
		ax = fig.gca()
		ax.set_aspect('equal')
		plt.savefig("../Outputs/" + datasettag + "/FactionsAndCommunities/" + clusteringtag + "/" + folder + "/" + c + "_" + datasettag + "_" + clusteringtag + 'Breakdown.png', bbox_inches='tight')
		plt.close()
		counterc += 1
	commlist.close()
		
#############################################################
# BORROWED FROM...
#    Copyright (C) 2009 by
#    Thomas Aynaud <thomas.aynaud@lip6.fr>
#    All rights reserved.
#    BSD license.

def modularity(partition, graph, weight='weight'):
    """Compute the modularity of a partition of a graph

    Parameters
    ----------
    partition : dict
       the partition of the nodes, i.e a dictionary where keys are their nodes
       and values the communities
    graph : networkx.Graph
       the networkx graph which is decomposed
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'


    Returns
    -------
    modularity : float
       The modularity

    Raises
    ------
    KeyError
       If the partition is not a partition of all graph nodes
    ValueError
        If the graph has no link
    TypeError
        If graph is not a networkx.Graph

    References
    ----------
    .. 1. Newman, M.E.J. & Girvan, M. Finding and evaluating community
    structure in networks. Physical Review E 69, 26113(2004).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)
    >>> modularity(part, G)
    """
    if type(graph) != nx.Graph:
        raise TypeError("Bad graph type, use only non directed graph")

    inc = dict([])
    deg = dict([])
    links = graph.size(weight=weight)
    if links == 0:
        raise ValueError("A graph without link has an undefined modularity")

    for node in graph:
        com = partition[node]
        deg[com] = deg.get(com, 0.) + graph.degree(node, weight=weight)
        for neighbor, datas in graph[node].items():
            edge_weight = datas.get(weight, 1)
            if partition[neighbor] == com:
                if neighbor == node:
                    inc[com] = inc.get(com, 0.) + float(edge_weight)
                else:
                    inc[com] = inc.get(com, 0.) + float(edge_weight) / 2.

    res = 0.
    for com in set(partition.values()):
        res += (inc.get(com, 0.) / links) - \
               (deg.get(com, 0.) / (2. * links)) ** 2
    return res

###########################################################################
###########################################################

def ProfileSimilarity(Profile1, Profile2, measure = 'cosine', max = 0):

	VectorLength1 = 0
	VectorLength2 = 0
	for ind, entry in enumerate(Profile1):
		VectorLength1 += np.power(Profile1[ind],2)
		VectorLength2 += np.power(Profile2[ind],2)
	VectorLength1 = np.sqrt(VectorLength1)
	VectorLength2 = np.sqrt(VectorLength2)

	sumofdiff = 0
	sumofsqdiff = 0
	dotproduct = 0
	for ind, entry in enumerate(Profile1):
		sumofdiff += np.abs(np.subtract(Profile1[ind], Profile2[ind]))
		sumofsqdiff += np.power(np.subtract(Profile1[ind], Profile2[ind]), 2)
		dotproduct += np.dot(Profile1[ind], Profile2[ind])
	if measure == 'cosine':
		similarity = np.divide(dotproduct, np.dot(VectorLength1, VectorLength2))
	if measure == 'sum':
		similarity = np.sqrt(sumofsqdiff) #np.sqrt(sumofsquares)
	if measure == 'euclid':
		similarity = sumofdiff #np.sqrt(sumofsquares)

	return similarity

###########################################################
###############################################################

def WeightedGraphDensity(G):

	EdgeWeights = [G[edge[0]][edge[1]]['weight'] for edge in G.edges()]
	EdgeWeightSum = np.sum(EdgeWeights)
	print(len(EdgeWeights))
	print(EdgeWeightSum)
	N = len(G.nodes())
	Density = np.divide(2*EdgeWeightSum, N*(N-1))

	return Density

###############################################################
