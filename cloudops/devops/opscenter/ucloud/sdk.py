# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
from urllib import parse
import hashlib
import requests
import http.client
import operator
import json


project_id = ''  # 项目ID 请在Dashbord 上获取
base_url = "https://api.ucloud.cn"


class UCLOUDException(Exception):
    def __str__(self):
        return "Error"


def _verfy_ac(private_key, params):
    params_data = ""
    for key, value in params:
        params_data = params_data + str(key) + str(value)
    params_data = params_data+private_key
    
    hash_new = hashlib.sha1()
    hash_new.update(params_data.encode("utf8"))
    hash_value = hash_new.hexdigest()
    return hash_value


class UConnection(object):
    def __init__(self, base_url):
        self.base_url = base_url
        o = parse.urlsplit(base_url)
        if o.scheme == 'https':
            self.conn = http.client.HTTPSConnection(o.netloc)
        else:
            self.conn = http.client.HTTPConnection(o.netloc)

    def __del__(self):
        self.conn.close()

    def get(self, resouse, params):
        url = "%s%s" % (self.base_url, resouse)
        response = requests.get(url=url, params=params)
        return response

    def post(self, uri, params):
        # print("%s%s %s" % (self.base_url, uri, params))
        headers = {"Content-Type": "application/json"}
        self.conn.request("POST", uri, json.JSONEncoder().encode(params), headers)
        response = json.loads(self.conn.getresponse().read())
        return response


class UcloudApiClient(object):
    # 添加 设置 数据中心和  zone 参数
    def __init__(self, base_url, public_key, private_key):
        self.g_params = {}
        self.g_params['PublicKey'] = public_key
        self.private_key = private_key
        self.conn = UConnection(base_url)

    def get(self, uri, params):
        _params = dict(self.g_params, **params)
        sort_params = sorted(_params.items(), key=operator.itemgetter(0))
        if project_id:
            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, sort_params)
        return self.conn.get(uri, _params)

    def post(self, uri, params):
        _params = dict(self.g_params, **params)

        if project_id :
            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, _params)
        return self.conn.post(uri, _params)
