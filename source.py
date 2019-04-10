# (c) Guillaume Rozier, 2019
# Projet Open-Source, license AGPL

import csv
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import scipy
import scipy.interpolate

sondages_dic = {}
nb_sieges = 74 #Hypothèse UK dans l'europe
sondages = []
colors = ['#e6b8af', '#990000', '#e06666', '#cc0000', '#f4cccc', '#ff0e78', '#6aa84f', '#35a9dc', '#00ffff', '#316395', '#1155cc', '#c27ba0', '#073763', '#999999', '#ead1dc', '#ffff00', '#9fc5e8']

#build 'sondages_dic' dictionary
with open("sondages/sondages_hyp_GJ.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    line_count=0
    for row in csv_reader:
        sondages = sondages + [row]
        if line_count==0:
            partis = row[2:]
        else:
            sondages_dic[row[0]]={}
            sondage_str =  np.array([row[i] for i in range(2,19)])
            sondage_str[sondage_str == ''] = float("nan") #données manquantes
            sondages_dic[row[0]]["resultats"] = sondage_str.astype(float)
        line_count+=1

def replace_x_by_y(x, y, object):
    for a in range(0, len(object)):
        for i in range(0, len(object[a])):
            if object[a][i] == x:
                object[a][i] = y
    return object

dates = np.array([x[0] for x in sondages[1:]])
donnees = np.array([ np.array(d[2:]) for d in np.asarray(sondages[1:]) ])
donnees = replace_x_by_y('', float("nan"), donnees) #données manquantes
donnees = [donnees[i].astype(float) for i in range(0, len(donnees))]


##########
# Plot sondages
##########
def plot_sondages(dates, donnees, colors, export):
    grid = plt.GridSpec(10, 10, wspace=0.4, hspace=0.3)

    fig = plt.figure(figsize=(15,8))
    ax = fig.add_subplot(grid[:9,:9])
    fig.suptitle('Intention de vote aux élections européennes en France (hypothèses liste gilets jaunes et UK dans UE)')
    plt.xlabel('Dates')
    plt.ylabel('Intention de vote (%)')
    dates_timestamp = [float(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d").timetuple())) for s in dates]

    for i in range(len(donnees[0])):
        d = np.array([donnees[j][i] for j in range(0,len(donnees))]).astype(float)
        x,y = zip(*sorted((xVal, np.mean([yVal for a, yVal in zip(dates_timestamp, d) if xVal==a])) for xVal in set(dates_timestamp)))
        interp = scipy.interpolate.interp1d(x, y)

        ax.plot(dates, d, '.', color=colors[i]) #plot points
        ax.plot(dates, [interp(x) for x in dates_timestamp], color=colors[i], label=partis[i]) #plot interpolation
        ax.legend(bbox_to_anchor=(0.75, 0.35, 0.5, 0.5))
    plt.xticks(dates, dates, rotation=30, horizontalalignment='right')
    ax.grid(True, which='major', linestyle='-', alpha=0.6)
    plt.minorticks_on()
    ax.grid(True, which='minor', linestyle=':', alpha=0.2)

    if export == True:
        fig.savefig('export/sondages/'+max(dates), dpi=300)


##########
#Pie chart
##########
def calcul_sieges_obtenus(partis, sondages_dic, nb_sieges, colors, export):

    ##########
    # Attribution des sièges initiale
    # sieges_obtenus = resultat * nb_sieges
    ##########

    for i in sondages_dic:
        sondages_dic[i]['resultats'] = sondages_dic[i]['resultats'][:-1]

    res_dernier_sondages_dic = sondages_dic[max(sondages_dic)]['resultats']

    cpt=0

    partis.pop(-1) #Suppression de "Autres"
    colors.pop(-1)
    print(res_dernier_sondages_dic)
    for i in res_dernier_sondages_dic:
        if i<5:
            res_dernier_sondages_dic[cpt]=0 #Aucun siège si résultat < 5%
        cpt += 1

    sieges_obtenus = (res_dernier_sondages_dic * 74 / 100).astype(int)


    ##########
    # Attribution des sièges restants un à un
    ##########
    rest = nb_sieges - sum(sieges_obtenus)

    while rest > 0:
        indice_siege_restant = np.argmax(sondages_dic[max(sondages_dic)]['resultats']/(sieges_obtenus+1))
        sieges_obtenus[indice_siege_restant] += 1
        rest = nb_sieges - sum(sieges_obtenus)

    return partis, sieges_obtenus

def plot_sieges_pie_chart(partis, sieges_obtenus, colors, export):

    ##########
    #Graph Pie Chart
    ##########

    fig2, ax2 = plt.subplots()
    partis2=partis
    cpt_suppr=0
    for i in range(0, len(sieges_obtenus)):
        if sieges_obtenus[i-cpt_suppr]==0: #Suppresion des partis n'ayant pas de siège
            sieges_obtenus = np.delete(sieges_obtenus, i-cpt_suppr)
            partis.pop(i - cpt_suppr)
            colors.pop(i - cpt_suppr)
            cpt_suppr += 1

    ax2.pie(sieges_obtenus, labels=partis, autopct=lambda p: '{:.0f} sièges'.format(sum(sieges_obtenus)*p/100), startangle=90, colors=colors)
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    #plt.show()
    if export == True:
        fig2.savefig('export/pie_chart_sieges/'+max(dates), dpi=300)

plot_sondages(dates, donnees, colors, True)
partis, sieges_obtenus = calcul_sieges_obtenus(partis, sondages_dic, nb_sieges, colors, True)
plot_sieges_pie_chart(partis, sieges_obtenus, colors, export=True)
