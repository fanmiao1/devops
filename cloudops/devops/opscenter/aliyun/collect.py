# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
from .region import region_list
from .instances import Instances
from opscenter.models import Server
from opscenter.server_info_template import data_template
import requests
try: from usercenter.build_message import build_message
except: pass


def collect_aliyun_instances(request, region_id, support_id):
    headers = {}
    cookies = ""
    if request.COOKIES:
        cookies = request.COOKIES
    elif request.META.get("HTTP_AUTHORIZATION"):
        headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION")

    true = 'true'
    false = 'false'
    response = []
    try:
        instance = Instances(support_id)
        print(region_id)
        if not region_id:
            return {'result': '请选择地域！', 'code': 0}
        if region_id == 'all':
            for region_id in region_list:
                response +=instance.get_instances_detail(region_id)['Instances'][
                    'Instance']
        else:
            response += instance.get_instances_detail(region_id)['Instances'][
                'Instance']
    except Exception as _:
        return {'result': '认证错误！', 'code': 0}
    success_collect = []
    success_update = []
    have_server_list = Server.objects.values_list('server_id', flat=True)
    for ins in response:
        URL = 'http://{host}/opscenter/server/list/'.format(host=request.get_host())
        METHOD = 'post'
        if ins['InstanceId'] in have_server_list:
            s_id_obj = Server.objects.filter(server_id=ins['InstanceId'])
            if s_id_obj.count() > 0:
                for dd in s_id_obj:
                    s_id = dd.id
                URL = 'http://{host}/opscenter/server/detail/{pk}/'.format(pk=s_id, host=request.get_host())
                METHOD = 'put'
        if ins['OSType'] == 'linux':
            os = 0
        else:
            os = 1
        try:
            region = region_list[ins['RegionId']]
        except KeyError:
            region = ins['RegionId']
        if ins['InnerIpAddress']['IpAddress']:
            inner_ip = ins['InnerIpAddress']['IpAddress'][0]
        elif ins['VpcAttributes']['PrivateIpAddress']['IpAddress']:
            inner_ip = ins['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
        else:
            inner_ip = ''
        data_template['可用区'] = ins['ZoneId']
        data_template['创建时间'] = ins['CreationTime'].split('T')[0]
        data_template['到期时间'] = ins['ExpiredTime'].split('T')[0]
        data_template['自动续费'] = ''
        data_template['CPU'] = str(ins['Cpu'])+'核'
        data_template['内存'] = str(ins['Memory'])+'M'
        data_template['操作系统'] = ins['OSName']

        data = {
            'server_id': ins['InstanceId'],
            "name": ins['InstanceName'],
            "inner_ip": inner_ip,
            "public_ip": ins['PublicIpAddress']['IpAddress'][0] if ins['PublicIpAddress']['IpAddress'] else "",
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
                success_update.append(ins['InstanceName'])
            else:
                success_collect.append(ins['InstanceName'])
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
