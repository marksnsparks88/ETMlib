import requests
import sqlite3
import os, re

response = requests.get("https://esi.evetech.net/latest/markets/groups/?datasource=tranquility")
market_group_ids=response.json()

#download market group info
if os.path.exists('market_group_info_tmp.json'):
    with open('market_group_info_tmp.json', 'r') as f:
        market_group_info=[json.loads(j) for j in f]
else:
    market_group_info=[]
    
for i in market_group_ids:
    got = False
    for j in market_group_info:
        if i == j['market_group_id']:
            got = True
            break
    if got == False:
        url = "https://esi.evetech.net/latest/markets/groups/{}/?datasource=tranquility&language=en".format(i)
        group_info = requests.get(url)
        if group_info.status_code == 200:
            market_group_info.append(group_info.json())
            with open('market_group_info_tmp.json', 'a') as f:
                f.write(group_info.text)
                f.write("\n")
            print(" Recieved {} out of 1926".format(len(market_group_info)), end="\r")
        else:
            print("Group {} skipped with error code {}".format(i, sgroup_info.status_code))

        
#download item info
if os.path.exists('market_type_info_tmp.json'):
    with open('market_type_info_tmp.json', 'r') as f:
        market_type_info=[json.loads(j) for j in f]
else:
    market_type_info=[]
    
for i in range(len(market_group_info)):
    if len(market_group_info[i]['types']) > 0:
        for j in market_group_info[i]['types']:
            got = False
            for k in market_type_info:
                if j == k['type_id']:
                    got = True
                    break
            if got == False:
                url = "https://esi.evetech.net/latest/universe/types/{}/?datasource=tranquility&language=en".format(j)
                type_info = requests.get(url)
                if type_info.status_code == 200:
                    market_type_info.append(type_info.json())
                    with open('market_type_info_tmp.json', 'a') as f:
                        f.write(type_info.text)
                        f.write("\n")
                    print(" Recieved {} out of 15876".format(len(market_type_info)), end="\r")
                else:
                    print("Type {} skipped with error code {}".format(j, type_info.status_code))

#download system info
response = requests.get("https://esi.evetech.net/latest/universe/systems/?datasource=tranquility")
system_ids=response.json()

if os.path.exists('system_info_tmp.json'):
    with open('system_info_tmp.json', 'r') as f:
        system_info=[json.loads(j) for j in f]
else:
    system_info=[]
    
for i in system_ids:
    got = False
    for j in system_info:
        if i == j['system_id']:
            got = True
            break
    if got == False:
        url = "https://esi.evetech.net/latest/universe/systems/{}/?datasource=tranquility&language=en".format(i)
        system_request = requests.get(url)
        if system_request.status_code == 200:
            system_info.append(system_request.json())
            with open('system_info.json', 'a') as f:
                f.write(system_request.text)
                f.write("\n")
            print(" Recieved {} out of 8485".format(len(system_info)), end="\r")
        else:
            print("Group {} skipped with error code {}".format(i, system_request.status_code))

#download station info
if os.path.exists('station_info_tmp.json'):
    with open('station_info_tmp.json', 'r') as f:
        station_info=[json.loads(j) for j in f]
else:
    station_info=[]

for i in system_info:
    if 'stations' in system_info.keys():
        for j in i['stations']:
            got = False
            for k in station_info:
                if j == k['station_id']:
                    got = True
                    break
        if got == False:
            url = "https://esi.evetech.net/latest/universe/stations/{}/?datasource=tranquility&language=en".format(j)
            station_request = requests.get(url)
            if station_request.status_code == 200:
                station_info.append(station_request.json())
                with open('station_info_tmp.json', 'a')as f:
                    f.write(station_request.text)
                    f.write("\n")
                print(" Recieved {} out of 5144".format(len(station_info)), end="\r")
            else:
                print("Group {} skipped with error code {}".format(i, station_request.status_code))
                
#download constellation info
response = requests.get("https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility")
constellation_ids=response.json()

if os.path.exists('constellation_info_tmp.json'):
    with open('constellation_info_tmp.json', 'r') as f:
        constellation_info=[json.loads(j) for j in f]
else:
    constellation_info=[]
    
for i in constellation_ids:
    got = False
    for j in constellation_info:
        if i == j['constellation_id']:
            got = True
            break
    if got == False:
        url = "https://esi.evetech.net/latest/universe/constellations/{}/?datasource=tranquility&language=en".format(i)
        constellation_request = requests.get(url)
        if constellation_request.status_code == 200:
            constellation_info.append(constellation_request.json())
            with open('constellation_info.json', 'a') as f:
                f.write(constellation_request.text)
                f.write("\n")
            print(" Recieved {} out of 1174".format(len(constellation_info)), end="\r")
        else:
            print("Group {} skipped with error code {}".format(i, constellation_request.status_code))

#download region info
response = requests.get("https://esi.evetech.net/latest/universe/regions/?datasource=tranquility")
region_ids=response.json()

if os.path.exists('region_info_tmp.json'):
    with open('region_info_tmp.json', 'r') as f:
        region_info=[json.loads(j) for j in f]
else:
   region_info=[]
    
for i in region_ids:
    got = False
    for j in region_info:
        if i == j['region_id']:
            got = True
            break
    if got == False:
        url = "https://esi.evetech.net/latest/universe/regions/{}/?datasource=tranquility&language=en".format(i)
        region_request = requests.get(url)
        if region_request.status_code == 200:
            region_info.append(region_request.json())
            with open('region_info.json', 'a') as f:
                f.write(region_request.text)
                f.write("\n")
            print(" Recieved {} out of 112".format(len(region_info)), end="\r")
        else:
            print("Group {} skipped with error code {}".format(i, region_request.status_code))

#remove un-needed item info
for i in market_type_info:
    if 'dogma_attributes' in i.keys():
        del i['dogma_attributes']
    if 'dogma_effects' in i.keys():
        del i['dogma_effects']

#create child group list
for i in range(len(market_group_info)):
    if 'child_groups' not in market_group_info[i].keys():
        market_group_info[i]['child_groups']=[]
    for j in range(len(market_group_info)):
        if 'parent_group_id' in market_group_info[j].keys():
            if market_group_info[j]['parent_group_id'] == market_group_info[i]['market_group_id']:
                market_group_info[i]['child_groups'].append(market_group_info[j]['market_group_id'])

#merge lists into strings for database
for i in range(len(market_group_info)):
    for k, v in market_group_info[i].items():
        if type(v).__name__ == 'list':
            if len(v) == 0:
                market_group_info[i][k] = None
            else:
                liststr = [str(n) for n in v]
                market_group_info[i][k] = ' '.join(liststr)
                


