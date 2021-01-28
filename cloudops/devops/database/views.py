#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import strip_tags
from usercenter.permission import check_permission
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from workflow.get_name_by_id import get_name_by_id
from workflow.models import project_group
from django.core.paginator import Paginator
from .forms import *
from .aes_pycryto import Prpcrypt
from .inception import InceptionDao
from .funcs import is_invalid_conn, is_invalid_ipv4_address, exec_sqlalert, delete_db_user, get_privs, is_exist_user, \
    sqlserver_parse, migration
from usercenter.build_message import send_message
from django.urls import reverse
import ipaddress
from django.db.models import Q
import operator
import json
import datetime
import MySQLdb as mdb
import pymssql
import ast
from django.contrib import messages
from devops import settings
from django.utils.timezone import utc
from django.utils.timezone import timedelta
from dateutil.parser import parse
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .tasks import async_execute_sql, async_migration
from .monitor.aliyun import ALiYun
from opscenter.models import Support
from database.models import RDSInstance
from pandas import DataFrame
from django.views.generic import TemplateView

prpCryptor = Prpcrypt()
inceptionDao = InceptionDao()


class DateEncoder(json.JSONEncoder):
    """
    重写构造json类，遇到日期特殊处理，其余的用内置
    """
    def default(self, obj):
        if settings.USE_TZ:
            utc_dt = obj.replace(tzinfo=utc)
            obj = utc_dt.astimezone(datetime.timezone(timedelta(hours=8)))
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # elif isinstance(obj, date):
        #     return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


@login_required
def get_database(request, instance_id):
    """
    新建用户、权限申请，数据库下拉框展示
    """
    instance_info = Instance.objects.get(id=instance_id)
    # print (instance_info.instance_type)
    result = []
    if str(instance_info.instance_type) == 'MySQL':
        conn = mdb.connect(host=instance_info.server_ip,
                           user=instance_info.instance_username,
                           passwd=prpCryptor.decrypt(instance_info.instance_password),
                           port=instance_info.instance_port, charset='utf8')
        execute_sql = """show databases;"""
    elif str(instance_info.instance_type) == 'SQL SERVER':
        conn = pymssql.connect(host=instance_info.server_ip,
                               user=instance_info.instance_username,
                               password=prpCryptor.decrypt(instance_info.instance_password),
                               port=instance_info.instance_port, charset='utf8')
        execute_sql = """ Select Name from sys.databases where is_broker_enabled=0 and is_fulltext_enabled=1  """
    c = conn.cursor()
    c.execute(execute_sql)
    exclude_db = ['test', 'sys', 'mysql', 'information_schema', 'performance_schema']
    for row in c.fetchall():
        result.append([row[0]]) if row[0] not in exclude_db else ''
    conn.close()
    return JsonResponse({'data': result})


@login_required
def get_database_table(request):
    """
    新建用户、权限申请，数据库下拉框展示
    """
    result = []
    if request.method == 'POST':
        data = request.POST
        print(data)
        instance_id = request.POST.get('instance_id')
        databases = request.POST.getlist('databases[]')
        print(instance_id, databases)
        instance_info = Instance.objects.get(id=instance_id)
        result = []
        if str(instance_info.instance_type) == 'MySQL':
            conn = mdb.connect(host=instance_info.server_ip,
                               user=instance_info.instance_username,
                               passwd=prpCryptor.decrypt(instance_info.instance_password),
                               port=instance_info.instance_port, charset='utf8')
        elif str(instance_info.instance_type) == 'SQL SERVER':
            conn = pymssql.connect(host=instance_info.server_ip,
                                   user=instance_info.instance_username,
                                   password=prpCryptor.decrypt(instance_info.instance_password),
                                   port=instance_info.instance_port, charset='utf8')
        c = conn.cursor()
        for database_id in databases:
            if instance_info.instance_type.cate_name == 'MySQL':
                execute_sql = """select concat(table_schema, '.',table_name) from information_schema.tables where table_type='BASE TABLE' AND table_schema in ('%s')""" % database_id
            elif instance_info.instance_type.cate_name == 'SQL SERVER':
                execute_sql = """select name from %s.sys.tables """ % database_id
            c.execute(execute_sql)
            exclude_db = ['test', 'sys', 'mysql', 'information_schema', 'performance_schema']
            for row in c.fetchall():
                result.append([row[0]]) if row[0] not in exclude_db else ''
        conn.close()
    return JsonResponse({'data': result})


@login_required
def get_project_user(request, project_id):
    """
    新建用户、权限申请，数据库下拉框展示
    """
    user_id = project_group.objects.only('user_id').filter(project_id=project_id).values_list('user_id', flat=True)
    project_user = User.objects.filter(id__in=user_id)
    result = []
    for item in project_user:
        result.append([item.id, item.last_name + item.first_name])
    return JsonResponse({'data': result})


@login_required
def get_project(request):
    """
    新建用户、权限申请，项目下拉框展示
    """
    result = []
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        groups = []
        if request.user.is_superuser:
            groups = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=user_id).values_list('project', flat=True)]
            for group in list_group:
                project_info = project.objects.get(id=group)
                groups.append(group)
                groups.append(project.objects.get(
                    project=project_info.parent_project).id) if project_info.have_parent_project else ''
                if not project_info.have_parent_project:
                    groups.extend([entry for entry in
                                   project.objects.filter(parent_project=project_info.project).values_list('id',
                                                                                                           flat=True)])
        list_group = list(set(groups))
        projects = project.objects.filter(id__in=list_group, status=9)
        for item in projects:
            result.append([item.id, item.project])
    return JsonResponse({'data': result})


@login_required
def review_sql(request):
    review_result = []
    is_pass = False
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        sql = request.POST.get('sql')
        instance_info = Instance.objects.get(id=instance_id)
        host = instance_info.server_ip
        port = int(instance_info.instance_port)
        user = str(instance_info.instance_username)
        password = prpCryptor.decrypt(instance_info.instance_password)
        instance_type = str(instance_info.instance_type)
        result_type = ''
        if instance_type == 'MySQL':
            is_pass, review_result, result_type = inceptionDao.sql_review(sql, host, port, user, password)
            print(is_pass, review_result)
        elif instance_type == 'SQL SERVER':
            review_result = sqlserver_parse(sql, host, port, user, password)
        return JsonResponse(
            {'result': review_result, 'is_pass': is_pass, 'instance_type': instance_type, 'result_type': result_type})


@login_required
def search_sql(request):
    if request.method == 'POST':
        search_result = []
        sql = request.POST.get('sql')
        if ' ' in sql:
            key = sql.split(' ')
            sql_key = '+'
            while '' in key:
                key.remove('')
            for i, row in enumerate(key):
                sql_key += row
                if i != len(key)-1:
                    sql_key += ' +'
        else:
            sql_key = '+' + sql
        all_records = Application.objects.extra(
            where=["MATCH(execute_sql) AGAINST (%s IN BOOLEAN MODE) AND is_delete <> 1"],
            params=[sql_key])

        for application in all_records:
            try:
                appliant = get_name_by_id.get_name(application.appliant.id)
            except AttributeError:
                appliant = ''
            search_result.append({
                "id": application.id if application.id else "",
                "appliant": appliant if appliant else "",
                "application_time": application.application_time if application.application_time else "",
                "execute_sql": application.execute_sql if application.execute_sql else "",
            })
        return HttpResponse(json.dumps({'result': search_result, 'count': all_records.count()}, cls=DateEncoder))
        # return JsonResponse({'result': search_result})

    return render(request, 'database/search_sql.html')


@login_required
def get_user(request, instance_id):
    """
    权限申请，数据库用户下拉框展示
    """
    instance_info = Instance.objects.get(id=instance_id)
    result = []
    if str(instance_info.instance_type) == 'MySQL':
        conn = mdb.connect(host=instance_info.server_ip,
                           user=instance_info.instance_username,
                         passwd=prpCryptor.decrypt(instance_info.instance_password),
                         port=instance_info.instance_port, charset='utf8')
        execute_sql = """SELECT distinct concat('`',user,'`@`',host,'`') as name from mysql.user 
                          WHERE user NOT IN ('root', 'sys', 'mysql','test', 'information_schema', 'performance_schema')
                          ORDER BY name asc"""
    elif str(instance_info.instance_type) == 'SQL SERVER':
        conn = pymssql.connect(host=instance_info.server_ip,
                             user=str(instance_info.instance_username),
                             password=prpCryptor.decrypt(instance_info.instance_password),
                             port=int(instance_info.instance_port), charset='utf8')
        # execute_sql = """ Select name FROM sys.syslogins where  isntuser = 0 and denylogin=0 """
        execute_sql = """ Select a.name FROM sys.syslogins a inner join sys.sql_logins b on a.sid=b.sid where isntuser = 0 and denylogin=0 and isntname=0 and status<>10 and b.is_disabled=0 order by a.name  """
    c = conn.cursor()
    c.execute(execute_sql)
    for row in c.fetchall():
        result.append([row[0]])
    conn.close()
    return JsonResponse({'data': result})


@login_required
def get_project_instance(request, project_id):
    """
    获取项目下的关联实例
    """
    project_info = project.objects.get(id=project_id)
    if project_info.have_parent_project:
        parent_project_id = project.objects.get(project=project_info.parent_project)
        instanceList = Instance.objects.filter(project_id=parent_project_id).exclude(is_delete=1)
    else:
        instanceList = Instance.objects.filter(project_id=project_id).exclude(is_delete=1)
    # print (instanceList)
    list1 = []
    for item in instanceList:
        list1.append([item.id, item.instance_name])
    return JsonResponse({'data': list1})


@login_required
def get_instance_dba(request, instance_id):
    """
    获取项目下的关联实例
    """
    instance_info = Instance.objects.get(id=instance_id)
    user_info = User.objects.get(id=instance_info.ops_user.id)
    list1 = []
    list1.append([user_info.id, user_info.last_name+user_info.first_name])
    return JsonResponse({'data': list1})


@login_required
@check_permission
def jump_queries_analyzing(request):
    """允许跳转到查询分析页面"""
    return JsonResponse({'result': 'true'})


@login_required
@check_permission
def jump_monitor(request):
    """允许跳转到监控页面"""
    return JsonResponse({'result':'true'})


