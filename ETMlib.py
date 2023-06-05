import gevent
from gevent.pool import Pool
from gevent import monkey as curious_george
curious_george.patch_all()
import traceback
from Authenticate import OAuth
import requests
from requests.adapters import HTTPAdapter
import sqlite3
import os, sys, time, csv
import datetime as dt
import json
import esi_paths as esi
#helper functions
class AsyncRequest(object):
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()
        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}
        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None
    def send(self, **kwargs):
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        try:
            self.response = self.session.request(self.method, self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
            self.traceback = traceback.format_exc()
        return self

def get_bulk_info(urls, size=None, headers=None):
    urlObjs = []
    if size == None:
        size = len(urls)
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=200))
        for u in range(len(urls)):
            if headers != None:
                obj = AsyncRequest('GET', urls[u], session=session, headers=headers, timeout=None)
            else:
                obj = AsyncRequest('GET', urls[u], session=session, timeout=None)
            urlObjs.append(obj)
    else:
        session = [requests.Session() for i in range(size)]
        for s in session:
            s.mount('https://', HTTPAdapter())
        for u in range(len(urls)):
            if headers != None:
                obj = AsyncRequest('GET', urls[u], session=session[u%size], headers=headers, timeout=None)
            else:
                obj = AsyncRequest('GET', urls[u], session=session[u%size], timeout=None)
            urlObjs.append(obj)
        
    pool = Pool(size)
    jobs = []
    for j in urlObjs:
        jobs.append(pool.spawn(j.send))
    gevent.joinall(jobs)
    resp = []
    for r in urlObjs:
        resp.append(r.response)
        r.session.close()
    return resp

#character info
def get_character_transactions():
    if not os.path.exists('logs/characters'):
        os.makedirs('logs/characters')
    auth = OAuth()
    auth_data = auth.get()
    for i in range(len(auth_data)):
        url = esi.wallet_transactions.format(auth_data[i][0])
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            if resp.json()['error'] == 'token is expired':
                auth.refresh()
                char_auth_data = auth.get()[i]
                headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                resp = requests.get(url, headers=headers)
        
        print(resp.status_code)
        old_trans_file = "logs/characters/"+str(auth_data[i][0])+"_transactions.json"
        
        if os.path.exists(old_trans_file):
            with open(old_trans_file, 'r') as f:
                old_trans = json.load(f)
        else:
            old_trans = []
            
        
        extra = []
        for n in resp.json():
            in_ = False
            for o in old_trans:
                if n['transaction_id'] == o['transaction_id']:
                    in_ = True
            if in_ == False:
                extra.append(n)
                
        with open('eve-cache/market_types.json', 'r') as f:
            market_types = json.load(f)
            
        type_ids = []
        for i in market_types:
            if i['published'] == True:
                type_ids.append((i['name'], i['type_id']))
            
        with open("eve-cache/stations.json", "r") as f:
            stations = json.load(f)
            
        with open("eve-cache/structures.json", "r") as f:
            structures = json.load(f)
        
        for i in extra:
            for j in type_ids:
                if i['type_id'] == j[1]:
                    i['type_name'] = j[0]
            for j in stations:
                if i['location_id'] == j['station_id']:
                    i['location_name'] = j['name']
            for j in structures:
                if i['location_id'] == j['id']:
                    i['location_name'] = j['name']
                
        with open(old_trans_file, 'w') as f:
            json.dump(extra+old_trans, f, indent=1)

def get_character_orders():
    if not os.path.exists('logs/characters'):
        os.makedirs('logs/characters')
    auth = OAuth()
    auth_data = auth.get()
    for i in range(len(auth_data)):
        url = esi.market_character_orders.format(auth_data[i][0])
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            if resp.json()['error'] == 'token is expired':
                auth.refresh()
                char_auth_data = auth.get()[i]
                headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                resp = requests.get(url, headers=headers)
        
        data = resp.json().copy()
        orders_file = "logs/characters/"+str(auth_data[i][0])+"_orders.json"
        
        with open('eve-cache/market_types.json', 'r') as f:
            market_types = json.load(f)
            
        type_ids = []
        for i in market_types:
            if i['published'] == True:
                type_ids.append((i['name'], i['type_id']))
            
        with open('eve-cache/stations.json', 'r') as f:
            stations = json.load(f)
        
        with open('eve-cache/structures.json', 'r') as f:
            structures = json.load(f)
            
        for i in data:
            for j in type_ids:
                if i['type_id'] == j[1]:
                    i['type_name'] = j[0]
            for j in stations:
                if i['location_id'] == j['station_id']:
                    i['location_name'] = j['name']
            for j in structures:
                if i['location_id'] == j['id']:
                    i['location_name'] = j['name']
                    
        with open(orders_file, 'w') as f:
            json.dump(data, f, indent=1)

