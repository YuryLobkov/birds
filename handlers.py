import json

def birds_on_create(hashMap, _files=None, _data=None):
    if hashMap.get('listener') == 'add_bird':
        hashMap.put('ShowScreen', 'BirdAdd')
    return hashMap


def birds_on_start(hashMap, _files=None, _data=None):
    hashMap.put('SQLQuery',json.dumps({"query":"SELECT * FROM Birds","params":""})) # not executing?
    return hashMap

def birds_after_start(hashMap, _files=None, _data=None):
    return hashMap


def birds_on_add(hashMap, _files=None, _data=None):
    if hashMap.get('listener') == 'btn_save':
        hashMap.put("SQLConnectDatabase","")
        hashMap.put('SQLExec', json.dumps({"query":f"INSERT INTO Birds (name, color) VALUES ({hashMap.get('bird_name')}, {hashMap.get('feather_color')})","params":""}))    
        hashMap.put('ShowScreen', 'BirdsList')
    return hashMap

def birds_add_on_start(hashMap, _files=None, _data=None):
    return hashMap

def init_bd_on_start(hashMap,_files=None,_data=None):
    hashMap.put("SQLConnectDatabase","")
    hashMap.put("SQLExec",json.dumps({"query":"create table IF NOT EXISTS Birds(id integer primary key autoincrement, name text, color text)","params":""}))
    return hashMap