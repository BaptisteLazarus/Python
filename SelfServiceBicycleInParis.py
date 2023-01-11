# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 22:43:50 2022

@author: 33665
"""
import pandas

from matplotlib import pyplot as plt
import seaborn

%matplotlib inline

import requests

import folium

#import of stations informations et
url = "https://opendata.paris.fr/api/records/1.0/search/"
dataset = "velib-disponibilite-en-temps-reel"
#get the number of stations
r = requests.get(url = url, params = dict(dataset = dataset)).json()
#get everuthing
df = pandas.DataFrame([s["fields"] for s in requests.get(url = url, params = dict(dataset = dataset, rows = r['nhits'])).json()['records']])
df.head()

#capacity distribution
seaborn.displot(data = df, x = "capacity")
seaborn.boxplot(data = df, x = "capacity")

#cities distribution
plt.figure(figsize=(18,18))
seaborn.boxplot(data = df, x = "capacity", y = "city_name")

#Display the stations on a map
def popup(station):
    msg = "<strong>" + station["name"] + "</strong>"\
        + " (" + station["nom_arrondissement_communes"] + ")"
    return msg

centre = [48.87, 2.35]
paris = folium.Map(location = centre, zoom_start = 11)

for st in range(df.shape[0]):
    station = df.iloc[st,:]
    # print(popup(station))
    folium.Marker(station["coordonnees_geo"],
                  tooltip = station["name"],
                  popup = popup(station)).add_to(paris)
paris

#For each city, calculate stations/capacity/bikes available/docks available numbers and GPS coordinates 
ag_count = df.filter(["nom_arrondissement_communes", "capacity"])\
    .groupby("nom_arrondissement_communes")\
    .count()\
    .rename(columns = {"capacity": "nbStations"})
ag_count.head()

ag_sum = df.filter(["nom_arrondissement_communes", "capacity", "numbikesavailable", "numdocksavailable"])\
    .groupby("nom_arrondissement_communes")\
    .aggregate(["sum"])\
    .droplevel(level = 1, axis = 1)\
    .rename(columns = {"capacity": "capacité", "numbikesavailable": "vélosDispo",
                       "numdocksavailable": "placesDispo"})
ag_sum.head()

ag_mean = df.filter(["nom_arrondissement_communes"])\
    .assign(lat = [c[0] for c in df["coordonnees_geo"]])\
    .assign(lng = [c[1] for c in df["coordonnees_geo"]])\
    .groupby("nom_arrondissement_communes")\
    .aggregate(["mean"])\
    .droplevel(level = 1, axis = 1)
ag_mean.head()

ag_final = pandas.concat([ag_count, ag_sum, ag_mean], axis = 1)
ag_final.head()

#display markers for each city(located in stations center of the city) with belows informations
def popup_ville(ville):
    msg = "<strong>" + ville.name + "</strong><ul>"\
        + "<li>Nombre de stations : " + str(ville["nbStations"]) + "</li>"\
        + "<li>Capacité totale : " + str(ville["capacité"]) + "</li>"\
        + "<li>Vélos disponibles : " + str(ville["vélosDispo"]) + "</li>"\
        + "<li>Places disponibles : " + str(ville["placesDispo"]) + "</li></ul>"
    iframe = folium.IFrame(msg)
    popup = folium.Popup(iframe,
                     min_width = 300,
                     max_width = 300)
    return popup

centre = [48.87, 2.35]
carte_ville = folium.Map(location = centre, zoom_start = 11)

for v in range(ag_final.shape[0]): #
    ville = ag_final.iloc[v,:]
    folium.Marker([ville.lat, ville.lng],
                  tooltip = ville.name,
                  popup = popup_ville(ville)).add_to(carte_ville)
carte_ville
