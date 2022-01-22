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

def cache(data, file_, as_csv=True, mode='w'):
    dir_ = file_.rsplit('/', 1)[0]
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    if as_csv == True:
        try:
            h = list(data[0].keys())
        except:
            print("data", data)
        csv = []
        for i in data:
            line=[]
            for k in h:
                line.append(str(i[k]))
            csv.append(",".join(line))
        with open(file_, mode) as f:
            f.write(','.join(h)+"\n")
            for i in csv:
                f.write(i+"\n")
    else:
        with open(file_, mode) as f:
            json.dump(data, f, indent=1)

def load_cache(file_, as_list=True):
    if as_list == True:
        data = []
        with open(file_, 'r') as f:
            tdata = f.readlines()
        for i in tdata:
            l = i.replace("\n", "").split(",")
            data.append(l)
    else:
        try:
            with open(file_, 'r') as f:
                data = json.load(f)
        except:
            data=[]
            with open(file_, 'r') as f:
                header = f.readline().replace("\n", "").split(",")
                for l in f.readlines():
                    d = l.replace("\n", "").split(",")
                    dict_={}
                    for h in range(len(header)):
                        dict_[header[h]] = d[h]
                    data.append(dict_)
    return data

#character info
def get_character_transactions():
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
                
        type_ids=[]
        location_ids=[]
        structure_ids=[]
        for i in extra:
            if i['type_id'] not in type_ids:
                type_ids.append(i['type_id'])
            if i["location_id"] <= 0xffffffff:
                if i['location_id'] not in location_ids:
                    location_ids.append(i['location_id'])
            else:
                if i['location_id'] not in structure_ids:
                    structure_ids.append(i['location_id'])
        
        type_ids = get_id_names(type_ids)
        location_ids = get_id_names(location_ids)
        structure_ids = get_pos_info(structure_ids)
        
        location_ids = location_ids+structure_ids
        
        for i in extra:
            for j in type_ids:
                if i['type_id'] == j['id']:
                    i['type_name'] = j['name']
            for j in location_ids:
                if i['location_id'] == j['id']:
                    i['location_name'] = j['name']
                
        print("Saving {}".format(old_trans_file))
        with open(old_trans_file, 'w') as f:
            json.dump(extra+old_trans, f, indent=1)
        
def get_balance():
    auth = OAuth()
    auth_data = auth.get()
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
        
        balances.append([auth_data[i][1], resp.json()])
    return balances
    
def get_character_orders():
    auth = OAuth()
    auth_data = auth.get()
    temp=[]
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
        
                
        type_ids=[]
        location_ids=[]
        structure_ids=[]
        for i in data:
            if i['type_id'] not in type_ids:
                type_ids.append(i['type_id'])
            if i["location_id"] <= 0xffffffff:
                if i['location_id'] not in location_ids:
                    location_ids.append(i['location_id'])
            else:
                if i['location_id'] not in structure_ids:
                    structure_ids.append(i['location_id'])
        
        type_ids = get_id_names(type_ids)
        location_ids = get_id_names(location_ids)
        structure_ids = get_pos_info(structure_ids)
        
        location_ids = location_ids+structure_ids
        for i in data:
            for j in type_ids:
                if i['type_id'] == j['id']:
                    i['type_name'] = j['name']
            for j in location_ids:
                if i['location_id'] == j['id']:
                    i['location_name'] = j['name']
                    
        with open(orders_file, 'w') as f:
            json.dump(data, f, indent=1)
        
