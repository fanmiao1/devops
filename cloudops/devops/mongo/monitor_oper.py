# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/13
@  author  : Xieyz
@  software: PyCharm
"""
import datetime

from mongo.operation import Operating


class MonGoOperation(object):

    def __init__(self):
        self.client = Operating(db="jiankong", collection="jilu")

    def write(self, write_value):
        my_value = write_value
        my_value['datetime'] = datetime.datetime.strptime(str(write_value['datetime']), "%Y-%m-%d %H:%M:%S")+\
                               datetime.timedelta(hours=-8)
        self.client.insert(my_value)

    def get(self, server_id, datetime_range=""):
        if datetime_range:
            start_datetime = datetime.datetime.strptime(datetime_range.split(" ~ ")[0], "%Y-%m-%d %H:%M") + \
                             datetime.timedelta(hours=-8)
            end_datetime = datetime.datetime.strptime(datetime_range.split(" ~ ")[1], "%Y-%m-%d %H:%M") + \
                           datetime.timedelta(hours=-8)
            result = self.client.find(
                {"$and": [
                     {
                         "server_id": server_id
                     },
                     {
                         "datetime": {"$gte": start_datetime, "$lt": end_datetime}
                     },
                ]}
            )
        else:
            result, count = self.client.find({"server_id": server_id})
        return result

    def get_one(self, server_id):
        result = self.client.find_one({"server_id": server_id})
        return result
