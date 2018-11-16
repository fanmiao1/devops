from django.conf import settings
from .aes_pycryto import Prpcrypt
import sqlparse
import MySQLdb


"""
Author: qingyw
Date: 2018/03/22
@note: Inception Class
functions: sql_review
:return:sreview result
"""


class InceptionDao(object):

    def __init__(self):
        try:
            # inception remote backup server settings #
            # self.inception_host = getattr(settings, 'INCEPTION_HOST')
            # self.inception_port = getattr(settings, 'INCEPTION_PORT')
            # self.inception_user = getattr(settings, 'INCEPTION_USER')
            # self.inception_password = getattr(settings, 'INCEPTION_PASSWORD')

            # inception connect setting #
            self.inception_host = getattr(settings, 'INCEPTION_HOST')
            self.inception_port = getattr(settings, 'INCEPTION_PORT')
            # self.inception_user = getattr(settings, 'INCEPTION_USER')
            # self.inception_password = getattr(settings, 'INCEPTION_PASSWORD')

            self.prpCryptor = Prpcrypt()

        except AttributeError as a:
            print("Error: %s" % a)
        except ValueError as v:
            print("Error: %s" % v)

    def _fetchall(self, sql, paramHost, paramPort, paramUser, paramPasswd, paramDb):
        """
        封装mysql连接和获取结果集方法
        """
        cur = None
        conn = None
        is_pass = True
        try:
            conn = MySQLdb.connect(host=paramHost, user=paramUser, passwd=paramPasswd, db=paramDb, port=paramPort, charset='utf8')
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(sql)
            result = cur.fetchall()
            if result:
                for row in result:
                    if row['errlevel'] == 2:
                        is_pass = False
                        break
        except Exception as e:
            is_pass = False
            print(str(e))
            return is_pass, str(e)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
        return is_pass, result

    def mysql_parse(self, sql, paramHost, paramPort, paramUser, paramPasswd, paramDb):
        result_key = []
        result_value = []
        conn = MySQLdb.connect(host=paramHost, user=paramUser, passwd=paramPasswd, db=paramDb, port=paramPort,
                               charset='utf8')
        cursor = conn.cursor()
        list_sql = sqlparse.split(sql)
        for row in list_sql:
            try:
                cursor.execute('EXPLAIN ' + row)
            except Exception as e:
                result_key.append(row)
                result_value.append(str(e))
        if result_key:
            return False, dict(zip(result_key, result_value))
        else:
            return True, 'ok'

    def sql_review(self, execute_sql, db_host, db_port, db_user, db_password):

        # 工单审核使用
        sql = """/*--user=%s;--password=%s;--host=%s;--enable-check=1;--port=%s;*/""" % (
            db_user, db_password, db_host, db_port) \
              + """ inception_magic_start;""" \
              + execute_sql.replace('\n', ' ').replace('\r', '') + \
              """inception_magic_commit;"""
        incept_status, incept_result = self._fetchall(sql, self.inception_host, self.inception_port, '', '', '')
        explain_status, explain_result = self.mysql_parse(execute_sql.replace('\n', ' ').replace('\r', ''), db_host,
                                                          db_port, db_user, db_password, '')
        if incept_status and explain_status:
            return True, incept_result, 'incept'
        elif incept_status and not explain_status:
            return True, incept_result, 'incept'
        elif explain_status and not incept_status:
            return True, explain_result, 'explain'
        elif not incept_status and not explain_status:
            return False, incept_result, 'incept'
