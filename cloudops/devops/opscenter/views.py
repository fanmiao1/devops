# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
import json
import datetime
import pytz

import paramiko
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from django.views.generic.base import View
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import DetectWeb, DetectWebAlarmLogs
from lib.pagination import MyPageNumberPagination
from lib.revision_log import change
from usercenter.build_message import build_message
from usercenter.permission import check_permission, check_object_perm
from workflow.get_name_by_id import get_name_by_id
from .filter import *
from .serializers import *
from .tasks import run_ansible, run_ansible_module, run_cron
from devops.settings import MONITOR_REDIS_API


class SshOperationLogsView(TemplateView):
    """凭证视图"""
    template_name = 'opscenter/behavior_audit.html'

    def get_context_data(self, **kwargs):
        context = super(SshOperationLogsView, self).get_context_data(**kwargs)
        return context


class SshOperationLogsList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """Ssh行为日志列表、新增"""
    queryset = SshOperationLogs.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    filter_class = SshOperationLogsFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SshOperationLogsDetailSerializer
        else:
            return SshOperationLogsSerializer

    @check_object_perm(codename='opscenter.add_certificate')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_certificate')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CertificateView(TemplateView):
    """凭证视图"""
    template_name = 'opscenter/cert_manage.html'

    def get_context_data(self, **kwargs):
        context = super(CertificateView, self).get_context_data(**kwargs)
        return context


class CertificateList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """凭证列表、新增"""
    queryset = Certificate.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = CertificateFilter
    pagination_class = MyPageNumberPagination
    ordering_fields = ('id', 'name', 'protocol', 'username', 'port', 'remark')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CertificateDetailSerializer
        else:
            return CertificateSerializer

    @check_object_perm(codename='opscenter.add_certificate')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_certificate')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CertificateDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """凭证读取、更新、删除"""
    queryset = Certificate.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CertificateDetailSerializer
        else:
            return CertificateSerializer

    @check_object_perm(codename='opscenter.add_certificate')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_certificate')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_certificate')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProtocolList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """协议列表、新增"""
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer

    @check_object_perm(codename='opscenter.add_protocol')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_protocol')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProtocolDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """协议读取、更新、删除"""
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer

    @check_object_perm(codename='opscenter.add_protocol')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_protocol')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_protocol')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class SupportList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """服务商列表"""
    queryset = Support.objects.all()
    serializer_class = SupportSerializer

    @check_object_perm(codename='opscenter.add_support')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ServerView(TemplateView):
    """服务器列表视图"""
    template_name = 'opscenter/server_manage.html'

    def get_context_data(self, **kwargs):
        context = super(ServerView, self).get_context_data(**kwargs)
        return context


class ServerDetailView(TemplateView):
    """服务器详情视图"""
    template_name = 'opscenter/server_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ServerDetailView, self).get_context_data(**kwargs)
        return context


from django.views.generic import DetailView
class ServerList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, DetailView):
    """服务器列表、新增"""
    queryset = Server.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ServerFilter
    pagination_class = MyPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServerDetailSerializer
        else:
            return ServerSerializer

    @check_object_perm(codename='opscenter.add_server')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_server')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ServerDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """服务器读取、更新、删除"""
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServerDetailSerializer
        else:
            return ServerSerializer

    @check_object_perm(codename='opscenter.add_server')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_server')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_server')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ServerAllList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """所有服务器列表(不分页)"""
    queryset = Server.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ServerFilter
    serializer_class = ServerSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServerDetailSerializer
        else:
            return ServerSerializer

    @check_object_perm(codename='opscenter.add_server')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ServerGroupList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """服务器分组列表、新增"""
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer

    @check_object_perm(codename='opscenter.add_servergroup')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_servergroup')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ServerGroupDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """服务器分组读取、更新、删除"""
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer

    @check_object_perm(codename='opscenter.add_servergroup')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_servergroup')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_servergroup')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AnsibleTaskList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """Ansible任务列表、新增"""
    queryset = AnsibleTask.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AnsibleTaskDetailSerializer
        else:
            return AnsibleTaskSerializer

    @check_object_perm(codename='opscenter.add_ansibletask')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_ansibletask')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AnsibleTaskDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """Ansible任务读取、更新、删除"""
    queryset = AnsibleTask.objects.all()
    serializer_class = AnsibleTaskSerializer

    @check_object_perm(codename='opscenter.add_ansibletask')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_ansibletask')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_ansibletask')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ScriptView(TemplateView):
    """脚本视图"""
    template_name = 'opscenter/script_manage.html'

    def get_context_data(self, **kwargs):
        context = super(ScriptView, self).get_context_data(**kwargs)
        return context


class ScriptList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """脚本列表、新增"""
    queryset = script.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    serializer_class = ScriptSerializer

    @check_object_perm(codename='opscenter.add_script')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_script')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ScriptDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """脚本读取、更新、删除"""
    queryset = script.objects.all()
    serializer_class = ScriptSerializer

    @check_object_perm(codename='opscenter.add_script')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_script')
    @change()
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_script')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ScriptAllList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """脚本列表、新增"""
    queryset = script.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    serializer_class = ScriptSerializer

    @check_object_perm(codename='opscenter.add_script')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_script')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ScriptLogView(TemplateView):
    """脚本日志视图"""
    template_name = 'opscenter/script_exec_log.html'

    def get_context_data(self, **kwargs):
        qs = script.objects.get(id = kwargs['id'])
        context = super(ScriptLogView, self).get_context_data(**kwargs)
        context['script_name'] = qs.script_name
        context['script_group'] = qs.script_group
        return context


