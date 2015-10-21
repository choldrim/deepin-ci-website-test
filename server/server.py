#!/usr/bin/env python3

import json

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/v1/hosts", methods=["GET"])
def get_host():
    rv_id = request.form.get("rv_id")
    rv_id = rv_id.strip()
    print("review id:", rv_id)

    if not rv_id:
        ret_data = {}
        ret_data["result"] = False
        ret_data["message"] = "params not correct"
        return json.dumps(ret_data)

    data = {}
    with open("hosts.json") as fp:
        _data = fp.read()
        if len(_data.strip()):
            data = json.loads(_data)

    ret_data = {"rv_id":"", "host":""}
    ret_data["rv_id"] = rv_id
    ret_data["host"] = data.get(rv_id, "")
    return json.dumps(ret_data)


@app.route("/v1/hosts", methods=["POST"])
def set_host():
    rv_id = request.form.get("rv_id")
    host = request.form.get("host")

    ret_data = {"result":False}

    if not rv_id and not host:
        ret_data["message"] = "params not correct"
        return json.dumps(ret_data)

    data = {}
    with open("hosts.json") as fp:
        _data = fp.read()
        if len(_data.strip()):
            data = json.loads(_data)

        data[rv_id] = host

    with open("hosts.json", "w") as fp:
        json.dump(data, fp)

    ret_data["result"] = True
    return json.dumps(ret_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010, debug=True)