def get_character_assets():
    if not os.path.exists('logs/characters'):
        os.makedirs('logs/characters')
        
    auth = OAuth()
    auth_data = auth.get()
    auth.refresh()
    for i in range(len(auth_data)):
        data=[]
        url = esi.assets.format(auth_data[i][0], 1)
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.head(url, headers=headers)
        pages = int(resp.headers['X-pages'])
        for j in range(1, pages+1):
            url = esi.assets.format(auth_data[i][0], j)
            headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
            resp = requests.get(url, headers=headers)
            if resp.status_code == 403:
                if resp.json()['error'] == 'token is expired':
                    auth.refresh()
                    char_auth_data = auth.get()[i]
                    headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                    resp = requests.get(url, headers=headers)
            data = data+resp.json()
        

        assets_file = "logs/characters/"+str(auth_data[i][0])+"_assets.json"
        
        item_tmp=[]
        for j in data:
            if j['item_id'] not in item_tmp:
                    item_tmp.append(j['item_id'])
        
        item_ids=[]
        for j in range(0, len(item_tmp), 1000):
            item_ids.append(item_tmp[j:j+1000])

        with open('eve-cache/market_types.json', 'r') as f:
            market_types = json.load(f)
            
        type_ids = []
        for j in market_types:
            if j['published'] == True:
                type_ids.append((j['name'], j['type_id']))
            
        with open("eve-cache/stations.json", "r") as f:
            stations = json.load(f)
            
        with open("eve-cache/structures.json", "r") as f:
            structures = json.load(f)
        
        item_data=[]
        for j in item_ids:
            item_data = item_data + get_asset_names(j, auth_data[i][0])
        item_ids = item_data
        
        for j in data:
            for k in type_ids:
                if j['type_id'] == k[1]:
                    j['type_name'] = k[0]
            for k in item_ids:
                if j['item_id'] == k['item_id']:
                    j['item_name'] = k['name']
            for k in stations:
                if j['location_id'] == k['station_id']:
                    j['location_name'] = k['name']
            for k in structures:
                if j['location_id'] == k['id']:
                    j['location_name'] = k['name']
                    
        for j in data:
            for k in data:
                if j['location_id'] == k['item_id']:
                    j['location_name'] = k['item_name']
        
        transactions_file = "logs/characters/"+str(auth_data[i][0])+"_transactions.json"
        with open(transactions_file) as f:
            trans = json.load(f)
            
        totals=[]
        for j in data:
            in_ = False
            for k in totals:
                if j['type_id'] == k['type_id']:
                    in_ = True
                    k['quantity'] = k['quantity']+j['quantity']
            if in_ == False:
                item={}
                item['type_id'] = j['type_id']
                item['quantity'] = j['quantity']
                totals.append(item)

        for j in totals:
            qtot = 0
            ptot = 0
            for k in trans:
                if j['type_id'] == k['type_id'] and k['is_buy'] == True:
                    for l in range(k['quantity']):
                        if qtot < j['quantity']:
                            qtot = qtot+1
                            ptot = ptot + k['unit_price']
                
            j['med_price'] = float("{:.2f}".format(ptot / j['quantity']))
        
        for j in data:
            for k in totals:
                if j['type_id'] == k['type_id']:
                    j['asset_price'] = k['med_price']
            
                    
        with open(assets_file, 'w') as f:
            json.dump(data, f, indent=1)

def get_character_skills():
    if not os.path.exists('logs/characters'):
        os.makedirs('logs/characters')
        
    auth = OAuth()
    auth_data = auth.get()
    for i in range(len(auth_data)):
        url = esi.skills.format(auth_data[i][0])
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            if resp.json()['error'] == 'token is expired':
                auth.refresh()
                char_auth_data = auth.get()[i]
                headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                resp = requests.get(url, headers=headers)
        data = resp.json()
        ids=[]
        for j in data['skills']:
            if j['skill_id'] not in ids:
                ids.append(j['skill_id'])
                
        ids = requests.post(esi.uni_names, data=str(ids))
        for j in data['skills']:
            for k in ids.json():
                if j['skill_id'] == k['id']:
                    j['skill_name'] = k['name']
        
        with open('logs/characters/'+str(auth_data[i][0])+'_skills.json', 'w') as f:
            json.dump(data, f, indent=1)

def get_character_balance():
    if not os.path.exists('logs/characters'):
        os.makedirs('logs/characters')
    auth = OAuth()
    auth_data = auth.get()
    date = time.strftime("%a %d %b %Y", time.gmtime())
    balances = []
    for i in range(len(auth_data)):
        url = esi.wallet_balance.format(auth_data[i][0])
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            if resp.json()['error'] == 'token is expired':
                auth.refresh()
                char_auth_data = auth.get()[i]
                headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                resp = requests.get(url, headers=headers)
        with open('logs/characters/'+str(auth_data[i][0])+'_balance', 'a') as f:
            f.write(date+','+str(resp.json())+"\n")
        balances.append([auth_data[i][1], resp.json()])
    