@login_required
@check_permission
def show_privileges(request, id, user=''):
    """
    展示用户权限信息
    """
    instance_info = Instance.objects.get(id=id)
    if user != '':
        user = user.replace('%25', '%').replace('%40', '@')
        ip_segment = user.split('@')[-1]
        pre_user = '@'.join(user.split('@')[0:len(user.split('@')) - 1])
        user = str("'" + pre_user + "'@'" + ip_segment + "'")

        instancelog = InstanceLog()
        instancelog.instance_id = id
        is_delete = delete_db_user(instance_info.server_ip, instance_info.instance_username,
                                   prpCryptor.decrypt(instance_info.instance_password), instance_info.instance_port,
                                       str(instance_info.instance_type), user)
        instancelog.content = '{操作人:' + get_name_by_id.get_name(request.user.id) + ', action: 删除, info:删除 ' + user + ' 用户' + ('成功' if is_delete else '失败') + '}'
        instancelog.save()
        return JsonResponse({'result':'true'})
    else:
        if request.method == 'POST':
            pageSize = int(request.POST.get('pageSize'))  # 如何manufactoryy每页项目
            pageNumber = int(request.POST.get('pageNumber'))
            offset = request.POST.get('offset') # 数据库中共有多少页
            search = request.POST.get('search')
            sort_column = request.POST.get('sort')  # 该列需要排序
            order = request.POST.get('order')  # 升序或降序
            if search:  # 判断是否有搜索字
                sql = """SELECT CONCAT("SHOW GRANTS FOR '", user, "'@'", host,"'") as 'grant_sql' FROM mysql.user WHERE user LIKE '%""" + search + '%' + "';"
            else:
                sql = """SELECT CONCAT("SHOW GRANTS FOR '", user, "'@'", host,"'") as 'grant_sql' FROM mysql.user ;"""
            priv_info = get_privs(instance_info.server_ip, instance_info.instance_username,
                                  prpCryptor.decrypt(instance_info.instance_password), instance_info.instance_port, str(instance_info.instance_type), sql)
            all_records_count = len(priv_info['rows'])
            if not offset:
                offset = 0
            if not pageSize:
                pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
            response_data = {'total': all_records_count, 'rows': []}
            response_data['rows'] = priv_info['rows'][(pageNumber-1)*pageSize:pageNumber*pageSize]
            return JsonResponse(response_data)
    return render(request, 'database/show_instance_user.html', {'instance_id': id, 'instance_name': instance_info.instance_name})


@login_required
@check_permission
def get_user_privilege(request, id, user):
    """
    展示用户权限信息
    """
    from .funcs import get_user_privs
    if request.method == 'POST':
        instance_info = Instance.objects.get(id=id)
        user = user.replace('%25', '%').replace('%40', '@')
        ip_segment = user.split('@')[-1]
        pre_user = '@'.join(user.split('@')[0:len(user.split('@')) - 1])
        user = str("'" + pre_user + "'@'" + ip_segment + "'")
        sql = """SHOW GRANTS FOR {user}""".format(user=user)
        priv_info = get_user_privs(instance_info.server_ip, instance_info.instance_username,
                              prpCryptor.decrypt(instance_info.instance_password), instance_info.instance_port, str(instance_info.instance_type), sql)
    return JsonResponse(priv_info, safe=False)


@login_required
@check_permission
def revoke_user_privilege(request, id):
    """
    展示用户权限信息
    """
    from .funcs import revoke_user_privs
    if request.method == 'POST':
        instance_info = Instance.objects.get(id=id)
        privs = request.POST.get('privs', '').split(',')
        status = revoke_user_privs(instance_info.server_ip, instance_info.instance_username,
                                   prpCryptor.decrypt(instance_info.instance_password),
                                   instance_info.instance_port, str(instance_info.instance_type), privs)
        code = 1 if status else 0
        if code:
            instancelog = InstanceLog()
            instancelog.instance_id = id
            instancelog.content = get_name_by_id.get_name(request.user.id) + '回收权限:' + request.POST.get('privs', '')
            instancelog.save()
    return JsonResponse({'code': code})


@login_required
@check_permission
def reset_db_passwd(request, id, user):
    """
    展示用户权限信息
    """
    from .funcs import reset_db_user
    if request.method == 'POST':
        instance_info = Instance.objects.get(id=id)
        user = user.replace('%25', '%').replace('%40', '@')
        ip_segment = user.split('@')[-1]
        pre_user = '@'.join(user.split('@')[0:len(user.split('@')) - 1])
        user = str("'" + pre_user + "'@'" + ip_segment + "'")
        passwd = request.POST.get('passwd', '')
        is_reset = reset_db_user(instance_info.server_ip, instance_info.instance_username,
                                   prpCryptor.decrypt(instance_info.instance_password), instance_info.instance_port,
                                       str(instance_info.instance_type), user, passwd)
        code = 1 if is_reset else 0
        if code:
            instancelog = InstanceLog()
            instancelog.instance_id = id
            instancelog.content = get_name_by_id.get_name(request.user.id) + ' 重置 ' + user + ' 密码'
            instancelog.save()
    return JsonResponse({'code': code})


@login_required
def show_operation_log(request, id):
    """
    展示操作记录
    """
    instance_info = Instance.objects.get(id=id)
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = search.strip()
            all_records = InstanceLog.objects.filter(instance_id=id, content__icontains=search)
        else:
            all_records = InstanceLog.objects.filter(instance_id=id)
        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'createtime']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for row in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": row.id if row.id else "",
                "content": row.content if row.content else "",
                "createtime": row.createtime if row.createtime else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'database/operation_log.html', {'instance_id': id, 'instance_name': instance_info.instance_name})



@login_required
@check_permission
def add_instance(request):
    """
    @author: qingyw
    @note: 添加实例
    :param request:
    :return:
    """
    if request.method == "POST":
        add_instance = InstanceForm(request.POST)
        if not request.POST.get('project_name'):
            errors = '请选择项目！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': add_instance})
        elif not request.POST.get('instance_type'):
            errors = '请选择实例类型！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': add_instance})
        elif not request.POST.get('ops_user'):
            errors = '请选择运维DBA！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': add_instance})
        if add_instance.is_valid():
            data = add_instance.cleaned_data
            server_ip = data.get('server_ip').replace(' ', '')
            instance_name = data.get('instance_name')
            ops_user = data.get('ops_user')
            instance_username = data.get('instance_username')
            instance_password = data.get('instance_password')
            instance_port = data.get('instance_port')
            project_name = data.get('project_name')
            instance_env = data.get('instance_env')
            instance_type = data.get('instance_type')
            is_exist_name = Instance.objects.filter(instance_name=instance_name, is_delete=0)
            is_exist_ip_port = Instance.objects.filter(server_ip=server_ip, instance_port=instance_port, is_delete=0)
            is_conn, instance_role, subordinate_info = is_invalid_conn(server_ip, instance_username, instance_password, instance_port, str(instance_type))

            # instanceform = InstanceForm(
            #     initial={
            #         'server_ip': str(ipaddress.ip_address(server_ip)),
            #         'instance_name': instance_name,
            #         'instance_username': instance_username,
            #         'instance_password': instance_password,
            #         'instance_port': instance_port,
            #         'project_name': project_name,
            #         'instance_env': instance_env,
            #         'instance_type': instance_type,
            #     }
            # )
            if is_exist_name:
                errors = '该实例名已存在！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': add_instance})
            elif is_exist_ip_port:
                errors = '该 IP、port 已经存在，请勿重复添加！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': add_instance})
            elif is_conn:
                errors = 'ooh，该实例连接失败,请验证用户名或密码是否正确 ！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': add_instance})
            else:
                instanceform = Instance()
                instancelog = InstanceLog()
                instanceform.server_ip = server_ip
                instanceform.instance_name = instance_name
                instanceform.instance_username = instance_username
                instanceform.instance_password = prpCryptor.encrypt(instance_password)
                instanceform.project = project_name
                instanceform.ops_user = ops_user
                instanceform.instance_port = instance_port
                instanceform.instance_type = instance_type
                instanceform.instance_env = instance_env
                instanceform.instance_role = instance_role
                instanceform.save()
                instanceid = Instance.objects.latest('id')
                instancelog.instance_id = instanceid.id
                instancelog.content = '{applicant:' + get_name_by_id.get_name(request.user.id) + ', action: 新增, info:添加' + instance_type.cate_name + '实例}'
                instancelog.save()
                if len(subordinate_info):
                    instancestruct = InstanceStruct()
                    instancestruct.instance_id = instanceid.id
                    instancestruct.main_host = subordinate_info[0]
                    instancestruct.main_port = subordinate_info[1]
                    instancestruct.subordinate_type = subordinate_info[2]
                    instancestruct.subordinate_delay = subordinate_info[3]
                    instancestruct.save()
                return render(request, 'database/instances.html', {'add_instance': add_instance})
        else:
            errors = add_instance.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': add_instance})
    else:
        instanceform = InstanceForm()
    return render(request, 'database/change_instance.html', {"instanceform": instanceform})


@login_required
@check_permission
def instances(request, id=0):
    """
    @author: qingyw
    @note: 实例管理
    :param request:
    :return: 实例列表
    """
    if id != 0:
        Instance.objects.filter(id=id).update(is_delete=1)
        InstanceStruct.objects.filter(instance_id=id).delete()
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = search.strip()
            all_records = Instance.objects.filter(
                Q(instance_name__icontains=search) |
                Q(project__project__icontains=search) |
                Q(instance_username__icontains=search) |
                Q(instance_type__cate_name__icontains=search)).exclude(is_delete=1)
            if search in '生产':
                all_records = Instance.objects.filter(instance_env=1).exclude(is_delete=1)
            elif search in '测试':
                all_records = Instance.objects.filter(instance_env=2).exclude(is_delete=1)
            elif search in '开发':
                all_records = Instance.objects.filter(instance_env=3).exclude(is_delete=1)
            elif '.' in search or search.isdigit():
                all_records = Instance.objects.extra(
                    where=["LOCATE(%s, INET_NTOA(server_ip)) OR id=%s OR instance_port=%s"],
                    params=[search, search, search]).exclude(is_delete=1)

        else:
            all_records = Instance.objects.all().exclude(is_delete=1)  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'server_ip', 'instance_name', 'instance_username', 'instance_port',
                               'instance_env', ]:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('server_ip')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for row in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": row.id if row.id else "",
                "server_ip": row.server_ip if row.server_ip else "",
                "instance_name": row.instance_name if row.instance_name else "",
                "instance_username": row.instance_username if row.instance_username else "",
                "instance_port": row.instance_port if row.instance_port else "",
                "project_name": row.project.project if row.project.project else "",
                # "ops_user": list.ops_user if list.ops_user. else "",
                "instance_env": '生产环境' if row.instance_env == 1 else '测试环境' if row.instance_env == 2 else '开发环境',
                "instance_type": row.instance_type.cate_name if row.instance_type.cate_name else "",
                "instance_role": row.instance_role if row.instance_role else "",
            })
        return JsonResponse(response_data)
    return render(request, 'database/instances.html')