def get_character_assets():
    auth = OAuth()
    auth_data = auth.get()
    dall=[]
    for i in range(len(auth_data)):
        url = esi.assets.format(auth_data[i][0])
        headers = {"Authorization": "Bearer {}".format(auth_data[i][2])}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            if resp.json()['error'] == 'token is expired':
                auth.refresh()
                char_auth_data = auth.get()[i]
                headers = {"Authorization": "Bearer {}".format(char_auth_data[2])}
                resp = requests.get(url, headers=headers)
        
        data = resp.json().copy()
        assets_file = "logs/characters/"+str(auth_data[i][0])+"_assets.json"
        
        type_ids=[]
        item_ids=[]
        station_ids=[]
        structure_ids=[]
        location_ids=[]
        for j in data:
            if j['type_id'] not in type_ids:
                type_ids.append(j['type_id'])
            if j['location_type'] == 'station':
                if j["location_id"] <= 0xffffffff:
                    if j['location_id'] not in location_ids:
                        station_ids.append(j['location_id'])
                else:
                    if j['location_id'] not in structure_ids:
                        structure_ids.append(j['location_id'])
            else:
                if j['location_id'] not in location_ids:
                    location_ids.append(j['location_id'])
            if j['item_id'] not in item_ids:
                    item_ids.append(j['item_id'])
                    
        type_ids = get_id_names(type_ids) if len(type_ids) != 0 else []
        item_ids = get_asset_names(item_ids, auth_data[i][0]) if len(item_ids) != 0 else []
        station_ids = get_id_names(station_ids) if len(station_ids) != 0 else []
        structure_ids = get_pos_info(structure_ids) if len(structure_ids) != 0 else []
        #location_ids = get_asset_locations(location_ids, auth_data[i][0]) if len(location_ids) != 0 else []
        
        location_ids = structure_ids+station_ids
        for j in data:
            for k in type_ids:
                if j['type_id'] == k['id']:
                    j['type_name'] = k['name']
            for k in item_ids:
                if j['item_id'] == k['item_id']:
                    j['item_name'] = k['name']
            for k in location_ids:
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
            #j['med_price'] = ptot / j['quantity']
        
        for j in data:
            for k in totals:
                if j['type_id'] == k['type_id']:
                    j['asset_price'] = k['med_price']
            
                    
        with open(assets_file, 'w') as f:
            json.dump(data, f, indent=1)
        
def get_asset_locations(ids, character_id):
    auth = OAuth()
    auth_data = []
    for i in auth.get():
        if i[0] == character_id:
            auth_data = i
    
    headers = {"Authorization": "Bearer {}".format(auth_data[2])}
    response = requests.post(esi.asset_locations.format(character_id), data=str(ids), headers=headers)
    if response.status_code == 401 or response.status_code == 403:
        print("Refreshing...")
        auth.refresh()
        for i in auth.get():
            if i[0] == character_id:
                auth_data = i
        headers = {"Authorization": "Bearer {}".format(auth_data[2])}
        response = requests.post(esi.asset_locations.format(character_id), data=str(ids), headers=headers)
    return response.json()

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

def ledger(character_id):
    with open("logs/characters/"+str(character_id)+"_transactions.json") as f:
        trans = json.load(f)

    ledger=[]
    for i in trans:
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

    for i in sorted(ledger, key=lambda i: i[-1], reverse=True):
        print(i[0])
        print("{:<10}{:<15}{:<10}{:<15}".format("brought", "value", "Sold", "Value"))
        print("{:.<10,}{:.<15,.2f}{:.<10,}{:.<15,.2f}{:,.2f}".format(i[1], i[2], i[3], i[4], i[5]))

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
def get_id_names(ids):
    ids = list(dict.fromkeys(ids))
    headers = {"accept": "application/json",
               "Accept-Language": "en", 
               "Content-Type": "application/json",
               "Cache-Control": "no-cache"}
    resp = requests.post(esi.uni_names, data=str(ids), headers=headers)
    
    if resp.status_code == 400:
        return[]
    return resp.json()

def get_type_names():
    resp = requests.get(esi.uni_types.format(1))
    type_names = get_id_names(resp.json())
    for i in range(2, int(resp.headers['X-pages'])+1):
        resp = requests.get(esi.uni_types.format(i))
        type_names = type_names + get_id_names(resp.json())
    cache(type_names, "eve-cache/uni_types.csv", as_csv=False, mode='w')

