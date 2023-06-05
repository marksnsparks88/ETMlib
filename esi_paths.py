#root
root = "https://esi.evetech.net/latest"
#Alliance
alliances = root+"/alliances/"                                                                   #List all active player alliances
alliance_info = root+"/alliances/{}/"                                                            #Public information about an alliance
alliance_corp = root+"/alliance/{}/corporations/"                                                #List all current member corporations of an alliance
alliance_icons = root+"/alliance/{}/icons"                                                       #Get the icon urls for a alliance
#Assets

assets = root+"/characters/{}/assets/"                                                           #Return a list of the characters assets
asset_locations = root+"/characters/{}/assets/locations/"                                         #Return locations for a set of item ids, which you can get from character assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)
asset_names = root+"/characters/{}/assets/names/"                                                #Return names for a set of item ids, which you can get from character assets endpoint. Typically used for items that can customize names, like containers or ships.

corp_assets = root+"/corporations/{}/assets"                                                     #Return a list of the corporation assets
corp_asset_locations = root+"/corporations/{}/assets/locations"                                  #Return locations for a set of item ids, which you can get from corporation assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)
corp_asset_names = root+"/corporations/{}/assets/names/"                                         #Return names for a set of item ids, which you can get from corporation assets endpoint. Only valid for items that can customize names, like containers or ships
#Bookmarks

bookmarks = root+"/characters/{}/bookmarks"                                                      #A list of your character’s personal bookmarks
bookmark_folders = root+"/characters/{}/bookmarks/folders"                                       #A list of your character’s personal bookmark folders
corp_bookmarks = root+"/corporations/{}/bookmarks"                                               #A list of your corporation’s bookmarks
corp_bookmark_folders = root+"/corporations/{}/bookmarks/folders"                                #A list of your corporation’s bookmark folders
#Calender
#Character

char_public = root+"/characters/{}/"                                                             #Public information about a character
char_blueprints = root+"/characters/{}/blueprints/"                                              #Return a list of blueprints the character owns


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

market_character_orders = root+"/characters/{}/orders/"                                          #List open market orders placed by a character
market_types = root+"/markets/{}/types/?datasource=tranquility&page={}"                          #Return a list of type IDs that have active orders in the region, for efficient market indexing.
market_history = root+"/markets/{}/history/?datasource=tranquility&type_id={}"                   #Return a list of historical market statistics for the specified type in a region
market_orders = root+"/markets/{}/orders/?datasource=tranquility&order_type={}&page={}&type_id={}"#Return a list of orders in a region
market_groups = root+"/markets/groups/?datasource=tranquility"                                   #Get a list of item groups
market_group_info = root+"/markets/groups/{}/?datasource=tranquility"                            #Get information on an item group
#Opportunities
#Planetary Interaction
#Routes
#Search
#Skills

skills = root+"/characters/{}/skills/"                                                           #List all trained skills for the given character
#Sovereignty
#Status
#Universe
uni_ids = root+"/universe/ids/"                                                                  #Resolve a set of names to IDs in the following categories: agents, alliances, characters, constellations, corporations factions, inventory_types, regions, stations, and systems. Only exact matches will be returned
uni_names = root+"/universe/names/"                                                              #Resolve a set of IDs to names and categories. Supported ID’s for resolving are: Characters, Corporations, Alliances, Stations, Solar Systems, Constellations, Regions, Types, Factions
uni_regions = root+"/universe/regions/?datasource=tranquility&language=en"                       #Get a list of regions
uni_region_info = root+"/universe/regions/{}/?datasource=tranquility&language=en"                #Get information on a region
uni_types = root+"/universe/types/?datasource=tranquility&page={}"                               #Get a list of type ids
uni_type_info = root+"/universe/types/{}"                                                        #Get information on a type
uni_structure_ids = root+"/universe/structures/"                                                 #List all public structures
uni_structure_info = root+"/universe/structures/{}/"                                             #Returns information on requested structure if you are on the ACL. Otherwise, returns “Forbidden” for all inputs.
#User Interface
#Wallet

wallet_balance = root+"/characters/{}/wallet/"                                                   #Returns a character’s wallet balance
wallet_journal = root+"/characters/{}/wallet/journal/"                                            #Retrieve the given character’s wallet journal going 30 days back
wallet_transactions = root+"/characters/{}/wallet/transactions/"                                  #Get wallet transactions of a character
#Wars



