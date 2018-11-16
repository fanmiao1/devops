# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/10
@  author  : Xieyz
@  software: PyCharm
"""
import requests

from opscenter.models import Server
from CMDB.models import Assets
from usercenter.build_message import build_message


def get_local_server(request, support_id):
    headers = {}
    cookies = ""
    if request.COOKIES:
        cookies = request.COOKIES
    elif request.META.get("HTTP_AUTHORIZATION"):
        headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION")

    success_collect = []
    success_update = []
    asset_obj = Assets.objects.filter(asset_type__name='服务器')
    have_server_list = Server.objects.values_list('server_id', flat=True)
    for i in asset_obj:
        URL = 'http://{host}/opscenter/server/list/'.format(host=request.get_host())
        METHOD = 'post'
        if i.asset_id in have_server_list:
            s_id_obj = Server.objects.filter(server_id=i.asset_id)
            if s_id_obj.count() > 0:
                for dd in s_id_obj:
                    s_id = dd.id
                URL = 'http://{host}/opscenter/server/detail/{pk}/'.format(pk=s_id, host=request.get_host())
                METHOD = 'put'
        try:
            other_info = eval(i.asset_info)
        except:
            other_info = {}
        try:
            name = other_info['名称']
            if not name:
                name = i.asset_id
        except:
            name = i.asset_id

        try:
            if other_info['操作系统'][:3] == 'win':
                os = 1
            else:
                os = 0
        except:
            os = 0
        try:
            inner_ip = other_info['IP地址']
        except:
            inner_ip = ''
        data = {
            'server_id': i.asset_id,
            'name': name,
            'support': support_id,
            'region': '本地',
            'remark': i.remark,
            'os': os,
            'inner_ip': inner_ip,
            'server_info': i.asset_info
        }
        if METHOD == 'put':
            response = requests.put(URL, data=data, cookies=cookies, headers=headers)
        else:
            response = requests.post(URL, data=data, cookies=cookies, headers=headers)
        if str(response.status_code)[:1] == '2':
            if METHOD == 'put':
                success_update.append(i.asset_id)
            else:
                success_collect.append(i.asset_id)
    try:
        if len(success_collect) > 0 or len(success_update) > 0:
            build_message(
                **{'message_title': '收集本地实例结果',
                'message_content': '共成功添加{n}个本地实例：{success_list};'
                                   ' \n 共成功更新{up_n}个本地实例：{success_update_list}'.format(
                    n=len(success_collect), success_list=str(success_collect), up_n=len(success_update),
                    success_update_list=success_update),
                'message_url': '/opscenter/server/',
                'message_user': request.user.id
                }
            )
    except:
        pass
    return {'result': '成功收集实例：' + str(success_collect), 'code': 1}
