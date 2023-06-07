import base64
import hashlib
import secrets
import urllib
import requests
import sys
import os
import re
import sqlite3
from jose import jwt
from http.server import BaseHTTPRequestHandler, HTTPServer

scopes="publicData esi-calendar.respond_calendar_events.v1 esi-calendar.read_calendar_events.v1 esi-location.read_location.v1 esi-location.read_ship_type.v1 esi-mail.organize_mail.v1 esi-mail.read_mail.v1 esi-mail.send_mail.v1 esi-skills.read_skills.v1 esi-skills.read_skillqueue.v1 esi-wallet.read_character_wallet.v1 esi-wallet.read_corporation_wallet.v1 esi-search.search_structures.v1 esi-clones.read_clones.v1 esi-characters.read_contacts.v1 esi-universe.read_structures.v1 esi-bookmarks.read_character_bookmarks.v1 esi-killmails.read_killmails.v1 esi-corporations.read_corporation_membership.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-fleets.read_fleet.v1 esi-fleets.write_fleet.v1 esi-ui.open_window.v1 esi-ui.write_waypoint.v1 esi-characters.write_contacts.v1 esi-fittings.read_fittings.v1 esi-fittings.write_fittings.v1 esi-markets.structure_markets.v1 esi-corporations.read_structures.v1 esi-characters.read_loyalty.v1 esi-characters.read_opportunities.v1 esi-characters.read_chat_channels.v1 esi-characters.read_medals.v1 esi-characters.read_standings.v1 esi-characters.read_agents_research.v1 esi-industry.read_character_jobs.v1 esi-markets.read_character_orders.v1 esi-characters.read_blueprints.v1 esi-characters.read_corporation_roles.v1 esi-location.read_online.v1 esi-contracts.read_character_contracts.v1 esi-clones.read_implants.v1 esi-characters.read_fatigue.v1 esi-killmails.read_corporation_killmails.v1 esi-corporations.track_members.v1 esi-wallet.read_corporation_wallets.v1 esi-characters.read_notifications.v1 esi-corporations.read_divisions.v1 esi-corporations.read_contacts.v1 esi-assets.read_corporation_assets.v1 esi-corporations.read_titles.v1 esi-corporations.read_blueprints.v1 esi-bookmarks.read_corporation_bookmarks.v1 esi-contracts.read_corporation_contracts.v1 esi-corporations.read_standings.v1 esi-corporations.read_starbases.v1 esi-industry.read_corporation_jobs.v1 esi-markets.read_corporation_orders.v1 esi-corporations.read_container_logs.v1 esi-industry.read_character_mining.v1 esi-industry.read_corporation_mining.v1 esi-planets.read_customs_offices.v1 esi-corporations.read_facilities.v1 esi-corporations.read_medals.v1 esi-characters.read_titles.v1 esi-alliances.read_contacts.v1 esi-characters.read_fw_stats.v1 esi-corporations.read_fw_stats.v1 esi-characterstats.read.v1"

class Window(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Eve Sign in</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Sign in Complete</p>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This window can now be closed.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        auth_code = self.path

class Callback_Server():
    def __init__(self, hostName, serverPort):
        self.webServer = HTTPServer((hostName, serverPort), Window)
        print("http://{}:{}".format(hostName, str(serverPort)))
        run = True
        while run:
            self.webServer.handle_request()
            if "/?code=" in auth_code:
                run = False
                self.webServer.server_close()
                self.code = re.findall("(?:=)(.*?)(?:&)", auth_code)[0]

class OAuth():
    def __init__(self, client_id="ff320ee128f54bfb8a7c3fbf6b55e467", scopes=scopes):
        self.client_id=client_id
        self.scopes=scopes

        self.EveLogin="https://login.eveonline.com"
        self.aurthorize=self.EveLogin+"/v2/oauth/authorize/"
        self.token=self.EveLogin+"/v2/oauth/token"
        self.jwk_set_url=self.EveLogin+"/oauth/jwks"
        
        self.hostName="localhost"
        self.serverPort=8080
        self.callback_url="http://"+self.hostName+":"+str(self.serverPort)
        
        self.dbfile ="eve-cache/OAuth.db"
        if not os.path.exists("eve-cache"):
            os.makedirs('eve-cache')
        
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
            jwt_ = jwt.decode(data["access_token"], jwk_set, algorithms=jwk_set["alg"], issuer="login.eveonline.com", audience="EVE Online")
    
            character_id_ = jwt_["sub"].split(":")[2]
            character_name_ = jwt_["name"]
            print(character_name_)
            
            params=(character_id_, character_name_, access_token, refresh_token)
            
            cur.execute("CREATE TABLE IF NOT EXISTS OAuth(character_id interger, character_name text, access_token text, refresh_token text)")
            try:
                db_character_id = cur.execute("SELECT character_id FROM OAuth WHERE character_id = ?", ([character_id_])).fetchall()[0][0]
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
        
    def refresh(self):
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()
        auth_data = c.execute("SELECT * FROM OAuth").fetchall()
        for cdata in auth_data:
            character_id_ = cdata[0]
            character_name_ = cdata[1]
            refresh_token = cdata[3]
            headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "Host": "login.eveonline.com"}
            form_values = {"grant_type": "refresh_token",
                            "refresh_token": refresh_token,
                            "client_id": self.client_id,
                            "scope": self.scopes,}
            response = requests.post(self.token, data=form_values, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                c.execute("UPDATE OAuth SET access_token = ? WHERE character_id = ?", [data['access_token'], character_id_])
                
        db.commit()
        c.close()
        db.close()
                
    
    def get(self):
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()
        auth_data = c.execute("SELECT * FROM OAuth").fetchall()#(row (id, name, access, refresh))
        c.close()
        db.close()
        return auth_data




    

    
      