def ledger(character_id, date='2003-03-06'):
    with open("logs/characters/"+str(character_id)+"_transactions.json") as f:
        trans = json.load(f)
    
    sd = date.split('-')
    date = dt.datetime(int(sd[0]), int(sd[1]), int(sd[2]))
    ledger=[]
    for i in trans:
        td = i['date'].split('T')[0].split('-')
        td = dt.datetime(int(td[0]), int(td[1]), int(td[2]))
        if td >= date:
            in_ = False
            for j in ledger:
                if i['type_name'] == j[0]:
                    in_ = True
                    if i['is_buy'] == True:
                        j[1] = j[1] + i['quantity']
                        j[2] = j[2] + (i['unit_price']*i['quantity'])
                    else:
                        j[3] = j[3] + i['quantity']
                        j[4] = j[4] + (i['unit_price']*i['quantity'])
                    j[5] = j[4] - j[2]
            if in_ == False:
                if i['is_buy'] == True:
                    brought_value = i['unit_price']*i['quantity']
                    brought_quantity = i['quantity']
                    sold_value = 0
                    sold_quantity = 0
                else:
                    brought_value = 0
                    brought_quantity = 0
                    sold_value = i['unit_price']*i['quantity']
                    sold_quantity = i['quantity']
        
                profit = sold_value - brought_value
                item = [i['type_name'],
                        brought_quantity,
                        brought_value,
                        sold_quantity,
                        sold_value,
                        profit]
                ledger.append(item)

    print("{:<50}{:<10}{:<25}{:<10}{:<25}".format("item", "brought", "value", "Sold", "Value"))
    for i in sorted(ledger, key=lambda i: i[-1], reverse=True):
        print("{:.<50}{:.<10,}{:.<25,.2f}{:.<10,}{:.<25,.2f}{:,.2f}".format(i[0], i[1], i[2], i[3], i[4], i[5]))

def get_asset_names(ids, character_id):
    auth = OAuth()
    auth_data = []
    for i in auth.get():
        if i[0] == character_id:
            auth_data = i
    
    headers = {"Authorization": "Bearer {}".format(auth_data[2])}
    response = requests.post(esi.asset_names.format(character_id), data=str(ids), headers=headers)
    if response.status_code == 401 or response.status_code == 403:
        print("Refreshing...")
        auth.refresh()
        for i in auth.get():
            if i[0] == character_id:
                auth_data = i
        headers = {"Authorization": "Bearer {}".format(auth_data[2])}
        response = requests.post(esi.asset_names, data=str(ids), headers=headers)
    return response.json()

def getSkill(file_, skill, full=True):
    with open(file_, 'r') as f:
        data = json.load(f)
    for i in data['skills']:
        if i['skill_name'] == skill:
            if full == True:
                return i['trained_skill_level']
            else:
                return i['active_skill_level']

#esi data
def get_type_info(size=None):
    resp = requests.head(esi.uni_types.format(1))
    pages = int(resp.headers['X-pages'])
    print(pages)
    types=[]
    for i in range(1, pages+1):
        print('page:', i, end="\r")
        type_ids = requests.get(esi.uni_types.format(i))
        
        urls=[]
        for j in type_ids.json():
            urls.append(esi.uni_type_info.format(j))
            
        data = get_bulk_info(urls, size=size)
        
        failed = []
        ndx=0
        while ndx != len(data):
            if data[ndx].status_code != 200:
                failed.append(data[ndx])
                del data[ndx]
            else:
                ndx += 1
        
        while len(failed) > 0:
            failed = []
            retry = get_bulk_info(failed, size=size)
            for j in retry:
                if j.status_code != 200:
                    failed.append(j)
                else:
                    data.append(j)
        
        for i in data:
            types.append(i.json())
    
    print()
    market_types=[]
    for i in types:
        if 'market_group_id' in i.keys():
            market_types.append(i)
            
    with open('eve-cache/market_types.json', 'w') as f:
        json.dump(market_types, f, indent=1)
        
    with open('eve-cache/types.json', 'w') as f:
        json.dump(types, f, indent=1)

def get_structure_info(size=None):
    auth = OAuth()
    auth.refresh()
    char_data = auth.get()
    
    resp = requests.get(esi.uni_structure_ids)
        
    urls=[]
    for i in resp.json():
        urls.append(esi.uni_structure_info.format(i))
    
    data = []
    for char in char_data:
        headers = {"Authorization": "Bearer {}".format(char[2])}
        resp = get_bulk_info(urls, size=size, headers=headers)
        data = data+resp
        
    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
                
    structs = []
    for i in data:
        id_ = int(i.url.split('/')[-2])
        d = i.json()
        d['id'] = id_
        if len(structs) == 0:
            structs.append(d)
        if d not in structs:
            structs.append(d)
            
    with open('eve-cache/structures.json', 'w') as f:
        json.dump(structs, f, indent=1)

def get_group_info(size=None):
    resp = requests.get(esi.market_groups)
    urls=[]
    for i in resp.json():
        urls.append(esi.market_group_info.format(i))
        
    data = get_bulk_info(urls, size=size)
    
    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
                
    market_groups=[]
    for i in data:
        market_groups.append(i.json())
        
    with open('eve-cache/market_groups.json', 'w') as f:
        json.dump(market_groups, f, indent=1)

