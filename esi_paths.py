#esi_root
esi_root = "https://esi.evetech.net/latest"
#Alliance
alliances = esi_root+"/alliances/" #List all active player alliances
alliance_info = esi_root+"/alliances/{}/" #Public information about an alliance
alliance_corp = esi_root+"/alliance/{}/corporations/" #List all current member corporations of an alliance
alliance_icons = esi_root+"/alliance/{}/icons" #Get the icon urls for a alliance
#Assets
assets_scope = "esi-assets.read_assets.v1 "
assets = esi_root+"/characters/{}/assets/" #Return a list of the characters assets
asset_locations = esi_root+"/characters/{}/assets/locations" #Return locations for a set of item ids, which you can get from character assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)
asset_names = esi_root+"/characters/{}/assets/names/"#Return names for a set of item ids, which you can get from character assets endpoint. Typically used for items that can customize names, like containers or ships.
corp_assets_scope = "esi-assets.read_corporation_assets.v1 "
corp_assets = esi_root+"/corporations/{}/assets" #Return a list of the corporation assets
corp_asset_locations = esi_root+"/corporations/{}/assets/locations" #Return locations for a set of item ids, which you can get from corporation assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)
corp_asset_names = esi_root+"/corporations/{}/assets/names/" #Return names for a set of item ids, which you can get from corporation assets endpoint. Only valid for items that can customize names, like containers or ships
#Bookmarks
bookmarks_scope = "esi-bookmarks.read_character_bookmarks.v1 "
bookmarks = esi_root+"/characters/{}/bookmarks" #A list of your character’s personal bookmarks
bookmark_folders = esi_root+"/characters/{}/bookmarks/folders" #A list of your character’s personal bookmark folders
corp_bookmarks_scope = " esi-bookmarks.read_corporation_bookmarks.v1 "
corp_bookmarks = esi_root+"/corporations/{}/bookmarks" #A list of your corporation’s bookmarks
corp_bookmark_folders = esi_root+"/corporations/{}/bookmarks/folders" #A list of your corporation’s bookmark folders
#Calender
#Character
blueprints_scope = "esi-characters.read_blueprints.v1 "
blueprints = esi_root+"/characters/{}/blueprints/" #Return a list of blueprints the character owns
#Clones
#Contacts
#Contracts
#Corporation
#Dogma
#Faction Warfare
#Fittings
#Fleets
#Incursions
#Industry
#Insurance
#Killmails
#Location
#Loyalty
#Mail
#Market
orders_scope = "esi-markets.read_character_orders.v1 "
orders = esi_root+"/characters/{}/orders/" #List open market orders placed by a character
#Opportunities
#Planetary Interaction
#Routes
#Search
#Skills
#Sovereignty
#Status
#Universe
type_info = esi_root+"/universe/types/{}" #Get information on a type
#User Interface
#Wallet
wallet_scope = "esi-wallet.read_character_wallet.v1 "
wallet = esi_root+"/characters/{}/wallet/" #Returns a character’s wallet balance
journal = esi_root+"/characters/{}/wallet/journal" #Retrieve the given character’s wallet journal going 30 days back
transactions = esi_root+"/characters/{}/wallet/transactions" #Get wallet transactions of a character
#Wars



