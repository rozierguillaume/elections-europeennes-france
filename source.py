# (c) Guillaume Rozier, 2019
# Projet Open-Source, license AGPL

import csv
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import scipy
import scipy.interpolate
import json

colors = ['#e6b8af', '#990000', '#e06666', '#cc0000', '#f4cccc', '#ff0e78', '#6aa84f', '#35a9dc', '#00ffff', '#316395', '#1155cc', '#c27ba0', '#073763', '#999999', '#ead1dc', '#e0e000', '#9fc5e8']
nb_sieges = 74 #Hypothèse UK dans l'europe

##########
# Lecture csv sondages
##########
def read_sondages(path):
    sondages = []
    sondages_dic = {}
    #build 'sondages_dic' dictionary
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            sondages = sondages + [row]
            if line_count==0:
                partis = row[2:]
            else:
                #sondages_dic[row[0]]=np.array([])

                sondage_str =  np.array([row[i] for i in range(2,19)])
                sondage_str[sondage_str == ''] = float("nan") #données manquantes
                sondages_dic[line_count] = {}
                sondages_dic[line_count]={"date":row[0], "resultats":sondage_str.astype(float)}

                #if row[0] in sondages_dic:
                    #sondages_dic[row[0]] = np.vstack((sondages_dic[row[0]], sondage_str.astype(float)))
                #else:
                    #sondages_dic[row[0]] = np.array([sondage_str.astype(float)])

            line_count+=1
    #print(sondages_dic)

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

    return dates, donnees, partis, sondages_dic

    ##########
    # Plot sondages
    ##########

##########
# Plot sondages
##########
def plot_sondages(dates, donnees, colors, export):
    grid = plt.GridSpec(10, 10, wspace=0.4, hspace=0.3)

    fig = plt.figure(figsize=(15,8))
    ax = fig.add_subplot(grid[:9,:9])
    fig.suptitle('Intention de vote aux élections européennes en France\n(hypothèses liste gilets jaunes et UK dans UE)', fontsize=15)
    plt.xlabel('Dates')
    plt.ylabel('Intention de vote (%)')
    dates_timestamp = [float(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d").timetuple())) for s in dates]

    for i in range(len(donnees[0])):
        d = np.array([donnees[j][i] for j in range(0,len(donnees))]).astype(float)
        x,y = zip(*sorted((xVal, np.mean([yVal for a, yVal in zip(dates_timestamp, d) if xVal==a])) for xVal in set(dates_timestamp)))
        interp = scipy.interpolate.interp1d(x, y)

        ax.plot(dates, d, 'o', color=colors[i]) #plot points
        ax.plot(dates, [interp(x) for x in dates_timestamp], color=colors[i], label=partis[i], linewidth=1.5) #plot interpolation
        ax.legend(bbox_to_anchor=(0.75, 0.35, 0.5, 0.5))
    plt.xticks(dates, dates, rotation=30, horizontalalignment='right')
    ax.grid(True, which='major', linestyle='-', alpha=0.6)
    plt.minorticks_on()
    ax.grid(True, which='minor', linestyle=':', alpha=0.2)

    if export == True:
        fig.savefig('export/sondages/'+max(dates), dpi=200)


##########
# Calcul du nombre de sièges obtenus
##########
def calcul_sieges_obtenus(partis, sondages_dic, nb_sieges, colors, export):

    ##########
    # Attribution des sièges initiale
    # sieges_obtenus = resultat * nb_sieges
    ##########

    partis.pop(-1) #Suppression de "Autres"
    colors.pop(-1)

    for id in sondages_dic:
        sondages_dic[id]['resultats'] = sondages_dic[id]['resultats'][:-1] #suppression de "Autres"
        sondages_dic[id]['sieges'] = (sondages_dic[id]['resultats'] * 74 / 100).astype(int)
        cpt = 0
        for val in sondages_dic[id]['resultats']:
            if (val < 5) or not (val >= 0):
                sondages_dic[id]['sieges'][cpt] = 0 #Aucun siège si résultat < 5% ou si données non disponible (not i>=0)
            cpt += 1

    ##########
    # Attribution des sièges restants un à un
    ##########

    reste = nb_sieges - sum(sondages_dic[id]['sieges'])

    while reste > 0:
        indice_siege_restant = np.argmax(sondages_dic[id]['resultats']/(sondages_dic[id]['sieges']+1))
        sondages_dic[id]['sieges'][indice_siege_restant] += 1
        reste = nb_sieges - sum(sondages_dic[id]['sieges'])

    for id in sondages_dic:
         sondages_dic[id]['resultats'] = sondages_dic[id]['resultats'].tolist()
         sondages_dic[id]['sieges'] = sondages_dic[id]['sieges'].tolist()

    if export == True:
        with open('export/data/sondages_avec_sieges.json', 'w') as file:
            json.dump(sondages_dic, file, indent=4)

    return partis, sondages_dic

##########
# Export sieges obtenus
##########

def export_sieges(partis, sondages_dic):
    for i in sondages_dic:

        calcul_sieges_obtenus(partis, sondages_dic[sondages_dic]['resultats'], nb_sieges, colors, True)


##########
# Pie chart sieges obtenus (dernier sondage uniquement)
##########
def plot_sieges_pie_chart(partis, sieges_obtenus, colors, export):

    ##########
    #Graph Pie Chart
    ##########

    fig2, ax2 = plt.subplots(figsize=(8,8))
    partis2=partis
    cpt_suppr=0
    print(len(partis))
    print(len(sieges_obtenus))
    for i in range(0, len(sieges_obtenus)):
        if sieges_obtenus[i-cpt_suppr]==0: #Suppresion des partis n'ayant pas de siège
            sieges_obtenus = np.delete(sieges_obtenus, i-cpt_suppr)
            partis.pop(i - cpt_suppr)
            colors.pop(i - cpt_suppr)
            cpt_suppr += 1

    ax2.pie(sieges_obtenus, labels=partis, autopct=lambda p: '{:.0f} sièges'.format(sum(sieges_obtenus)*p/100), startangle=90, colors=colors)
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig2.suptitle('Projection nombre de siège, dernier sondage\n(hypothèses liste gilets jaunes et UK dans UE)', fontsize=15)

    #plt.show()
    if export == True:
        fig2.savefig('export/pie_chart_sieges/'+max(dates), dpi=200)


##########
# Run
##########
dates, donnees, partis, sondages_dic = read_sondages("sondages/sondages_hyp_GJ.csv")
plot_sondages(dates, donnees, colors, True)
partis, sondages_dic = calcul_sieges_obtenus(partis, sondages_dic, nb_sieges, colors, True)
#print(sondages_dic)
plot_sieges_pie_chart(partis, sondages_dic[max(sondages_dic)]['sieges'], colors, export=True)