def get_region_info(size=None):
    resp = requests.get(esi.uni_regions)
    urls=[]
    for i in resp.json():
        urls.append(esi.uni_region_info.format(i))
    
    data = get_bulk_info(urls, size=size)

    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
                
    regions=[]
    for i in data:
        regions.append(i.json())
    
    with open('eve-cache/regions.json', 'w') as f:
        json.dump(regions, f, indent=1)

def get_system_station_info(size=None):
    resp = requests.get(esi.uni_systems)
    system_ids = resp.json()
    
    urls=[]
    for i in system_ids:
        urls.append(esi.uni_system_info.format(i))
        
    data = get_bulk_info(urls, size=size)
    
    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
    
    system_info=[]
    urls=[]
    for i in data:
        system_info.append(i.json())
        if 'stations' in list(i.json().keys()):
            for j in i.json()['stations']:
                urls.append(esi.uni_station_info.format(j))
    
    with open('eve-cache/systems.json', 'w') as f:
        json.dump(system_info, f, indent=1)
        
    data = get_bulk_info(urls, size=size)
    
    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
    
    station_info=[]
    for i in data:
        station_info.append(i.json())
    
    with open('eve-cache/stations.json', 'w') as f:
        json.dump(station_info, f, indent=1)

#market data
def list_active_orders():
    activeOrders=[]
    with open('eve-cache/regions.json', 'r') as f:
        regions = json.load(f)
    
    region_ids=[]
    for i in regions:
        if 'description' in list(i.keys()):
            region_ids.append((i['region_id'], i['name']))
    
    for region in region_ids:
        resp = requests.head(esi.market_types.format(region[0], 1))
        pages = int(resp.headers['X-pages'])
        urls=[]
        for i in range(1, pages+1):
            urls.append(esi.market_types.format(region[0], i))
        data = get_bulk_info(urls, size=100)
        types=[]
        for i in data:
            types = types+i.json()
        
        elem = {}
        elem['name'] = region[1]
        elem['id'] = region[0]
        elem['orders'] = len(types)
        activeOrders.append(elem)
        
    for i in sorted(activeOrders, key=lambda j: j['orders'], reverse=True):
        if i['orders'] > 0:
            print("{:<10}{:<25}{}".format(i['id'], i['name'], i['orders']))

def market_orders(region, type_):
    if not os.path.exists('logs/market/'+str(region)):
        os.makedirs('logs/market/'+str(region))
        
    data = requests.get(esi.market_orders.format(region, 'all', 1, type_))
    data = data.json()
    with open("eve-cache/market_types.json", "r") as f:
        market_types = json.load(f)
        
    for i in market_types:
        if i['type_id'] == type_:
            name = i['name']
            name = name.replace("/", "_")
            name = name.replace(",", ";")
            
    if len(data) != 0:
        with open('logs/market/'+str(region)+'/'+str(type_)+'_'+name+'.csv', 'w') as f:
            f.write(','.join(list(data[0].keys()))+"\n")
            for i in data:
                ln=[]
                for j in list(i.values()):
                    ln.append(str(j))
                f.write(','.join(list(ln))+"\n")

def display(region, type_):
    for i in os.listdir("logs/market/"+str(region)):
        if str(type_) == i.split("_")[0]:
            f_name = i
            break
        
    name = "logs/market/"+str(region)+"/"+f_name
    print(name)
    data=[]
    with open(name, 'r') as f:
        for ln in f.readlines():
            data.append(ln.strip("\n").split(','))
            
    with open('eve-cache/stations.json', 'r') as f:
        stations = json.load(f)
        
    with open('eve-cache/structures.json', 'r') as f:
        structures = json.load(f)
        
    with open('eve-cache/systems.json', 'r') as f:
        systems = json.load(f)
    
    with open('eve-cache/regions.json', 'r') as f:
        regions = json.load(f)
        
    for i in regions:
        if i['region_id'] == region:
            region_name = i['name']
            
    header = data.pop(0)
    header = header+['station_name', 'system_name']
        
    buy = []
    sell = []
    w1 = len(header[6])
    w2 = len(header[12])
    w3 = len(header[13])
    for i in data:
        i.append('Unknown Structure/Station')
        if i[1] == 'True':
            for j in structures:
                if int(i[3]) == j['id']:
                    i[12] = j['name']
            for j in stations:
                if int(i[3]) == j['station_id']:
                    i[12] = j['name']
            for j in systems:
                if int(i[8]) == j['system_id']:
                    i.append(j['name'])
            buy.append(i)
        else:
            for j in structures:
                if int(i[3]) == j['id']:
                    i[12] = j['name']
            for j in stations:
                if int(i[3]) == j['station_id']:
                    i[12] = j['name']
            for j in systems:
                if int(i[8]) == j['system_id']:
                    i.append(j['name'])
            sell.append(i)
        print(i)
        if len(i[6]) > w1:
            w1 = len("{:,.2f}".format(float(i[6])))
        if len(i[12]) > w2:
            w2 = len(i[12])
        if len(i[13]) > w3:
            w3 = len(i[13])
    
    sell = sorted(sell, key=lambda i: float(i[6]), reverse=True)
    buy = sorted(buy, key=lambda i: float(i[6]), reverse=True)
    system=''
    while system != 'q':
        best_sell = 1E16
        best_buy = 0
                
        print(region_name, f_name)
        print("{:^{w1}}  {:<{w2}} {:<{w3}} {}".format(header[6], header[12], header[13], header[7], w1=w1, w2=w2, w3=w3))
        for i in sell:
            if system == '':
                print("{:<{w1},.2f}   {:<{w2}} {:<{w3}} {}".format(float(i[6]), i[12], i[13], i[7], w1=w1, w2=w2, w3=w3))
                if float(i[6]) < best_sell:
                    best_sell = float(i[6])
            elif system == i[13]:
                print("{:<{w1},.2f}   {:<{w2}} {:<{w3}} {}".format(float(i[6]), i[12], i[13], i[7], w1=w1, w2=w2, w3=w3))
                if float(i[6]) < best_sell:
                    best_sell = float(i[6])

        print("-"*(w1+w2+w3+6))
                
        for i in buy:
            if system == '':
                print("{:<{w1},.2f}   {:<{w2}} {:<{w3}} {}".format(float(i[6]), i[12], i[13], i[7], w1=w1, w2=w2, w3=w3))
                if float(i[6]) > best_buy:
                    best_buy = float(i[6])
            elif system == i[13]:
                print("{:<{w1},.2f}   {:<{w2}} {:<{w3}} {}".format(float(i[6]), i[12], i[13], i[7], w1=w1, w2=w2, w3=w3))
                if float(i[6]) > best_buy:
                    best_buy = float(i[6])
                    
        print("Best sell:{:,}, Best buy:{:,}, Margin:{:,}".format(float(best_sell), float(best_buy), (float(best_sell)-float(best_buy))))
        system = input()