class ScriptLogList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """脚本日志列表、新增"""
    queryset = script_log.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    filter_class = ScriptLogFilter
    serializer_class = ScriptLogSerializer

    @check_object_perm(codename='opscenter.add_scriptlog')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_scriptlog')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ScriptLogDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """脚本日志读取、更新、删除"""
    queryset = script_log.objects.all()
    serializer_class = ScriptLogSerializer

    @check_object_perm(codename='opscenter.add_scriptlog')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_scriptlog')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.delete_scriptlog')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CronView(TemplateView):
    """计划任务视图"""
    template_name = 'opscenter/cron_list.html'

    def get_context_data(self, **kwargs):
        context = super(CronView, self).get_context_data(**kwargs)
        try:
            content_type_id = ContentType.objects.get(
                app_label=cron._meta.app_label,
                model = cron._meta.object_name
            ).id
            context['content_type_id'] = content_type_id
        except: pass
        return context


class CronList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """计划任务列表、新增"""
    queryset = cron.objects.exclude(status='delete').order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    filter_class = CronFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CronDetailSerializer
        else:
            return CronSerializer

    @check_object_perm(codename='opscenter.add_cron')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.add_cron')
    def post(self, request, *args, **kwargs):
        create = self.create(request, *args, **kwargs)
        if str(create.status_code)[:1] == '2':
            cron.objects.filter(id=create.data['id']).update(status='loading')
            RevisionLogs.objects.create(
                content_type = ContentType.objects.get(app_label=cron._meta.app_label, model=cron._meta.object_name),
                content = '添加计划任务',
                object_id = create.data['id'],
                user = request.user
            )
            send_cron(create.data, request.user)
        return create


class CronAllList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """所有计划任务列表(不分页)"""
    queryset = cron.objects.exclude(status='delete')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    serializer_class = CronDetailSerializer

    @check_object_perm(codename='opscenter.add_server')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CronDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """计划任务读取、更新、删除"""
    queryset = cron.objects.all()
    serializer_class = CronSerializer

    @check_object_perm(codename='opscenter.add_cron')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='opscenter.change_cron')
    @change()
    def put(self, request, *args, **kwargs):
        update = self.update(request, *args, **kwargs)
        if str(update.status_code)[:1] == '2':
            if update.data['status'] != 'delete':
                cron.objects.filter(id=update.data['id']).update(status='loading')
            send_cron(update.data, request.user)
        return update

    @check_object_perm(codename='opscenter.delete_cron')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RevisionLogList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """修改日志列表、新增"""
    queryset = RevisionLogs.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    filter_class = RevisionLogFilter
    serializer_class = RevisionLogSerializer

    @check_object_perm(codename='opscenter.add_revisionlogs')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RemoteExecView(TemplateView):
    """Ansible执行模块视图"""
    template_name = 'opscenter/remote_exec.html'

    def get_context_data(self, **kwargs):
        context = super(RemoteExecView, self).get_context_data(**kwargs)
        return context

from .aliyun.instances import Instances
def get_instances_status(request):
    """获取实例状态"""
    support_id = request.POST.get('support_id', '')
    region_id = request.POST.get('region_id', '')
    response = eval(Instances(support_id, region_id).get_full_instances_status())['InstanceStatuses']['InstanceStatus']
    result = {}
    for i in response:
        result[i['InstanceId']] = i['Status']
    return JsonResponse({'result': result})

from .aliyun.region import region_list as aliyun_region_list
from .ucloud.region import region_list as ucloud_region_list
from .aws.region import region_list as aws_region_list
def get_region(request):
    """获取地域"""
    result = {}
    aliyun_region = []
    for i in aliyun_region_list:
        aliyun_region.append({"value": i, "name": aliyun_region_list[i]})
    ucloud_region = []
    for i in ucloud_region_list:
        ucloud_region.append({"value": i, "name": ucloud_region_list[i]})
    aws_region = []
    for i in aws_region_list:
        aws_region.append({"value": i, "name": aws_region_list[i]})
    result['aliyun_region_list'] = aliyun_region
    result['ucloud_region_list'] = ucloud_region
    result['aws_region_list'] = aws_region
    return JsonResponse({'result': result})

def get_instances_desc(request):
    """获取实例详情"""
    true = False
    false = True
    support_id_list = Support.objects.values_list('id', flat=True)
    region_id_list = Server.objects.values_list('region', flat=True)
    region_id_list = list(set(region_id_list))
    if region_id_list == [None] or support_id_list == [None]:
        return JsonResponse({'result': '没有公有云服务器'})
    response = []
    for support_id in support_id_list:
        for region_id in region_id_list:
            response += eval(Instances(support_id).get_instances_detail(region_id))['Instances']['Instance']
    result = {}
    for i in response:
        result[i['InstanceId']] = i
    return JsonResponse({'result': result})


from .aliyun.collect import collect_aliyun_instances
from .ucloud.collect import collect_ucloud_instances
from .aws.collect import collect_aws_instances
from .local.collect import get_local_server
# @login_required
# def collect_instances(request):
#     """收集实例"""
#     support_id = request.POST.get('support_id', '')
#     region_id = request.POST.get('region_id', '')
#     api_type_obj = Support.objects.get(id=support_id)
#     if api_type_obj.access_key_id != 'local':
#         api_type = api_type_obj.type
#         collect_res = {'result': '内部错误', 'code': 0}
#         if int(api_type) == 1:
#             collect_res = collect_aliyun_instances(request, region_id, support_id)
#         elif int(api_type) == 2:
#             collect_res = collect_ucloud_instances(request, region_id, support_id)
#         elif int(api_type) == 3:
#             collect_res = collect_aws_instances(request, region_id, support_id)
#     else:
#         collect_res = get_local_server(request, support_id)
#     return JsonResponse(collect_res)


class CollectInstances(APIView):
    queryset = Support.objects.all()
    authentication_classes = (SessionAuthentication, JSONWebTokenAuthentication)

    def post(self, request, format=None):
        support_id = request.POST.get('support_id', '')
        region_id = request.POST.get('region_id', '')
        api_type_obj = Support.objects.get(id=support_id)
        if api_type_obj.access_key_id != 'local':
            api_type = api_type_obj.type
            collect_res = {'result': '内部错误', 'code': 0}
            if int(api_type) == 1:
                collect_res = collect_aliyun_instances(request, region_id, support_id)
            elif int(api_type) == 2:
                collect_res = collect_ucloud_instances(request, region_id, support_id)
            elif int(api_type) == 3:
                collect_res = collect_aws_instances(request, region_id, support_id)
        else:
            collect_res = get_local_server(request, support_id)
        return JsonResponse(collect_res)