@login_required
def rds(request):
    """
    @author: qingyw
    @note: ALI RDS 实例管理
    :param request:
    :return: 实例列表
    """
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = search.strip()
            all_records = RDSInstance.objects.filter(
                Q(id__icontains=search) |
                Q(instance_id__icontains=search) |
                Q(region_id__icontains=search) |
                Q(instance_description__icontains=search))
        else:
            all_records = RDSInstance.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'instance_id', 'region_id', 'expire_time']:
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('create_time')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for ali_rds in pageinator.page(pageNumber):
            response_data['rows'].append({
                # "id": ali_rds.id if ali_rds.id else "",
                "platform": ali_rds.support.name if ali_rds.support else "",
                "instance_id": ali_rds.instance_id if ali_rds.instance_id else "",
                "instance_description": ali_rds.instance_description if ali_rds.instance_description else "",
                "instance_class": ali_rds.instance_class if ali_rds.instance_class else "",
                "instance_type": ali_rds.instance_type if ali_rds.instance_type else "",
                "engine": ali_rds.engine + (ali_rds.engine_version if ali_rds.engine_version else "") if ali_rds.engine else "",
                "region_id": ali_rds.region_id if ali_rds.region_id else "",
                "create_time": ali_rds.create_time if ali_rds.create_time else "",
                "expire_time": (ali_rds.expire_time - timezone.now()).days if ali_rds.expire_time else '',
                "instance_status": ali_rds.instance_status if ali_rds.instance_status else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'database/instances.html')


@login_required
@check_permission
def modify_instance(request, id):
    """
    @author: qingyw
    @note: 实例管理 - 修改
    :param request:
    :param control: 变量用作控制
    :return:
    """
    dataform = Instance.objects.get(id=id)
    instanceform = InstanceForm(
        initial={
            'server_ip': dataform.server_ip,
            'instance_name': dataform.instance_name,
            'ops_user': dataform.ops_user,
            'project_name': dataform.project,
            'instance_username': dataform.instance_username,
            'instance_password': dataform.instance_password,
            'instance_port': dataform.instance_port,
            'instance_env': dataform.instance_env,
            'instance_type': dataform.instance_type,
        }
    )

    if request.method == "POST":
        modify_instance = InstanceForm(request.POST)
        if not request.POST.get('project_name'):
            errors = '请选择项目！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': instanceform})
        elif not request.POST.get('instance_type'):
            errors = '请选择实例类型！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': instanceform})
        elif not request.POST.get('ops_user'):
            errors = '请选择运维DBA！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': instanceform})
        if modify_instance.is_valid():
            data = modify_instance.cleaned_data
            server_ip = data.get('server_ip').replace(' ', '')
            instance_name = data.get('instance_name')
            ops_user = data.get('ops_user')
            instance_username = data.get('instance_username')
            instance_password = data.get('instance_password')
            instance_port = data.get('instance_port')
            project_name = data.get('project_name')
            instance_env = data.get('instance_env')
            instance_type = data.get('instance_type')
            # print(instance_type, type(str(instance_type)))
            is_exist_name = Instance.objects.filter(instance_name=instance_name, is_delete=0).exclude(id=id)
            is_exist_ip_port = Instance.objects.filter(server_ip=server_ip, instance_port=instance_port,
                                                       is_delete=0).exclude(id=id)
            is_conn, instance_role, subordinate_info = is_invalid_conn(server_ip, instance_username, instance_password, instance_port, str(instance_type))
            # print (is_conn, instance_role, subordinate_info)
            if is_exist_name:
                errors = '该实例名已存在！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': instanceform})
            elif is_exist_ip_port:
                errors = '该 IP、port 已经存在，请勿重复添加！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': instanceform})
            elif is_conn:
                errors = 'ooh，该实例连接失败,请验证用户名或密码是否正确 ！'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/change_instance.html', {'instanceform': instanceform})
            else:
                Instance.objects.filter(id=id).update(server_ip=server_ip, instance_name=instance_name,
                                                      ops_user=ops_user,
                                                      instance_username=instance_username,
                                                      instance_password=prpCryptor.encrypt(instance_password),
                                                      instance_port=instance_port,
                                                      project=project_name,
                                                      instance_env=instance_env,
                                                      instance_role=instance_role)

                is_exists_struct = InstanceStruct.objects.filter(instance_id=id).count()
                if is_exists_struct and instance_role == 'Main':
                    InstanceStruct.objects.filter(instance_id=id).delete()
                elif is_exists_struct and instance_role == 'Subordinate':
                    InstanceStruct.objects.filter(instance_id=id).update(main_host=subordinate_info[0], subordinate_type=subordinate_info[1],
                                                  subordinate_delay=subordinate_info[2], updatetime=timezone.now())
                else:
                    if len(subordinate_info):
                        instancestruct = InstanceStruct()
                        instancestruct.instance_id = id
                        instancestruct.main_host = subordinate_info[0]
                        instancestruct.main_port = subordinate_info[1]
                        instancestruct.subordinate_type = subordinate_info[2]
                        instancestruct.subordinate_delay = subordinate_info[3]
                        instancestruct.save()

                content_key = ['applicant', 'action', 'info']
                content_value = [get_name_by_id.get_name(request.user.id), '修改']
                info_key, info_value = [], []

                if not operator.eq((dataform.server_ip), data.get('server_ip')):
                    info_key.append('server_ip')
                    info_value.append(
                        {'before': dataform.server_ip, 'after': data.get('server_ip')})
                if not operator.eq(dataform.instance_name, data.get('instance_name')):
                    info_key.append('instance_name')
                    info_value.append({'before': dataform.instance_name, 'after': data.get('instance_name')})
                if not operator.eq(dataform.ops_user, data.get('ops_user')):
                    info_key.append('ops_user')
                    info_value.append({'before': dataform.ops_user, 'after': data.get('ops_user')})
                if not operator.eq(dataform.instance_username, data.get('instance_username')):
                    info_key.append('instance_username')
                    info_value.append({'before': dataform.instance_username, 'after': data.get('instance_username')})
                if not operator.eq(prpCryptor.decrypt(dataform.instance_password), data.get('instance_password')):
                    info_key.append('instance_password')
                    info_value.append("更新了密码")
                if not operator.eq(dataform.instance_port, int(data.get('instance_port'))):
                    info_key.append('instance_port')
                    info_value.append({'before': dataform.instance_port, 'after': int(data.get('instance_port'))})
                if not operator.eq(dataform.project, data.get('project_name')):
                    info_key.append('project_name')
                    info_value.append({'before': dataform.project, 'after':data.get('project_name')})
                if not operator.eq(dataform.instance_env, int(data.get('instance_env'))):
                    info_key.append('instance_env')
                    info_value.append({
                        'before': '生产环境' if dataform.instance_env == 1 else '测试环境' if dataform.instance_env == 2 else '开发环境',
                        'after': '生产环境' if int(data.get('instance_env')) == 1 else '测试环境' if int(
                            data.get('instance_env')) == 2 else '开发环境'})
                if not operator.eq(dataform.instance_type, data.get('instance_type')):
                    info_key.append('instance_type')
                    info_value.append({'before': dataform.instance_type.cate_name, 'after': data.get('instance_type')})
                content_value.append(dict(zip(info_key, info_value)))
                instancelog = InstanceLog()
                instancelog.instance_id = id
                instancelog.content = str(dict(zip(content_key, content_value)))
                instancelog.save()
                return render(request, 'database/instances.html')
        else:
            errors = modify_instance.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/change_instance.html', {'instanceform': instanceform})

    return render(request, 'database/change_instance.html', {"instanceform": instanceform})


@login_required
def instance_detail(request, id, process_id=0):
    """
    @author: qingyw
    @note: 实例管理 - 详情
    :param request:
    :param control: 变量用作控制
    :return:
    """
    from .funcs import get_processlist, kill_process, get_db_size, get_instance_size
    instance_info = Instance.objects.get(id=id)
    if process_id != 0:
        status = kill_process(instance_info.server_ip,
                              instance_info.instance_username,
                              prpCryptor.decrypt(instance_info.instance_password),
                              instance_info.instance_port,
                              process_id)
    if instance_info.instance_type.cate_name == 'MySQL':
        status, processlist_info = get_processlist(instance_info.server_ip,
                                                   instance_info.instance_username,
                                                   prpCryptor.decrypt(instance_info.instance_password),
                                                   instance_info.instance_port)
        if instance_info.instance_role == 'Main':
            subordinate_id = InstanceStruct.objects.filter(main_host=instance_info.server_ip,
                                                     main_port=instance_info.instance_port).values_list('instance_id',
                                                                                                          flat=True)
            subordinates = Instance.objects.filter(id__in=subordinate_id)
            subordinate_info = {'count': subordinates.count(), 'main': instance_info, 'subordinates': subordinates}
        elif instance_info.instance_role == 'Subordinate':
            main = InstanceStruct.objects.get(instance_id=instance_info.id)
            subordinate_id = InstanceStruct.objects.filter(main_host=main.main_host,
                                                     main_port=main.main_port).values_list('instance_id',
                                                                                                   flat=True)
            subordinates = Instance.objects.filter(id__in=subordinate_id)
            subordinate_info = {'count': subordinates.count(), 'main': main, 'subordinate': subordinates}
        else:
            processlist_info = ''
            subordinate_info = {}
    # db_size = get_db_size(instance_info.server_ip,
    #                       instance_info.instance_username,
    #                       prpCryptor.decrypt(instance_info.instance_password),
    #                       instance_info.instance_port)
    instance_size = get_instance_size(instance_info.server_ip,
                                      instance_info.instance_username,
                                      prpCryptor.decrypt(instance_info.instance_password),
                                      instance_info.instance_port)
    print(instance_size)
    instance_detail = {
        "line": instance_info,
        "processlist": processlist_info,
        "subordinate": subordinate_info,
        "instance": instance_size,
    }
    return render(request, 'database/instance_detail.html', instance_detail)