def get_bulk_history(region, size=None):
    if not os.path.exists('logs/history/'+str(region)):
        os.makedirs('logs/history/'+str(region))
        
    with open('eve-cache/market_types.json', 'r') as f:
        market_types = json.load(f)
        
    type_ids = []
    for i in market_types:
        if i['published'] == True:
            type_ids.append((i['name'], i['type_id']))
            
    urls = []
    for i in type_ids:
        urls.append(esi.market_history.format(region, i[1]))
    
    print("Downloading...", end="")
    data = get_bulk_info(urls, size=size)
    
    failed = []
    ndx=0
    while ndx != len(data):
        try:
            if data[ndx].status_code != 200:
                failed.append(data[ndx])
                del data[ndx]
            else:
                ndx += 1
        except AttributeError:
            print(data[ndx].exception)
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
    print("Done")
    name=""   
    days=400.0
    summary_data=[]
    cnt=0
    for r in data:
        if len(r.json()) != 0:
            print(cnt, end="\r")
            cnt+=1
            id_ = r.url.split('=')[-1]
            for i in type_ids:
                if i[1] == int(id_):
                    name = i[0]
                    name = name.replace("/", "_")
                    name = name.replace(",", ";")
                
            tot_average=0.0
            tot_highest=0.0
            tot_lowest=0.0
            tot_order_count=0.0
            tot_volume=0.0
            for i in r.json():
                tot_average = tot_average+i['average']
                tot_highest = tot_highest+i['highest']
                tot_lowest = tot_lowest+i['lowest']
                tot_order_count = tot_order_count+i['order_count']
                tot_volume = tot_volume+i['volume']
            med_average = tot_average/days if tot_average != 0 else 0
            med_highest = tot_highest/days if tot_highest != 0 else 0
            med_lowest = tot_lowest/days if tot_lowest != 0 else 0
            med_order_count = tot_order_count/days if tot_order_count != 0 else 0
            med_volume = tot_volume/days if tot_volume != 0 else 0
            med_data_e={'id':id_, 
                        'name': name,
                        'med_average':str(med_average),
                        'med_highest':str(med_highest),
                        'med_lowest':str(med_lowest),
                        'med_order_count':str(med_order_count),
                        'med_volume':str(med_volume)}
            summary_data.append(med_data_e)
            
            pth = 'logs/history/'+str(region)+'/'+id_+"_"+name+".csv"
            if os.path.exists(pth):
                hist = []
                with open(pth, 'r') as f:
                    for l in f:
                        hist.append(l.replace("\n", "").split(","))
                
                extra=[]
                for j in r.json():
                    in_ = False
                    for k in hist:
                        if j['date'] == k[1]:
                            in_ == True
                            break
                    if in_ == False:
                        l=[]
                        for k in j.values():
                            l.append(str(k))
                        extra.append(l)
                hist = hist+extra
                with open(pth, 'w') as f:
                    for j in hist:
                        f.write(','.join(i)+"\n")
            else:
                with open(pth, 'w') as f:
                    f.write(','.join(list(r.json()[0].keys()))+"\n")
                    for j in r.json():
                        ln = []
                        for k in list(j.values()):
                            ln.append(str(k))
                        f.write(','.join(ln)+"\n")
                
    with open('logs/history/'+str(region)+".csv", 'w') as f:
        f.write(','.join(list(summary_data[0].keys()))+"\n")
        for j in summary_data:
            f.write(','.join(list(j.values()))+"\n")

