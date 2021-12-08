import base64
import hashlib
import secrets
import urllib
import requests
import sys
import os
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError, JWTClaimsError
import re
from Callback_server import Callback_Server

client_id="ff320ee128f54bfb8a7c3fbf6b55e467"
loginUrl="https://login.eveonline.com/oauth/"




def validate_eve_jwt(jwt_token):

    jwk_set_url = "https://login.eveonline.com/oauth/jwks"

    res = requests.get(jwk_set_url)
    res.raise_for_status()

    data = res.json()

    try:
        jwk_sets = data["keys"]
    except KeyError as e:
        print("Something went wrong when retrieving the JWK set. The returned "
              "payload did not have the expected key {}. \nPayload returned "
              "from the SSO looks like: {}".format(e, data))
        sys.exit(1)

    jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))

    try:
        return jwt.decode(
            jwt_token,
            jwk_set,
            algorithms=jwk_set["alg"],
            issuer="login.eveonline.com"
        )
    except ExpiredSignatureError:
        print("The JWT token has expired: {}")
        sys.exit(1)
    except JWTError as e:
        print("The JWT signature was invalid: {}").format(str(e))
        sys.exit(1)
    except JWTClaimsError as e:
        try:
            return jwt.decode(
                        jwt_token,
                        jwk_set,
                        algorithms=jwk_set["alg"],
                        issuer="https://login.eveonline.com"
                    )
        except JWTClaimsError as e:
            print("The issuer claim was not from login.eveonline.com or "
                  "https://login.eveonline.com: {}".format(str(e)))
            sys.exit(1)


def print_auth_url(client_id, code_challenge=None):

    base_auth_url = "https://login.eveonline.com/v2/oauth/authorize/"
    params = {"response_type": "code",
                "redirect_uri": "http://localhost:8080",
                "client_id": client_id,
                "scope": "esi-characters.read_blueprints.v1 esi-markets.read_character_orders.v1",
                "state": "unique-state"}

    if code_challenge:
        params.update({"code_challenge": code_challenge,
                        "code_challenge_method": "S256"})

    string_params = urllib.parse.urlencode(params)
    full_auth_url = "{}?{}".format(base_auth_url, string_params)

    print(full_auth_url)


def send_token_request(form_values, add_headers={}):
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                "Host": "login.eveonline.com"}

    if add_headers:
        headers.update(add_headers)

    res = requests.post(
        "https://login.eveonline.com/v2/oauth/token",
        data=form_values,
        headers=headers,
    )

    print("Request sent to URL {} with headers {} and form values: "
          "{}\n".format(res.url, headers, form_values))
    res.raise_for_status()

    return res


def handle_sso_token_response(sso_response):

    if sso_response.status_code == 200:
        data = sso_response.json()
        access_token = data["access_token"]

        print("\nVerifying access token JWT...")

        jwt = validate_eve_jwt(access_token)
        character_id = jwt["sub"].split(":")[2]
        character_name = jwt["name"]
        blueprint_path = ("https://esi.evetech.net/latest/characters/{}/"
                          "blueprints/".format(character_id))

        print("\nSuccess! Here is the payload received from the EVE SSO: {}"
              "\nYou can use the access_token to make an authenticated "
              "request to {}".format(data, blueprint_path))

        input("\nPress any key to have this program make the request for you:")

        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }

        res = requests.get(blueprint_path, headers=headers)
        print("\nMade request to {} with headers: "
              "{}".format(blueprint_path, res.request.headers))
        res.raise_for_status()

        data = res.json()
        print("\n{} has {} blueprints".format(character_name, len(data)))
    else:
        print("\nSomething went wrong! Re read the comment at the top of this "
              "file and make sure you completed all the prerequisites then "
              "try again. Here's some debug info to help you out:")
        print("\nSent request with url: {} \nbody: {} \nheaders: {}".format(
            sso_response.request.url,
            sso_response.request.body,
            sso_response.request.headers
        ))
        print("\nSSO response code is: {}".format(sso_response.status_code))
        print("\nSSO response JSON is: {}".format(sso_response.json()))
        
def main(client_id):

    random = base64.urlsafe_b64encode(secrets.token_bytes(32))
    m = hashlib.sha256()
    m.update(random)
    d = m.digest()
    code_challenge = base64.urlsafe_b64encode(d).decode().replace("=", "")

    client_id = client_id

    print_auth_url(client_id, code_challenge=code_challenge)
            
    auth = Callback_Server("localhost", 8080)

    code_verifier = random

    form_values = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth.code,
        "code_verifier": code_verifier
    }

    input("\nPress any key to continue:")

    res = send_token_request(form_values)

    handle_sso_token_response(res)


if __name__ == "__main__":
    main(client_id)