@login_required
@check_permission
def database_release_flow_view(request):
    """
    @author: Xieyz, qingyw
    @note: 数据库变更工作流
    :param request:
    :return: 数据库变更工作流列表
    """
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        groups = []
        if request.user.is_superuser:
            groups = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
            for group in list_group:
                project_info = project.objects.get(id=group)
                groups.append(group)
                groups.append(project.objects.get(
                    project=project_info.parent_project).id) if project_info.have_parent_project else ''
                if not project_info.have_parent_project:
                    groups.extend([entry for entry in
                                   project.objects.filter(parent_project=project_info.project).values_list('id',
                                                                                                           flat=True)])
        list_group = list(set(groups))
        if search:  # 判断是否有搜索字
            search = '%s' % search
            search = search.strip()
            all_records = Application.objects.filter((
                Q(appliant__last_name__icontains=search) |
                Q(appliant__first_name__icontains=search) |
                Q(appliant__username__icontains=search) |
                Q(application_type__icontains=search) |
                Q(project__project__icontains=search) |
                Q(instance__instance_name__icontains=search) |
                Q(application_content__icontains=search) |
                Q(appliant__last_name__icontains=search[0],
                  appliant__first_name__icontains=search[1:]) |
                Q(appliant__last_name__icontains=search[0:2],
                  appliant__first_name__icontains=search[2:])) &
                Q(project_id__in=list_group)
            ).exclude(is_delete=1)

            if search in '申请权限':
                all_records = Application.objects.filter(project_id__in=list_group, application_type=1).exclude(
                    is_delete=1)
            elif search in '新建用户':
                all_records = Application.objects.filter(project_id__in=list_group, application_type=2).exclude(
                    is_delete=1)
            elif search in '执行SQL':
                all_records = Application.objects.filter(project_id__in=list_group, application_type=3).exclude(
                    is_delete=1)
            elif search == '待审批':
                all_records = Application.objects.filter(project_id__in=list_group, application_status=1).exclude(
                    is_delete=1)
            elif search in '待执行':
                all_records = Application.objects.filter(Q(application_status=3) | Q(application_status=2),
                                                         project_id__in=list_group).exclude(
                    is_delete=1)
            elif search == '驳回':
                all_records = Application.objects.filter(project_id__in=list_group, application_status=0).exclude(
                    is_delete=1)
            elif search == '已执行':
                all_records = Application.objects.filter(project_id__in=list_group, application_status=4).exclude(
                    is_delete=1)
        else:
            all_records = Application.objects.filter(project_id__in=list_group).exclude(is_delete=1)  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'server_ip', 'instance_name', 'instance_username', 'instance_port',
                               'instance_env', ]:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for application in pageinator.page(pageNumber):
            try:
                appliant = get_name_by_id.get_name(application.appliant.id)
            except AttributeError:
                appliant = ''
            response_data['rows'].append({
                "id": application.id if application.id else "",
                "appliant": appliant if appliant else "",
                "application_type": application.get_application_type_display() if application.get_application_type_display() else "",
                "project": application.project.project if application.project.project else "",
                "instance": application.instance.instance_name if application.instance.instance_name else "",
                "application_content": strip_tags(application.application_content)[:10] if application.application_content else "",
                "application_time": application.application_time if application.application_time else "",
                "execute_time": application.execute_time if application.execute_time else "",
                "finished_time": application.finished_time if application.finished_time else "",
                "application_status": application.get_application_status_display() if application.get_application_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
        # return JsonResponse(response_data)

    return render(request, 'database/database_release_flow.html')


@login_required
@check_permission
def apply_sql(request):
    """
    @author: qingyw
    @note: 数据库变更-执行 SQL
    :param request:
    :param control: 变量用作控制
    :return:
    """
    if request.method == "POST":
        review_result = ''
        apply_sql = ApplySQLForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR, '请选择项目!')
            return render(request, 'database/apply_sql.html', {'applicationform': apply_sql})
        if apply_sql.is_valid():
            data = apply_sql.cleaned_data
            project_name = data.get('project_name')
            instance_name = data.get('instance_name')
            project_manager = data.get('project_manager')
            ops_user = data.get('ops_user')
            execute_sql = data.get('execute_sql')
            instance_info = Instance.objects.get(id=instance_name)
            host = instance_info.server_ip
            port = int(instance_info.instance_port)
            user = str(instance_info.instance_username)
            password = prpCryptor.decrypt(instance_info.instance_password)
            instance_type = str(instance_info.instance_type)
            if instance_type == 'MySQL':
                is_pass, review_result, result_type = inceptionDao.sql_review(execute_sql, host, port, user, password)
                if not is_pass:
                    errors = "SQL 存在语法错误，请先校验 SQL，无错误后提交！"
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'database/apply_sql.html', {'applicationform': apply_sql})
            elif instance_type == 'SQL SERVER':
                review_result = sqlserver_parse(execute_sql, host, port, user, password)
                if review_result != 'ok':
                    errors = "SQL 存在语法错误，请检查！"
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'database/apply_sql.html', {'applicationform': apply_sql})
            application_content = data.get('application_content')
            applicationform = Application()
            # 申请类型 1 申请权限 2 新建用户 3 执行 SQL
            applicationform.application_type = 3
            appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
            project_info = project.objects.get(id=project_name)
            if '客服人员' in appoint_user_list and (
                    project_info.project == '佰易系统' or str(project_info.parent_project) == '佰易系统'):
                applicationform.application_status = 2
            else:
                applicationform.application_status = 1
            applicationform.appliant = User.objects.get(id=request.user.id)
            applicationform.project_id = project_name
            applicationform.instance_id = instance_name
            applicationform.ops_user_id = ops_user
            applicationform.execute_sql = execute_sql
            applicationform.application_content = application_content
            applicationform.review_result = review_result
            applicationform.save()

            applicationid = Application.objects.latest('id')
            applicationlog = ApplicationLog()
            applicationlog.application_id = applicationid.id
            applicationlog.content = '{applicant:' + get_name_by_id.get_name(
                request.user.id) + ', action: 新增, info:申请执行SQL}'
            applicationlog.save()

            # 发送消息
            send_message(action='数据库变更申请', detail_id=applicationid.id)
            messages.add_message(request, messages.SUCCESS, '申请成功，请等待审批')
            if applicationform.application_status == 2:
                send_message(action='数据库变更申请审批', detail_id=applicationid.id, adopt='通过', sector='运维DBA')
            return HttpResponseRedirect(reverse('database_release_flow'))
        else:
            errors = apply_sql.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/apply_sql.html', {'applicationform': apply_sql})
    else:
        applicationform = ApplySQLForm()
    return render(request, 'database/apply_sql.html', {"applicationform": applicationform})


@login_required
@check_permission
def apply_new_user(request):
    """
    @author: qingyw
    @note: 数据库变更-新建用户
    :param request:
    :param control: 变量用作控制
    :return:
    """
    if request.method == "POST":
        apply_new_user = ApplyNewUserForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR, '请选择项目!')
            return render(request, 'database/apply_new_user.html', {'applicationform': apply_new_user})
        if apply_new_user.is_valid():
            execute_sql = ''
            data = apply_new_user.cleaned_data
            project_name = data.get('project_name')
            instance_name = data.get('instance_name')
            database_name = request.POST.getlist('database_name')
            table_name = request.POST.getlist('table_name')
            privileges = request.POST.getlist('privileges')
            ip_segment = data.get('ip_segment')
            if ip_segment == '0':
                messages.add_message(request, messages.ERROR, '请选择访问网段!')
                return render(request, 'database/apply_new_user.html', {'applicationform': apply_new_user})
            ops_user = data.get('ops_user')
            username = data.get('username')
            password = data.get('password')
            instance_info = Instance.objects.get(id=instance_name)
            application_content = data.get('application_content')
            if str(instance_info.instance_type) == 'MySQL':
                user_info = "CREATE USER '" + username + "'@'" + ip_segment + "'"
            elif str(instance_info.instance_type) == 'SQL SERVER':
                user_info = "CREATE LOGIN [" + username + "]"
            if is_exist_user(instance_info.server_ip, instance_info.instance_port,
                             str(instance_info.instance_username), prpCryptor.decrypt(instance_info.instance_password),
                             str(instance_info.instance_type), username, ip_segment):
                errors = "数据库已经存在该用户，请勿重复申请。"
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/apply_new_user.html', {'applicationform': apply_new_user})
            elif Application.objects.filter(execute_sql__startswith=user_info, is_delete=0).exclude(
                            Q(application_status=0) | Q(application_status=4)).count():
                errors = "该用户已经在申请中，请确认你的信息是否正确。"
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'database/apply_new_user.html', {'applicationform': apply_new_user})
            else:
                if str(instance_info.instance_type) == 'MySQL':
                    execute_sql = "CREATE USER '" + username + "'@'" + ip_segment + "' IDENTIFIED BY '" + password + "' ;\n"
                    if len(table_name):
                        for row in table_name:
                            db, tab = row.split('.')
                            execute_sql += "GRANT  " + ','.join(
                                privileges) + " ON `" + db + "`.`" + tab + "` TO '" + username + "'@'" + ip_segment + "' ;" + "\n"
                    else:
                        for db in database_name:
                            execute_sql += "GRANT  " + ','.join(
                                privileges) + " ON `" + db + "`.*" + " TO '" + username + "'@'" + ip_segment + "' ;" + "\n"
                elif str(instance_info.instance_type) == 'SQL SERVER':
                    execute_sql = "CREATE LOGIN [" + username + "] WITH PASSWORD = '" + password + "' , CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF ;" + "\n"
                    for db in database_name:
                        execute_sql += "USE [" + db + "];" + "CREATE USER [" + username + "] FOR LOGIN [" + username + "] ;" + "\n"
                        execute_sql += "GRANT  " + ','.join(
                            privileges) + " TO [" + username + "] ;" + "\n"
                applicationform = Application()
                # 申请类型 1 申请权限 2 新建用户 3 执行 SQL
                applicationform.application_type = 2
                applicationform.application_status = 1
                applicationform.appliant = User.objects.get(id=request.user.id)
                applicationform.project_id = project_name
                applicationform.instance_id = instance_name
                applicationform.database_name = database_name
                applicationform.ops_user_id = ops_user
                applicationform.execute_sql = execute_sql
                applicationform.application_content = application_content
                applicationform.save()

                applicationid = Application.objects.latest('id')
                applicationlog = ApplicationLog()
                applicationlog.application_id = applicationid.id
                applicationlog.content = '{applicant: ' + get_name_by_id.get_name(
                    request.user.id) + ', action: 新增, info:申请新建用户 ' + username + ', 并申请' + ','.join(
                    database_name) + " 数据库 " + ', '.join(privileges) + " 权限}"
                applicationlog.save()

            # 发送消息
            send_message(action='数据库变更申请', detail_id=applicationid.id)
            messages.add_message(request, messages.SUCCESS, '申请成功，请等待审批')
            return HttpResponseRedirect(reverse('database_release_flow'))
        else:
            errors = apply_new_user.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/apply_new_user.html', {'applicationform': apply_new_user})
    else:
        applicationform = ApplyNewUserForm()
    return render(request, 'database/apply_new_user.html', {"applicationform": applicationform})


