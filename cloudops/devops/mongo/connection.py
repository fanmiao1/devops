# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/13
@  author  : XieYZ
@  software: PyCharm
"""
from devops.settings import MONGO_URL, MONGO_PORT
from pymongo import MongoClient


def conn():
    client = MongoClient(MONGO_URL, MONGO_PORT)
    close(client)
    return client


def close(client):
    client.close()
