import ETMlib
import os, requests, json




with open('eve-cache/region_names.json') as f:
    regions = json.load(f)
with open('eve-cache/group_info.json', 'r') as f:
  marketGroups = json.load(f)
with open('eve-cache/type_names.json', 'r') as f:
  marketItems = json.load(f)

choice = 0
selected = ['root']
region = 10000032
path=[['root']]
run = True
while run:
    for p in path:
        print(p[0], end='/')
    print()
    menu = [['root'], ['back'], ['region']]
    if selected[0] == 'root':
        path = [['root']]
        for i in marketGroups:
            if 'parent_group_id' not in i.keys():
                menu.append([i['name'], i['market_group_id'], i['types']])
    elif selected[0] == 'back':
        del path[-2:]
        selected = path[-1]
        continue
    elif selected[0] == 'region':
        del path[-1]
        selected = path[-1]
        for i in range(len(regions)):
            print(i, regions[i]['id'], regions[i]['name'])
        region = input('which region: ')
        region = regions[int(region)]['id']
        continue
    elif selected[2] == 'item':
        ETMlib.market_orders(region, selected[1])
        ETMlib.display(region, selected[1])
    elif len(selected[2]) != 0:
        for i in selected[2]:
            for j in marketItems:
                if j['id'] == i:
                    menu.append([j['name'], j['id'], 'item'])

    else:
        for i in marketGroups:
            if 'parent_group_id' in i.keys():
                if i['parent_group_id'] == int(selected[1]):
                    menu.append([i['name'], i['market_group_id'], i['types']])
    
    for i in range(len(menu)):
        print(i, menu[i])
    
    choice = input('select group: ')
    if choice == 'q':
        run = False
    else:
        selected = menu[int(choice)]
        print(selected[0])
        path.append(selected)



        
