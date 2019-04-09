import csv
import numpy as np

sond = {}
sondages=[]

#build 'sond' dictionary
with open("Sondages/Sondages_hyp_GJ.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    line_count=0
    for row in csv_reader:
        sondages=sondages+[row]
        if line_count ==0:
            partis = [row[i] for i in range(2,18)]
        else:
            sond[row[0]]={}
            sond[row[0]]["resultats"] = np.array([float(row[i]) for i in range(2,18)])
        line_count+=1

print(max(sond))


##########
# Attribution des sièges initiale
# sieges_obtenus = resultat * nb_sieges
##########
nb_sieges = 74 #hypothese UK dans UE
res_dernier_sond = sond[max(sond)]['resultats']
cpt=0

for i in res_dernier_sond:
    if i<5:
        res_dernier_sond[cpt]=0
    cpt += 1

sieges_obtenus = (res_dernier_sond * 74 / 100).astype(int)


##########
# Attribution des sièges restants un à un
##########
rest = nb_sieges - sum(sieges_obtenus)

while rest > 0:
    indice_siege_restant = np.argmax(sond[max(sond)]['resultats']/(sieges_obtenus+1))
    sieges_obtenus[indice_siege_restant] += 1
    rest = nb_sieges - sum(sieges_obtenus)

print([partis, sieges_obtenus])