def get_bulk_market(region, size=None):
    strt = time.perf_counter()
    if not os.path.exists('logs/market/'+str(region)):
        os.makedirs('logs/market/'+str(region))

    resp = requests.head(esi.market_types.format(region, 1))
    pages = int(resp.headers['X-pages'])
    urls=[]
    for i in range(1, pages+1):
        urls.append(esi.market_types.format(region, i))
        
    dl1strt = time.perf_counter()
    data = get_bulk_info(urls, size=100)
    dl1end = time.perf_counter()
    dl1T = dl1end-dl1strt
    print('dl1T:', dl1T)
    
    type_ids = []
    for i in data:
        type_ids = type_ids+i.json()
        
    with open("eve-cache/market_types.json", "r") as f:
        market_types = json.load(f)
    
    unpub=[]
    type_names=[]
    for i in market_types:
        if i['published'] == False:
            unpub.append(i['type_id']) 
        else:
            type_names.append((i['type_id'], i['name']))
    
    ndx=0
    while ndx != len(type_ids):
        if type_ids[ndx] in unpub:
            del type_ids[ndx]
        else:
            ndx += 1
    
    urls=[]
    for i in type_ids:
        urls.append(esi.market_orders.format(region, 'all', 1, i))
        
    dl2strt = time.perf_counter()
    data = get_bulk_info(urls, size=size)
    dl2end = time.perf_counter()
    dl2T = dl2end - dl2strt
    print('dl2T:', dl2T)
    
    failed = []
    ndx=0
    while ndx != len(data):
        if data[ndx].status_code != 200:
            failed.append(data[ndx])
            del data[ndx]
        else:
            ndx += 1
    
    while len(failed) > 0:
        failed = []
        retry = get_bulk_info(failed, size=size)
        for j in retry:
            if j.status_code != 200:
                failed.append(j)
            else:
                data.append(j)
        

    for r in data:
        type_ = r.url.split('=')[-1]
        for i in type_names:
            if i[0] == int(type_):
                name = i[1]
                name = name.replace("/", "_")
                name = name.replace(",", ";")
                
        if len(r.json()) != 0:
            with open('logs/market/'+str(region)+'/'+type_+'_'+name+'.csv', 'w') as f:
                f.write(','.join(list(r.json()[0].keys()))+"\n")
                for i in r.json():
                    ln=[]
                    for j in list(i.values()):
                        ln.append(str(j))
                    f.write(','.join(list(ln))+"\n")
    stp = time.perf_counter()
    
    T = stp-strt
    print('total Dl time:', dl1T+dl2T, 'total p time:', T - (dl1T+dl2T), "total", T)

def get_margins(character, region, station=None):
    strt = time.perf_counter()
    log_file = "logs/characters/"+str(character)+"_skills.json"
    Accounting = getSkill(log_file, "Accounting", full=True)
    Brokers_fee = getSkill(log_file, "Broker Relations", full=True)
    
    csvs = os.listdir('logs/market/'+str(region))
    volumes = []
    with open('logs/history/'+str(region)+'.csv', 'r') as f:
        for ln in f.readlines():
            volumes.append(ln.strip("\n").split(","))
            
    with open("eve-cache/stations.json", "r") as f:
        stations = json.load(f)
        
    with open("eve-cache/structures.json", "r") as f:
        structures = json.load(f)
    
    stations = stations+structures
    if station != None:
        station_ids=[]
        for i in stations:
            for j in station.split(','):
                if j in i['name']:
                    if 'station_id' in i.keys():
                        station_ids.append(i['station_id'])
                    else:
                        station_ids.append(i['id'])
            
    all_margins=[]
    cnt=0
    for csv in csvs:
        id_name = csv.replace(".csv", "").split("_", 1)
        id_ = id_name[0]
        name = id_name[1]
        med_order_count = 0
        med_volume = 0
        for v in range(1, len(volumes)):
            if volumes[v][0] == id_:
                med_order_count = float(volumes[v][5])
                med_volume = float(volumes[v][6])
        
        print(cnt, end='\r')
        cnt+=1
        best_sell = 1E16
        best_buy = 0
        if station != None:
            with open('logs/market/'+str(region)+'/'+csv) as f:
                f.readline()
                for ln in f.readlines():
                    ln = ln.strip("\n").split(',')
                    if int(ln[3]) in station_ids:
                        price = float(ln[6])
                        if ln[1] == 'True' and price > best_buy:
                            best_buy = price
                        elif ln[1] == 'False' and price < best_sell:
                            best_sell = price
        else:
            with open('logs/market/'+str(region)+'/'+csv) as f:
                f.readline()
                for ln in f.readlines():
                    ln = ln.strip("\n").split(',')
                    price = float(ln[6])
                    if ln[1] == 'True' and price > best_buy:
                        best_buy = price
                    elif ln[1] == 'False' and price < best_sell:
                        best_sell = price
        
        
        base_sell_relist = relist(best_sell, best_sell, Brokers_fee, Accounting, 0, 0)
        best_sell_tax = sales_tax(best_sell, Accounting)
        best_sell_tax = best_sell_tax + brokers_fee(best_sell, Brokers_fee, 0, 0)

        base_buy_relist = relist(best_buy, best_buy, Brokers_fee, Accounting, 0, 0)
        best_buy_tax = brokers_fee(best_buy, Brokers_fee, 0, 0)

        margin = float(best_sell)-float(best_buy)
        markup = 'inf'
        if best_buy != 0:
            markup = ((float(best_sell)-float(best_buy))/float(best_buy))*100

        margin_ = [id_,
                name,
                best_buy,
                best_buy_tax,
                base_buy_relist,
                best_sell,
                best_sell_tax,
                base_sell_relist,
                margin,
                markup,
                med_order_count,
                med_volume]
        
        all_margins.append(margin_)
    print()
    header = [['id_',
               'name',
               'best_buy',
               'best_buy_tax',
               'base_buy_relist',
               'best_sell',
               'best_sell_tax',
               'base_sell_relist',
               'margin',
               'markup',
               'med_order_count',
               'med_volume']]
    all_margins = header+all_margins
    with open('logs/market/'+str(region)+'_margins.csv', 'w') as f:
        for line in all_margins:
            l=[]
            for i in line:
                l.append(str(i))
            f.write(','.join(l)+"\n")
    stp = time.perf_counter()
    print("total", stp-strt)

