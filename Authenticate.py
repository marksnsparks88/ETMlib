import base64
import hashlib
import secrets
import urllib
import requests
import sys
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
        
        self.access_token = ""
        self.refresh_token = ""
    def authenticate(self):
        random = base64.urlsafe_b64encode(secrets.token_bytes(32))
        m = hashlib.sha256()
        m.update(random)
        d = m.digest()
        code_challenge = base64.urlsafe_b64encode(d).decode().replace("=", "")
        
        base_auth_url = "https://login.eveonline.com/v2/oauth/authorize/"
        params = {"response_type": "code",
                    "redirect_uri": self.callback_url,
                    "client_id": self.client_id,
                    "scope": self.scopes,
                    "state": "unique-state",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256"}

        string_params = urllib.parse.urlencode(params)
        full_auth_url = "{}?{}".format(base_auth_url, string_params)

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
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            
            res = requests.get(self.jwk_set_url)
            data = res.json()
            jwk_sets = data["keys"]
            jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))
            jwt_ = jwt.decode(access_token, jwk_set, algorithms=jwk_set["alg"], issuer="login.eveonline.com")
    
            character_id = jwt_["sub"].split(":")[2]
            character_name = jwt_["name"]
            
            return jwt_
            
            #------#
            blueprint_path = ("https://esi.evetech.net/latest/characters/{}/blueprints/".format(character_id))

            headers = {
                "Authorization": "Bearer {}".format(access_token)
            }

            res = requests.get(blueprint_path, headers=headers)

            data = res.json()
        
    def refresh(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.eveonline.com"}
        form_values = {"grant_type": "refresh_token",
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                        "scope": self.scopes,}
        response = requests.post(self.token, data=form_values, headers=headers)
        if response.status_code = 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            

if __name__ == "__main__":
    auth = OAuth()
    auth.authenticate()
    
