'''
This file calculates the average number of characters per adegan number
'''

import glob
import numpy
import matplotlib.pyplot as plt
import seaborn
import matplotlib.ticker as ticker
import numpy as np
numberArray = []
c = 0
distance = []
lakonData = "number,characters,sigma,"

for x in range(1,24):
	lakonData += "lakon%s," %x

for y in range (0,12):
	numberArray.append([])
	distance.append(y+1)

for fileItem in sorted(glob.glob("../html/lakonPages/data/*.csv")):

	#file has been read, now goint to the adegan
	adegans = open(fileItem).readlines()
	for x in range (1, 13): #thre are maximum 12 adegans across the collection, but here we take 13 since the csv has heathers
		if (x < len(adegans)):
			numberOfCharacters = int(adegans[x].split(',')[0])
			numberArray[x-1].append(numberOfCharacters)
		else:
			numberArray[x-1].append(0)

energy = []
sigma = []
d=1

for n in numberArray:
	print n
	characterNumbers = ",".join(str(x) for x in n)
	n = list(filter(lambda a: a != 0, n))
	lakonData += "\n%s,%s,%s,%s" % (d,numpy.mean(n),numpy.std(n),characterNumbers)
	energy.append(numpy.mean(n))
	sigma.append(numpy.std(n)*2)
	plt.boxplot(numberArray)
	d+=1

#plt.errorbar(distance, energy, sigma, capsize=5, elinewidth=2, markeredgewidth=2)
plt.plot(distance,energy)
#plt.xlim(1,14)
#ax = plt.axes()
#ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
#ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

#plt.show()

with open("../html/data/lakondata.csv", "w") as file:
		file.write(lakonData)
		print "lakondata.csv created"
