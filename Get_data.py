from Authenticate import OAuth
import requests
import sqlite3
import os

if not os.path.exists("OAuth.db"):
        auth = OAuth()
        auth.authenticate()
    
db = sqlite3.connect("OAuth.db")
c = db.cursor()
data = c.execute("SELECT character_id, character_name, access_token, refresh_token FROM OAuth").fetchall()

character_id = data[0][0]
character_name = data[0][1]
access_token = data[0][2]
refresh_token = data[0][3]

headers = {"Authorization": "Bearer {}".format(access_token)}

balance_path = ("https://esi.evetech.net/latest/characters/{}/wallet/".format(character_id))
balance = requests.get(balance_path, headers=headers)

if balance.status_code == 401 or balance.status_code == 403:
    print(balance.status_code)
    auth = OAuth()
    auth.refresh('Threon en Gravonere')
    data = c.execute("SELECT character_id, character_name, access_token, refresh_token FROM OAuth").fetchall()

    access_token = data[0][2]

    headers = {"Authorization": "Bearer {}".format(access_token)}
    balance = requests.get(balance_path, headers=headers)
elif balance.status_code == 200:
    pass
else:
    print(balance.status_code)
    print(len(balance.text))
    print("something else went wrong")
    
print("id: {}, character: {}, wallet ballance: {:,}".format(character_id, character_name, balance.json()))   
    
    
 
#print("-----------------blueprints-----------------------")
#blueprint = ("https://esi.evetech.net/latest/characters/{}/blueprints/".format(data[0][0]))
#res = requests.get(blueprint, headers=headers)
#print(len(res.json()))
#for i in res.json(): print(i)

print("-----------------orders-----------------------")
orders = ("https://esi.evetech.net/latest/characters/{}/orders/".format(data[0][0]))
res = requests.get(orders, headers=headers)
print(len(res.json()))
for i in res.json(): print(i)

#print("-----------------journal-----------------------")
#journal = ("https://esi.evetech.net/latest/characters/{}/wallet/journal".format(data[0][0]))
#res = requests.get(journal, headers=headers)
#for i in res.json(): print(i)

#print("-----------------transactions-----------------------")
#transactions = ("https://esi.evetech.net/latest/characters/{}/wallet/transactions".format(data[0][0]))
#res = requests.get(transactions, headers=headers)
#for i in res.json(): print(i)

#print("-----------------assets-----------------------")
#assets = ("https://esi.evetech.net/latest/characters/{}/assets/".format(data[0][0]))
#res = requests.get(assets, headers=headers)
#print(len(res.json()))
#for i in res.json(): print(i)   
    
    
    
    
    
    
    
    
    
