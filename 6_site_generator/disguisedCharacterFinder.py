import re

inputFile = "../input/stories.txt"
narratives = open(inputFile).read()
memba = []
membaList = ""
matchObj = re.findall(r'\[(\w*@\w*)\]',narratives)

for match in matchObj:
	if not match in memba:
		memba.append(match)

for mem in memba:
	print mem
	membaList += "\n" + str(mem)

with open("../input/listOfDisguisedCharacters.txt", "w") as file:
		file.write(membaList)
		print "File created sucessfully"

'''Result
.Sinduragen@Kanastren
.Godakesa@Arjuna
.Guard@Yamadipati
.RaraTemon@SitiSendari
.RaraTemon@Sri
.JakaPupon@Sadana
.Rarawangen@Antakawulan
.LesmanaMurdaka@Arjuna
.Bimasakti@Werkudara
.Bimasakti@Wenang
.Gatotkaca@Brajadhenta
.Sintawaka@RaraIreng
.Kesawasidhi@Kresna
.Brahala@Kresna
.Nagasewu@Nagagini
.BayuBajra@Antareja
.Nagabanda@Nagatatmala
.NagaSewu@Nagagini
.Nindyamaya@Werkudara
.Amonggati@Anoman
.Raksasa@Parasara
.SuksmaLanggeng@Arjuna
.Boar@Sengkuni
.Gatotkaca@Bendana
.Lion@Prasara
.Woman@Durga
.Tiger@Wisnu
.Kalanjaya@Citrasena
.Kalantaka@Citrarata
.Basudewa@Gorawangsa
Raksasa1@Indra
Raksasa2@Bayu
Ratmuka@Arjuna
Arjuna@Ratmuka
Narada@Dhamdharat

'''
