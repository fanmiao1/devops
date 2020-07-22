import ipaddress
import pymssql
import mysql.connector as mc
import MySQLdb as mdb
from MySQLdb.constants import FIELD_TYPE
import sqlparse
import time
import math
from django.utils import timezone
from .aes_pycryto import Prpcrypt
prpCryptor = Prpcrypt()


def is_invalid_ipv4_address(address):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        ipaddress.ip_address(address)
    except Exception as e:
        print(e)
        return True
    return False


def is_invalid_conn(server_ip, instance_username, instance_password, instance_port, instance_type):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    instance_role, subordinate_info = '', []

    try:
        if instance_type == 'MySQL':
            try:
                conn = mc.connect(host=server_ip, user=instance_username,
                                       password=instance_password,
                                       port=instance_port, charset='utf8')
            except Exception as e:
                print(e)
                return True, instance_role, subordinate_info
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SHOW SLAVE STATUS")
                result = cursor.fetchone()
                if result is not None:
                    instance_role = 'Subordinate'
                    subordinate_info.append(result['Main_Host'])
                    subordinate_info.append(result['Main_Port'])
                    if result['SQL_Delay']:
                        subordinate_info.append(1)
                    else:
                        subordinate_info.append(0)
                    subordinate_info.append(result['SQL_Delay'])
                else:
                    instance_role = 'Main'

                conn.close()
                return False, instance_role, subordinate_info
            except Exception as e:
                return False, instance_role, subordinate_info
        elif instance_type == 'SQL SERVER':
            conn = pymssql.connect(host=server_ip, user=instance_username,
                                   password=instance_password,
                                   port=instance_port, charset='utf8')
            conn.close()

            return False, instance_role, subordinate_info

    except Exception as e:
        print(e)
        return True, instance_role, subordinate_info


def exec_sqlalert(server_ip, instance_username, instance_password, instance_port, instance_type, exec_sql):
    exec_result = []
    try:
        if instance_type == 'MySQL':
            try:
                conn = mc.connect(host=server_ip, user=instance_username, password=instance_password,
                                  port=instance_port, charset='utf8')
                conn.ping(True)
                cursor = conn.cursor()

                for result in cursor.execute(exec_sql, multi=True):
                    try:
                        if result.with_rows:
                            statement_result = result.fetchall()
                            if len(statement_result):
                                exec_result.append("总数量:{} 查询结果:{}".format(
                                   len(statement_result), str(statement_result)))
                                return True, "\n".join(exec_result)
                    except Exception as e:
                        exec_result.append(str(e))
                        conn.rollback()
                        conn.close()
                        return False, "\n".join(exec_result)
                conn.commit()
                conn.close()
                return False, "\n".join(exec_result)
            except Exception as e:
                exec_result.append(str(e))
                return False, "\n".join(exec_result)

        elif str(instance_type) == 'SQL SERVER':
            try:
                conn = pymssql.connect(host=server_ip, user=instance_username,
                                       password=instance_password,
                                       port=instance_port, charset='utf8')
                # print(conn)
                cursor = conn.cursor()
                list_sql = sqlparse.split(exec_sql)
                # print(list_sql, type(list_sql))
                for sql in list_sql:
                    try:
                        cursor.execute(sql)
                        # result = cursor.fetchall()
                        # if result:
                        #     exec_result.append("'{}' 查询结果:{}".format(
                        #         sql, str(result)))
                        # else:
                        if cursor.rowcount:
                            exec_result.append("总数量:{} 查询结果:{}".format(
                                cursor.rowcount, str(cursor.fetchall())))
                            return True, "\n".join(exec_result)
                    except Exception as e:
                        exec_result.append(str(e))
                        conn.rollback()
                        conn.close()
                        return False, "\n".join(exec_result)
                conn.commit()
                conn.close()
                return False, "\n".join(exec_result)
            except Exception as e:
                return False, exec_result.append(str(e))

    except Exception as e:
        exec_result.append(str(e))
        return False, "\n".join(exec_result)


