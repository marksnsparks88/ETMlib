import yaml, os, json, re

def convertAll(dir_, to_dir='json/', chunk = 2, lang = 'en'):
    tree = os.walk(dir_.rsplit('/', 1)[0])
    while True:
        try:
            dir_ = next(tree)
            for f in dir_[2]:
                pth = dir_[0]+'/'+f
                if not os.path.exists(to_dir+pth.split('.')[0]+'.json'):
                    yaml2json(pth, to_dir, chunk, lang)
                else:
                    print("Already converted:", to_dir+pth.split('.')[0]+'.json')
        except StopIteration:
            break


def yaml2json(yaml_, to_dir, chunk = 2, lang='en'):
    cnt=0
    tmp = []
    yaml_ = yaml_.rsplit('/', 1)
    file_ = yaml_[1]
    pth = to_dir+yaml_[0]+'/'
    print("starting: {}".format(pth+file_))
    if not os.path.exists(pth):
        os.makedirs(pth)
    with open(yaml_[0]+'/'+file_, "r") as yf:
        s = ''
        for i in yf:
            nname = file_.split(".")[0]+str(cnt)
            if re.search("^\w*:|^-", i):
                with open(pth+nname+".yaml", "a") as jf:
                    jf.write(s)
                    jf.write("\n")
                size = (os.stat(pth+nname+".yaml").st_size/1024)/1024
                if size > chunk:
                    tmp.append(nname)
                    print(' split_cnt', cnt, end="\r")
                    cnt +=1
                s=''
            s = s+i
    tmp.append(nname)
    print(' split_cnt', cnt)
    all_ = {}
    for i in range(len(tmp)):
        print(" converting", tmp[i], end="\r")
        with open(pth+tmp[i]+".yaml", "r") as f:
            d = yaml.safe_load(f)
            
        os.remove(pth+tmp[i]+".yaml")
            
        if lang != "all":
            stripLang(lang, d)
        if type(d).__name__ == 'dict':    
            for k in d.keys():
                all_[k] = d[k]
        else:
            if len(all_) == 0:
                all_ = []
            all_ = all_+d
            
        del d
    
    jname = pth+file_.split('.')[0]
    with open(jname+".json", "w") as f:
        json.dump(all_, f, indent=1)
    print("finished converting: {}".format(jname+".json"))
    
            


