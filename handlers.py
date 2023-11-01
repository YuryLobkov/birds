import json
from pony.orm.core import db_session

from pony.orm import Database, Required, select, delete

db = Database()
db.bind(
    provider="sqlite",
    filename="//data/data/ru.travelfood.simple_ui/databases/SimpleWMS",
)


class Birds(db.Entity):
    name = Required(str)
    color = Required(str)

@db_session
def delete_all_birds():
    delete(b for b in Birds)

db.generate_mapping(create_tables=False)


@db_session
def write_bird(name, color):
    b1 = Birds(name=name, color=color)

@db_session
def read_birds():
    birds_list = select(b for b in Birds)[:]
    birds = json.dumps([b.to_dict() for b in birds_list], ensure_ascii=False)
    return birds

def birds_on_create(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "add_bird":
        hashMap.put("ShowScreen", "BirdAdd")
    return hashMap


def birds_on_start(hashMap, _files=None, _data=None):
    hashMap.put('temp_var', read_birds())
    return hashMap


def birds_after_start(hashMap, _files=None, _data=None):
    # delete_all_birds()
    return hashMap


def birds_on_add(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "btn_save":
        write_bird(hashMap.get("bird_name"), color=hashMap.get("feather_color"))
        hashMap.put("ShowScreen", "BirdsList")
    return hashMap


def birds_add_on_start(hashMap, _files=None, _data=None):
    return hashMap


def init_bd_on_start(hashMap, _files=None, _data=None):
    hashMap.put("SQLConnectDatabase", "")
    hashMap.put(
        "SQLExec",
        json.dumps(
            {
                "query": "create table IF NOT EXISTS Birds(id integer primary key autoincrement, name text, color text)",
                "params": "",
            }
        ),
    )
    return hashMap
