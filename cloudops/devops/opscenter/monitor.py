# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/13
@  author  : Xieyz
@  software: PyCharm
"""
from devops.task_error import TaskError
import redis


class Monitor(object):

    def __init__(self):
        self.REDIS_HOST = 'localhost'
        self.REDIS_POST = 6379
        self.db = 0
        self.conn_redis = redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_POST,
                                            db=self.db, decode_responses=True)

    def server_monitor(self, write_value):
        # 写入Redis的Key
        try:
            # 写入数据
            key = write_value['server_id']
            self.conn_redis.rpush(key, write_value)
        except TaskError as err:
            code = 0
            result = str(err)
        else:
            # 移出最后一个值
            len_key = self.conn_redis.llen(key)
            if len_key > 24 * 12:
                self.conn_redis.ltrim(key, 0, len_key - 2)
            code = 1
            result = 'success'
        finally:
            res = {'code': code, 'result': result}
            return (res)

    def get_redis(self, key):
        # 获取所有监控的信息
        res = self.conn_redis.lrange(key, 0, self.conn_redis.llen(key) - 1)
        return res