@login_required
@check_permission
def apply_privilege(request):
    """
    @author: qingyw
    @note: 数据库变更-添加授权
    :param request:
    :param control: 变量用作控制
    :return:
    """
    if request.method == "POST":
        apply_priv = ApplyPrivilegeForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return render(request, 'database/apply_privilege.html', {'applicationform': apply_priv})
        # print(apply_priv)
        # print(apply_priv.is_valid())
        if apply_priv.is_valid():
            data = apply_priv.cleaned_data
            project_name = data.get('project_name')
            instance_name = data.get('instance_name')
            instance_info = Instance.objects.get(id=instance_name)
            database_name = request.POST.getlist('database_name')
            table_name = request.POST.getlist('table_name')
            # print(database_name)
            username = request.POST.getlist('username')
            privileges = request.POST.getlist('privileges')
            ops_user = data.get('ops_user')
            application_content = data.get('application_content')
            execute_sql = ""
            # for db in database_name
            if str(instance_info.instance_type) == 'MySQL':
                if len(table_name):
                    for row in table_name:
                        db, tab = row.split('.')
                        for user in username:
                            execute_sql += "GRANT  " + ','.join(privileges) + " ON `" + db + "`.`" + tab + "` TO " + user + " ; \n"
                else:
                    for db in database_name:
                        for user in username:
                            execute_sql += "GRANT  " + ','.join(privileges) + " ON `" + db + "`.*" + " TO " + user + " ; \n"
            elif str(instance_info.instance_type) == 'SQL SERVER':
                for db in database_name:
                    for user in username:
                        execute_sql += "USE [" + db + "]; \n IF USER_ID('" + user + "') IS NULL CREATE USER [" + user + \
                                       "] FOR LOGIN [" + user + "] ;\n GRANT  " + ','.join(
                                        privileges) + " TO [" + user + "] ;" + "\n"
                # for db in database_name:
            # print(execute_sql)
            applicationform = Application()
            # 申请类型 1 申请权限 2 新建用户 3 执行 SQL
            applicationform.application_type = 1
            applicationform.application_status = 1
            applicationform.appliant = User.objects.get(id=request.user.id)
            applicationform.project_id = project_name
            applicationform.instance_id = instance_name
            applicationform.database_name = database_name
            applicationform.ops_user_id = ops_user
            applicationform.execute_sql = execute_sql
            applicationform.application_content = application_content
            applicationform.save()

            applicationid = Application.objects.latest('id')
            applicationlog = ApplicationLog()
            applicationlog.application_id = applicationid.id
            applicationlog.content = '{applicant: ' + get_name_by_id.get_name(request.user.id) + ', action: 新增, info: 为' + ','.join(
                username) + ' 申请 ' + ','.join(database_name) + " 数据库 " + ','.join(privileges) + " 权限}"
            applicationlog.save()

            # 发送消息
            send_message(action='数据库变更申请', detail_id=applicationid.id)
            messages.add_message(request, messages.SUCCESS, '申请成功，请等待审批')
            return HttpResponseRedirect(reverse('database_release_flow'))
        else:
            errors = apply_priv.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/apply_privilege.html', {'applicationform': apply_priv})
    else:
        applicationform = ApplyPrivilegeForm()
    return render(request, 'database/apply_privilege.html', {"applicationform": applicationform})


@login_required
def database_release_delete(request, id):
    """
   @author: Xieyz
   @note: 数据库变更工作流删除
   :param request:
   :param id: Application表的ID
   :return:
   """
    del_judge_obj = Application.objects.get(id=id)
    if (del_judge_obj.application_status == 1 or del_judge_obj.application_status == 0) and del_judge_obj.appliant == request.user:
        Application.objects.filter(id=id).update(is_delete=1)
        delete_log = ApplicationLog()
        delete_log.application_id = id
        delete_log.content = "{操作人: " + get_name_by_id.get_name(request.user.id) + ", action: 删除申请流}"
        delete_log.save()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.application_status != 1 or del_judge_obj.application_status != 0:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.appliant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def database_release_detail_view(request, id):
    update_execute_result = Application.objects.get(id=id)
    if update_execute_result.is_delete:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('database_release_flow'))
    else:
        if request.method == "POST":
            getdataform = SQLForm(request.POST)
            getrebackform = rebackForm(request.POST)
            edit_sql = Application.objects.get(id=id)
            if getdataform.has_changed() and getdataform.is_valid():
                if edit_sql.application_status == 0 or edit_sql.application_status == 1:
                    data = getdataform.data
                    # update_execute_result = Application.objects.get(id=id)
                    if not operator.eq(data.get('exec_sql'), update_execute_result.execute_sql):
                        # 更新日志
                        instance_info = Instance.objects.get(id=update_execute_result.instance_id)
                        host = instance_info.server_ip
                        port = int(instance_info.instance_port)
                        user = str(instance_info.instance_username)
                        password = prpCryptor.decrypt(instance_info.instance_password)
                        instance_type = str(instance_info.instance_type)
                        if instance_type == 'MySQL':
                            is_pass, review_result, result_type = inceptionDao.sql_review(data.get('exec_sql'), host, port, user, password)
                            if not is_pass:
                                errors = "SQL 存在语法错误，请先查看校验结果！"
                                messages.add_message(request, messages.ERROR, errors)
                                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')

                        elif instance_type == 'SQL SERVER':
                            review_result = sqlserver_parse(data.get('exec_sql'), host, port, user, password)
                            if review_result != 'ok':
                                errors = "SQL 存在语法错误，请检查！"
                                messages.add_message(request, messages.ERROR, errors)
                                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
                        update_logs = ApplicationLog()
                        update_logs.application_id = id
                        update_logs.content = "{applicant: " + get_name_by_id.get_name(
                            request.user.id) + ", action: 修改 SQL, info: {before: '" \
                            + update_execute_result.execute_sql.replace('\r', '').replace('\n', '') + \
                            "', after: '" + data.get('exec_sql').replace('\r', '').replace('\n', '') + "'}"

                        update_execute_result.execute_sql = data.get('exec_sql')
                        update_execute_result.review_result = review_result
                        appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
                        if '客服人员' in appoint_user_list and (
                                update_execute_result.project.project == '佰易系统' or str(
                                update_execute_result.project.parent_project) == '佰易系统'):
                            update_execute_result.application_status = 2
                        else:
                            update_execute_result.application_status = 1
                        update_execute_result.save()
                        update_logs.save()
                        return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
                else:
                    messages.add_message(request, messages.ERROR, '状态已改变，请刷新页面查看!')
                    request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                    return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
            if getrebackform.has_changed() and getrebackform.is_valid():
                # if update_execute_result.project.project_manager.id != request.user.id:
                #     messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                #     request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                #     return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
                data = getrebackform.cleaned_data
                reback = Application.objects.get(id=id)

                if reback.application_status == 1:
                    project_manager = project_group.objects.filter(project=reback.project,
                                                                   user_type=Group.objects.get(name='项目经理')).values_list(
                        'user', flat=True)
                    if not (request.user.id in project_manager or reback.project.project_manager.id == request.user.id):
                            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                            return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')

                if reback.application_status == 2:
                    if reback.ops_user.id != request.user.id:
                        messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                        return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')

                if reback.application_status == 0 or reback.application_status > 3:
                    messages.add_message(request, messages.ERROR, '状态已改变，请刷新页面查看!')
                    request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                    return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
                else:
                    reback.reback_reason = data.get('reback_reason')
                    reback.application_status = 0
                    update_logs = ApplicationLog()
                    update_logs.application_id = id
                    update_logs.content = "{操作人: " + get_name_by_id.get_name(request.user.id) + ", action: 驳回申请, info: {"+ data.get('reback_reason') + "}"
                    reback.save()
                    update_logs.save()
                    send_message(action='数据库变更申请审批', detail_id=id, adopt='不通过')
                    return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')

        application_info = Application.objects.get(id=id)
        project_manager = [get_name_by_id.get_name(id) for id in
                           project_group.objects.filter(project=application_info.project,
                                                        user_type=Group.objects.get(name='项目经理')).values_list('user',
                                                                                                              flat=True)]
        log = ApplicationLog.objects.filter(application_id=id).order_by('-createtime')
        debriefing = Application.objects.only('execute_result').get(id=id).execute_result
        exec_sql = Application.objects.only('execute_sql').get(id=id).execute_sql
        review_result = Application.objects.only('review_result').get(id=id).review_result
        if review_result:
            if review_result != 'ok':
                review_result = ast.literal_eval(review_result)
                # review_result = review_result

        releasetestreportform = DebriefingForm(  # 测试报告表单
            initial={
                'content': debriefing,
            })
        sqlform = SQLForm(  # 测试报告表单
            initial={
                'exec_sql': exec_sql,
            })
        rebackform = rebackForm()
        instance_detail = {
            "line": application_info,
            "flow_log": log,
            "form": releasetestreportform,
            "sql": sqlform,
            "reback": rebackform,
            "review_result": review_result,
            "project_manager": project_manager,
        }
        return render(request, 'database/database_release_detail.html', instance_detail)


@login_required
@check_permission
def database_release_approval_view(request, id, control):
    """
    @author: Xieyz qingyw
    @note: 数据库变更审批
    :param request:
    :param id: Application表的id
    :param control: 变量用作控制
    :return:
    """
    approval_content = ''
    application = Application.objects.get(id=id)
    application_log = ApplicationLog()
    login_name = get_name_by_id.get_name(request.user.id)
    if application.is_delete == 1:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('database_release_flow'))
    else:
        if control == 2:
            project_manager = project_group.objects.filter(project=application.project,
                                                           user_type=Group.objects.get(name='项目经理')).values_list(
                'user', flat=True)

            if application.application_status >= 2 or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '已经被审批！')
                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
            if request.user.id in project_manager or application.project.project_manager.id == request.user.id:
                approval_content = '项目经理审批：' + login_name + '同意'
                # 发送消息
                send_message(action='数据库变更申请审批', detail_id=id, adopt='通过', sector='运维DBA')
            else:
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')

        if control == 3:
            if application.application_status >= 3 or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '已经被审批！')
                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
            approval_content = '运维DBA审批：' + login_name + '同意'
            # 发送消息
            send_message(action='数据库变更申请审批通过', detail_id=id)

        if control <= 3:
            application.application_status = control
            application.save()
            application_log.application_id = id
            application_log.content = approval_content
            application_log.save()

        if control == 4:
            if application.application_status >= 4 or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '这条工作流已经被执行！')
                return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')
            instance_name = str(application.instance)
            instance_info = Instance.objects.get(instance_name=instance_name)
            # 异步执行sql

            async_execute_sql.delay(application.id,
                                    login_name,
                                    instance_info.server_ip,
                                    str(instance_info.instance_username),
                                    prpCryptor.decrypt(instance_info.instance_password),
                                    int(instance_info.instance_port),
                                    str(instance_info.instance_type),
                                    str(application.execute_sql),
                                    )
            time.sleep(0.1)

    return HttpResponseRedirect('/database/instance/release_flow/release_detail/' + str(id) + '/')


