# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
import requests
import time

from opscenter.models import Server
from .instances import Instances
from .region import region_list, zone_list
from opscenter.server_info_template import data_template
try: from usercenter.build_message import build_message
except: pass


def collect_ucloud_instances(request, region_id, support_id):
    headers = {}
    cookies = ""
    if request.COOKIES:
        cookies = request.COOKIES
    elif request.META.get("HTTP_AUTHORIZATION"):
        headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION")

    true = False
    false = True
    response = []
    try:
        instance = Instances(support_id)
        if not region_id:
            return {'result': '请选择地域！', 'code': 0}
        if region_id == 'all':
            for region_id in region_list:
                response += eval(instance.get_instances_detail(region_id))['UHostSet']
        else:
            response += eval(instance.get_instances_detail(region_id))['UHostSet']
    except Exception as _:
        return {'result': '认证错误！', 'code': 0}
    success_collect = []
    success_update = []
    have_server_list = Server.objects.values_list('server_id', flat=True)
    for ins in response:
        URL = 'http://{host}/opscenter/server/list/'.format(host=request.get_host())
        METHOD = 'post'
        if ins['UHostId'] in have_server_list:
            s_id_obj = Server.objects.filter(server_id=ins['UHostId'])
            if s_id_obj.count() > 0:
                for dd in s_id_obj:
                    s_id = dd.id
                URL = 'http://{host}/opscenter/server/detail/{pk}/'.format(pk=s_id, host=request.get_host())
                METHOD = 'put'
        if ins['OsType'] == 'linux':
            os = 0
        else:
            os = 1
        try:
            region = zone_list[ins['Zone']]
        except KeyError:
            region = ins['Zone']
        inner_ip = None
        public_ip = None
        for i in ins['IPSet']:
            if i['Type'] == "Private":
                inner_ip = i['IP']
            else:
                public_ip = i['IP']
        data_template['可用区'] = ins['Zone']
        data_template['创建时间'] = str(time.strftime("%Y-%m-%d",time.localtime(ins['CreateTime'])))
        data_template['到期时间'] = str(time.strftime("%Y-%m-%d",time.localtime(ins['ExpireTime'])))
        data_template['自动续费'] = '是' if ins['AutoRenew'] == 'Yes' else '否'
        data_template['CPU'] = str(ins['CPU']) + '核'
        data_template['内存'] = str(ins['Memory']) + 'M'
        data_template['操作系统'] = ins['OsName']
        data = {
            'server_id': ins['UHostId'],
            "name": ins['Name'],
            "inner_ip": inner_ip,
            "public_ip": public_ip,
            "os": os,
            "server_info": str(data_template),
            "region": region,
            "remark": None,
            "support": support_id,
        }
        if METHOD == 'put':
            response = requests.put(URL, data=data, cookies=cookies, headers=headers)
        else:
            response = requests.post(URL, data=data, cookies=cookies, headers=headers)
        if str(response.status_code)[:1] == '2':
            if METHOD == 'put':
                success_update.append(ins['Name'])
            else:
                success_collect.append(ins['Name'])
            s = requests.session()
            s.keep_alive = False
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
    result = '成功添加{success_collect}个实例，更新了{success_update}个实例'.format(
        success_collect=len(success_collect), success_update=len(success_update))
    return {'result': result, 'code': 1}
