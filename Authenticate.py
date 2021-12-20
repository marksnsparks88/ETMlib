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
        self.scopes="publicData esi-location.read_location.v1 esi-location.read_ship_type.v1 esi-skills.read_skills.v1 esi-skills.read_skillqueue.v1 esi-wallet.read_character_wallet.v1 esi-clones.read_clones.v1 esi-bookmarks.read_character_bookmarks.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-fittings.read_fittings.v1 esi-markets.structure_markets.v1 esi-characters.read_loyalty.v1 esi-characters.read_medals.v1 esi-characters.read_standings.v1 esi-characters.read_agents_research.v1 esi-industry.read_character_jobs.v1 esi-markets.read_character_orders.v1 esi-characters.read_blueprints.v1 esi-characters.read_corporation_roles.v1 esi-location.read_online.v1 esi-contracts.read_character_contracts.v1 esi-clones.read_implants.v1 esi-characters.read_fatigue.v1 esi-characters.read_notifications.v1 esi-markets.read_corporation_orders.v1 esi-industry.read_character_mining.v1 esi-planets.read_customs_offices.v1 esi-characters.read_titles.v1 esi-alliances.read_contacts.v1 esi-characters.read_fw_stats.v1 esi-characterstats.read.v1"
        
        self.EveLogin="https://login.eveonline.com"
        self.aurthorize=self.EveLogin+"/v2/oauth/authorize/"
        self.token=self.EveLogin+"/v2/oauth/token"
        self.jwk_set_url=self.EveLogin+"/oauth/jwks"
        
        self.hostName="localhost"
        self.serverPort=8080
        self.callback_url="http://"+self.hostName+":"+str(self.serverPort)
        
        self.dbfile ="OAuth.db"
        
    def authenticate(self):
        print("Authenticating")
        db = sqlite3.connect(self.dbfile)
        cur = db.cursor()
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
        
        print("Open the link Below to go to the Eve Online login Page")
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
            
            cur.execute("CREATE TABLE IF NOT EXISTS OAuth(character_id interger, character_name text, access_token text, refresh_token text)")
            try:
                db_character_id = c.execute("SELECT character_id FROM OAuth WHERE character_id = ?", ([character_id_])).fetchall()[0][0]
            except IndexError:
                db_character_id = 0
            if int(character_id_) != int(db_character_id):
                cur.execute("INSERT INTO OAuth VALUES (?, ?, ?, ?)", params)
                db.commit()
            elif int(character_id_) == int(db_character_id):
                cur.execute("UPDATE OAuth SET access_token = ?, refresh_token = ? WHERE character_id = ?", [data["access_token"], data["refresh_token"], character_id_])
                db.commit()
            cur.close()
            db.close()
            return (character_id_, character_name_, access_token)
        return None
        
    def refresh(self, character_name):
        db = sqlite3.connect(self.dbfile)
        cur = db.cursor()
        
        cdata = cur.execute("SELECT *  FROM OAuth WHERE character_name = ?", ([character_name])).fetchall()
        character_id_ = cdata[0][0]
        character_name_ = cdata[0][1]
        refresh_token = cdata[0][3]
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.eveonline.com"}
        form_values = {"grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "scope": self.scopes,}
        response = requests.post(self.token, data=form_values, headers=headers)
        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
            
            cur.execute("UPDATE OAuth SET access_token = ? WHERE refresh_token = ?", [data['access_token'], data['refresh_token']])
            db.commit()
            cur.close()
            db.close()
            return (character_id_, character_name_, access_token)
        return None
            

if __name__ == "__main__":
    try:
        args = sys.argv[1]
    except:
        args = []
        
    auth = OAuth()
    if os.path.exists(auth.dbfile):
        if len(args) > 0:
            character = auth.authenticate()
            if character:
                print("Character: {} with id: {} authenticated".format(character[1]), character[0])
                print("Access token: {}".format(character[2]))
        else:
            character = auth.refresh()
            if character:
                print("Character: {} with id: {} updated".format(character[1]), character[0])
                print("Access token: {}".format(character[2]))
    else:
        character = auth.authenticate()
        if character:
            print("Character: {} with id: {} authenticated".format(character[1]), character[0])
            print("Access token: {}".format(character[2]))
    

    
      






