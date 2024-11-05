import sys, os
import errno
import numpy as np
import networkx as nx
import CooccurrenceNetworks as co

###############################################################

datasettag = sys.argv[1]

###############################################################

EpisodeNodes, CharacterNodes, B, G, GI, __, __ = co.LoadGraphs(datasettag)
#EpisodeNodes, CharacterNodes, B = co.ConstructBipartite(datasettag)
#G = co.CharacterCooccurrenceNetwork(B, EpisodeNodes, CharacterNodes)
#GI = co.InverseWeightCooccurrenceNetwork(G)

print(EpisodeNodes)

###############################################################

#FactionByCharacter = co.CharacterFactionAffiliations(datasettag)
#CharacterFactions = co.FactionCharacterLists(FactionByCharacter)

try:
    os.makedirs("../Outputs/" + datasettag + "/")
except OSError as exception:
    if exception.errno != errno.EEXIST:
    	raise

thresholded = open("../Outputs/" + datasettag + "/ThresholdedGlobalMetrics" + datasettag + ".csv" , 'w')
thresholded.write("Threshold,Nodes removed,Nodes,Edges,Components,Algebraic Connectivity,Density,Average clustering coefficient,Average Shortest Path,Diameter\n")

thresholded.write("0,0," + str(len(G.nodes())) + "," + str(len(G.edges())) + "," + str(nx.number_connected_components(G)) + "," + str(nx.algebraic_connectivity(G)) + "," + str(nx.density(G)) + "," + str(nx.average_clustering(G)) + ",")
if (nx.number_connected_components(G) == 1):
	thresholded.write(str(nx.average_shortest_path_length(G, weight="weight")) + "," + str(nx.diameter(G)))
else:
	thresholded.write(",")
thresholded.write("\n")	


maxweight = int(np.max([G[edge[0]][edge[1]]['weight'] for edge in G.edges()]))

for threshold in range(1,maxweight+1):
	H = co.WeightedNetworkThreshold(G, threshold)
	HI = co.InverseWeightCooccurrenceNetwork(H)
	thresholded.write(str(threshold) + "," + str(len(G.nodes())-len(H.nodes())) + "," + str(len(H.nodes())) + "," + str(len(H.edges())) + "," + str(nx.number_connected_components(H)) + "," + str(nx.algebraic_connectivity(H)) + "," + str(nx.density(H)) + "," + str(nx.average_clustering(H)) + ",")
	if (nx.number_connected_components(H) == 1):
		thresholded.write(str(nx.average_shortest_path_length(HI, weight="weight")) + "," + str(nx.diameter(HI)))
	else:
		thresholded.write(",")
	thresholded.write("\n")

thresholded.close()

###############################################################