def get_privs(server_ip, instance_username, instance_password, instance_port, instance_type, sql):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''

    response_data = {'rows': []}

    try:
        if instance_type == 'MySQL':
            conn = mc.connect(host=server_ip, user=instance_username,
                                       password=instance_password,
                                       port=instance_port, charset='utf8')
            cursor = conn.cursor(dictionary=True)
            inner_cursor = conn.cursor()
            # sql = """select concat("SHOW GRANTS FOR '", user, "'@'", host,"'") as 'grant_sql' from mysql.user ;"""
            cursor.execute(sql)
            for result in cursor.fetchall():
                grant_sql = result['grant_sql'].decode()
                inner_cursor.execute(grant_sql)
                privs = []
                for inner_result in inner_cursor.fetchall():
                    privs.append('{} <br/> '.format(inner_result[0]))
                response_data['rows'].append({
                    "user": grant_sql[16:],
                    "privs": ''.join(privs),
                })
            conn.close()
            return response_data
    except Exception as e:
        print(e)
        return response_data


def get_user_privs(server_ip, instance_username, instance_password, instance_port, instance_type, sql):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''

    privs = []
    try:
        if instance_type == 'MySQL':
            conn = mc.connect(host=server_ip, user=instance_username,
                                       password=instance_password,
                                       port=instance_port, charset='utf8')
            cursor = conn.cursor()
            cursor.execute(sql)
            for result in cursor.fetchall():
                privs.append(result[0])
            return privs
    except Exception as e:
        print(e)
        return privs


def revoke_user_privs(server_ip, instance_username, instance_password, instance_port, instance_type, privs):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        if instance_type == 'MySQL':
            conn = mc.connect(host=server_ip, user=instance_username,
                              password=instance_password,
                              port=instance_port, charset='utf8')
            cursor = conn.cursor()
            for row in privs:
                sql = row.replace('GRANT', 'REVOKE', 1).replace('TO', 'FROM', 1)
                if 'WITH GRANT OPTION' in sql.upper():
                    pos = sql.upper().index('ON')
                    grant_sql = sql[:pos] + ',GRANT OPTION ' + sql[pos:]
                    cursor.execute(grant_sql.replace('WITH GRANT OPTION', ''))
                else:
                    cursor.execute(row.replace('GRANT', 'REVOKE').replace('TO', 'FROM'))
            conn.close()
            return True
    except Exception as e:
        print(e)
        return False


def delete_db_user(server_ip, instance_username, instance_password, instance_port, instance_type, user):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        if instance_type == 'MySQL':
            try:
                conn = mc.connect(host=server_ip, user=instance_username,
                                           password=instance_password,
                                           port=instance_port, charset='utf8')
                cursor = conn.cursor()
                sql = """ DROP USER %s """ % user
                cursor.execute(sql)
                conn.close()
                return True
            except Exception as e:
                print(e)
                return False
    except Exception as e:
        print(e)
        return False


def reset_db_user(server_ip, instance_username, instance_password, instance_port, instance_type, user, passwd):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        if instance_type == 'MySQL':
            try:
                conn = mc.connect(host=server_ip, user=instance_username,
                                           password=instance_password,
                                           port=instance_port, charset='utf8')
                cursor = conn.cursor()
                sql = "ALTER USER {user} IDENTIFIED BY '{passwd}' ".format(user=user, passwd=passwd)
                cursor.execute(sql)
                cursor.execute("FLUSH PRIVILEGES")
                conn.close()
                return True
            except Exception as e:
                print(e)
                return False
    except Exception as e:
        print(e)
        return False


def is_exist_user(server_ip, instance_port, instance_username, instance_password, instance_type, username, ip_segment=''):
    '''
    is_exist_user 判断新建用户是否存在于 DB 中
    '''

    if instance_type == 'MySQL':
        conn = mc.connect(host=server_ip, user=instance_username,
                          password=instance_password,
                          port=instance_port, charset='utf8')
        execute_sql = """ SELECT 1 from mysql.user WHERE user='%s' and host='%s' LIMIT 1""" % (username, ip_segment)
    elif instance_type == 'SQL SERVER':
        conn = pymssql.connect(host=server_ip, user=instance_username,
                               password=instance_password,
                               port=instance_port, charset='utf8')
        execute_sql = """ SELECT 1 FROM sys.syslogins where  name='%s'""" % (username)
    c = conn.cursor()
    c.execute(execute_sql)
    result = c.fetchall()
    conn.close()
    if len(result) > 0:
        return True
    else:
        return False