def get_region_names():
    resp = requests.get(esi.uni_regions)
    data = get_id_names(resp.json())
    cache(data, "eve-cache/region_names.json", as_csv=False)

def get_group_info(size=None):
    resp = requests.get(market_groups)
    group_info_urls=[]
    for i in resp.json():
        group_info_urls.append(market_group_info.format(i))
    print(size, len(group_info_urls))
    resp = get_bulk_info(group_info_urls, size=size)
    data=[]
    for i in resp:
        data.append(i.json())
    cache(data, "eve-cache/market_group_info.json", as_csv=False)

def get_pos_info(ids):
    auth = OAuth()
    auth_data = auth.get()
    
    headers = {"Authorization": "Bearer {}".format(auth_data[0][2])}
    urls = []
    for i in ids:
        urls.append(esi.uni_structure_info.format(i))
                
    res = get_bulk_info(urls, headers=headers)
    for r in res:
        if r.reason == 'Unauthorized' or r.reason == 'Forbidden':
            auth.refresh()
            auth_data = auth.get()
            headers = {"Authorization": "Bearer {}".format(auth_data[0][2])}
            res = get_bulk_info(urls, headers=headers)
            break
    pos=[]
    for r in res:
        if r.reason == "Forbidden":
            d = {'category': 'unknown', 'name': r.json()['error'], 'id':int(r.url.rsplit('/', 2)[1])}
        else:
            d = {'category': 'unknown', 'name': r.json()['name'], 'id':int(r.url.rsplit('/', 2)[1])}
        pos.append(d)
    return pos

#market data
def list_active_orders():
    activeOrders=[]
    with open('eve-cache/region_names.json', 'r') as f:
        regions = json.load(f)
    for region in regions:
        elem={}
        resp = requests.get(esi.market_types.format(region['id'], 1))
        pages = int(resp.headers['X-pages'])
        types = resp.json()
        if pages > 1:
            for i in range(2, pages+1):
                resp = requests.get(esi.market_types.format(region['id'], i))
                types = types+resp.json()
        elem['name'] = region['name']
        elem['id'] = region['id']
        elem['orders'] = len(types)
        activeOrders.append(elem)
        
    for i in sorted(activeOrders, key=lambda j: j['orders'], reverse=True):
        if i['orders'] > 0:
            print("{:<10}{:<25}{}".format(i['id'], i['name'], i['orders']))
        
def market_orders(region, type_):
    buy = requests.get(esi.market_orders.format(region, 'buy', 1, type_))
    sell = requests.get(esi.market_orders.format(region, 'sell', 1, type_))
    ids=[]
    structs = []
    for i in buy.json()+sell.json():
        ids.append(i['system_id'])
        if i['location_id'] <= 0xffffffff:
            ids.append(i['location_id'])
        else:
            structs.append(i['location_id'])
    ids = list(dict.fromkeys(ids))
    ids = get_id_names(ids+[type_])
    
    structs = list(dict.fromkeys(structs))
    structs = get_pos_info(structs)
    
    all_ = ids+structs
    nbuy=[]
    for i in buy.json():
        for id_ in all_:
            if i['type_id'] == id_['id']:
                i['type_name'] = id_['name']
            elif i['location_id'] == id_['id']:
                i['location_name'] = id_['name']
            elif i['system_id'] == id_['id']:
                i['system_name'] = id_['name']
        sortKey = sorted(i)
        ndict = {}
        for k in sortKey:
            ndict[k] = i[k]
        nbuy.append(ndict)
    buy = sorted(nbuy, key=lambda k : k['price'], reverse=True)
    nsell=[]
    for i in sell.json():
        for id_ in all_:
            if i['type_id'] == id_['id']:
                i['type_name'] = id_['name']
            elif i['location_id'] == id_['id']:
                i['location_name'] = id_['name']
            elif i['system_id'] == id_['id']:
                i['system_name'] = id_['name']
        sortKey = sorted(i)
        ndict = {}
        for k in sortKey:
            ndict[k] = i[k]
        nsell.append(ndict)
    sell = sorted(nsell, key=lambda k : k['price'], reverse=True)
    cache(sell+buy, 'logs/market/'+str(region)+'/'+str(type_)+'.csv', as_csv=True)

