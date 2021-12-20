from Authenticate import OAuth
import requests
import sqlite3
import os, sys, time



def init_auth_data(db_file):
    db = sqlite3.connect(db_file)
    c = db.cursor()
    data = c.execute("SELECT * FROM OAuth").fetchall()
    c.close()
    db.close()
    return data #(row (id, name, access, refresh))
    
def get_character_data(character_data, auth_data, logs):
    url_root = "https://esi.evetech.net/latest/characters/"
    data = {}
    for character in auth_data
        if character_data == 'orders':
            url = "{}{}/orders/".format(url_root, character[0])
        elif character_data == 'blueprints':
            url = "{}{}/blueprints/".format(character[0])
        elif character_data == 'journal':
            url = "{}{}/wallet/journal".format(character[0])
        elif character_data == 'transactions':
            url = "{}{}/wallet/transactions".format(character[0])
        elif character_data = 'assets':
            url = "{}{}/assets/".format(character[0])
        elif character_data = 'balance':
            url = "{}{}/balance/".format(character[0])
        
        headers = {"Authorization": "Bearer {}".format(character[2])}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 401 or balance.status_code == 403:
            print("Refreshing...")
            charr_auth_data = auth.refresh(character[1])
            headers = {"Authorization": "Bearer {}".format(char_auth_data[0][2])}
            response = requests.get(url, headers=headers)
        
        
        log_file = logs+'/'+time.ctime()+'_'+character[0]+'_'character_data+'.json'
        with open(log_file, 'w') as f:
            json.dumps(response, f, indent=1)
        data[character[0]] = response.json()
        
    return data

auth_data = init_auth_data('OAuth.db')
resp = get_character_data('orders', auth_data, 'logs')
for char in resp:
    for i in char:
        print(i)

    
    
    
    
    
    
    
    