def sqlserver_parse(sql, host, port, user, password):
    conn = pymssql.connect(host=host, user=user,
                           password=password,
                           port=port, charset='utf8')
    # print(conn)
    result = ''
    cursor = conn.cursor()
    # list_sql = sql.replace('\n', '').split(';')
    cursor.execute('SET SHOWPLAN_ALL ON;')
    # for sql in list_sql:
    try:
        cursor.execute(sql)
        result = 'ok'
    except Exception as e:
        result = e.args[1].decode()
    cursor.execute('SET SHOWPLAN_ALL OFF;')
    conn.close()
    return result


def execute_sql(server_ip, instance_username, instance_password, instance_port, instance_type, exec_sql):
    exec_result = []
    try:
        if instance_type == 'MySQL':
            try:
                conn = mc.connect(host=server_ip, user=instance_username, password=instance_password,
                                  port=instance_port, charset='utf8')
                conn.ping(True)
                cursor = conn.cursor()
                for result in cursor.execute(exec_sql, multi=True):
                    try:
                        if result.with_rows:
                            exec_result.append("'{}' 查询结果:{}".format(
                                result.statement, str(result.fetchall())))
                        else:
                            exec_result.append("'{}' 受影响的行: {}".format(
                                result.statement, result.rowcount))
                    except Exception as e:
                        exec_result.append(str(e))
                        conn.rollback()
                        conn.close()
                        return False, "\n".join(exec_result)
                conn.commit()
                conn.close()
                return True, "\n".join(exec_result)
            except Exception as e:
                print('connection was closed...' + str(e))
                exec_result.append(str(e))
                return False, "\n".join(exec_result)

        elif str(instance_type) == 'SQL SERVER':
            try:
                conn = pymssql.connect(host=server_ip, user=instance_username,
                                       password=instance_password,
                                       port=instance_port, charset='utf8')
                # print(conn)
                cursor = conn.cursor()
                list_sql = sqlparse.split(exec_sql)
                # print(list_sql, type(list_sql))
                for sql in list_sql:
                    try:
                        cursor.execute(sql)
                        # result = cursor.fetchall()
                        # if result:
                        #     exec_result.append("'{}' 查询结果:{}".format(
                        #         sql, str(result)))
                        # else:
                        exec_result.append("'{}' 受影响的行: {}".format(
                            sql, cursor.rowcount if cursor.rowcount > 0 else 0))
                    except Exception as e:
                        exec_result.append(str(e))
                        conn.rollback()
                        conn.close()
                        return False, "\n".join(exec_result)
                conn.commit()
                conn.close()
                return True, "\n".join(exec_result)
            except Exception as e:
                return False, exec_result.append(str(e))

    except Exception as e:
        exec_result.append(str(e))
        return False, "\n".join(exec_result)


def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    stamp = ("".join(time_stamp.split()[0].split("-"))+"".join(time_stamp.split()[1].split(":"))).replace('.', '')
    return stamp


