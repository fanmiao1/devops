# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/5
@  author  : Xieyz
@  software: PyCharm
"""
import requests

from .region import region_list
from .instances import Instances
from opscenter.models import Server
from opscenter.server_info_template import data_template
from dateutil.tz import tzutc
try: from usercenter.build_message import build_message
except: pass


def collect_aws_instances(request, region_id, support_id):
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
                response += instance.get_instances_detail(region_id)
        else:
            response += instance.get_instances_detail(region_id)
    except Exception as _:
        print (str(_))
        return {'result': '认证错误！', 'code': 0}
    success_collect = []
    success_update = []
    have_server_list = Server.objects.values_list('server_id', flat=True)
    for ins in response:
        URL = 'http://{host}/opscenter/server/list/'.format(host=request.get_host())
        METHOD = 'post'
        ins = ins['Instances'][0]
        if ins['InstanceId'] in have_server_list:
            s_id_obj = Server.objects.filter(server_id=ins['InstanceId'])
            if s_id_obj.count() > 0:
                for dd in s_id_obj:
                    s_id = dd.id
                URL = 'http://{host}/opscenter/server/detail/{pk}/'.format(pk=s_id, host=request.get_host())
                METHOD = 'put'
        try:
            region = region_list[ins['Placement']['AvailabilityZone'][:-1]]
        except KeyError:
            region = ins['Placement']['AvailabilityZone']
        try:
            inner_ip = ins['PrivateIpAddress']
        except Exception as _:
            inner_ip = None
        try:
            public_ip = ins['PublicIpAddress']
        except Exception as _:
            public_ip = None
        try:
            name = ins['Tags'][0]['Value']
        except Exception as _:
            name = ins['InstanceId']
        data_template['可用区'] = region
        data_template['创建时间'] = ins['LaunchTime'].strftime('%Y-%m-%d')
        data_template['自动续费'] = '是'
        data_template['CPU'] = str(int(ins['CpuOptions']['CoreCount'])*int(ins['CpuOptions']['ThreadsPerCore']))+'核'
        data = {
            'server_id': ins['InstanceId'],
            "name": name,
            "inner_ip": inner_ip,
            "public_ip": public_ip,
            "os": 0,
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
                success_update.append(name)
            else:
                success_collect.append(name)
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