def get_trade_routes(regiona, regionb):
    strt = time.perf_counter()
    regionacsv = os.listdir('logs/market/'+str(regiona))
    regionbcsv = os.listdir('logs/market/'+str(regionb))
    with open('eve-cache/market_types.json', 'r') as f:
        market_types = json.load(f)
    
    volumes = []
    for i in market_types:
        volumes.append((i['name'], i['packaged_volume']))
        
    with open('eve-cache/regions.json', 'r') as f:
        regions = json.load(f)
    
    for r in regions:
        if r['region_id'] == regiona:
            regiona_name = r['name']
        if r['region_id'] == regionb:
            regionb_name = r['name']
    
    header = ['name',
                'buy_from',
                'sell_to',
                'buy_quantity',
                'buy_volume',
                'buy_range_high',
                'buy_range_low',
                'purchase_cost',
                'sell_quantity',
                'sell_volume',
                'sell_range_high',
                'sell_range_low',
                'sell_value',
                'profit']
    routes = [header]
    cnt = 0
    for regA in regionacsv:
        for regB in regionbcsv:
            if regA == regB:
                cnt += 1
                print(cnt, end="\r")
                id_name = regA.replace('.csv', '').split('_')
                unit_volume = 0
                for i in volumes:
                    if i[0] == id_name[1]:
                        unit_volume = float(i[1])
                
                Asell =[]
                Abuy = []
                Absell = 1E16
                Abbuy = 0
                with open('logs/market/'+str(regiona)+'/'+regA, 'r') as f:
                    f.readline()
                    for ln in f.readlines():
                        order = ln.strip("\n").split(',')
                        if len(order) > 0:
                            if order[1] == "True":
                                Abuy.append(order)
                                if float(order[6]) > Abbuy:
                                    Abbuy = float(order[6])
                            else:
                                Asell.append(order)
                                if float(order[6]) < Absell:
                                    Absell = float(order[6])
                
                Bsell = []
                Bbuy = []
                Bbsell = 1E16
                Bbbuy = 0
                with open('logs/market/'+str(regionb)+'/'+regB, 'r') as f:
                    f.readline()
                    for ln in f.readlines():
                        order = ln.strip("\n").split(',')
                        if len(order) > 0:
                            if order[1] == "True":
                                Bbuy.append(order)
                                if float(order[6]) > Bbbuy:
                                    Bbbuy = float(order[6])
                            else:
                                Bsell.append(order)
                                if float(order[6]) < Bbsell:
                                    Bbsell = float(order[6])
                
                overlap = False
                
                buy_quantity = 0
                buy_volume = 0
                buy_range_high = 0
                buy_range_low = 1E16
                purchase_cost = 0
                
                sell_quantity = 0
                sell_volume = 0
                sell_range_high = 0
                sell_range_low = 1E16
                sell_value = 0
                profit = 0
                
                if Absell < Bbbuy:
                    overlap = True
                    buy_from = regiona_name
                    sell_to = regionb_name
                    for i in Asell:
                        if float(i[6]) < Bbbuy:
                            buy_quantity = buy_quantity + int(i[10])
                            purchase_cost = purchase_cost + (float(i[6]) * float(i[10]))
                            if float(i[6]) > buy_range_high:
                                buy_range_high = float(i[6])
                            if float(i[6]) < buy_range_low:
                                buy_range_low = float(i[6])
                    
                    buy_volume = buy_quantity * unit_volume    
                    for i in Bbuy:
                        if float(i[6]) > Absell:
                            sell_quantity = sell_quantity + int(i[10])
                            sell_value = sell_value + (float(i[6]) * float(i[10]))
                            if float(i[6]) > sell_range_high:
                                sell_range_high = float(i[6])
                            if float(i[6]) < sell_range_low:
                                sell_range_low = float(i[6])
                            
                    sell_volume = sell_quantity * unit_volume
                    profit = sell_value - purchase_cost
                elif Bbsell < Abbuy:
                    overlap = True
                    buy_from = regionb_name
                    sell_to = regiona_name
                    for i in Bsell:
                        if float(i[6]) < Abbuy:
                            buy_quantity = buy_quantity + int(i[10])
                            purchase_cost = purchase_cost + (float(i[6]) * float(i[10]))
                            if float(i[6]) > buy_range_high:
                                buy_range_high = float(i[6])
                            if float(i[6]) < buy_range_low:
                                buy_range_low = float(i[6])
                    
                    buy_volume = buy_quantity * unit_volume 
                    for i in Abuy:
                        if float(i[6]) > Bbsell:
                            sell_quantity = sell_quantity + int(i[10])
                            sell_value = sell_value + (float(i[6]) * float(i[10]))
                            if float(i[6]) > sell_range_high:
                                sell_range_high = float(i[6])
                            if float(i[6]) < sell_range_low:
                                sell_range_low = float(i[6])
                            
                    sell_volume = sell_quantity * unit_volume
                    profit = sell_value - purchase_cost
                
                if overlap == True:
                    route = [id_name[1],
                            buy_from,
                            sell_to,
                            buy_quantity,
                            buy_volume,
                            buy_range_high,
                            buy_range_low,
                            purchase_cost,
                            sell_quantity,
                            sell_volume,
                            sell_range_high,
                            sell_range_low,
                            sell_value,
                            profit]
                    routes.append(route)
    stp = time.perf_counter()
    print("total", stp-strt)
    
    with open('logs/market/'+str(regiona)+'_'+str(regionb)+'.csv', 'w') as f:
        for ln in routes:
            l = []
            for i in ln:
                l.append(str(i))
            f.write(','.join(l)+"\n")
        
