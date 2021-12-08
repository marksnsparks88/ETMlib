import base64
import hashlib
import secrets
import urllib
import requests
import sys
import os
import sqlite3
from jose import jwt
from Callback_server import Callback_Server




class OAuth():
    def __init__(self):
        self.client_id="ff320ee128f54bfb8a7c3fbf6b55e467"
        self.scopes="esi-characters.read_blueprints.v1 esi-markets.read_character_orders.v1"
        
        self.EveLogin="https://login.eveonline.com"
        self.aurthorize=self.EveLogin+"/v2/oauth/authorize/"
        self.token=self.EveLogin+"/v2/oauth/token"
        self.jwk_set_url=self.EveLogin+"/oauth/jwks"
        
        self.hostName="localhost"
        self.serverPort=8080
        self.callback_url="http://"+self.hostName+":"+str(self.serverPort)
        
        self.dbfile ="data.db"
        
    def authenticate(self):
        db = sqlite3.connect(self.dbfile)
        random = base64.urlsafe_b64encode(secrets.token_bytes(32))
        m = hashlib.sha256()
        m.update(random)
        d = m.digest()
        code_challenge = base64.urlsafe_b64encode(d).decode().replace("=", "")
        
        
        params = {"response_type": "code",
                    "redirect_uri": self.callback_url,
                    "client_id": self.client_id,
                    "scope": self.scopes,
                    "state": "unique-state",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256"}
        
        string_params = urllib.parse.urlencode(params)
        full_auth_url = "{}?{}".format(self.aurthorize, string_params)
        
        print(full_auth_url)
            
        auth = Callback_Server(self.hostName, self.serverPort)
        
        code_verifier = random
        
        form_values = {"grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "code": auth.code,
                        "code_verifier": code_verifier}
        
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.eveonline.com"}
        
        response = requests.post(self.token, data=form_values, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
            
            res = requests.get(self.jwk_set_url)
            res = res.json()
            jwk_sets = res["keys"]
            jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))
            jwt_ = jwt.decode(data["access_token"], jwk_set, algorithms=jwk_set["alg"], issuer="login.eveonline.com")
    
            character_id_ = jwt_["sub"].split(":")[2]
            character_name_ = jwt_["name"]
            print(character_name_)
            
            params=(character_id_, character_name_, access_token, refresh_token)
            
            c = db.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS OAuth(character_id interger, character_name text, access_token text, refresh_token text)")
            try:
                db_character_id = c.execute("SELECT character_id FROM OAuth WHERE character_id = ?", ([character_id_])).fetchall()[0][0]
            except IndexError:
                db_character_id = 0
            if int(character_id_) != int(db_character_id):
                c.execute("INSERT INTO OAuth VALUES (?, ?, ?, ?)", params)
                db.commit()
            elif int(character_id_) == int(db_character_id):
                c.execute("UPDATE OAuth SET access_token = ?, refresh_token = ? WHERE character_id = ?", [data["access_token"], data["refresh_token"], character_id_])
                db.commit()
            c.close()
            db.close()
        
    def refresh(self, character_name):
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()
        refresh_token = c.execute("SELECT refresh_token FROM OAuth WHERE character_name = ?", ([character_name])).fetchall()[0][0]
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.eveonline.com"}
        form_values = {"grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "scope": self.scopes,}
        response = requests.post(self.token, data=form_values, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            
            c.execute("UPDATE OAuth SET access_token = ? WHERE refresh_token = ?", [data['access_token'], data['refresh_token']])
            db.commit()
            c.close()
            db.close()
            

if __name__ == "__main__":
    auth = OAuth()
    character = 'Threon en Gravonere'
    if os.path.exists(auth.dbfile):
        auth.refresh(character)
    else:
        auth.authenticate()
    
    db = sqlite3.connect(auth.dbfile)
    c = db.cursor()
    
    data = c.execute("SELECT character_id, character_name, access_token, refresh_token FROM OAuth").fetchall()
    print(data[0][0])
            
    #------#
    blueprint_path = ("https://esi.evetech.net/latest/characters/{}/blueprints/".format(data[0][0]))
    
    orders_path = ("https://esi.evetech.net/latest/characters/{}/orders/".format(data[0][0]))
    
    path = orders_path

    headers = {"Authorization": "Bearer {}".format(data[0][2])}

    res = requests.get(path, headers=headers)

    for i in res.json():
        print(i)
    