class CheckAutoRenew(APIView):
    queryset = Server.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def post(self, request):
        support_id = request.POST.get('support_id', '')
        id = request.POST.get('id', '')
        obj = Server.objects.get(id=int(id))
        region = obj.region
        server_id = obj.server_id
        region_id = ''
        support_obj = Support.objects.get(id=support_id)
        support_type = support_obj.type
        res = '无法识别'
        code = 1
        if support_type == 1:
            for i in aliyun_region_list:
                if aliyun_region_list[i] == region:
                    region_id = i
            if not region_id:
                return JsonResponse({'result': '检查失败！', 'code': 0})
            instance = Instances(support_id)
            response = instance.get_instance_auto_renew(region_id, server_id)
            false = 'false'
            true = 'true'
            is_auto = eval(response)['InstanceRenewAttributes']['InstanceRenewAttribute'][0]['AutoRenewEnabled']
            if is_auto == true:
                res = '是'
            else:
                res = '否'
        elif support_type == 2:
            if '自动续费' in obj.server_info:
                try:
                    res = eval(obj.server_info)['自动续费']
                except:
                    code = 0
        elif support_type == 3:
            res = '是'
        else:
            code = 0
        return JsonResponse({'result': res, 'code': code})


# @login_required
# def check_auto_renew(request):
#     """检查是否开启自动续费"""
#     support_id = request.POST.get('support_id', '')
#     id = request.POST.get('id', '')
#     obj = Server.objects.get(id=int(id))
#     region = obj.region
#     server_id = obj.server_id
#     region_id = ''
#     support_obj = Support.objects.get(id=support_id)
#     support_type = support_obj.type
#     res = '无法识别'
#     code = 1
#     if support_type == 1:
#         for i in aliyun_region_list:
#             if aliyun_region_list[i] == region:
#                 region_id = i
#         if not region_id:
#             return JsonResponse({'result': '检查失败！', 'code': 0})
#         instance = Instances(support_id)
#         response = instance.get_instance_auto_renew(region_id, server_id)
#         false = 'false'
#         true = 'true'
#         is_auto = eval(response)['InstanceRenewAttributes']['InstanceRenewAttribute'][0]['AutoRenewEnabled']
#         if is_auto == true:
#             res = '是'
#         else:
#             res = '否'
#     elif support_type == 2:
#         if '自动续费' in obj.server_info:
#             try:
#                 res = eval(obj.server_info)['自动续费']
#             except:
#                 code = 0
#     elif support_type == 3:
#         res = '是'
#     else:
#         code = 0
#     return JsonResponse({'result': res, 'code': code})

@login_required
def connect_ssh_view(request):
    '''
    @author: Xieyz
    @note: SSH连接
    :return: SSH
    '''
    return render(request, 'opscenter/connect_ssh.html')

import requests
@login_required
def check_connect(request):
    data = json.loads(request.body)
    try:
        data['con_ip']
    except KeyError:
        return JsonResponse({'con_status': "false", 'message': '请选择连接IP!'})
    try:
        data['con_id']
    except KeyError:
        return JsonResponse({'con_status': "false", 'message': '请选择一台主机!'})
    #
    # for i in data:
    #     if not data[i]:
    #         return JsonResponse({'con_status': "false", 'message' : '请输入'+i.replace('con_','')})
    con_ip = data['con_ip']
    ip_obj = Server.objects.only(con_ip).get(id=data['con_id'])
    ip = getattr(ip_obj,con_ip)
    cert_url = "http://{host}/opscenter/certificate/detail/{cid}".format(host=request.get_host(),cid=data['cid'])
    response = requests.get(cert_url, cookies=request.COOKIES)
    cert_re = response.json()
    try:
        check_ssh = paramiko.SSHClient()
        check_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        check_ssh.connect(
            hostname=ip,
            port= cert_re['port'],
            username= cert_re['username'],
            password= cert_re['key'],
            timeout=10
        )
        check_ssh.close()
        return JsonResponse({'con_status': 'true', 'message': '连接成功!'})
    except Exception as error:
        return JsonResponse({'con_status': 'false', 'message': str(error)})

from devops.task_error import TaskError
from .monitor import Monitor
def get_monitor_info_api(request):
    try:
        try:
            info = request.POST.get('info', '')
            info = eval(info)
        except Exception as _:
            raise TaskError('数据类型有误，请传输字典类型！')
        else:
            if isinstance(info, dict):
                m = Monitor()
                send = m.server_monitor(info)
                try:
                    code = send['code']
                    if code == 1:
                        result = code
                    else:
                        raise TaskError(send['result'])
                except Exception as _:
                    raise TaskError('监控数据传输过程出现异常，请检查数据是否正常！')
                else:
                    result = 'success'
            else:
                raise TaskError('数据类型有误，请传输字典类型！')
    except TaskError as err:
        code = 0
        result = str(err)
    res = {'code': code, 'result': result}
    print (res)
    return JsonResponse(res)

# def get_redis_list(request):
#     key = request.POST.get('key', '')
#     key_list = request.POST.getlist('key[]', [])
#     result = {}
#     m = Monitor()
#     if key_list:
#         for i in key_list:
#             try:
#                 result[i] = m.get_redis(i)
#             except:
#                 continue
#     else:
#         try:
#             result = m.get_redis(key)
#         except:
#             code = 0
#             result = 'error'
#     res = {'code': 1, 'result': result}
#     return JsonResponse(res)

def time_zone():
    tz = pytz.timezone("Asia/Shanghai")
    return tz