@login_required
@check_permission
def sql_alert(request, id=0):
    groups = []
    if id != 0:
        # if request.user.is_superuser:
        #     groups = project.objects.filter(status=9).values_list('id', flat=True)
        # else:
        #     groups = [entry for entry in
        #               project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
        sql_alert = SQLAlert.objects.get(id=id)
        if request.user.is_superuser or sql_alert.applicant.id == request.user.id:
            sql_alert.is_delete = 1
            sql_alert.save()
            if sql_alert.periodic_task:
                PeriodicTask.objects.filter(name=sql_alert.title).delete()
            sql_alert_log = SQLAlertLog()
            sql_alert_log.sql_alert_id = id
            sql_alert_log.content = get_name_by_id.get_name(request.user.id) + ': 删除预警任务'
            sql_alert_log.save()
            send_message(action='预警SQL删除操作', detail_id=id)
        else:
            messages.add_message(request, messages.ERROR, '没有权限删除该预警SQL！')
        return HttpResponseRedirect(reverse('sql_alert'))

    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序

        if request.user.is_superuser:
            groups = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
            for group in list_group:
                project_info = project.objects.get(id=group)
                groups.append(group)
                groups.append(project.objects.get(
                    project=project_info.parent_project).id) if project_info.have_parent_project else ''
                if not project_info.have_parent_project:
                    groups.extend([entry for entry in
                                   project.objects.filter(parent_project=project_info.project).values_list('id',
                                                                                                           flat=True)])
        list_group = list(set(groups))
        if search:  # 判断是否有搜索字
            search = search.strip()
            all_records = SQLAlert.objects.filter((
                Q(title__icontains=search) |
                Q(project__project__icontains=search) |
                Q(instance__instance_name__icontains=search) |
                Q(applicant__last_name__icontains=search[0],
                  applicant__first_name__icontains=search[1:]) |
                Q(applicant__last_name__icontains=search[0:1],
                  applicant__first_name__icontains=search[2:])) &
                Q(project_id__in=list_group)
            ).exclude(is_delete=1)
        else:
            all_records = SQLAlert.objects.filter(project_id__in=list_group).exclude(is_delete=1)  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'project', 'instance']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        time_unit = {
            1: 'seconds',
            2: 'minutes',
            3: 'hours',
            4: 'days',
        }
        response_data = {'total': all_records_count, 'rows': []}
        for sqlalert in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(sqlalert.applicant.id)
            except AttributeError:
                applicant = ''
            response_data['rows'].append({
                "id": sqlalert.id if sqlalert.id else "",
                "applicant": applicant if applicant else "",
                "title": sqlalert.title[:20] if sqlalert.title else "",
                "carbon_copy": ", ".join(get_name_by_id.get_name(User.objects.get(id=user_id).id) for user_id in
                                         sqlalert.carbon_copy.split(',')) if sqlalert.carbon_copy else "",
                "project": sqlalert.project.project if sqlalert.project.project else "",
                "instance": sqlalert.instance.instance_name if sqlalert.instance.instance_name else "",
                "start_time": sqlalert.start_time if sqlalert.start_time else "",
                "schedule": 'every ' + str(sqlalert.interval) + ' ' + time_unit[sqlalert.interval_unit] if sqlalert.interval else "",
                "total_run_count": sqlalert.periodic_task.total_run_count if sqlalert.periodic_task else '',
                "last_run_at": sqlalert.periodic_task.last_run_at if sqlalert.periodic_task else '',
                "application_time": sqlalert.application_time if sqlalert.application_time else '',
                "application_status": sqlalert.application_status if sqlalert.application_status <= 3 else str(sqlalert.periodic_task.enabled),
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'database/sqlalert.html')


@login_required
def sql_alert_log(request, id):
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        all_records = SQLAlertLog.objects.filter(sql_alert_id=id)
        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'create_time', 'content']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % sort_column
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()
        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 5  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for sqlalert_log in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": sqlalert_log.id if sqlalert_log.id else "",
                "content": sqlalert_log.content[:100] + '...' if len(sqlalert_log.content) > 99 else sqlalert_log.content,
                "create_time": sqlalert_log.create_time if sqlalert_log.create_time else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))


@login_required
@check_permission
def apply_sql_alert(request):
    if request.method == 'POST':
        sql_alert = SQLAlertForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR, '请选择项目!')
            return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
        if sql_alert.is_valid():
            data = sql_alert.cleaned_data
            title = data.get('title')
            project_id = data.get('project_name')
            instance_id = data.get('instance_name')
            carbon_copy = request.POST.getlist('carbon_copy') if request.POST.getlist('carbon_copy') else ''
            interval = data.get('interval')
            interval_unit = data.get('interval_unit')
            start_time = data.get('start_time')
            sql = data.get('sql')
            application_content = data.get('application_content')
            list_key = ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE']
            for key in list_key:
                if key in sql.upper():
                    messages.add_message(request, messages.ERROR, '仅限 SELECT 查询语句!')
                    return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
            if PeriodicTask.objects.filter(name=title) or SQLAlert.objects.filter(title=title, is_delete=0):
                messages.add_message(request, messages.ERROR, '已存在相同 title 的任务，请勿重复提交！')
                return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
            instance_info = Instance.objects.get(id=instance_id)
            host = instance_info.server_ip
            port = int(instance_info.instance_port)
            user = str(instance_info.instance_username)
            password = prpCryptor.decrypt(instance_info.instance_password)
            instance_type = str(instance_info.instance_type)
            if instance_type == 'MySQL':
                is_pass, review_result, result_type = inceptionDao.sql_review(sql, host, port, user, password)
                if not is_pass:
                    errors = "SQL 存在语法错误，请先校验 SQL，无错误后提交！"
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
            elif instance_type == 'SQL SERVER':
                review_result = sqlserver_parse(sql, host, port, user, password)
                if review_result != 'ok':
                    errors = "SQL 存在语法错误，请检查！"
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
            sqlalert = SQLAlert()
            sqlalert.title = title
            sqlalert.instance_id = instance_id
            sqlalert.project_id = project_id
            sqlalert.carbon_copy = ','.join(carbon_copy)
            sqlalert.interval = interval
            sqlalert.interval_unit = interval_unit
            sqlalert.sql = sql
            sqlalert.start_time = start_time
            sqlalert.applicant = User.objects.get(id=request.user.id)
            sqlalert.application_content = application_content
            sqlalert.application_status = 1
            sqlalert.review_result = review_result
            sqlalert.save()

            sqlalertid = SQLAlert.objects.latest('id')
            sqlalertlog = SQLAlertLog()
            sqlalertlog.sql_alert_id = sqlalertid.id
            sqlalertlog.content = '{applicant:' + get_name_by_id.get_name(
                request.user.id) + ', action: 新增, info:申请-添加预警 SQL}'
            sqlalertlog.save()
            # 发送消息
            send_message(action='数据预警SQL申请', detail_id=sqlalertid.id)
            messages.add_message(request, messages.SUCCESS, '申请成功，请等待审批')
            return HttpResponseRedirect(reverse('sql_alert'))
        else:
            errors = sql_alert.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/apply_sql_alert.html', {'sqlalertform': sql_alert})
    else:
        sqlalertform = SQLAlertForm()
    return render(request, 'database/apply_sql_alert.html', {"sqlalertform": sqlalertform})

@login_required
@check_permission
def sqlalert_approval(request, id, control):
    """
    @author: qingyw
    @note: 数据预警 SQL 审批流
    :param request:
    :param id: sql_alert_id
    :param control: 变量用作控制
    :return:
    """
    approval_content = ''
    application = SQLAlert.objects.get(id=id)
    application_log = SQLAlertLog()
    login_name = get_name_by_id.get_name(request.user.id)
    if application.is_delete == 1:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('sql_alert'))
    else:
        if control == 2:
            project_manager = project_group.objects.filter(project=application.project,
                                                           user_type=Group.objects.get(name='项目经理')).values_list(
                'user', flat=True)

            if application.application_status >= 2 or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '已经被审批！')
                return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
            if request.user.id in project_manager or application.project.project_manager.id == request.user.id:
                approval_content = '项目经理审批：' + login_name + '同意'
                # 发送消息
                send_message(action='数据预警SQL申请审批', detail_id=id, adopt='通过', sector='运维DBA')
            else:
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')

        if control == 3:
            if application.application_status >= 3 or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '已经被审批！')
                return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
            approval_content = '运维DBA审批：' + login_name + '同意'
            # 发送消息
            send_message(action='数据预警SQL申请审批通过', detail_id=id)

        application.application_status = control
        application.save()

        application_log.sql_alert_id = id
        application_log.content = approval_content
        application_log.save()
    return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')


@login_required
@check_permission
def sqlalert_enable(request, id, control):
    approval_content = ''
    application = SQLAlert.objects.get(id=id)
    application_log = SQLAlertLog()
    login_name = get_name_by_id.get_name(request.user.id)
    if application.is_delete == 1:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('sql_alert'))
    else:
        if control == 4:
            if application.periodic_task:
                if application.periodic_task.enabled or application.application_status == 0:
                    messages.add_message(request, messages.ERROR, '该条工作流状态已更改，请刷新')
                    return HttpResponseRedirect(reverse('sql_alert'))
            time_unit = {
                1: 'seconds',
                2: 'minutes',
                3: 'hours',
                4: 'days',
            }
            if application.periodic_task:
                periodic_task = PeriodicTask.objects.get(name=application.title)
                periodic_task.enabled = True
            else:
                schedule, created = IntervalSchedule.objects.get_or_create(every=application.interval,
                                                                           period=time_unit[application.interval_unit], )
                periodic_task = PeriodicTask.objects.create(
                    interval=schedule,
                    name=application.title,
                    task='database.tasks.async_exec_sqlalert',
                    kwargs=json.dumps({
                        'sql_alert_id': application.id,
                    }),
                )
            periodic_task.save()
            application.periodic_task = periodic_task
            application.start_time = timezone.now()
            approval_content = login_name + ': 预警任务已启用'
            send_message(action='数据预警SQL已启用', detail_id=id)

        if control == 5:
            if (not application.periodic_task.enabled) or application.application_status == 0:
                messages.add_message(request, messages.ERROR, '该条工作流状态已更改，请刷新')
                return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
            periodic_task = PeriodicTask.objects.get(name=application.title)
            periodic_task.enabled = False
            periodic_task.save()
            approval_content = login_name + ': 预警任务已停用'
            send_message(action='数据预警SQL已停用', detail_id=id)
        application.application_status = control
        application.save()
        application_log.sql_alert_id = id
        application_log.content = approval_content
        application_log.save()
    return HttpResponseRedirect(reverse('sql_alert'))


