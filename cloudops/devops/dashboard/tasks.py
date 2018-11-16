#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   time    : 2018/4/4 10:32
#   author  : Mosasaur Wu
#   software: PyCharm
from celery import shared_task
from django.utils import timezone
from dashboard.data_collection import collect_rds_instance
from usercenter.build_message import send_message


@shared_task()
def async_collect_rds_instance(*args, **kwargs):
    """
    异步执行sql
    :param args:
    :param kwargs:
    :return:
    """
    status = collect_rds_instance('阿里云')
    if status:
        print("拉取数据成功")
    else:
        print("没有拉取到数据")





