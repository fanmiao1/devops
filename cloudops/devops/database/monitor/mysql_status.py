"""
Author: qingyw
Date: 2018/03/22
@note: Prpcrypt Class
functions: decrypt、encrypt
:return:
"""
import sys
import MySQLdb as mdb


class MySQLStatus:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.port = kwargs.get('port')
        try:
            self.conn = mdb.connect(
                host=self.host,
                user=self.user,
                port=self.port,
                passwd=self.password)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(str(e))
            sys.exit()

    def get_status(self, variable_name):
        sql = "SHOW GLOBAL STATUS LIKE '{}' ".format(variable_name)
        self.cursor.execute(sql)
        return int(self.cursor.fetchone()[1])

    def get_TPS(self):
        # com_commit + com_rollback
        com_commit = self.get_status('Com_commit')
        com_rollback = self.get_status('Com_rollback')
        return com_commit + com_rollback

    def get_QPS(self):
        # Questions
        return self.get_status('Questions')

    def get_IOPS(self):
        # Innodb_data_reads + Innodb_data_writes + Innodb_dblwr_writes + Innodb_log_writes
        return self.get_status('Innodb_data_reads') + self.get_status('Innodb_data_writes') + self.get_status(
            'Innodb_dblwr_writes') + self.get_status('Innodb_log_writes')

    def get_recv_k(self):
        return self.get_status('Bytes_received')/1024

    def get_sent_k(self):
        return self.get_status('Bytes_sent')/1024

    def get_inno_row_readed(self):
        return self.get_status('Innodb_rows_read')

    def get_inno_row_update(self):
        return self.get_status('Innodb_rows_updated')

    def get_inno_row_delete(self):
        return self.get_status('Innodb_rows_deleted')

    def get_inno_row_insert(self):
        return self.get_status('Innodb_rows_inserted')

    def get_com_insert(self):
        return self.get_status('Com_select')

    def get_com_delete(self):
        return self.get_status('Com_delete')

    def get_com_update(self):
        return self.get_status('Com_update')

    def get_com_select(self):
        return self.get_status('Com_select')

    def get_inno_log_writes(self):
        return self.get_status('Innodb_log_writes')

    def get_active_session(self):
        return self.get_status('Threads_running')

    def get_total_session(self):
        return self.get_status('Threads_connected')

    def exec(self, name):
        if name == 'total_session':
            return self.get_total_session()
        elif name == 'active_session':
            return self.get_active_session()
        elif name == 'inno_row_insert':
            return self.get_inno_row_insert()
        elif name == 'inno_row_delete':
            return self.get_inno_row_delete()
        elif name == 'inno_row_update':
            return self.get_inno_row_update()
        elif name == 'inno_row_readed':
            return self.get_inno_row_readed()
        elif name == 'Inno_log_writes':
            return self.get_inno_log_writes()
        elif name == 'sent_k':
            return self.get_sent_k()
        elif name == 'recv_k':
            return self.get_recv_k()
        elif name == 'io':
            return self.get_IOPS()
        elif name == 'QPS':
            return self.get_QPS()
        elif name == 'TPS':
            return self.get_TPS()
        elif name == 'com_insert':
            return self.get_com_insert()
        elif name == 'com_delete':
            return self.get_com_delete()
        elif name == 'com_update':
            return self.get_com_update()
        elif name == 'com_select':
            return self.get_com_select()