def migration(ori_host, ori_user, ori_pass, ori_port, ori_db, ori_tab, ori_type, tar_host, tar_user, tar_pass, tar_port, tar_db,
              is_new_db, is_data, is_view, is_routine, is_event, is_bak):
    try:
        exec_result = []
        if ori_type == 'MySQL':
            conv = mdb.converters.conversions.copy()
            conv[FIELD_TYPE.DECIMAL] = float
            conv[FIELD_TYPE.NEWDECIMAL] = float
            conv[FIELD_TYPE.TIME] = str
            conv[FIELD_TYPE.DATE] = str
            conv[FIELD_TYPE.TIMESTAMP] = str
            conv[FIELD_TYPE.DATETIME] = str
            conv[FIELD_TYPE.BIT] = bool
            conv[FIELD_TYPE.VAR_STRING] = str
            conv[FIELD_TYPE.TINY_BLOB] = str
            conv[FIELD_TYPE.MEDIUM_BLOB] = str
            conv[FIELD_TYPE.BLOB] = str
            conv[FIELD_TYPE.LONG_BLOB] = str
            conv[FIELD_TYPE.STRING] = str
            try:
                ori_conn = mdb.connect(host=ori_host, user=ori_user, passwd=ori_pass,
                                       port=ori_port, charset='utf8', conv=conv)
                tar_conn = mdb.connect(host=tar_host, user=tar_user, passwd=tar_pass,
                                       port=tar_port, charset='utf8', conv=conv)
                ori_cursor = ori_conn.cursor()
                tar_cursor = tar_conn.cursor()
                ori_cursor.execute("SET wait_timeout=28800;")
                ori_cursor.execute("SET net_read_timeout=180;")
                tar_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                # create db
                if is_new_db:
                    for db in ori_db.split(','):
                        tar_cursor.execute("CREATE DATABASE IF NOT EXISTS `{DB}`".format(DB=db))
                        exec_result.append(" {DB} database created successfully.".format(DB=db))
                # create table
                for db_tab in ori_tab.split(','):
                    db, tab = db_tab.split('.')[0], db_tab.split('.')[1]
                    ori_cursor.execute(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db}' AND table_name='{tab}' AND table_type='BASE TABLE' ".format(
                            db=db, tab=tab))
                    is_exists_ori_tab = ori_cursor.fetchall()[0][0]
                    if is_exists_ori_tab:
                        ori_cursor.execute("SHOW CREATE TABLE `{DB}`.`{tab}`".format(DB=db, tab=tab))
                        new_tab = ori_cursor.fetchall()[0][1]
                        sql = "USE `{DB}`".format(DB=db) if is_new_db else "USE `{DB}`".format(DB=tar_db)
                        tar_cursor.execute(sql)
                        if (not is_new_db) and is_bak:
                            tar_cursor.execute(
                                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db}' AND table_name='{tab}' AND table_type='BASE TABLE' ".format(db=tar_db, tab=tab))
                            is_exists_tab = tar_cursor.fetchall()[0][0]
                            if is_exists_tab:
                                bak_tab_name = tab + '_bak_' + get_time_stamp()
                                tar_cursor.execute("CREATE TABLE `{bak_tab}` LIKE `{tab}`".format(bak_tab=bak_tab_name, tab=tab))
                                tar_cursor.execute("INSERT INTO `{bak_tab}` SELECT * FROM `{tab}`".format(bak_tab=bak_tab_name, tab=tab))
                                exec_result.append("table {tab} backuped to {bak_tab} successfully.".format(tab=tab, bak_tab=bak_tab_name))
                        tar_cursor.execute("DROP TABLE IF EXISTS `{tab}`".format(tab=tab))
                        tar_cursor.execute(new_tab)
                        exec_result.append("{tab} table created successfully.".format(tab=tab))
                        # import data
                        if is_data:
                            ori_cursor.execute("SELECT COUNT(*) FROM `{DB}`.`{tab}`".format(DB=db, tab=tab))
                            row_count = ori_cursor.fetchall()[0][0]
                            exec_result.append("{tab} table count: {count}.".format(tab=db_tab, count=row_count))
                            print("{tab} table count: {count} record.".format(tab=db_tab, count=row_count))
                            # every 10000 record
                            for row in range(int(math.ceil(row_count/10000))):
                                ori_cursor.execute("SELECT * from `{DB}`.`{tab}` LIMIT 10000 OFFSET {row}".format(DB=db, tab=tab, row=row*10000))
                                results = ','.join(map(str, ori_cursor.fetchall())).replace('None', 'NULL')
                                tar_cursor.execute("INSERT INTO `{tab}` VALUES {value}".format(tab=tab, value=results))
                            exec_result.append("{tab} record migrated successfully.".format(tab=tab))

                # import view
                if is_view:
                    for db in ori_db.split(','):
                        sql = "USE `{DB}`".format(DB=db) if is_new_db else "USE `{DB}`".format(DB=tar_db)
                        ori_cursor.execute(
                            "SELECT concat(table_schema,'.',table_name) FROM information_schema.views WHERE table_schema='{db}'".format(
                                db=db))
                        for eve in ori_cursor.fetchall():
                            ori_cursor.execute("SHOW CREATE VIEW {view}".format(view=eve[0]))
                            tar_cursor.execute(sql)
                            tar_cursor.execute(ori_cursor.fetchall()[0][1])
                            exec_result.append(
                                "VIEW {view} created successfully.".format(view=eve[0]))
                # import routine
                if is_routine:
                    for db in ori_db.split(','):
                        sql = "USE `{DB}`".format(DB=db) if is_new_db else "USE `{DB}`".format(DB=tar_db)
                        ori_cursor.execute(
                            "SELECT CONCAT('`', db, '`.`', name, '`'), type from mysql.proc where db='{db}'".format(db=db))
                        for eve in ori_cursor.fetchall():
                            ori_cursor.execute("SHOW CREATE {type} {routine}".format(type=eve[1], routine=eve[0]))
                            tar_cursor.execute(sql)
                            tar_cursor.execute(ori_cursor.fetchall()[0][2])
                            exec_result.append("{type} {routine} created successfully.".format(type=eve[1], routine=eve[0]))
                # import event
                if is_event:
                    for db in ori_db.split(','):
                        sql = "USE `{DB}`".format(DB=db) if is_new_db else "USE `{DB}`".format(DB=tar_db)
                        ori_cursor.execute("SELECT CONCAT('`', db, '`.`', name, '`') from mysql.event where db='{db}'".format(db=db))
                        for eve in ori_cursor.fetchall():
                            ori_cursor.execute("SHOW CREATE EVENT {event}".format(event=eve[0]))
                            tar_cursor.execute(sql)
                            tar_cursor.execute(ori_cursor.fetchall()[0][3])
                            exec_result.append("event {event} created successfully.".format(event=eve[0]))
                tar_conn.commit()
                tar_conn.close()
                ori_conn.commit()
                ori_conn.close()
                return True, "\n".join(exec_result)
            except Exception as e:
                exec_result.append('connection was closed...' + str(e))
                print('connection was closed...' + str(e))
                return False, "\n".join(exec_result)
    except Exception as e:
        exec_result.append('migration error...' + str(e))
        print('migration error...' + str(e))
        return False, "\n".join(exec_result)