def stripLang(keep, dict_):
    langs = ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'ru', 'zh']
    langs = [l for l in langs if l != keep]
    cnt = 0
    while len(dict_) != cnt:
        try:
            d1 = list(dict_.keys())[cnt]
        except AttributeError:
            d1 = cnt
        if len(str(dict_[d1])) == 0:
            del dict_[d1]
            continue
        elif d1 in langs:
            del dict_[d1]
        else:
            cnt+=1
            cnt1=0
            typestr = type(dict_[d1]).__name__
            if typestr == 'dict' or typestr == 'list':
                while len(dict_[d1]) != cnt1:
                    try:
                        d2 = list(dict_[d1].keys())[cnt1]
                    except AttributeError:
                        d2 = cnt1
                    if len(str(dict_[d1][d2])) == 0:
                        del dict_[d1][d2]
                        continue
                    elif d2 in langs:
                        del dict_[d1][d2]
                    else:
                        cnt1+=1
                        cnt2=0
                        typestr1 = type(dict_[d1][d2]).__name__
                        if typestr1 == 'dict' or typestr1 == 'list':
                            while len(dict_[d1][d2]) != cnt2:
                                try:
                                    d3 = list(dict_[d1][d2].keys())[cnt2]
                                except AttributeError:
                                    d3 = cnt2
                                if len(str(dict_[d1][d2][d3])) == 0:
                                    del dict_[d1][d2][d3]
                                    continue
                                elif d3 in langs:
                                    del dict_[d1][d2][d3]
                                else:
                                    cnt2+=1
                                    cnt3=0
                                    typestr2 = type(dict_[d1][d2][d3]).__name__
                                    if typestr2 == 'dict' or typestr2 == 'list':
                                        while len(dict_[d1][d2][d3]) != cnt3:
                                            try:
                                                d4 = list(dict_[d1][d2][d3].keys())[cnt3]
                                            except AttributeError:
                                                d4 = cnt3
                                            if len(str(dict_[d1][d2][d3][d4])) == 0:
                                                del dict_[d1][d2][d3][d4]
                                                continue
                                            elif d4 in langs:
                                                del dict_[d1][d2][d3][d4]
                                            else:
                                                cnt3+=1
                                                cnt4=0
                                                typestr3 = type(dict_[d1][d2][d3][d4]).__name__
                                                if typestr3 == 'dict' or typestr3 == 'list':
                                                    while len(dict_[d1][d2][d3][d4]) != cnt4:
                                                        try:
                                                            d5 = list(dict_[d1][d2][d3][d4].keys())[cnt4]
                                                        except AttributeError:
                                                            d5 = cnt4
                                                        if len(str(dict_[d1][d2][d3][d4][d5])) == 0:
                                                            del dict_[d1][d2][d3][d4][d5]
                                                            continue
                                                        elif d5 in langs:
                                                            del dict_[d1][d2][d3][d4][d5]
                                                        else:
                                                            cnt4+=1
                                                            cnt5=0
                                                            typestr4 = type(dict_[d1][d2][d3][d4][d5]).__name__
                                                            if typestr4 == 'dict' or typestr4 == 'list':
                                                                while len(dict_[d1][d2][d3][d4][d5]) != cnt5:
                                                                    try:
                                                                        d6 = list(dict_[d1][d2][d3][d4][d5].keys())[cnt5]
                                                                    except AttributeError:
                                                                        d6 = cnt5
                                                                    if len(str(dict_[d1][d2][d3][d4][d5][d6])) == 0:
                                                                        del dict_[d1][d2][d3][d4][d5][d6]
                                                                        continue
                                                                    elif d6 in langs:
                                                                        del dict_[d1][d2][d3][d4][d5][d6]
                                                                    else:
                                                                        cnt5+=1
                                                                        cnt6=0
                                                                        typestr5 = type(dict_[d1][d2][d3][d4][d5][d6]).__name__
                                                                        if typestr5 == 'dict' or typestr5 == 'list':
                                                                            while len(dict_[d1][d2][d3][d4][d5][d6]) != cnt6:
                                                                                try:
                                                                                    d7 = list(dict_[d1][d2][d3][d4][d5][d6].keys())[cnt6]
                                                                                except AttributeError:
                                                                                    d7 = cnt6
                                                                                if len(str(dict_[d1][d2][d3][d4][d5][d6][d7])) == 0:
                                                                                    del dict_[d1][d2][d3][d4][d5][d6][d7]
                                                                                    continue
                                                                                elif d7 in langs:
                                                                                    del dict_[d1][d2][d3][d4][d5][d6][d7]
                                                                                else:
                                                                                    cnt6+=1
                                                                                    cnt7=0
                                                                                    typestr6 = type(dict_[d1][d2][d3][d4][d5][d6][d7]).__name__
                                                                                    if typestr6 == 'dict' or typestr == 'list':
                                                                                        while len(dict_[d1][d2][d3][d4][d5][d6][d7]) != cnt7:
                                                                                            try:
                                                                                                d8 = list(dict_[d1][d2][d3][d4][d5][d6][d7].keys())[cnt7]
                                                                                            except AttributeError:
                                                                                                d8 = cnt7
                                                                                            if len(str(dict_[d1][d2][d3][d4][d5][d6][d7][d8])) == 0:
                                                                                                del dict_[d1][d2][d3][d4][d5][d6][d7][d8]
                                                                                                continue
                                                                                            elif d8 in langs:
                                                                                                del dict_[d1][d2][d3][d4][d5][d6][d7][d8]
                                                                                            else:
                                                                                                cnt7+=1
                                                                                            if type(dict_[d1][d2][d3][d4][d5][d6][d7]).__name__ == 'dict' and list(dict_[d1][d2][d3][d4][d5][d6][d7].keys())[0] == keep and len(dict_[d1][d2][d3][d4][d5][d6][d7].keys()) == 1:
                                                                                                d8 = list(dict_[d1][d2][d3][d4][d5][d6][d7].keys())[0]
                                                                                                dict_[d1][d2][d3][d4][d5][d6][d7] = dict_[d1][d2][d3][d4][d5][d6][d7][d8]
                                                                                if type(dict_[d1][d2][d3][d4][d5][d6]).__name__ == 'dict' and list(dict_[d1][d2][d3][d4][d5][d6].keys())[0] == keep and len(dict_[d1][d2][d3][d4][d5][d6].keys()) == 1:
                                                                                    d7 = list(dict_[d1][d2][d3][d4][d5][d6].keys())[0]
                                                                                    dict_[d1][d2][d3][d4][d5][d6] = dict_[d1][d2][d3][d4][d5][d6][d7]
                                                                    if type(dict_[d1][d2][d3][d4][d5]).__name__ == 'dict' and list(dict_[d1][d2][d3][d4][d5].keys())[0] == keep and len(dict_[d1][d2][d3][d4][d5].keys()) == 1:
                                                                        d6 = list(dict_[d1][d2][d3][d4][d5].keys())[0]
                                                                        dict_[d1][d2][d3][d4][d5] = dict_[d1][d2][d3][d4][d5][d6]
                                                        if type(dict_[d1][d2][d3][d4]).__name__ == 'dict' and list(dict_[d1][d2][d3][d4].keys())[0] == keep and len(dict_[d1][d2][d3][d4].keys()) == 1:
                                                            d5 = list(dict_[d1][d2][d3][d4].keys())[0]
                                                            dict_[d1][d2][d3][d4] = dict_[d1][d2][d3][d4][d5]
                                            if type(dict_[d1][d2][d3]).__name__ == 'dict' and list(dict_[d1][d2][d3].keys())[0] == keep and len(dict_[d1][d2][d3].keys()) == 1:
                                                d4 = list(dict_[d1][d2][d3].keys())[0]
                                                dict_[d1][d2][d3] = dict_[d1][d2][d3][d4]
                                if type(dict_[d1][d2]).__name__ == 'dict' and list(dict_[d1][d2].keys())[0] == keep and len(dict_[d1][d2].keys()) == 1:
                                    d3 = list(dict_[d1][d2].keys())[0]
                                    dict_[d1][d2] = dict_[d1][d2][d3]
                    if type(dict_[d1]).__name__ == 'dict' and list(dict_[d1].keys())[0] == keep and len(dict_[d1].keys()) == 1:
                        d2 = list(dict_[d1].keys())[0]
                        dict_[d1] = dict_[d1][d2]
        if type(dict_).__name__ == 'dict' and list(dict_.keys())[0] == keep and len(dict_.keys()) == 1:
            d1 = list(dict_.keys())[0]
            dict_ = dict_[d1]         


yaml2json('sde/fsd/races.yaml', to_dir='json/',chunk=2, lang='en')
