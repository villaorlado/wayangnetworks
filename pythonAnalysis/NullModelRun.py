import os, sys
import pickle as pk
import errno
import numpy as np
import networkx as nx
#import matplotlib.pyplot as plt
import CooccurrenceNetworks as co

#######################################################################

datasettag = sys.argv[1]

#######################################################################

ensembletag = sys.argv[2]

#######################################################################

NumberOfRealizations = sys.argv[3]

########################################################################


EpisodeNodes, CharacterNodes, B, G, GI, E, EI = co.LoadGraphs(datasettag)

# # Prepare directory for output files (spreadsheets, plots, etc.):
# try:
#     os.makedirs("../Outputs/" + datasettag + "/Objects/")
# except OSError as exception:
#     if exception.errno != errno.EEXIST:
#     	raise

# if os.path.isfile("./Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl"):
# 	EpisodeNodes = pk.load(open("../Outputs/" + datasettag + "/Objects/EpisodeNodes" + datasettag + ".pkl","rb"))
# 	CharacterNodes = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterNodes" + datasettag + ".pkl","rb"))
# 	B = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl","rb"))
# 	G = pk.load(open("../Outputs/" + datasettag + "/Objects/CharacterCooccurrence" + datasettag + ".pkl","rb"))
# 	GI = pk.load(open("../Outputs/" + datasettag + "/Objects/InverseWeightCharacterCooccurrence" + datasettag + ".pkl","rb"))
# else:
# 	EpisodeNodes, CharacterNodes, B = co.ConstructBipartite(datasettag)
# 	G = co.CharacterCooccurrenceNetwork(B, EpisodeNodes, CharacterNodes)
# 	GI = co.InverseWeightCooccurrenceNetwork(G)
# 	pk.dump(EpisodeNodes, open( "../Outputs/" + datasettag + "/Objects/EpisodeNodes" + datasettag + ".pkl", "wb" ))
# 	pk.dump(CharacterNodes, open( "../Outputs/" + datasettag + "/Objects/CharacterNodes" + datasettag + ".pkl", "wb" ))
# 	pk.dump(B, open( "../Outputs/" + datasettag + "/Objects/CharacterEpisodeBipartite" + datasettag + ".pkl", "wb" ))
# 	pk.dump(G, open( "../Outputs/" + datasettag + "/Objects/CharacterCooccurrence" + datasettag + ".pkl", "wb" ))
# 	pk.dump(GI, open( "../Outputs/" + datasettag + "/Objects/InverseWeightCharacterCooccurrence" + datasettag + ".pkl", "wb" ))

###########################################################

Degrees = nx.degree(B, weight = 'weight')
EpisodeDegrees = dict()
for episode in EpisodeNodes:
	EpisodeDegrees[episode] = Degrees[episode]
CharacterDegrees = dict()
for character in CharacterNodes:
	CharacterDegrees[character] = Degrees[character]

##########################################################

CharacterStrengths = nx.degree(G, weight = 'weight')
CharacterBetweenness = nx.betweenness_centrality(GI, weight = 'weight', normalized = True)

EpisodeStrengths = nx.degree(E, weight = 'weight')
EpisodeBetweenness = nx.betweenness_centrality(EI, weight = 'weight', normalized = True)

LinkWeightsTarget = dict()
LinkDegreeProduct = dict()
LinkBetweenness = nx.edge_betweenness_centrality(GI, weight = 'weight', normalized = True)

for edge in GI.edges():
	LinkWeightsTarget[edge] = G[edge[0]][edge[1]]['weight']
	LinkDegreeProduct[edge] = np.dot(CharacterDegrees[edge[0]], CharacterDegrees[edge[1]])

##########################################################

# ibs = open("../Outputs/" + datasettag + "/CharList.csv" , 'w')
# for character in CharacterNodes:
# 	ibs.write(character + "," + "\n")#," + str(factioneccentricity[faction]) + "," + str(factioncloseness[faction]) + "\n")
# ibs.close()	

#CharacterFactions, FactionCharacters = co.LoadFactions(datasettag)
CharacterFactions, FactionCharacters = co.LoadFactionsMultiple(datasettag)

# CharacterFactions = co.CharacterFactionAffiliations(datasettag)
# FactionCharacters = co.FactionCharacterLists(CharacterFactions)
InterfactionBetweenness = co.LoadInterfactionBetweennessMultiple(datasettag)#co.InterfactionBetweennessCentrality(GI, FactionCharacters)
FactionWorldBetweenness = co.LoadFactionWorldBetweennessMultiple(datasettag)#co.FactionWorldBetweennessCentrality(GI, FactionCharacters)

##########################################################

co.NullModelEnsemble(datasettag, ensembletag, EpisodeDegrees, CharacterDegrees, NumberOfRealizations, FactionCharacters, LinkWeightsTarget,1)
#co.NullModelEnsemble(datasettag, ensembletag, EpisodeDegrees, CharacterDegrees, NumberOfRealizations, 0, LinkWeightsTarget)
#co.NullModelEnsemble(datasettag, ensembletag, EpisodeDegrees, CharacterDegrees, NumberOfRealizations, 0, LinkWeightsTarget, 1)

##########################################################

co.NullModelEnsembleProcess(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness, InterfactionBetweenness, FactionWorldBetweenness, LinkWeightsTarget, LinkDegreeProduct, LinkBetweenness,EpisodeDegrees,EpisodeStrengths,EpisodeBetweenness)
#co.NullModelEnsembleProcess(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness,[],[],LinkWeightsTarget,LinkDegreeProduct,LinkBetweenness)
#co.NullModelEnsembleProcess(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness,[],[],LinkWeightsTarget,LinkDegreeProduct,LinkBetweenness,EpisodeDegrees,EpisodeStrengths,EpisodeBetweenness)


co.NullModelEnsembleBetweennessVsDegree(datasettag, ensembletag, CharacterDegrees, CharacterStrengths, CharacterBetweenness)
co.NullModelEnsembleBetweennessVsDegreeEpisodes(datasettag, ensembletag, EpisodeDegrees, EpisodeStrengths, EpisodeBetweenness)

co.NullModelEnsembleLinkBetweennessVs(datasettag, ensembletag, LinkWeightsTarget, LinkDegreeProduct, LinkBetweenness)