def get_processlist(server_ip, instance_username, instance_password, instance_port):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        conn = mc.connect(host=server_ip, user=instance_username,
                          password=instance_password,
                          port=instance_port, charset='utf8')
        cursor = conn.cursor(dictionary=True)
        sql = """ SELECT * FROM information_schema.processlist WHERE INFO IS NOT NULL ORDER BY time desc LIMIT 15"""
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return True, result
    except Exception as e:
        print(str(e))
        return False, str(e)


def kill_process(server_ip, instance_username, instance_password, instance_port, process_id):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        conn = mc.connect(host=server_ip, user=instance_username,
                          password=instance_password,
                          port=instance_port, charset='utf8')
        cursor = conn.cursor()
        sql = """ KILL {process_id}""".format(process_id=process_id)
        cursor.execute(sql)
        conn.close()
        return True
    except Exception as e:
        print(str(e))
        return False


def get_db_size(server_ip, instance_username, instance_password, instance_port):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        conn = mc.connect(host=server_ip, user=instance_username,
                          password=instance_password,
                          port=instance_port, charset='utf8')
        cursor = conn.cursor(dictionary=True)
        sql = """ SELECT table_schema AS 'db', round(sum(DATA_LENGTH+INDEX_LENGTH)/1024/1024/1024,2) AS 'size'
                  FROM information_schema.tables
                  WHERE table_schema NOT IN ('performance_schema','test','information_schema','mysql','sys')
                  GROUP BY table_schema ORDER BY 2 DESC limit 3;"""
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(str(e))
        return str(e)


def get_instance_size(server_ip, instance_username, instance_password, instance_port):
    '''
    @author: qingyw
    @note: 「MySQL 数据库管理模块」 引用方法
    '''
    try:
        conn = mc.connect(host=server_ip, user=instance_username,
                          password=instance_password,
                          port=instance_port, charset='utf8')
        cursor = conn.cursor(dictionary=True)
        sql = """ SELECT round(sum(DATA_LENGTH+INDEX_LENGTH)/1024/1024/1024,2) AS 'size' 
                  FROM information_schema.tables"""
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(str(e))
        return str(e)