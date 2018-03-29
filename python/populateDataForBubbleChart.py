import xlrd

#variables
#data = [{x:120,r:0.5,color:"green",name:"gatotkaca", origin:"India"}]
data = []

#functions
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num-1

book = xlrd.open_workbook("../input/characters_withLakonAndQuantitativeData.xlsx") #name of the file to open
sh = book.sheet_by_index(0)

for num in range(1,sh.nrows):
	name = sh.cell_value(rowx=num, colx=0)
	punokawan = origin = sh.cell_value(rowx=num, colx=1)
	if (punokawan == "Punokawan"):
		origin = "Punokawan"
	else: 
		origin = sh.cell_value(rowx=num, colx=4)	
	weightedDegree = sh.cell_value(rowx=num,colx=col2num("AC"))
	if weightedDegree:
		dictionary = {"x":float(weightedDegree/734),"r":0.5,"origin":str(origin),"name":str(name)}
		#dictionary.name = name
		data.append(dictionary)

#print str(data)

#bisma, daryamaya, ngembat landeyan, setyajid

data = []
book = xlrd.open_workbook("../input/interchangeability.xlsx") #name of the file to open
sh = book.sheet_by_index(0)

for num in range(1,sh.nrows):
	name = sh.cell_value(rowx=num, colx=0)
	weightedDegree = sh.cell_value(rowx=num,colx=2)
	permissible = int(sh.cell_value(rowx=num,colx=3))
	if permissible == 1:
		origin = "Change";
	else:
		origin = "NoChange";
	dictionary = {"x":float(weightedDegree/734),"r":0.5,"origin":str(origin),"name":str(name)}
	data.append(dictionary)
	
print str(data)
