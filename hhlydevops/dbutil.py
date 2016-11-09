#!/usr/bin/env python
#coding=utf-8
from DBUtils.PooledDB import PooledDB 
import MySQLdb as mysql
from utils import util                                                                                        
import traceback
import config
import sys


class DB():
    def __init__(self):
        self.host = config.db_host
        self.name = config.db_name
        self.user = config.db_user
        self.passwd = config.db_passwd
        self.pool = PooledDB(mysql, mincached=4, maxcached=10, host=self.host,db=self.name,user=self.user,passwd=self.passwd,setsession=['SET AUTOCOMMIT = 1'],charset="utf8")

    def connect_db(self):
        self.db = self.pool.connection()
        self.cur = self.db.cursor()

    def close_db(self):
        self.cur.close()
        self.db.close()

    def execute(self, sql):
        self.connect_db()
        return self.cur.execute(sql)
    
    def get_list(self,table,fields,where=None):
        if isinstance(where, dict) and where:
            conditions = []
            for k,v in where.items():
                if isinstance(v, list):
                    conditions.append("%s IN (%s)" % (k, ','.join(v)))
                elif isinstance(v, str) or isinstance(v, unicode):
                    conditions.append("%s='%s'" % (k, v)) 
                elif isinstance(v, int):
                    conditions.append("%s=%s" % (k, v))
            sql = "select %s from %s where %s" % (",".join(fields),table,' AND '.join(conditions))
        elif not where:
            sql = "SELECT %s FROM %s" % (','.join(fields), table)
        try: 
            util.WriteLog('db').info("sql: %s" % sql)
            self.execute(sql)
            result = self.cur.fetchall()
            if result:
                result = [dict((k,row[i]) for i, k in enumerate(fields)) for row in result]
            else:
                result = {}
            return result;
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db() 

    def get_one(self,table,fields,where):
        if isinstance(where, dict) and where:
            conditions = []
            for k,v in where.items():
                conditions.append("%s='%s'" % (k, v))
        sql = "select %s from %s where %s" % (",".join(fields),table,' AND '.join(conditions))
        try:
            self.execute(sql)
            result = self.cur.fetchone()
            if result:
                result = dict((k, result[i])for i, k in enumerate(fields))
            else:
                result = {}
            return result
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()


    def update(self,table,fields):
        data = ",".join(["%s='%s'"%(k,v) for k,v in fields.items()])
        sql = "update %s set %s where id=%s " % (table,data,fields["id"])
        try:
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    def create(self,table,data):
        fields,values = [],[]
        for k, v in data.items():
            fields.append(k)
            values.append("'%s'" % v)
        sql = "insert into %s (%s) values (%s)" % (table,",".join(fields),",".join(values))
        try:
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    def delete(self,table,where):
        if isinstance(where, dict) and where:
            conditions = []
            for k,v in where.items():
                conditions.append("%s='%s'" % (k, v))
        sql = "delete from %s where %s" % (table,' AND '.join(conditions))
        try:
            sql = "select %s from %s"% (",".join(fields),table)
            util.WriteLog('db').info("sql: %s" % sql)
            self.execute(sql)
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()


    def check(self,table,fields,where):
        if isinstance(where, dict) and where:
            conditions = []
            for k,v in where.items():
                conditions.append("%s='%s'" % (k, v))
        sql = "select %s from %s where %s" % (','.join(fields),table,' AND '.join(conditions))
        try:
            self.execute(sql)
            result = self.cur.fetchone()
            if result:
                result = dict((k, result[i]) for i, k in enumerate(fields))
            else:
                result = ""
            return result
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()
