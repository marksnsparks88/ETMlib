import requests
import sqlite3
import os, re
import json

#download market group info
if os.path.exists('market_group_info_tmp.json'):
    with open('market_group_info_tmp.json', 'r') as f:
        market_group_info=[json.loads(j) for j in f]
else:
    market_group_info=[]

response = requests.get("https://esi.evetech.net/latest/markets/groups/?datasource=tranquility")
market_group_ids=response.json()
    
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
if os.path.exists('system_info_tmp.json'):
    with open('system_info_tmp.json', 'r') as f:
        system_info=[json.loads(j) for j in f]
else:
    system_info=[]
    
response = requests.get("https://esi.evetech.net/latest/universe/systems/?datasource=tranquility")
system_ids=response.json()

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
            print("System {} skipped with error code {}".format(i, system_request.status_code))

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
                print("Station {} skipped with error code {}".format(i, station_request.status_code))
                
#download constellation info
if os.path.exists('constellation_info_tmp.json'):
    with open('constellation_info_tmp.json', 'r') as f:
        constellation_info=[json.loads(j) for j in f]
else:
    constellation_info=[]
    
response = requests.get("https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility")
constellation_ids=response.json()

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
            with open('constellation_info_tmp.json', 'a') as f:
                f.write(constellation_request.text)
                f.write("\n")
            print(" Recieved {} out of 1174".format(len(constellation_info)), end="\r")
        else:
            print("Constellation {} skipped with error code {}".format(i, constellation_request.status_code))

#download region info
if os.path.exists('region_info_tmp.json'):
    with open('region_info_tmp.json', 'r') as f:
        region_info=[json.loads(j) for j in f]
else:
   region_info=[]
    
response = requests.get("https://esi.evetech.net/latest/universe/regions/?datasource=tranquility")
region_ids=response.json()

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
            with open('region_info_tmp.json', 'a') as f:
                f.write(region_request.text)
                f.write("\n")
            print(" Recieved {} out of 112".format(len(region_info)), end="\r")
        else:
            print("Region {} skipped with error code {}".format(i, region_request.status_code))

create_table('market_group_info', market_group_info, 'eve-data.db')
add_data('market_group_info', market_group_info, 'eve-data.db')

create_table('market_type_info', market_type_info, 'eve-data.db')
add_data('market_type_info', market_type_info, 'eve-data.db')

create_table('station_info', station_info, 'eve-data.db')
add_data('station_info', station_info, 'eve-data.db')

create_table('system_info',system_info, 'eve-data.db')
add_data('system_info', system_info, 'eve-data.db')

create_table('constellation_info', constellation_info, 'eve-data.db')
add_data('constellation_info', constellation_info, 'eve-data.db')

create_table('region_info', region_info, 'eve-data.db')
add_data('region_info', region_info, 'eve-data.db')

def get_table_headers(list_):
    keys = list(list_[0].keys())
    kt = {}
    for i in range(1, len(list_)):
        new_keys = list_[i].keys()
        for k in new_keys:
            if k not in keys:
                keys.append(k)
        for k in keys:
            if k not in kt:
                try:
                    type_ = type(list_[i][k]).__name__
                except KeyError:
                    continue
                if type_ == 'list' or type_ == 'dict':
                    type_ = 'TEXT'
                elif type_ == 'int':
                    type_ = 'INTEGER'
                elif type_ == 'str':
                    type_ = 'TEXT'
                elif type_ == 'bool':
                    type_ = 'TEXT'
                elif type_ == 'float':
                    type_ = 'REAL'
                kt[k] = type_
    header = ''
    for k, t in kt.items():
        header = header+"{} {}, ".format(k, t)
    return header[:-2]


def create_table(name, list_, db_file):
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    create_table = 'CREATE TABLE IF NOT EXISTS {} ( {} );'
    create_table.format(name, get_table_headers(list_))
    create_table = create_table.format(name, get_table_headers(list_))
    cur.execute(create_table)
    db.commit()
    cur.close()
    db.close()


def add_data(name, list_, db_file):
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    cur.execute("SELECT * FROM {} WHERE 1=0".format(name))
    columns = [c[0] for c in cur.description]
    line={}
    cols = "?,"*len(columns)
    cmd = "INSERT INTO {} VALUES ({})".format(name, cols[:-1])
    for i in range(len(list_)):
        line = list_[i]
        for k, v in line.items():
            type_ = type(v).__name__
            if type_ == 'bool':
                line[k] = str(v)
            elif type_ == 'list':
                line[k] = str(line[k])[1:-1].replace(" ", "")
            elif type_ == 'dict':
                line[k] = str(line[k]).replace("\'", "\"")
        for c in columns:
            if c not in line.keys():
                line[c] = ''
        params = []
        for c in columns:
            params.append(line[c])
        cur.execute(cmd, params)
    db.commit()
    cur.close()
    db.close()
