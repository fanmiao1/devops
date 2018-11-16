#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   time    : 2018/4/4 10:32
#   author  : Mosasaur Wu
#   software: PyCharm
from celery import shared_task
from django.utils import timezone
from .monitor.data_collection import collect_ali_instance, collect_ali_mysql, collect_local_mysql
from database.funcs import execute_sql, exec_sqlalert, migration
from usercenter.build_message import send_message
from database.models import ApplicationLog, Application, SQLAlert, SQLAlertLog, Instance, DataMigrate, DataMigrateLog, \
    Category
import ipaddress
from database.aes_pycryto import Prpcrypt
prpCryptor = Prpcrypt()


@shared_task()
def async_execute_sql(id, login_name, *args, **kwargs):
    """
    异步执行sql
    :param id: Application ID,
    :param login_name: login user,
    :param args:
    :param kwargs:
    :return:
    """
    msg = ['数据库变更执行成功',
           '数据库变更执行失败']
    start_time = timezone.now()
    Application.objects.filter(id=id).update(execute_time=timezone.now(), application_status=5)
    ApplicationLog.objects.create(application_id=id, content=(login_name + '执行中，请稍后留意状态'))
    from django import db
    db.close_old_connections()

    status, result = execute_sql(*args, **kwargs)
    print(status)
    if status:
        application_status = 4
        approval_content = login_name + ' 执行成功, 耗时 ' + str((
                        timezone.now() - start_time).seconds) + ' (s)'
    else:
        application_status = 0
        approval_content = login_name + ' 执行失败，流程返回到申请人'
    Application.objects.filter(id=id).update(finished_time=timezone.now(), execute_result=result, application_status=application_status)
    ApplicationLog.objects.create(application_id=id, content=approval_content)

    try:
        send_message(action=msg[0] if status else msg[1], detail_id=id)
    except Exception as _:
        pass


@shared_task()
def async_exec_sqlalert(*args, **kwargs):
    """
    预警SQL 报警
    :param args:
    :param kwargs:
    :return:
    """
    msg = '预警SQL数据报警'
    sql_alert = SQLAlert.objects.get(id=kwargs['sql_alert_id'])
    instance_info = Instance.objects.get(id=sql_alert.instance_id)

    status, result = exec_sqlalert(instance_info.server_ip,
                                   str(instance_info.instance_username),
                                   prpCryptor.decrypt(instance_info.instance_password),
                                   int(instance_info.instance_port),
                                   str(instance_info.instance_type),
                                   str(sql_alert.sql), )

    if status:
        application_log = SQLAlertLog()
        application_log.sql_alert_id = kwargs['sql_alert_id']
        application_log.content = result
        application_log.save()
        send_message(action=msg, detail_id=kwargs['sql_alert_id'])


@shared_task()
def async_migration(id, login_name, *args, **kwargs):
    """
    异步迁移
    :param id: data_migrate id,
    :param login_name: login user,
    :param args:
    :param kwargs:
    :return:
    """
    msg = ['数据迁移执行成功',
           '数据迁移执行失败']
    start_time = timezone.now()

    DataMigrate.objects.filter(id=id).update(execute_time=timezone.now(), application_status=4)
    DataMigrateLog.objects.create(data_migrate_id=id, create_time=timezone.now(), content=(login_name + ':迁移中，请稍后留意状态'))
    from django import db
    db.close_old_connections()
    status, result = migration(*args, **kwargs)
    print(status)
    if status:
        application_status = 5
        approval_content = login_name + ': 迁移成功, 耗时 ' + str((timezone.now() - start_time).seconds) + ' (s)' + '\n' + result
    else:
        application_status = 0
        approval_content = login_name + ': 迁移失败，详情见日志' + '\n' + result
    DataMigrateLog.objects.create(data_migrate_id=id, create_time=timezone.now(), content=approval_content)
    DataMigrate.objects.filter(id=id).update(finished_time=timezone.now(), application_status=application_status)
    try:
        send_message(action=msg[0] if status else msg[1], detail_id=id)
    except Exception as _:
        pass


@shared_task()
def async_collect_rds_instance(*args, **kwargs):
    """
    异步收集RDS
    :param args:
    :param kwargs:
    :return:
    """
    status = collect_ali_instance('阿里云')
    if status:
        print("拉取数据成功")
    else:
        print("没有拉取到数据")


@shared_task()
def async_get_local_perf(*args, **kwargs):
    """
    异步执行sql
    :param args:
    :param kwargs:
    :return:
    """
    cate_name = Category.objects.get(cate_name='MySQL')
    for instance in Instance.objects.filter(instance_type=cate_name, is_delete=0):
        status = collect_local_mysql(instance.id)
        if status:
            print("{name} 拉取数据成功".format(name=instance.instance_name))
        else:
            print("{name} 没有拉取到数据".format(name=instance.instance_name))


@shared_task()
def async_get_rds_perf(*args, **kwargs):
    """
    异步执行sql
    :param args:
    :param kwargs:
    :return:
    """
    status = collect_ali_mysql()
    if status:
        print("rds数据拉取成功")
    else:
        print("rds没有拉取到数据")
