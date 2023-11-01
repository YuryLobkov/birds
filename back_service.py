from flask import Flask
from flask import request
import json
app = Flask(__name__)


def camera_on_input():
    if hashMap.get('listener') == 'photo':
        img = hashMap.get('camera')
        print(img)


@app.route('/set_input_direct/<method>', methods=['POST'])
def set_input(method):
    func = method
    jdata = json.loads(request.data.decode("utf-8"))
    f = globals()[func]
    hashMap.d = jdata['hashmap']
    f()
    jdata['hashmap'] = hashMap.export()
    jdata['stop'] = False
    jdata['ErrorMessage'] = ""
    jdata['Rows'] = []

    return json.dumps(jdata)


class hashMap:
    d = {}

    @staticmethod
    def put(key, val):
        hashMap.d[key] = val

    @staticmethod
    def get(key):
        return hashMap.d.get(key)

    @staticmethod
    def remove(key):
        if key in hashMap.d:
            hashMap.d.pop(key)

    @staticmethod
    def containsKey(key):
        return key in hashMap.d

    @staticmethod
    def export():
        ex_hashMap = []
        for key in hashMap.d.keys():
            ex_hashMap.append({"key": key, "value": hashMap.d[key]})
        return ex_hashMap


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=2075, debug=True)