#tax functions
def sales_tax(price, accounting):
    base_sTax=8
    reduction_rate=0.88
    current_sTax= base_sTax - (reduction_rate*accounting)
    return (float(price)/100)*current_sTax

def brokers_fee(price, bRelations, faction_stand, corp_stand):
    base_fee=3
    reduction_rate=0.3
    current_fee = base_fee - (reduction_rate*bRelations) - (0.03*faction_stand) - (0.02*corp_stand)
    return (float(price)/100)*current_fee
    
def relist(start_price, mod_price, bRelations, ABRelations, faction_stand, corp_stand):
    base_discount = 50
    increase_rate = 6
    current_discount=(base_discount+(increase_rate*ABRelations))/100
    br = lambda p : brokers_fee(p, bRelations, faction_stand, corp_stand)
    return max(0, br(mod_price-start_price))+(1-current_discount)*br(mod_price)

#tmp functions
def summary(character_id):
    print("Updating Transactions")
    get_character_transactions()
    print("Updating Orders")
    get_character_orders()
    print("Updating Assets")
    get_character_assets()
    print("Updating Balance")
    get_character_balance()
    
    root = 'logs/characters/'
    with open(root+str(character_id)+'_assets.json', 'r') as f:
        assets = json.load(f)
    with open(root+str(character_id)+'_orders.json', 'r') as f:
        orders = json.load(f)
    balances = []
    with open(root+str(character_id)+'_balance', 'r') as f:
        for ln in f.readlines():
            balances.append(float(ln.strip("\n").split(',')[1]))
        
    totBuyOrders = 0
    buyOrders = 0
    totSellOrders = 0
    sellOrders = 0
    for i in orders:
        if 'is_buy_order' in i.keys():
            if i['is_buy_order'] == True:
                buyOrders += 1
                totBuyOrders = totBuyOrders + (i['price']*i['volume_remain'])
        else:
            sellOrders += 1
            totSellOrders = totSellOrders + (i['price']*i['volume_remain'])
    
    totAssets = 0
    Assets = 0
    for i in assets:
        Assets += 1
        totAssets = totAssets + (i['asset_price']*i['quantity'])
        
    print("Buy Orders: {}, Value: {:,.2f}".format(buyOrders, totBuyOrders))
    print("Sell Orders: {}, Value: {:,.2f}".format(sellOrders, totSellOrders))
    print("Assets: {}, Value: {:,.2f}".format(Assets, totAssets))
    print("Wallet Balance: {:,.2f}".format(balances[-1]))
    print("Balance change: {:,.2f}".format(balances[-1] - balances[-2]))
    print("Total: {:,.2f}".format(totBuyOrders+totSellOrders+totAssets+balances[-1]))
    

if __name__ == '__main__':
    summary(96500260)
