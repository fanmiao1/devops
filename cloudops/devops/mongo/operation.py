# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/13
@  author  : XieYZ
@  software: PyCharm
"""
import pymongo
from .connection import conn


class Operating(object):

    def __init__(self, db, collection):
        client = conn()
        conn_db = client[db]
        self.my_set = conn_db[collection]

    def insert(self, data):
        self.my_set.insert(data)

    def delete(self, index=None):
        if index:
            self.my_set.remove(index)
        else:
            self.my_set.remove()

    def update(self, index, data):
        self.my_set.update(index, {"$set": data})

    def find(self, index=None, sort=None, sort_type=None):
        if index:
            pipeline = [
                {"$match": index}
            ]
            result = self.my_set.find(index)
        else:
            result = self.my_set.find()
        if sort:
            if sort_type == 'asc':
                result = result.sort(sort, pymongo.ASCENDING)
            elif sort_type == 'desc':
                result = result.sort(sort, pymongo.DESCENDING)
            else:
                result = result.sort(sort)
        return result

    def find_one(self, index=None):
        if index:
            result = self.my_set.find_one(index)
        else:
            result = self.my_set.find_one()
        return result