@login_required
@check_permission
def sqlalert_detail(request, id):
    sqlalert = SQLAlert.objects.get(id=id)
    if sqlalert.is_delete:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('sql_alert'))
    else:
        if request.method == "POST":
            getdataform = SQLForm(request.POST)
            getrebackform = rebackForm(request.POST)
            if getdataform.has_changed() and getdataform.is_valid():
                data = getdataform.data
                # update_execute_result = Application.objects.get(id=id)
                if not operator.eq(data.get('exec_sql'), sqlalert.sql):
                    # 更新日志
                    instance_info = Instance.objects.get(id=sqlalert.instance_id)
                    host = instance_info.server_ip
                    port = int(instance_info.instance_port)
                    user = str(instance_info.instance_username)
                    password = prpCryptor.decrypt(instance_info.instance_password)
                    instance_type = str(instance_info.instance_type)
                    if instance_type == 'MySQL':
                        is_pass, review_result, result_type = inceptionDao.sql_review(data.get('exec_sql'), host, port, user, password)
                        if not is_pass:
                            errors = "SQL 存在语法错误，请先查看校验结果！"
                            messages.add_message(request, messages.ERROR, errors)
                            return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')

                    elif instance_type == 'SQL SERVER':
                        review_result = sqlserver_parse(data.get('exec_sql'), host, port, user, password)
                        if review_result != 'ok':
                            errors = "SQL 存在语法错误，请检查！"
                            messages.add_message(request, messages.ERROR, errors)
                            return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
                    update_logs = SQLAlertLog()
                    update_logs.sql_alert_id = id
                    update_logs.content = "{applicant: " + get_name_by_id.get_name(
                        request.user.id) + ", action: 修改 SQL, info: {before: '" \
                        + sqlalert.execute_sql.replace('\r', '').replace('\n', '') + \
                        "', after: '" + data.get('exec_sql').replace('\r', '').replace('\n', '') + "'}"

                    sqlalert.sql = data.get('exec_sql')
                    sqlalert.review_result = review_result
                    sqlalert.save()
                    update_logs.save()
                    return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
            if getrebackform.has_changed() and getrebackform.is_valid():
                data = getrebackform.cleaned_data
                reback = SQLAlert.objects.get(id=id)

                if reback.application_status == 1:
                    project_manager = project_group.objects.filter(project=reback.project,
                                                                   user_type=Group.objects.get(name='项目经理')).values_list(
                        'user', flat=True)
                    if not (request.user.id in project_manager or reback.project.project_manager.id == request.user.id):
                            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                            return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')

                if reback.application_status == 2:
                    dba = Group.objects.get(name='运维DBA').user_set.all()
                    if not(request.user.is_superuser or request.user.id in dba):
                        messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                        return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')

                if reback.application_status == 0 or reback.application_status > 3:
                    messages.add_message(request, messages.ERROR, '状态已改变，请刷新页面查看!')
                    request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                    return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')
                else:
                    reback.reback_reason = data.get('reback_reason')
                    reback.application_status = 0
                    update_logs = SQLAlertLog()
                    update_logs.sql_alert_id = id
                    update_logs.content = "{操作人: " + get_name_by_id.get_name(
                        request.user.id) + ", action: 驳回申请, info: {" + data.get('reback_reason') + "}"
                    reback.save()
                    update_logs.save()
                    send_message(action='数据预警SQL申请审批', detail_id=id, adopt='不通过')
                    return HttpResponseRedirect('/database/instance/sqlalert/release_detail/' + str(id) + '/')

        application_info = SQLAlert.objects.get(id=id)
        project_manager = [get_name_by_id.get_name(id) for id in
                           project_group.objects.filter(project=application_info.project,
                                                        user_type=Group.objects.get(name='项目经理')).values_list('user',
                                                                                                              flat=True)]
        log = SQLAlertLog.objects.filter(sql_alert_id=id).order_by('-create_time')
        exec_sql = SQLAlert.objects.only('sql').get(id=id).sql
        review_result = SQLAlert.objects.only('review_result').get(id=id).review_result
        # periodic_task = application_info.periodic_task if application_info.application_status >= 4 else ''
        if review_result:
            if review_result != 'ok':
                review_result = ast.literal_eval(review_result)
                # review_result = review_result

        sqlform = SQLForm(  # 测试报告表单
            initial={
                'exec_sql': exec_sql,
            })
        rebackform = rebackForm()
        cc = ", ".join(get_name_by_id.get_name(User.objects.get(id=user_id).id) for user_id in
                  sqlalert.carbon_copy.split(',')) if sqlalert.carbon_copy else "",
        sqlalert_detail = {
            "line": application_info,
            "flow_log": log,
            "sql": sqlform,
            "reback": rebackform,
            "review_result": review_result,
            "project_manager": project_manager,
            # "periodic_task": periodic_task,
            "carbon_copy": cc,
        }
        return render(request, 'database/sqlalert_detail.html', sqlalert_detail)


@login_required
def sqlalert_onverify(request, id):
    if request.method == 'POST':
        msg = '预警SQL数据报警'
        sql_alert = SQLAlert.objects.get(id=id)
        instance_info = Instance.objects.get(id=sql_alert.instance_id)

        status, result = exec_sqlalert(instance_info.server_ip,
                                       str(instance_info.instance_username),
                                       prpCryptor.decrypt(instance_info.instance_password),
                                       int(instance_info.instance_port),
                                       str(instance_info.instance_type),
                                       str(sql_alert.sql), )
        application_log = SQLAlertLog()
        application_log.sql_alert_id = id
        application_log.content = get_name_by_id.get_name(
            request.user.id) + '手动执行: ' + (result if result else '没有查询到相关数据')
        application_log.save()
        if status:
            send_message(action=msg, detail_id=id)
        return JsonResponse({'status': status, 'result': result[:30]})


@login_required
@check_permission
def data_migrate(request, id=0):
    groups = []
    if id != 0:
        # if request.user.is_superuser:
        #     groups = project.objects.filter(status=9).values_list('id', flat=True)
        # else:
        #     groups = [entry for entry in
        #               project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
        data_migrate = DataMigrate.objects.get(id=id)
        if request.user.is_superuser or data_migrate.applicant.id == request.user.id:
            data_migrate.is_delete = 1
            data_migrate.save()
            data_migrate_log = DataMigrateLog()
            data_migrate_log.data_migrate_id = id
            data_migrate_log.content = get_name_by_id.get_name(request.user.id) + ': 删除数据迁移申请'
            data_migrate_log.save()
        else:
            messages.add_message(request, messages.ERROR, '没有权限删除该申请！')
        return HttpResponseRedirect(reverse('data_migrate'))

    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序

        if request.user.is_superuser:
            groups = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
            for group in list_group:
                project_info = project.objects.get(id=group)
                groups.append(group)
                groups.append(project.objects.get(
                    project=project_info.parent_project).id) if project_info.have_parent_project else ''
                if not project_info.have_parent_project:
                    groups.extend([entry for entry in
                                   project.objects.filter(parent_project=project_info.project).values_list('id',
                                                                                                           flat=True)])
        list_group = list(set(groups))
        if search:  # 判断是否有搜索字
            search = search.strip()
            all_records = SQLAlert.objects.filter((
                Q(title__icontains=search) |
                Q(project__project__icontains=search) |
                Q(instance__instance_name__icontains=search) |
                Q(applicant__last_name__icontains=search[0],
                  applicant__first_name__icontains=search[1:]) |
                Q(applicant__last_name__icontains=search[0:1],
                  applicant__first_name__icontains=search[2:])) &
                Q(project_id__in=list_group)
            ).exclude(is_delete=1)
        else:
            all_records = DataMigrate.objects.filter(project_id__in=list_group).exclude(is_delete=1)  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'project', 'instance']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for migration in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(migration.applicant.id)
            except AttributeError:
                applicant = ''
            response_data['rows'].append({
                "id": migration.id if migration.id else "",
                "applicant": applicant if applicant else "",
                "title": migration.title[:20] if migration.title else "",
                "project": migration.project.project if migration.project.project else "",
                "origin_instance": migration.origin_instance.instance_name if migration.origin_instance.instance_name else "",
                "target_instance": migration.target_instance.instance_name if migration.target_instance.instance_name else "",
                "origin_db": migration.origin_db[:20] + '...' if len(migration.origin_db) > 20 else migration.origin_db,
                "target_db": migration.target_db[:20] + '...' if len(migration.target_db) > 20 else migration.target_db,
                "origin_tab": migration.origin_tab[:20] + '...' if len(migration.origin_tab) > 20 else migration.origin_tab,
                "application_time": migration.application_time if migration.application_time else '',
                "application_status": migration.application_status if migration.application_status else '',
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'database/datamigrate.html')


@login_required
def data_migrate_log(request, id):
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        all_records = DataMigrateLog.objects.filter(data_migrate_id=id)
        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'create_time', 'content']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % sort_column
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        all_records_count = all_records.count()
        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 5  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for data_migrate_log in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": data_migrate_log.id if data_migrate_log.id else "",
                "content": data_migrate_log.content[:100] + '...' if len(data_migrate_log.content) > 99 else data_migrate_log.content,
                "create_time": data_migrate_log.create_time if data_migrate_log.create_time else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))


@login_required
@check_permission
def apply_data_migrate(request):
    if request.method == 'POST':
        data_migrate = DataMigrateForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR, '请选择项目!')
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
        if not request.POST.get('origin_instance'):
            messages.add_message(request, messages.ERROR, '请选择源实例!')
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
        if not request.POST.get('target_instance'):
            messages.add_message(request, messages.ERROR, '请选择目标实例!')
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
        if not request.POST.get('origin_db'):
            messages.add_message(request, messages.ERROR, '请选择源数据库!')
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
        if not request.POST.get('origin_tab'):
            messages.add_message(request, messages.ERROR, '请选择源数据库表!')
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
        if data_migrate.is_valid():
            data = data_migrate.cleaned_data
            title = data.get('title')
            project_id = data.get('project_name')
            origin_instance = request.POST.get('origin_instance')
            target_instance = request.POST.get('target_instance')
            origin_db = request.POST.getlist('origin_db')
            target_db = request.POST.get('target_db')
            origin_tab = request.POST.getlist('origin_tab')
            is_export_data = data.get('is_export_data')
            application_content = data.get('application_content')
            origin_instance = Instance.objects.get(id=origin_instance)
            target_instance = Instance.objects.get(id=target_instance)
            if origin_instance.instance_type.cate_name != 'MySQL' or target_instance.instance_type.cate_name != 'MySQL':
                    errors = "当前只支持 MySQL 数据库迁移！"
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
            migration = DataMigrate()
            export_option = request.POST.getlist('export_option')
            for opt in export_option:
                if opt == '0':
                    migration.is_export_routine = 1
                elif opt == '1':
                    migration.is_export_event = 1
                elif opt == '2':
                    migration.is_export_target = 1
                elif opt == '3':
                    migration.is_export_view = 1
            migration.is_new_db = (0 if len(target_db) else 1)
            migration.title = title
            migration.project_id = project_id
            migration.origin_instance = origin_instance
            migration.target_instance = target_instance
            migration.origin_db = ','.join(origin_db)
            migration.target_db = target_db
            migration.origin_tab = ','.join(origin_tab)
            migration.is_export_data = is_export_data
            migration.applicant = User.objects.get(id=request.user.id)
            migration.application_content = application_content
            migration.application_status = 1
            migration.save()

            migrationid = DataMigrate.objects.latest('id')
            migrationlog = DataMigrateLog()
            migrationlog.data_migrate_id = migrationid.id
            migrationlog.content = get_name_by_id.get_name(
                request.user.id) + '申请将 ' + origin_instance.instance_name + ' 实例的 ' + ','.join(
                origin_db) + ' 的' + '\n'.join(
                origin_tab) + '表，迁移至 ' + target_instance.instance_name + '实例的' + target_db
            migrationlog.save()
            #发送消息
            send_message(action='数据迁移申请', detail_id=migrationid.id)
            messages.add_message(request, messages.SUCCESS, '申请成功，请等待审批')
            return HttpResponseRedirect(reverse('data_migrate'))
        else:
            errors = data_migrate.errors
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'database/apply_data_migrate.html', {'datamigrateform': data_migrate})
    else:
        datamigrateform = DataMigrateForm()
    return render(request, 'database/apply_data_migrate.html', {'datamigrateform': datamigrateform})