def display(region, type_):
    name = "logs/market/"+str(region)+"/"+str(type_)+".csv"
    data = ETMlib.load_cache(name)
    header = data.pop(0)
    buy = []
    sell = []
    for i in data:
        if i[1] == 'True':
            buy.append(i)
        else:
            sell.append(i)    
    system=''
    sp=bp=0
    while system != 'q':
        print("{:^13}{:<12}{:<15}{:<13}{:<59}{}".format(header[1], header[7], header[12], header[10], header[4], header[8]))
        for i in sell:
            if system == '':
                print("{:^13}{:<12,}{:<15}{:<13}{:<59}{}".format(i[1], float(i[7]), i[12], i[10], i[4], i[8]))
                sp = i[7]
            elif i[10] == system:
                print("{:^13}{:<12,}{:<15}{:<13}{:<59}{}".format(i[1], float(i[7]), i[12], i[10], i[4], i[8]))
                sp = i[7]
        print("-"*115)
        for i in range(len(buy)-1, -1, -1):
            if system == '':
                bp = buy[i][7]
            elif buy[i][10] == system:
                bp = buy[i][7]
                
        for i in range(len(buy)):
            if system == '':
                print("{:^13}{:<12,}{:<15}{:<13}{:<59}{}".format(buy[i][1], float(buy[i][7]), buy[i][12], buy[i][10], buy[i][4], buy[i][8]))
            elif buy[i][10] == system:
                print("{:^13}{:<12,}{:<15}{:<13}{:<59}{}".format(buy[i][1], float(buy[i][7]), buy[i][12], buy[i][10], buy[i][4], buy[i][8]))
        print("{:,} {:,} {:,}".format(float(sp), float(bp), (float(sp)-float(bp))))
        system = input()

def get_bulk_history(region, size=None):
    resp = requests.get(esi.market_types.format(region, 1))
    pages = int(resp.headers['X-pages'])
    type_ids = resp.json()
    if pages > 1:
        for i in range(2, pages+1):
            resp  = requests.get(esi.market_types.format(region, i))
            type_ids = type_ids+resp.json()
    print(len(type_ids), "types, continue?")
    continue_ = input()
    
    if continue_ == 'y':
        urls = []
        for i in type_ids:
            urls.append(esi.market_history.format(region, i))
            
        resp = get_bulk_info(urls, size=size)
        
        passed=[]
        failed=[]
        for r in resp:
            if r.status_code == 200:
                passed.append(r)
            else:
                print(r.status_code, r.reason)
                failed.append(r)

        retry = input("{} failed, try again? y/n ".format(len(failed)))
        
        while retry == 'y':
            retry_resp = get_bulk_info([i.url for i in failed], size=size)
            
            passed=[]
            failed=[]
            for r in retry_resp:
                if r.status_code == 200:
                    passed.append(r)
                else:
                    print(r.status_code, r.reason)
                    failed.append(r)
                    
            resp = resp+passed
            retry = input("{} failed, try again? y/n ".format(len(failed)))
        
        with open("eve-cache/type_names.json", "r") as f:
            type_names=json.load(f)
            
        name=""   
        days=400.0
        med_data=[]
        errors=[]
        for r in resp:
            id_ = r.url.split('=')[-1]
            for i in type_names:
                if i['id'] == int(id_):
                    name = i['name']
                    name = name.replace("/", "_")
                    name = name.replace(",", ";")
            tot_average=0.0
            tot_highest=0.0
            tot_lowest=0.0
            tot_order_count=0.0
            tot_volume=0.0
            if r.status_code == 200 and len(r.json()) != 0:
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
                med_data_e={'id':id_, 'med_average':med_average,
                                'med_highest':med_highest,
                                'med_lowest':med_lowest,
                                'med_order_count':med_order_count,
                                'med_volume':med_volume,
                                'name': name}
                med_data.append(med_data_e)
                cache(r.json(), "logs/history/"+str(region)+"/"+id_+"_"+name+".csv")
            elif r.status_code != 200:
                print(id_, r.status_code)
                errors.append(r)
            else:
                med_data_e={'id':id_, 'med_average':tot_average,
                                'med_highest':tot_highest,
                                'med_lowest':tot_lowest,
                                'med_order_count':tot_order_count,
                                'med_volume':tot_volume,
                                'name': name}
                med_data.append(med_data_e)
                len0 = {'average':0,
                        'date':0,
                        'highest':0,
                        'lowest':0,
                        'order_count':0,
                        'volume':0}
                cache([len0], "logs/history/"+str(region)+"/"+id_+"_"+name+".csv")
            print("", len(med_data), end="\r")
        cache(med_data, "logs/history/"+str(region)+".csv")
        print()
        return errors
    