def get_redis_list(request):
    key = request.POST.get('key', '')
    key_list = request.POST.getlist('key[]', [])
    data = {
        "key": key,
        "key_list": key_list,
        "start": request.POST.get('start', 0),
        "end": request.POST.get('end', -1)
    }
    res = requests.post('http://{host}/redis_api/get_redis_list'.format(host=MONITOR_REDIS_API), data=data)
    res_json = res.json()
    if key_list:
        for i in res_json['result']:
            if res_json['result'][i]:
                res_json['result'][i][0] = eval(res_json['result'][i][0])
                res_json['result'][i][0]['datetime'] = res_json['result'][i][0]['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    elif key:
        if res_json['result']:
            res_json['result'][0] = eval(res_json['result'][0])
            res_json['result'][0]['datetime'] = res_json['result'][0]['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    return JsonResponse(res_json)


# def get_mongo_list(request):
#     key = request.POST.get('key', '')
#     key_list = request.POST.getlist('key[]', [])
#     datetime_range = request.POST.get('datetime_range', '')
#     data = {
#         "key": key,
#         "key_list": key_list,
#         "datetime_range": datetime_range
#     }
#     res = requests.post('http://{host}/redis_api/get_mongo_list'.format(host=MONITOR_REDIS_API), data=data)
#     my_res = res.json()
#     my_res['result'] = eval(my_res['result'])
#     return JsonResponse(my_res)

import time
from mongo.monitor_oper import MonGoOperation
from pandas import DataFrame, Series
def get_mongo_list(request):
    key = request.POST.get('key', '')
    key_list = request.POST.getlist('key[]', [])
    datetime_range = request.POST.get('datetime_range', '')
    data = {
        "key": key,
        "key_list": key_list,
        "datetime_range": datetime_range
    }
    result = {}
    code = 1

    m = MonGoOperation()
    if key_list:
        for i in key_list:
            try:
                result[i] = m.get(i, datetime_range=datetime_range)
            except Exception as _:
                continue
    else:
        try:
            result = m.get(key, datetime_range=datetime_range)
        except Exception as _:
            code = 0
            print (str(_))
            result = 'error'
    # disk_io
    disk_io_columns_list = DataFrame(result.distinct('disk'), columns=['io'])['io'].values.tolist()
    disk_io_data_two_columns_list = DataFrame(disk_io_columns_list, columns=['data'])['data'].values.tolist()
    disk_io_data_one_columns_list = DataFrame(disk_io_data_two_columns_list, columns=['1','2'])['1'].values.tolist() +\
                                    DataFrame(disk_io_data_two_columns_list, columns=['1','2'])['2'].values.tolist()
    disk_read_count_data_list = DataFrame(
        disk_io_data_one_columns_list, columns=['datetime', 'read_count_data']).sort_values(by="datetime").values.tolist()
    disk_write_count_data_list = DataFrame(
        disk_io_data_one_columns_list, columns=['datetime', 'write_count_data']).sort_values(by="datetime").values.tolist()
    disk_io_read_bytes_data_apply = DataFrame(disk_io_data_one_columns_list, columns=['read_bytes_data']).apply(
        lambda x: round(x / 30 / 1000, 1))['read_bytes_data'].values.tolist()
    disk_io_write_bytes_data_apply = DataFrame(disk_io_data_one_columns_list, columns=['write_bytes_data']).apply(
        lambda x: round(x / 30 / 1000, 1))['write_bytes_data'].values.tolist()
    disk_datetime_list = DataFrame(disk_io_data_one_columns_list, columns=['datetime'])['datetime'].values.tolist()
    disk_read_bytes_data_list = DataFrame({'datetime':disk_datetime_list, 'read_bytes_data': disk_io_read_bytes_data_apply},
                                    columns=['datetime', 'read_bytes_data']).sort_values(by="datetime").values.tolist()
    disk_write_bytes_data_list = DataFrame({'datetime':disk_datetime_list, 'write_bytes_data': disk_io_write_bytes_data_apply},
                                 columns=['datetime', 'write_bytes_data']).sort_values(by="datetime").values.tolist()
    # net_io
    net_io_columns_list = DataFrame(result.distinct('net'), columns=['io'])['io'].values.tolist()
    net_io_data_two_columns_list = DataFrame(net_io_columns_list, columns=['data'])['data'].values.tolist()
    net_io_data_one_columns_list = DataFrame(net_io_data_two_columns_list, columns=['1', '2'])['1'].values.tolist() + \
                                    DataFrame(net_io_data_two_columns_list, columns=['1', '2'])['2'].values.tolist()
    net_io_recv_data_apply = DataFrame(net_io_data_one_columns_list, columns=['recv_data']).apply(
        lambda x: round(x / 30, 2))['recv_data'].values.tolist()
    net_io_send_data_apply = DataFrame(net_io_data_one_columns_list, columns=['send_data']).apply(
        lambda x: round(x / 30, 2))['send_data'].values.tolist()
    net_datetime_list = DataFrame(net_io_data_one_columns_list, columns=['datetime'])['datetime'].values.tolist()
    net_recv_data_list = DataFrame(
        {'datetime': net_datetime_list, 'recv_data': net_io_recv_data_apply},
        columns=['datetime', 'recv_data']).sort_values(by="datetime").values.tolist()
    net_send_data_list = DataFrame(
        {'datetime': net_datetime_list, 'send_data': net_io_send_data_apply},
        columns=['datetime', 'send_data']).sort_values(by="datetime").values.tolist()
    cpu_percent = DataFrame(result.distinct('cpu'), columns=['datetime','percent']).values.tolist()
    memory_percent = DataFrame(result.distinct('memory'), columns=['datetime','percent']).values.tolist()
    try:
        one_minute_load = DataFrame(result.distinct('loadavg'), columns=['datetime','lavg_1']).values.tolist()
        five_minute_load = DataFrame(result.distinct('loadavg'), columns=['datetime','lavg_5']).values.tolist()
        fifteen_minute_load = DataFrame(result.distinct('loadavg'), columns=['datetime','lavg_15']).values.tolist()
    except:
        one_minute_load = []
        five_minute_load = []
        fifteen_minute_load = []
        pass
    disk_percent = DataFrame(result.distinct('disk'), columns=['datetime','usage']).values.tolist()
    my_res = {
        'code': code,
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'one_minute_load': one_minute_load,
        'five_minute_load': five_minute_load,
        'fifteen_minute_load': fifteen_minute_load,
        'disk_percent': disk_percent,
        'disk_read_count_data_list': disk_read_count_data_list,
        'disk_write_count_data_list':disk_write_count_data_list,
        'disk_read_bytes_data_list':disk_read_bytes_data_list,
        'disk_write_bytes_data_list':disk_write_bytes_data_list,
        'net_recv_data_list': net_recv_data_list,
        'net_send_data_list': net_send_data_list
    }
    return JsonResponse(my_res)


def get_classify_info(request):
    key = request.POST.get('key', ''),
    key_list = request.POST.getlist('key[]', []),
    class_i = request.POST.get('class', '')
    hour = request.POST.get('hour', '')
    data = {
        "key": key,
        "key_list": key_list,
        "start": request.POST.get('start', 0),
        "end": request.POST.get('end', -1)
    }
    result = {}
    m = MonGoOperation()
    if key_list:
        for i in key_list[0]:
            info = {}
            now = datetime.datetime.now(time_zone())
            gap = datetime.timedelta(hours=int(hour))
            time_1 = now - gap
            try:
                vv = m.get(i, datetime_range='{time_1} ~ {time_2}'.format(
                    time_1=time_1.strftime('%Y-%m-%d %H:%M'), time_2=now.strftime('%Y-%m-%d %H:%M')))
                percent_dataFrame = DataFrame(vv.distinct(class_i), columns=['percent'])
                if not percent_dataFrame.empty:
                    info['max'] = percent_dataFrame.max()['percent']
                    info['min'] = percent_dataFrame.min()['percent']
                    info['av'] = float('%.2f' % average(percent_dataFrame['percent'].values.tolist()))
                    last_data = vv.distinct(class_i)[-1]
                    info['now'] = last_data['percent']
                    info['now_time'] = last_data['datetime']
                    result[i] = info
            except Exception as _:
                continue
    return JsonResponse({'code': 1, 'result': result})


def average(array):
    avg = 0.0
    n = len(array)
    for num in array:
        avg+= 1.0*float(num)/n
    return avg


def get_io_info(request):
    key = request.POST.get('key', ''),
    key_list = request.POST.getlist('key[]', []),
    class_i = request.POST.get('class', '')
    hour = request.POST.get('hour', '')
    data = {
        "key": key,
        "key_list": key_list,
        "start": request.POST.get('start', 0),
        "end": request.POST.get('end', -1)
    }
    result = {}
    m = MonGoOperation()
    if key_list:
        for i in key_list[0]:
            info = {}
            now = datetime.datetime.now(time_zone())
            gap = datetime.timedelta(hours=int(hour))
            time_1 = now - gap
            vv = m.get(i, datetime_range='{time_1} ~ {time_2}'.format(
                time_1=time_1.strftime('%Y-%m-%d %H:%M'), time_2=now.strftime('%Y-%m-%d %H:%M')))
            io_list = DataFrame(vv.distinct(class_i), columns=['io'])['io'].values.tolist()
            io_data_two_columns_list = DataFrame(io_list, columns=['data'])['data'].values.tolist()
            io_data_one_columns_list = DataFrame(io_data_two_columns_list,
                                                      columns=['1', '2'])['1'].values.tolist() + \
                                            DataFrame(io_data_two_columns_list,
                                                      columns=['1', '2'])['2'].values.tolist()
            if not DataFrame(io_data_one_columns_list).empty:
                last_data = vv.distinct(class_i)[-1]['io']['data'][-1]
                info['now_time'] = last_data['datetime']
                if class_i == 'net':
                    info['max_in'] = float('%.0f' % DataFrame(io_data_one_columns_list, columns=['recv_data']).max())
                    info['av_in'] = float('%.0f' % average(DataFrame(io_data_one_columns_list,
                                        columns=['recv_data'])['recv_data'].values.tolist()))
                    info['max_out'] = float('%.0f' % DataFrame(io_data_one_columns_list, columns=['send_data']).max())
                    info['av_out'] = float('%.0f' % average(DataFrame(io_data_one_columns_list,
                                        columns=['send_data'])['send_data'].values.tolist()))
                    info['now_in'] = float('%.0f' % last_data['recv_data'])
                    info['now_out'] = float('%.0f' % last_data['send_data'])
                elif class_i == 'disk':
                    info['now_iops_read'] = float('%.0f' % last_data['read_count_data'])
                    info['now_iops_write'] = float('%.0f' % last_data['write_count_data'])
                    info['now_bytes_read'] = float('%.1f' % (last_data['read_bytes_data'] / 1024))
                    info['now_bytes_write'] = float('%.1f' % (last_data['write_bytes_data'] / 1024))
                    info['max_iops_read'] = float(
                        '%.0f' % DataFrame(io_data_one_columns_list, columns=['read_count_data']).max())
                    info['max_iops_write'] = float(
                        '%.0f' % DataFrame(io_data_one_columns_list, columns=['write_count_data']).max())
                    info['max_bytes_read'] = float(
                        '%.1f' % (DataFrame(io_data_one_columns_list, columns=['read_bytes_data']).max() / 1024))
                    info['max_bytes_write'] = float(
                        '%.1f' % (DataFrame(io_data_one_columns_list, columns=['write_bytes_data']).max() / 1024))
                    info['av_iops_read'] = float('%.0f' % average(DataFrame(io_data_one_columns_list,
                                              columns=['read_count_data'])['read_count_data'].values.tolist()))
                    info['av_iops_write'] = float('%.0f' % average(DataFrame(io_data_one_columns_list,
                                              columns=['write_count_data'])['write_count_data'].values.tolist()))
                    info['av_bytes_read'] = float('%.0f' % (average(DataFrame(io_data_one_columns_list,
                                              columns=['read_bytes_data'])['read_bytes_data'].values.tolist()) / 1024))
                    info['av_bytes_write'] = float('%.0f' % (average(DataFrame(io_data_one_columns_list,
                                              columns=['write_bytes_data'])['write_bytes_data'].values.tolist()) / 1024))
                result[i] = info
    return JsonResponse({'code': 1, 'result': result})


def get_system_pids(request):
    key = request.POST.get('key', ''),
    key_list = request.POST.getlist('key[]', []),
    class_i = request.POST.get('class', '')
    hour = request.POST.get('hour', '')
    data = {
        "key": key,
        "key_list": key_list,
        "start": request.POST.get('start', 0),
        "end": request.POST.get('end', -1)
    }
    result = {}
    m = MonGoOperation()
    if key_list:
        info = {}
        now = datetime.datetime.now(time_zone())
        gap = datetime.timedelta(hours=int(1))
        time_1 = now - gap
        for i in key_list[0]:
            try:
                vv = m.get(i, datetime_range='{time_1} ~ {time_2}'.format(
                    time_1=time_1.strftime('%Y-%m-%d %H:%M'), time_2=now.strftime('%Y-%m-%d %H:%M')))
                percent_dataFrame = DataFrame(vv.distinct(class_i), columns=['count'])
                if not percent_dataFrame.empty:
                    info['max'] = int(percent_dataFrame.max()['count'])
                    info['min'] = int(percent_dataFrame.min()['count'])
                    info['av'] = float('%.0f' % average(percent_dataFrame['count'].values.tolist()))
                    last_data = vv.distinct(class_i)[-1]
                    info['now'] = int(last_data['count'])
                    info['now_time'] = vv.distinct('datetime')[-1] + datetime.timedelta(hours=8)
                    result[i] = info
            except Exception as _:
                continue
    return JsonResponse({'code': 1, 'result': result})

@login_required
@check_permission
def script_exec(request):
    script_id = request.POST.get('id')
    server_id = request.POST.get('server_id')
    if not script_id or not server_id:
        code = 0
        if not server_id:
            result = '请选择实例！'
        else:
            result = '请选择一个脚本！'
    else:
        url = "http://{host}/opscenter/script/detail/{id}/".format(host=request.get_host(), id=script_id)
        response = requests.get(url, cookies=request.COOKIES)
        re = response.json()
        if str(response.status_code)[:1] == '2':
            script_group = re['script_group']
            script_content = re['script_content']
            print (script_content)
            resource = []
            server_url = "http://{host}/opscenter/server/all/list/?id__in={sid}".format(host=request.get_host(), sid=server_id)
            server_response = requests.get(server_url, cookies=request.COOKIES)
            server_re = server_response.json()
            print (server_re)
            for i in server_re:
                exec_pa = {"hostname": "", "port": "", "username": "", "password": "", "ip": ""}
                try:
                    exec_pa['hostname'] = i['server_id']
                    certifi = i['certificate']
                    if certifi:
                        if certifi['username'] and certifi['key'] and certifi['port']:
                            exec_pa['username'] = certifi['username']
                            exec_pa['password'] = certifi['key']
                            exec_pa['port'] = certifi['port']
                    if i['public_ip'] or i['inner_ip']:
                        exec_pa['ip'] = i['public_ip'] if i['public_ip'] else i['inner_ip']
                except Exception as _:
                    pass
                resource.append(exec_pa)
            get_na = get_name_by_id.get_name(request.user.id)
            run_result = run_ansible.delay(resource, script_group, script_content, script_id, get_na)
            code = 1
            result = '成功开始执行脚本，执行完毕后可在执行记录查看结果！'
        else:
            code = 0
            result = '该脚本不存在！'
    return JsonResponse({'result': result, 'code': code})

@login_required
def get_ansible_module(request):
    from .ansible_module import module
    module_list = module
    return JsonResponse({'module_list': module_list})

@login_required
def ansible_exec(request):
    server_id = request.POST.get('server_id', '')
    model = request.POST.get('model', '')
    param = request.POST.get('param', '')
    if not server_id or not model:
        code = 0
        result = '「实例、模块」都不能为空！'
    else:
        if model != 'ping' and model !='win_ping':
            if not param:
                code = 0
                result = '「参数」不能为空！'
                return JsonResponse({'code': code, 'result': result})
        error = []
        data = {'resource': [], 'script_type': model, 'script_content': param}
        url = "http://{host}/opscenter/server/all/list/?id__in={sid}".format(host=request.get_host(), sid=server_id)
        response = requests.get(url, cookies=request.COOKIES)
        re = response.json()
        server_name_list = []
        for i in re:
            try:
                server_name_list.append(i['name'])
                exec_pa = {}
                exec_pa['hostname'] = i['server_id']
                certifi = i['certificate']
                if certifi:
                    if certifi['username'] and certifi['key'] and certifi['port']:
                        exec_pa['username'] = certifi['username']
                        exec_pa['password'] = certifi['key']
                        exec_pa['port'] = certifi['port']
                    else:
                        error.append({'server': i['name'], 'reason': '凭证无效'})
                        continue
                else:
                    error.append({'server': i['name'], 'reason': '实例无凭证'})
                    continue
                if i['public_ip'] or i['inner_ip']:
                    exec_pa['ip'] = i['public_ip'] if i['public_ip'] else i['inner_ip']
                else:
                    error.append({'server': i['name'], 'reason': '实例无IP'})
                    continue
                data['resource'].append(exec_pa)
            except Exception as _:
                error.append({'server': i['name'], 'reason': '未知原因'})
                continue
        task_data = {
            "server_id": server_id,
            "server_name": ','.join(server_name_list),
            "module": model,
            "parameter": param,
            "error": error,
            "operator": request.user.id
        }
        task_url = "http://{host}/opscenter/ansible_task/list/".format(host=request.get_host())
        task_response = requests.post(task_url, cookies=request.COOKIES, data=task_data)
        if str(task_response.status_code)[:1] == '2':
            task_re = task_response.json()
            run_result = run_ansible_module.delay(data['resource'], data['script_type'],
                data['script_content'], task_re, request.get_host(), request.COOKIES)
            code = 1
            result = 'success'
        else:
            code = 0
            result = '添加失败'
    return JsonResponse({'code': code, 'result': result})

from devops.settings import FILE_API
def send_cron(data, user):
    cron_id = data['id']
    script_content = ''
    if data['status'] == 'running':
        enable = 'yes'
        state = 'present'
    else:
        enable = 'no'
        state = 'absent'
    server_obj = Server.objects.get(id=data['server'])
    arguments = 'null'
    file_path = ''
    if data['type'] == 0:
        if server_obj.os == 0:
            o = data['order']
        else:
            o = 'cmd.exe'
            arguments = data['order']
    else:
        if data['script']:
            script_obj = script.objects.get(id=data['script'])
            script_content = script.objects.only('script_content').get(id=data['script']).script_content

            if server_obj.os != 0 and script_obj.script_group == 'py_monitor':
                file_path = '/usr/src/app/{m}.exe'.format(m=script_obj.script_name)
            else:
                sc = {
                    "script_content": script_content
                }
                sc_response = requests.post(FILE_API, json=sc)
                file_path = sc_response.json()['result']
            try:
                if server_obj.os == 0:
                    o = "/devops/{f}".format(f=data['name']+'_'+str(data['id']))
                    if script_obj.script_group == 'python':
                        o = "python {o}".format(o=o)
                    elif script_obj.script_group == 'py_monitor':
                        o = "python {o} {arg}".format(o=o, arg=server_obj.server_id)
                    else:
                        o = "sh {o}".format(o=o)
                else:
                    o = "c:\devops\{f}".format(f=data['name']+'_'+str(data['id']))
                    if script_obj.script_group == 'py_monitor':
                        arguments = server_obj.server_id
            except Exception as _:
                print("err: {e}".format(e=str(_)))
                o = data['script']
        else:
            o = data['script']
    if o:
        resource = []
        trigger = ''
        trigger_dict = eval(data['trigger'])[0]
        if server_obj.os == 0:
            for i in trigger_dict:
                value = trigger_dict[i]
                if value != '?':
                    trigger += '{key}="{value}" '.format(key=i, value=value)
            script_type = 'cron'
            exec_tigger = 'name="{name}" state={state} job="{job}" {trigger}'.format(
                name=data['name'], job=o, trigger=trigger, state=state)
        else:
            try:
                interval = trigger_dict['repetition']['interval']
            except:
                interval = null

            trigger_type = trigger_dict['type']
            trigger_dict.pop('type')
            for i in trigger_dict:
                value = trigger_dict[i]
                trigger += '\n        {key}: "{value}"'.format(key=i, value=value)
            content_template = """- hosts: all
  tasks:
  - name: "DevopsCronTask"
    win_scheduled_task:
      name: "{name}"
      actions:
      - path: {path}
        arguments: {arguments}
      triggers:
      - type: {type}{trigger}
        repetition:
        - interval: {interval}
      enable: {enable}
      state: {state}
      username: SYSTEM"""
            script_type = 'winyml'
            exec_tigger = content_template.format(
                name=data['name'], path=o, arguments=arguments, type=trigger_type,
                trigger=trigger,interval=interval, enable=enable, state=state)
        exec_pa = {"hostname": "", "port": "", "username": "", "password": "", "ip": ""}
        try:
            exec_pa['hostname'] = server_obj.server_id
            certifi = server_obj.certificate
            if certifi:
                if certifi.username and certifi.key and certifi.port:
                    exec_pa['username'] = certifi.username
                    exec_pa['password'] = certifi.key
                    exec_pa['port'] = certifi.port
            if server_obj.public_ip or server_obj.inner_ip:
                exec_pa['ip'] = server_obj.public_ip if server_obj.public_ip else server_obj.inner_ip
        except Exception as _:
            pass
        resource.append(exec_pa)
        rcron = run_cron.delay(resource, script_type, exec_tigger, cron_id, user, server_obj.os, data['status'],
                               data['type'], script_content, file_path)
    else:
        cron.objects.filter(id=data['id']).update(status='disable')

@login_required
def create_cron(request):
    data = {}
    err_list = []
    success = 0
    for i in request.POST:
        data[i] = request.POST[i]
    server_list = data['server_list'].split(',')
    for i in server_list:
        try: server_id = int(i)
        except: continue
        data['server'] = server_id
        url = "http://{host}/opscenter/cron/list/".format(host=request.get_host())
        response = requests.post(url, cookies=request.COOKIES, data=data)
        if str(response.status_code)[:1] == '2':
            success += 1
        else:
            try: err_list.append(Server.objects.only('name').get(id=server_id).name)
            except: pass
    err_n = len(server_list) - success
    if err_n > 0: err_mess = "，添加失败的实例为「{server}」".format(server=err_list)
    else: err_mess = ""
    build_message(
        **{'message_title': '添加计划任务结果',
           'message_content': '共成功添加{n}个名为「{name}」的计划任务，添加失败{fan}个{err}'.format(
            n=success, name=data['name'], fan=err_n, err=err_mess),
           'message_url': '/opscenter/cron/',
           'message_user': request.user.id
        }
    )
    return JsonResponse({'code': 1, 'result': '成功添加{n}个计划任务'.format(n=success)})

@login_required
def batch_delete(request):
    delete_list = request.POST.get('delete_list', '')
    delete_list = delete_list.split(',')
    success = 0
    err_list = []
    for i in delete_list:
        try: cron_id = int(i)
        except: continue
        url = "http://{host}/opscenter/cron/detail/{pk}/".format(host=request.get_host(), pk=i)
        data = {'id': i, 'status': 'delete'}
        response = requests.put(url, cookies=request.COOKIES, data=data)
        if str(response.status_code)[:1] == '2':
            success += 1
        else:
            try:
                cron_obj = cron.objects.get(id=cron_id)
                if cron_obj.server:
                    err_list.append("{name} - {server}".format(name=cron_obj.name, server=cron_obj.server.name))
                else:
                    err_list.append(cron_obj.name)
            except: pass
    err_n = len(delete_list) - success
    if err_n > 0:
        err_mess = "，删除失败的计划任务为「{cron}」".format(cron=err_list)
    else:
        err_mess = ""
    build_message(
        **{'message_title': '删除计划任务结果',
           'message_content': '共成功删除{n}个计划任务，删除失败{fan}个{err}'.format(
               n=success, fan=err_n, err=err_mess),
           'message_url': '/opscenter/cron/',
           'message_user': request.user.id
       }
    )
    return JsonResponse({'code': 1, 'result': '成功删除{n}个计划任务'.format(n=success)})


class SshView(TemplateView):
    """凭证视图"""
    template_name = 'ssh.html'

    def get_context_data(self, **kwargs):
        context = super(SshView, self).get_context_data(**kwargs)
        return context


@login_required
def get_server_list_by_group(request):
    group_id = request.GET.get('group_id')
    group_obj = ServerGroup.objects.get(id=int(group_id))
    server_id_set = group_obj.server
    server_id_list = server_id_set.split(',') if server_id_set else []
    server_obj = Server.objects.filter(id__in=server_id_list)
    result = []
    for i in server_obj:
        result.append({'id': i.server_id, 'name': i.server_id + ' - ' + i.name})
    return JsonResponse({'result': result})


@login_required
def get_server_group_list(request):
    group_obj = ServerGroup.objects.all()
    result = []
    for i in group_obj:
        result.append({'id': i.id, 'name': i.name})
    return JsonResponse({'result': result})


@login_required
def get_server_amount(request):
    server_obj = Server.objects.all()
    total = server_obj.count()
    run = server_obj.count()
    server_info_list = server_obj.values_list('server_info', flat=True)
    now_date = datetime.datetime.now()
    expired_at_once = 0
    expired = 0
    for i in server_info_list:
        try:
            gap = datetime.datetime.strptime(eval(i)['到期时间'], '%Y-%m-%d') - now_date
            if gap.days < 0:
                expired += 1
            elif gap.days <= 7:
                expired_at_once += 1
        except Exception:
            continue
    result = {
        "total": total,
        "run": run,
        "expired_at_once": expired_at_once,
        "expired": expired
    }
    return JsonResponse(result)

@login_required
def dashboard_asset_server_amount(request):
    server_obj = Server.objects.all()
    by_type_count = {}
    expired_at_once_data = []
    name_list = []
    pie_data = []
    now_date = datetime.datetime.now()
    for i in server_obj:
        try:
            gap = datetime.datetime.strptime(eval(i.server_info)['到期时间'], '%Y-%m-%d') - now_date
            if 0 <= gap.days <= 7:
                if i.support:
                    support = i.support.name
                else:
                    support = ''
                expired_at_once_data.append({
                    "server_id": i.server_id,
                    "name": i.name,
                    "support": support,
                    "expire_date": str(eval(i.server_info)['到期时间'])
                })
        except Exception:
            pass
        try:
            try:
                by_type_count[i.support.name] += 1
            except Exception:
                by_type_count[i.support.name] = 0
                by_type_count[i.support.name] += 1
        except Exception:
            pass
    for v in by_type_count:
        name_list.append(v)
        pie_data.append({"name": v, "value": by_type_count[v]})
    if expired_at_once_data:
        expired_at_once_data = DataFrame(
            expired_at_once_data).sort_values(by='expire_date').values.tolist()
    result = {
        "expired_at_once_data": expired_at_once_data,
        "name_list": name_list,
        "pie_data": pie_data,
    }
    return JsonResponse(result)

from pytz import timezone
utc_tz = timezone('UTC')
cst_tz = timezone('Asia/Shanghai')
@login_required
def dashboard_server_monitor(request):
    server_id = request.GET.get('server_id')
    data = {
        "key": server_id,
        "start": -1,
        "end": -1
    }
    res = requests.post('http://{host}/redis_api/get_redis_list'.format(host=MONITOR_REDIS_API), data=data)
    res_json = res.json()
    if res_json['result']:
        now_time = eval(res_json['result'][0])['datetime']
        cpu_usage = eval(res_json['result'][0])['cpu']['percent']
        memory_usage = eval(res_json['result'][0])['memory']['percent']
        disk_partition = eval(res_json['result'][0])['disk']['partition']
        t = datetime.timedelta(hours=8)
        result = {
            "now_time": time_span(now_time.replace(tzinfo=utc_tz) - t),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_partition":disk_partition,
        }
    else:
        result = {}
    try:
        m = MonGoOperation()
        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        datetime_range = "{yesterday} ~ {today}".format(
            yesterday=(now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            today=now.strftime("%Y-%m-%d %H:%M")
        )
        mongo_result = m.get(server_id, datetime_range=datetime_range)
    except Exception as _:
        pass

    try:
        result['one_minute_load'] = DataFrame(mongo_result.distinct('loadavg'), columns=['datetime','lavg_1']).values.tolist()
        result['five_minute_load'] = DataFrame(mongo_result.distinct('loadavg'), columns=['datetime','lavg_5']).values.tolist()
        result['fifteen_minute_load'] = DataFrame(mongo_result.distinct('loadavg'), columns=['datetime','lavg_15']).values.tolist()
    except:
        result['one_minute_load'] = []
        result['five_minute_load'] = []
        result['fifteen_minute_load'] = []

    try:
        result['memory_percent'] = DataFrame(mongo_result.distinct('memory'), columns=['datetime', 'percent']).values.tolist()
    except:
        result['memory_percent'] = []
    return JsonResponse(result)

from lib.relative_time import time_span
@login_required
def get_web_detect(request):
    web_obj = DetectWeb.objects.all()
    result = []
    for i in web_obj:
        log_obj = DetectWebAlarmLogs.objects.filter(web=i).order_by('-time')
        if log_obj:
            name = log_obj[0].web.website
            code = log_obj[0].status_code
            content = log_obj[0].content
            description = i.description
            time = time_span(log_obj[0].time)
            result.append({
                "name": name,
                "code": code,
                "content": content,
                "description": description,
                "time": time
            })
    return JsonResponse({"result": result})