@login_required
@check_permission
def datamigrate_detail(request, id):
    migration = DataMigrate.objects.get(id=id)
    migrate_log = []

    for log in DataMigrateLog.objects.filter(data_migrate=migration).order_by('-create_time'):
        migrate_log.append([log.create_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'), log.content])
    if migration.is_delete:
        messages.add_message(request, messages.ERROR, '该申请已经被删除！')
        return HttpResponseRedirect(reverse('data_migrate'))
    else:
        applicant = get_name_by_id.get_name(migration.applicant.id)
        APPLICATION_STATUS_CHOICES = {
            0: u'驳回',
            1: u'待审批',
            2: u'项目经理审批通过',
            3: u'运维DBA审批通过',
            4: u'迁移中',
            5: u'已完成',
        }
        data_migrate_detail = {
            "id": migration.id if migration.id else "",
            "applicant": applicant if applicant else "",
            "title": migration.title[:20] if migration.title else "",
            "project": migration.project.project if migration.project.project else "",
            "origin_instance": migration.origin_instance.instance_name if migration.origin_instance.instance_name else "",
            "target_instance": migration.target_instance.instance_name if migration.target_instance.instance_name else "",
            "origin_db": migration.origin_db if migration.origin_db else '',
            "target_db": migration.target_db if migration.target_db else '',
            "origin_tab": migration.origin_tab.replace(',', '\n') if migration.origin_tab else '',
            "is_new_db": 'Yes' if migration.is_new_db else 'No',
            "is_export_data": 'Yes' if migration.is_export_data else 'No',
            "is_export_view": 'Yes' if migration.is_export_view else 'No',
            "is_export_event": 'Yes' if migration.is_export_event else 'No',
            "is_export_routine": 'Yes' if migration.is_export_routine else 'No',
            "is_export_target": 'Yes' if migration.is_export_target else 'No',
            "application_time": migration.application_time if migration.application_time else '',
            "application_status": APPLICATION_STATUS_CHOICES[migration.application_status],
            "logs": migrate_log,
        }
        return HttpResponse(json.dumps(data_migrate_detail, cls=DateEncoder))


@login_required
@check_permission
def datamigrate_reback(request, id):
    if request.method == "POST":
            reback = DataMigrate.objects.get(id=id)
            if reback.application_status == 1:
                project_manager = project_group.objects.filter(project=reback.project,
                                                               user_type=Group.objects.get(name='项目经理')).values_list(
                    'user', flat=True)
                if not (request.user.id in project_manager or reback.project.project_manager.id == request.user.id):
                    error = '很抱歉，没有权限进行此操作！'
                    return JsonResponse({'result': error, 'code': 0})
            if reback.application_status == 2:
                dba = Group.objects.get(name='运维DBA').user_set.all()
                if not (request.user.is_superuser or request.user.id in dba):
                    error = '很抱歉，没有权限进行此操作！'
                    return JsonResponse({'result': error, 'code': 0})

            if reback.application_status == 0 or reback.application_status > 3:
                error = '状态已改变，请刷新页面查看!'
                return JsonResponse({'result': error, 'code': 0})
            else:
                reback_reason = request.POST.get('reback_reason')
                reback.reback_reason = reback_reason
                reback.application_status = 0
                update_logs = DataMigrateLog()
                update_logs.data_migrate_id = id
                update_logs.content = get_name_by_id.get_name(request.user.id) + "驳回申请:" + reback_reason
                reback.save()
                update_logs.save()
                send_message(action='数据迁移申请审批', detail_id=id, adopt='不通过')
                return JsonResponse({'result': '驳回成功', 'code': 1})

@login_required
@check_permission
def datamigrate_approval(request, id, control):
    application = DataMigrate.objects.get(id=id)
    approval_content = ''
    login_name = get_name_by_id.get_name(request.user.id)
    if control == 2:
        project_manager = project_group.objects.filter(project=application.project,
                                                       user_type=Group.objects.get(name='项目经理')).values_list(
            'user', flat=True)

        if application.application_status >= 2 or application.application_status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect(reverse('data_migrate'))
        if request.user.id in project_manager or application.project.project_manager.id == request.user.id:
            approval_content = '项目经理审批：' + login_name + '同意'
            # 发送消息
            send_message(action='数据迁移申请审批', detail_id=id, adopt='通过', sector='运维DBA')
        else:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(reverse('data_migrate'))

    if control == 3:
        if application.application_status >= 3 or application.application_status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect(reverse('data_migrate'))
        approval_content = '运维DBA审批：' + login_name + '同意'
        # 发送消息
        send_message(action='数据迁移申请审批通过', detail_id=id)

    if control <= 3:
        application.application_status = control
        application.save()
        DataMigrateLog.objects.create(data_migrate_id=id, content=approval_content)

    if control == 4:
        if application.application_status >= 4 or application.application_status == 0:
            messages.add_message(request, messages.ERROR, '这条工作流已经被执行！')
            return HttpResponseRedirect(reverse('data_migrate'))

        ori_instance = Instance.objects.get(id=application.origin_instance_id)
        tar_instance = Instance.objects.get(id=application.target_instance_id)
        async_migration.delay(
            application.id,
            login_name,
            ori_instance.server_ip,
            str(ori_instance.instance_username),
            prpCryptor.decrypt(ori_instance.instance_password),
            int(ori_instance.instance_port),
            application.origin_db,
            application.origin_tab,
            ori_instance.instance_type.cate_name,
            tar_instance.server_ip,
            str(tar_instance.instance_username),
            prpCryptor.decrypt(tar_instance.instance_password),
            int(tar_instance.instance_port),
            application.target_db,
            application.is_new_db,
            application.is_export_data,
            application.is_export_view,
            application.is_export_routine,
            application.is_export_event,
            application.is_export_target
        )
        time.sleep(0.1)
    return HttpResponseRedirect(reverse('data_migrate'))


def aliyun_instance_monitordata(request):
    monitordata = []
    supports = Support.objects.filter(name__icontains='阿里云').values_list('id', flat=True)
    min_keys = 'MySQL_COMDML,MySQL_MemCpuUsage,MySQL_DetailedSpaceUsage,MySQL_NetworkTraffic,MySQL_QPSTPS,MySQL_IOPS,MySQL_Sessions,MySQL_RowDML'
    starttime = (timezone.now() - timezone.timedelta(minutes=1)).isoformat(timespec='minutes').replace("+00:00", "Z")
    endtime = (timezone.now()).isoformat(timespec='minutes').replace("+00:00", "Z")
    if supports:
        for support_id in supports:
            region_id = RDSInstance.objects.filter(support_id=support_id).values_list('region_id', flat=True)
            if region_id:
                for reg_id in list(set(region_id)):
                    client = ALiYun(support_id, reg_id)
                    instance_id = RDSInstance.objects.filter(region_id=reg_id).values_list('instance_id', flat=True)
                    for ins_id in list(set(instance_id)):
                        instance_monitor = client.get_instance_monitordata(ins_id, min_keys, starttime, endtime)
                        monitordata.append(instance_monitor)
    return JsonResponse({'result': monitordata})


class MonitorDetailView(TemplateView):
    """服务器详情视图"""
    template_name = 'database/db_monitor.html'

    def get_context_data(self, **kwargs):
        context = super(MonitorDetailView, self).get_context_data(**kwargs)
        return context


# @login_required
# def get_monitor_data(request):
#     if request.method == 'POST':
#         data = {}
#         physical_instance = Instance.objects.filter(is_delete=0,
#                                                     instance_type=Category.objects.get(cate_name='MySQL')).values(
#             'instance_name')
#         ali_rds = RDSInstance.objects.all().values('instance_id', 'instance_description')
#         data['num'] = [physical_instance.count(), ali_rds.count()]
#         daterange = request.POST.get('datetime_range', '')
#         start_time, end_time = daterange.split('~')
#         start_time, end_time = parse(start_time), parse(end_time)
#         # start_time, end_time = parse(start_time).astimezone(datetime.timezone(timedelta(hours=8))), parse(
#         #    end_time).astimezone(datetime.timezone(timedelta(hours=8)))
#         print(start_time, end_time)
#         for item_id in Item.objects.all():
#             item_data = {}
#             for row in physical_instance:
#                 val = History.objects.filter(item_id=item_id, clock__gte=start_time, clock__lte=end_time,
#                                              instance_id=row['instance_name']).values('clock', 'delta_value')
#                 item_data[row['instance_name']] = DataFrame(list(val)).values.tolist()
#             for row in ali_rds:
#                 val = History.objects.filter(item_id=item_id, clock__gte=start_time, clock__lte=end_time,
#                                              instance_id=row['instance_id']).values('clock', 'delta_value')
#                 item_data[row['instance_description']] = DataFrame(list(val)).values.tolist()
#             data[item_id.db_key] = item_data
#         return JsonResponse(data)

@login_required
def get_monitor_data(request):
    from .monitor.data_collection import get_data
    from multiprocessing.pool import ThreadPool
    from django import db
    db.connections.close_all()
    pool = ThreadPool(processes=10)
    data, result = {}, {}
    daterange = request.POST.get('datetime_range', '')

    physical_instance = Instance.objects.filter(is_delete=0,
                                                instance_type=Category.objects.get(cate_name='MySQL')).values(
        'instance_name')
    ali_rds = RDSInstance.objects.filter(support__in=Support.objects.filter(name__icontains='阿里云')).values('instance_id', 'instance_description')
    aws_rds = RDSInstance.objects.filter(support__in=Support.objects.filter(name__icontains='aws')).values('instance_id', 'instance_description')
    data['num'] = [physical_instance.count(), ali_rds.count(), aws_rds.count()]
    start_time, end_time = daterange.split('~')
    start_time, end_time = parse(start_time), parse(end_time)
    # start_time, end_time = parse(start_time).astimezone(datetime.timezone(timedelta(hours=8))), parse(
    #    end_time).astimezone(datetime.timezone(timedelta(hours=8)))
    print(start_time, end_time)
    for item_id in Item.objects.all():
        result[item_id.id] = pool.apply_async(get_data, (item_id, physical_instance, ali_rds, start_time, end_time,))  # tuple of args for foo
    pool.close()
    for item_id in Item.objects.all():
        data[item_id.db_key] = result[item_id.id].get()
    db.connections.close_all()
    return JsonResponse(data)
