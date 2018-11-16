#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import json
# import requests
# from .models import WorkSheet
from .wechatApi import *


def send_generic_message(touser, msg, title='通知', url=get_current_domain(), btntxt='详情'):
    agent_id = get_agentid()
    corp_secret = get_corp_secret()
    send_url = 'http://10.1.1.192:8011/api/v1/msg/wechat/'
    values = {
        "touser": touser,
        "msgtype": 'textcard',
        "textcard": {
            'title': title,
            'description': '<br>' + msg,
            "url": url,
            "btntxt": btntxt,
        },
        "agentid": int(agent_id),
        "corpid": "ww0f3efc2873ad11c3",
        "corpsecret": corp_secret,
    }
    print (values)
    msges = (bytes(json.dumps(values), 'utf-8'))
    result = requests.post(send_url, data=msges)
    if result.status_code == 200:
        print ('「send_generic_message」: Send wechat message success')
        return '「send_generic_message」: Send wechat message success'
    else:
        print ('「send_generic_message」: Send wechat message Failed')
        return '「send_generic_message」: Send wechat message Failed'


def send_operator_wechat_message(id, msg):
    try:
        print('send_operator_wechat_message')
        worksheet_obj = WorkSheet.objects.get(id=id, status=2)
        if worksheet_obj.operator:
            the_email = worksheet_obj.operator.email
            user_id = GetUserIdByEmail(str(the_email), 1, 1).getUserId()
            BuildWechatMessage(user_id, msg).sendCard(worksheet_obj.wsid, 2)
        else:
            pass
    except Exception as _:
        pass


def send_receiver_wechat_message(id, msg):
    try:
        print('send_receiver_wechat_message')
        worksheet_obj = WorkSheet.objects.get(id=id)
        if worksheet_obj.receive_pepole:
            the_email = worksheet_obj.receive_pepole.email
            user_id = GetUserIdByEmail(str(the_email), 1, 1).getUserId()
            BuildWechatMessage(user_id, msg).sendCard(worksheet_obj.wsid)
        else:
            pass
    except Exception as _:
        pass


def send_pm_wechat_message(id, msg):
    from workflow.models import project_group, project
    try:
        print('send_pm_wechat_message')
        worksheet_obj = WorkSheet.objects.get(id=id, status=2)
        project_id = list(set(project_group.objects.filter(user_id=worksheet_obj.operator_id).values_list('project_id', flat=True)))
        pm = project.objects.filter(id__in=project_id)
        if worksheet_obj.operator:
            for row in pm:
                the_email = row.project_manager.email
                user_id = GetUserIdByEmail(str(the_email), 1, 1).getUserId()
                BuildWechatMessage(user_id, msg).sendCard(worksheet_obj.wsid, 0)
        else:
            pass
    except Exception as _:
        pass