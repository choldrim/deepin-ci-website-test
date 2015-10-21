#!/usr/bin/env python3

import json

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/v1/hosts", methods=["GET"])
def get_host():
    num = request.form.get("change_number")
    num = num.strip()
    print("review id:", num)

    if not num:
        ret_data = {}
        ret_data["result"] = False
        ret_data["message"] = "params not correct"
        return json.dumps(ret_data)

    data = {}
    with open("hosts.json") as fp:
        _data = fp.read()
        if len(_data.strip()):
            data = json.loads(_data)

    ret_data = {"change_number":"", "host":""}
    ret_data["change_number"] = num
    ret_data["host"] = data.get(num, {}).get("host", "")
    ret_data["domain"] = data.get(num, {}).get("domain", "")
    return json.dumps(ret_data)


@app.route("/v1/hosts", methods=["POST"])
def set_host():
    num = request.form.get("change_number")
    host = request.form.get("host")
    domain = request.form.get("domain")

    ret_data = {"result":False}

    if not num or not host or not domain:
        ret_data["message"] = "params error"
        return json.dumps(ret_data)

    data = {}
    with open("hosts.json") as fp:
        _data = fp.read()
        if len(_data.strip()):
            data = json.loads(_data)

    # handle data
    data[num] = {"host": host, "domain": domain}

    with open("hosts.json", "w") as fp:
        json.dump(data, fp)

    ret_data["result"] = True
    return json.dumps(ret_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010, debug=True)

