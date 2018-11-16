# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/20
@  author  : XieYZ
@  software: PyCharm
"""
from django.http import JsonResponse

from worksheet.wechatApi import GetDepartUserList


def detail_userlist(request):
    department_id = request.POST.get('id')
    fetch_child = request.POST.get('fetch_child', 0)
    user_list = GetDepartUserList(department_id=department_id, fetch_child=fetch_child).userList()
    return JsonResponse({'user_list': user_list})