def get_bulk_market(region, size=None):
    if not os.path.exists('logs/market/'+str(region)):
        os.makedirs('logs/market/'+str(region))
    resp = requests.get(esi.market_types.format(region, 1))
    pages = int(resp.headers['X-pages'])
    type_ids = resp.json()
    if pages > 1:
        for i in range(2, pages+1):
            resp  = requests.get(esi.market_types.format(region, i))
            type_ids = type_ids+resp.json()
    print(len(type_ids), "types, continue?")
    cont = input()
    
    if cont == 'y':
        urls = []
        for i in type_ids:
            urls.append(esi.market_orders.format(region, 'all', 1, i))
        resp = get_bulk_info(urls, size=size)
        
        failed=[]
        worked=[]
        for i in range(len(resp)):
            if resp[i].status_code != 200:
                try:
                    print(resp[i].json())
                except:
                    print(resp[i])
                failed.append(resp[i])
            else:
                worked.append(resp[i])
        resp=worked
                
                
        cont2 = input('download, complete, {} failed, try again? y/n'.format(len(failed)))
        while cont2 == 'y':
            tmp_resp = get_bulk_info([i.url for i in failed], size=size)
            
            failed=[]
            worked=[]
            for i in range(len(tmp_resp)):
                if tmp_resp[i].status_code != 200:
                    try:
                        print(tmp_resp[i].json())
                    except:
                        print(tmp_resp[i])
                    failed.append(tmp_resp[i])
                else:
                    worked.append(tmp_resp[i])
            resp=resp+worked
            cont2 = input('{} failed, try again? y/n'.format(len(failed)))
        
        types = []
        systems = []
        locations = []
        structs = []
        print('>', len(resp))
        for r in resp:
            if len(r.json()) != 0 and r.status_code == 200:
                type_ = r.url.split('=')[-1]
                types.append(int(type_))
                for order in r.json():
                    systems.append(order['system_id'])
                    if order['location_id'] <= 0xffffffff:
                        locations.append(order['location_id'])
                    else:
                        structs.append(order['location_id'])
                        
        ids = list(dict.fromkeys(types+systems+locations))
        nids=[]
        if len(ids)>1000:
            for i in range(0, len(ids), 1000):
                nids = nids+get_id_names(ids[i:i+1000])
        structs = list(dict.fromkeys(structs))
        structs = get_pos_info(structs)
        all_ = nids+structs
        cnt=0
        for r in resp:
            type_ = r.url.split('=')[-1]
            if len(r.json()) != 0:
                buy=[]
                sell=[]
                for order in r.json():
                    for id_ in all_:
                        try:
                            if order['type_id'] == id_['id']:
                                order['type_name'] = id_['name']
                            elif order['location_id'] == id_['id']:
                                order['location_name'] = id_['name']
                            elif order['system_id'] == id_['id']:
                                order['system_name'] = id_['name']
                        except:
                            print("-", r.status_code, order, id_)
                            
                    if order['is_buy_order'] == True:
                        buy.append(order)
                    else:
                        sell.append(order)
                        
                nbuy=[]
                for i in buy:
                    sortKey = sorted(i)
                    ndict = {}
                    for k in sortKey:
                        ndict[k] = i[k]
                    nbuy.append(ndict)
                buy = sorted(nbuy, key=lambda k : k['price'], reverse=True)
                nsell=[]
                for i in sell:
                    sortKey = sorted(i)
                    ndict = {}
                    for k in sortKey:
                        ndict[k] = i[k]
                    nsell.append(ndict)
                sell = sorted(nsell, key=lambda k : k['price'], reverse=True)
                cnt+=1
                print('saving', cnt, end="\r")
                cache(sell+buy, 'logs/market/'+str(region)+'/'+str(type_)+'.csv', as_csv=True)
            else:
                cnt+=1
                print('saving', cnt, end="\r")
                with open('logs/market/'+str(region)+'/'+str(type_)+'.csv', 'w') as f:
                    f.write('duration,is_buy_order,issued,location_id,location_name,min_volume,order_id,price,range,system_id,system_name,type_id,type_name,volume_remain,volume_total')
        print()
        return failed
                #input("-")

