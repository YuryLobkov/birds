import json
from os import name
from pony.orm.core import db_session
from pony.orm import (
    Database,
    Required,
    Optional,
    PrimaryKey,
    Set,
    select,
    delete,
    count,
)

db = Database()
db.bind(
    provider="sqlite",
    filename="//data/data/ru.travelfood.simple_ui/databases/SimpleWMS",
    create_db=True,
)


class Birds(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    color = Required(str)
    image = Optional(str)
    seen = Set("SeenBirds")


class SeenBirds(db.Entity):
    id = PrimaryKey(int, auto=True)
    datetime_seen = Required(str, sql_default="CURRENT_TIMESTAMP")
    bird_id = Optional(Birds)


@db_session
def delete_all_birds():
    delete(b for b in Birds)


db.generate_mapping(create_tables=True)


@db_session
def write_bird(name, color, image):
    b1 = Birds(name=name, color=color, image=image)


@db_session
def read_birds():
    birds_list = select(b for b in Birds)[:]
    birds = [b.to_dict() for b in birds_list]
    return birds


def birds_on_create(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "add_bird":
        hashMap.put("ShowScreen", "BirdAdd")
    if hashMap.get("listener") == "LayoutAction":
        seen_bird_id = json.loads(hashMap.get("card_data"))["key"]
        seen_bird_name = json.loads(hashMap.get("card_data"))["name"][6:]
        hashMap.put("toast", "Bird " + seen_bird_name + " saved as seen")
        hashMap.put("_seen_bird_id", str(seen_bird_id))
    return hashMap


def birds_on_start(hashMap, _files=None, _data=None):
    hashMap.put("getfiles", "")
    j_birds = read_birds()
    j = {
        "customcards": {
            "options": {"search_enabled": True, "save_position": True},
            "layout": {
                "type": "LinearLayout",
                "orientation": "vertical",
                "height": "match_parent",
                "width": "match_parent",
                "weight": "0",
                "Elements": [
                    {
                        "type": "LinearLayout",
                        "orientation": "horizontal",
                        "height": "wrap_content",
                        "width": "match_parent",
                        "weight": "0",
                        "Elements": [
                            {
                                "type": "Picture",
                                "show_by_condition": "",
                                "Value": "@pic1",
                                "NoRefresh": False,
                                "document_type": "",
                                "mask": "",
                                "Variable": "",
                                "BackgroundColor": "",
                                "width": "200",
                                "height": "100",
                                "weight": 1,
                            },
                            {
                                "type": "LinearLayout",
                                "orientation": "vertical",
                                "height": "wrap_content",
                                "width": "match_parent",
                                "weight": "1",
                                "Elements": [
                                    {
                                        "type": "TextView",
                                        "show_by_condition": "",
                                        "Value": "@name",
                                        "NoRefresh": False,
                                        "document_type": "",
                                        "mask": "",
                                        "Variable": "",
                                        "TextSize": "16",
                                        "TextColor": "#34c3eb",
                                        "TextBold": True,
                                        "TextItalic": False,
                                        "vertical_gravity": "center",
                                    },
                                    {
                                        "type": "TextView",
                                        "show_by_condition": "",
                                        "Value": "@color",
                                        "NoRefresh": False,
                                        "document_type": "",
                                        "mask": "",
                                        "Variable": "",
                                        "TextSize": "16",
                                        "TextColor": "#07a663",
                                        "TextBold": True,
                                        "TextItalic": False,
                                        "gravity_horizontal": "center",
                                    },
                                ],
                            },
                            {
                                "type": "LinearLayout",
                                "orientation": "horizontal",
                                "height": "match_parent",
                                "width": "wrap_content",
                                "weight": "5",
                                "Elements": [
                                    {
                                        "type": "Button",
                                        "height": "match_parent",
                                        "width": "match_parent",
                                        "weight": "0",
                                        "Value": "#f06e",
                                        "Variable": "@key",
                                    }
                                ],
                            },
                        ],
                    },
                ],
            },
        }
    }

    j["customcards"]["cardsdata"] = []
    for bird in j_birds:
        c = {
            "key": bird["id"],
            "name": "Name: " + bird["name"],
            "color": "Feathers color: " + bird["color"],
            "pic1": "~"
            + next((d["path"] for d in _files if d["id"] == bird["image"]), None),
        }
        j["customcards"]["cardsdata"].append(c)

    hashMap.put("cards", json.dumps(j, ensure_ascii=False).encode("utf8").decode())

    return hashMap


def birds_after_start(hashMap, _files=None, _data=None):
    # delete_all_birds() # only for debug, to clean table
    # db.drop_table("Birds")# only for debug
    return hashMap


def birds_on_add(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "btn_save":
        write_bird(
            hashMap.get("bird_name"),
            color=hashMap.get("feather_color"),
            image=hashMap.get("img"),
        )
        # cleaning hashmap after db write to clean form for next new bird
        hashMap.put("bird_name", "")
        hashMap.put("feather_color", "")
        hashMap.put("new_image", "")
        hashMap.put("camera", None)
        hashMap.put("gallery", None)
        hashMap.put("img", "")
        hashMap.put("ShowScreen", "BirdsList")
    return hashMap


def birds_add_on_start(hashMap, _files=None, _data=None):
    # Check if one of images has been provided
    if hashMap.get("camera") == None and hashMap.get("gallery") == None:
        hashMap.put("no_image", "No image")
    # case gallery (remove 'no image' text, write img var, put image to form and clean input variables)
    elif hashMap.containsKey("gallery") and hashMap.get("gallery") != None:
        hashMap.put("no_image", "")
        hashMap.put("img", hashMap.get("gallery"))
        hashMap.put(
            "new_image",
            "~"
            + next(
                (d["path"] for d in _files if d["id"] == hashMap.get("gallery")), ""
            ),
        )
        hashMap.put("gallery", None)
        hashMap.put("camera", None)
    # case camera, same as above
    elif hashMap.containsKey("camera") and hashMap.get("camera") != None:
        hashMap.put("no_image", "")
        hashMap.put("img", hashMap.get("camera"))
        hashMap.put(
            "new_image",
            "~"
            + next((d["path"] for d in _files if d["id"] == hashMap.get("camera")), ""),
        )
        hashMap.put("camera", None)
        hashMap.put("gallery", None)
    return hashMap


def init_bd_on_start(hashMap, _files=None, _data=None):
    hashMap.put("SQLConnectDatabase", "")
    hashMap.put(
        "SQLExec",
        json.dumps(
            {
                "query": "create table IF NOT EXISTS Birds(id integer primary key autoincrement, name text, color text, image text)",
                "params": "",
            }
        ),
    )
    return hashMap


def camera_on_start(hashMap, _files=None, _data=None):
    hashMap.put("mm_local", "")
    hashMap.put("mm_size", "30")
    hashMap.put("mm_compression", "30")
    return hashMap


def camera_on_input(hashMap, _files=None, _data=None):
    return hashMap


###----------------------seen birds handlers----------------


@db_session
def write_seen_birds(id):
    bs1 = SeenBirds(bird_id=id)


@db_session
def read_seen_birds():
    seen_birds_query = select(
        (
            (
                sb.bird_id.image,
                sb.bird_id.name,
                sb.datetime_seen,
                count(
                    sb2
                    for sb2 in SeenBirds
                    if sb2.bird_id == sb.bird_id
                    and sb2.datetime_seen <= sb.datetime_seen
                ),
            )
            for sb in SeenBirds
        )
    )[:]

    # Keys for entities of query
    keys = ["image", "name", "datetime_seen", "times_seen"]
    # Creating a list of dictionaries from the list of tuples
    seen_birds_list = [{keys[i]: item for i, item in enumerate(t)} for t in seen_birds_query]

    return seen_birds_list


def seen_birds_on_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "check":
        hashMap.put("toast", hashMap.get("_seen_bird_id"))
    if hashMap.get("listener") == "write_seen_bird_btn":
        write_seen_birds(hashMap.get("_seen_bird_id"))
        hashMap.put("_seen_bird_id", None)
    return hashMap


def seen_birds_on_start(hashMap, _files=None, _data=None):
    hashMap.put("getfiles", "")
    j_birds_seen = read_seen_birds()
    j = {
        "customcards": {
            "options": {"search_enabled": True, "save_position": True},
            "layout": {
                "type": "LinearLayout",
                "orientation": "vertical",
                "height": "match_parent",
                "width": "match_parent",
                "weight": "0",
                "Elements": [
                    {
                        "type": "LinearLayout",
                        "orientation": "horizontal",
                        "height": "wrap_content",
                        "width": "match_parent",
                        "weight": "0",
                        "Elements": [
                            {
                                "type": "Picture",
                                "show_by_condition": "",
                                "Value": "@pic1",
                                "NoRefresh": False,
                                "document_type": "",
                                "mask": "",
                                "Variable": "",
                                "BackgroundColor": "",
                                "width": "wrap_content",
                                "height": "match_parent",
                                "weight": 0,
                            },
                            {
                                "type": "LinearLayout",
                                "orientation": "vertical",
                                "height": "wrap_content",
                                "width": "match_parent",
                                "weight": "0",
                                "Elements": [
                                    {
                                        "type": "TextView",
                                        "show_by_condition": "",
                                        "Value": "@date_time",
                                        "NoRefresh": False,
                                        "document_type": "",
                                        "mask": "",
                                        "Variable": "",
                                        "TextSize": "16",
                                        "TextColor": "#34c3eb",
                                        "TextBold": True,
                                        "TextItalic": False,
                                        "vertical_gravity": "center",
                                    },
                                    {
                                        "type": "TextView",
                                        "show_by_condition": "",
                                        "Value": "@name",
                                        "NoRefresh": False,
                                        "document_type": "",
                                        "mask": "",
                                        "Variable": "",
                                        "TextSize": "16",
                                        "TextColor": "#07a663",
                                        "TextBold": True,
                                        "TextItalic": False,
                                        "gravity_horizontal": "center",
                                    },
                                    {
                                        "type": "TextView",
                                        "show_by_condition": "",
                                        "Value": "@seen_times",
                                        "NoRefresh": False,
                                        "document_type": "",
                                        "mask": "",
                                        "Variable": "",
                                        "TextSize": "16",
                                        "TextColor": "#07a663",
                                        "TextBold": True,
                                        "TextItalic": True,
                                        "gravity_horizontal": "center",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        }
    }

    j["customcards"]["cardsdata"] = []
    for bird_seen in j_birds_seen:
        c = {
            'pic1': '~'+ next((d['path'] for d in _files if d['id'] == bird_seen['image']), None),
            'name': bird_seen['name'],
            'date_time': bird_seen['datetime_seen'],
            'seen_times': bird_seen['times_seen']
        }
        j["customcards"]["cardsdata"].append(c)

    hashMap.put("cards", json.dumps(j, ensure_ascii=False).encode("utf8").decode())

    return hashMap
