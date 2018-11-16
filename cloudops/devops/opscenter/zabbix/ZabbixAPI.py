# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
import json
import requests

class ZabbixAPI:
    def __init__(self):
        # cf = ConfigParser.ConfigParser()
        # cf.read("EWP_OMS/config.ini")
        self.url = "http://zabbix.aukey.com/zabbix/api_jsonrpc.php"
        self.username= "Admin"
        self.password = "aukeys@2016.com"
        self.header = {"Content-Type": "application/json-rpc"}

    def getToken(self):
        # 获取Token并返回字符Token字符串

        data = {"jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.username,
                    "password": self.password
                },
                "id": 1,
                "auth": None
                }
        token = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(token.content)["result"]

    #主机列表
    def HostGet(self,hostid=None,hostip=None):
        data = {
            "jsonrpc":"2.0",
            "method":"host.get",
            "params":{
                "output":"extend",
                "selectGroups": "extend",
                "selectParentTemplates": ["templateid","name"],
                "selectInterfaces": ["interfaceid","ip"],
                "selectInventory": ["os"],
                "selectItems":["itemid","name"],
                "selectGraphs":["graphid","name"],
                "selectApplications":["applicationid","name"],
                "selectTriggers":["triggerid","name"],
                "selectScreens":["screenid","name"]
            },
            "auth": self.getToken(),
            "id":1,
        }
        if hostid:
            data["params"]={
                "output": "extend",
                "hostids": hostid,
                "sortfield": "name"
            }
        hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(hosts.content)["result"]
    #主机列表
    def HostCreate(self,hostname,hostip,groupid=None,templateid=None):
        data = {
            "jsonrpc":"2.0",
            "method":"host.create",
            "params": {
                "host": hostname,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": groupid
                    }
                ],
                "templates": [
                    {
                        "templateid": templateid
                    }
                ]
            },
            "auth": self.getToken(),
            "id":1,
        }
        hostcreate = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(hostcreate.content)["result"]

    #主机组列表
    def HostGroupGet(self,hostid=None,itemid=None):
        data = {
            "jsonrpc":"2.0",
            "method":"hostgroup.get",
            "params":{
                "output": "extend",
                "hostids": hostid,
                "itemids": itemid,
                "sortfield": "name"
            },
            "auth": self.getToken(),
            "id":1,
        }
        hostgroup = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(hostgroup.content)["result"]
    #监控项列表
    def ItemGet(self,hostid=None,itemid=None):
        data = {
            "jsonrpc":"2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "itemids": itemid,
                "sortfield": "name"
            },
            "auth": self.getToken(),
            "id":1,
        }
        item = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(item.content)["result"]

    #模板列表
    def TemplateGet(self, hostid=None,templateid=None):
        data = {
            "jsonrpc":"2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "templateids": templateid,
                "sortfield": "name"
            },
            "auth": self.getToken(),
            "id":1,
        }
        template = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(template.content)["result"]

    #图像列表
    def GraphGet(self,hostid=None,graphid=None):
        data = {
            "jsonrpc":"2.0",
            "method": "graph.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "graphids": graphid,
                "sortfield": "name"
            },
            "auth": self.getToken(),
            "id":1,
        }
        graph = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(graph.content)["result"]
    #历史数据
    def History(self,itemid,data_type):
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": data_type,
                "itemids": itemid,
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": 30
            },
            "auth": self.getToken(),
            "id": 2
        }
        history = hosts = requests.post(url=self.url, headers=self.header, data=json.dumps(data))
        return json.loads(history.content)["result"]