def get_margins(region, station=None):
    accounting = getSkill("logs/characters/96500260_skills.json", "Accounting", full=True)
    Brokers_fee = getSkill("logs/characters/96500260_skills.json", "Broker Relations", full=True)
    types = load_cache('eve-cache/type_names.json', as_list=False)
    
    csvs = os.listdir('logs/market/'+str(region))
    volumes = load_cache('logs/history/'+str(region)+'.csv')
    print(len(volumes), len(csvs))
    header = ['type_id', 'name', 'best_sell', 'best_buy', 'margin', 'markup', 'med_order_count', 'med_volume']
    all_margins=[]
    all_margins.append(header)
    for csv in csvs:
        name = ''
        med_order_count = ''
        med_volume = ''
        id_ = csv.split('.')[0]
        print('', len(all_margins), end="\r")
        margin=[]
        data = load_cache('logs/market/'+str(region)+'/'+csv)
        header = data.pop(0)
        buy = []
        sell = []
        for i in data:
            if i[1] == 'True':
                buy.append(i)
            else:
                sell.append(i)
        best_sell=0
        best_buy=0
        if station != None:
            if len(sell) != 0:
                for i in sell:
                    if i[10] == station:
                        best_sell = i[7]
            else:
                best_sell = 0
            if len(buy) != 0:
                for i in range(len(buy)-1, -1, -1):
                    if buy[i][10] == station:
                        best_buy = buy[i][7]
            else:
                best_buy = 0
        else:
            if len(sell) != 0:
                best_sell = sell[-1][7]
            else:
                best_sell = 0
            if len(buy) != 0:
                best_buy = buy[0][7]
            else:
                best_buy = 0
                
        for v in range(1, len(volumes)):
            if volumes[v][0] == id_:
                med_order_count = volumes[v][4]
                med_volume = volumes[v][5]
                
        for t in types:
            if t['id'] == int(id_):
                name = t['name']
                name = name.replace("/", "_")
                name = name.replace(",", ";")
        
        s_tax = sales_tax(best_sell, accounting)
        b_sell_fee = brokers_fee(best_sell, Brokers_fee, 0, 0)
        b_buy_fee = brokers_fee(best_buy, Brokers_fee, 0, 0)
        m = (float(best_sell)-float(best_buy)) - (s_tax+b_sell_fee+b_buy_fee)
        try:
            markup = ((float(best_sell)-float(best_buy))/float(best_buy))*100
        except ZeroDivisionError:
            markup = 0
        margin = [id_, name, best_sell, best_buy, m, markup, med_order_count, med_volume]
        all_margins.append(margin)
    print()
    with open('logs/market/'+str(region)+'_margins.csv', 'w') as f:
        for line in all_margins:
            l=[]
            for i in line:
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
