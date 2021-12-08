import base64
import hashlib
import secrets
import urllib
import requests
import sys
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
        
        self.db = sqlite3.connect("data.db")
        
    def authenticate(self):
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
            
            params=(character_id_, character_name_, access_token, refresh_token)
            
            c = self.db.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS OAuth(character_id interger, character_name text, access_token text, refresh_token text)")
            if c.execute("SELECT character_id FROM OAuth WHERE character_id = ?", ([character_id_])) != character_id_:
                c.execute("INSERT INTO OAuth VALUES (?, ?, ?, ?)", params)
            else:
                c.execute("UPDATE OAuth SET access_token = ? WHERE character_id = ?", (data["access_token"], character_id))
                c.execute("UPDATE OAuth SET refresh_token = ? WHERE character_id = ?", (data["refresh_token"], character_id))
            c.close()
            self.db.commit()
            self.db.close()
        
    def refresh(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.eveonline.com"}
        form_values = {"grant_type": "refresh_token",
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                        "scope": self.scopes,}
        response = requests.post(self.token, data=form_values, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            c = self.db.cursor()
            c.execute("UPDATE OAuth SET access_token = ? WHERE refresh_token = ?", (data['access_token'], data['refresh_token']))
            c.close()
            self.db.commit()
            self.db.close()
            

if __name__ == "__main__":
    auth = OAuth()
    auth_data = auth.authenticate()
            
    #------#
    blueprint_path = ("https://esi.evetech.net/latest/characters/{}/blueprints/".format(auth_data['character_id']))
    
    orders_path = ("https://esi.evetech.net/latest/characters/{}/orders/".format(auth_data['character_id']))
    
    path = orders_path

    headers = {"Authorization": "Bearer {}".format(auth_data['access_token'])}

    res = requests.get(path, headers=headers)

    data = res.json()
    
