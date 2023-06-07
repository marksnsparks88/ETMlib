# ETMlib

Eve online trade manager library. I will make a gui for it at some point but for now it's functional as a libaray.

Usage;
First setup character authentication.

Log in to eve developers @ https://developers.eveonline.com/ and create a new application.

Give it a name and description

select authentication & api access in connection type

select the scopes you want available in permissions

set http://localhost:8080 as the callback url

then click create application

view your application


in a python prompt;

Import Authenticate

#copy and paste the client id and scopes from the clipboard as parameters

auth = Authenticate.OAuth(client_id='your client', scopes='you scopes')

auth.authenticate()

#open the link and select a character and scopes

#Next import eve data, this will take a while...

import ETMlib

ETMlib.get_type_info()

ETMlib.get_structure_info()

ETMlib.get_group_info()

ETMlib.get_region_info()

ETMlib.get_system_station_info()

#this only has to be done once unless the data gets deleted or there's changes to the game

#character data, function names pretty self explanetory

ETMlib.get_character_transactions()

ETMlib.get_character_orders()

ETMlib.get_character_assets()

ETMlib.get_character_skills()

ETMlib.get_character_balance()

ETMlib.ledger(character_id)

#market data

#list your active orders

ETMlib.list_active_orders()

#get market orders for region, type

ETMlib.market_orders(region, type_)

#simple text display

ETMlib.display(region, type_)

#download bulk history for region

ETMlib.get_bulk_history(region)

#download bulk market orders for region

ETMlib.get_bulk_market(region)

#calculate margins for region, requires ETMlib.get_bulk_market(region) be run first

ETMlib.get_margins(character, region)

#calculate margins between two regions, requires ETMlib.get_bulk_market(region) be run first

ETMlib.get_trade_routes(regiona, regionb)

#data is stored as spreadsheets in logs

