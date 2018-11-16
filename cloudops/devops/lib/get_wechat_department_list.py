# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/23
@  author  : XieYZ
@  software: PyCharm
"""
from django.http import JsonResponse

from usercenter.models import Org
from worksheet.wechatApi import GetDepartUserList


def department_list(request):
    fetch_child = request.POST.get('fetch_child', 0)
    parentid = request.POST.get('parentid', 1)
    get_people = request.POST.get('get_people', 0)
    data = eval(Org.objects.only('org_data').get(oid=1).org_data)
    result = []
    if fetch_child == 0:
        for i in data:
            if i['id'] == 1:
                i['open'] = 'true'
            if i['parentid'] == int(parentid):
                i['isParent'] = 1
                result.append(i)
    else:
        result = data
    if int(get_people) == 1:
        user_list = GetDepartUserList(department_id=parentid, fetch_child=0).userList()
        for i in user_list:
            result.append({'id': i['email'],'name':i['name'], 'parentid': parentid, 'icon': i['avatar']})
    return JsonResponse({'result': result})
