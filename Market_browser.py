import sqlite3
db = sqlite3.connect("eve-data.db")
cur = db.cursor()
            
select_market = """SELECT market_group_id,name,parent_group_id,types 
                    FROM market_group_info 
                    WHERE {}=?"""
select_type="""SELECT type_id,name,market_group_id,description
                FROM market_type_info
                WHERE {}=?"""
select_market_parent = select_market.format("parent_group_id")
select_market_self = select_market.format("market_group_id")
select_type_self = select_type.format("type_id")
select_type_group = select_type.format("market_group_id")
            
choice = 0
indexes = ['']
items = ['']
types = ['']
GoBack = False
browse = True
while browse == True:
    NoItems = False
    if choice == 0 or choice == '':
        indexes = ['']
        #print(indexes)
        path = '.'
        for g in range(1, len(indexes)):
            group = cur.execute(select_market_self, ([indexes[g]])).fetchall()[0][1]
            path = path+' > '+str(group)
        print(path)
        items = cur.execute(select_market_parent, ([indexes[-1]])).fetchall()
        items = ['']+items
        for i in range(1, len(items)):
            #print("{}) [{}] {}".format(i, items[i][0], items[i][1]))
            print("{}) {}".format(i, items[i][1]))
    elif choice == '<':
        if len(indexes) > 1:
            del indexes[-1]
        #print(indexes)
        path = '.'
        for g in range(1, len(indexes)):
            group = cur.execute(select_market_self, ([indexes[g]])).fetchall()[0][1]
            path = path+' > '+str(group)
        print(path)
        items = cur.execute(select_market_parent, ([indexes[-1]])).fetchall()
        items = ['']+items
        for i in range(1, len(items)):
            #print("{}) [{}] {}".format(i, items[i][0], items[i][1]))
            print("{}) {}".format(i, items[i][1]))
    elif len(items) > 1:
        indexes.append(items[choice][0])
        #print(indexes)
        path = '.'
        for g in range(1, len(indexes)):
            group = cur.execute(select_market_self, ([indexes[g]])).fetchall()[0][1]
            path = path+' > '+str(group)
        print(path)
        items = cur.execute(select_market_parent, ([indexes[-1]])).fetchall()
        items = ['']+items
        for i in range(1, len(items)):
            #print("{}) [{}] {}".format(i, items[i][0], items[i][1]))
            print("{}) {}".format(i, items[i][1]))
        if len(items) == 1:
            types = cur.execute(select_type_group, ([indexes[-1]])).fetchall()
            types = ['']+types
            if len(types) > 1:
                for i in range(1, len(types)):
                    #print("{}) [{}] {}".format(i, types[i][0], types[i][1]))
                    print("{}) {}".format(i, types[i][1]))
            else:
                GoBack = True
                print("No Items")
                choice = '<'
                
    elif len(types) > 1:
        description = (cur.execute(select_type_self, ([types[choice][0]])).fetchall()[0][3])
        print(description)
        if not description:
            print("no description")
           
    if not GoBack:
        choice = input()
    if choice == 'q' or choice == 'quit':
        browse = False
    try:
        choice = int(choice)
    except ValueError:
        continue
