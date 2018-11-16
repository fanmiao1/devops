# -*- coding: utf-8 -*-
"""
@  time    : 2018/5/31
@  author  : Xieyz
@  software: PyCharm
"""
from .models import Certificate, Server, script_log, RevisionLogs, cron, SshOperationLogs
from django.contrib.auth.models import ContentType
import django_filters


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class CertificateFilter(django_filters.FilterSet):
    """凭证过滤器"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    protocol = django_filters.NumberFilter()
    username = django_filters.CharFilter(lookup_expr='icontains')
    port = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Certificate
        fields = ['name', 'protocol', 'username', 'port']


class ServerFilter(django_filters.FilterSet):
    """服务器过滤器"""
    id__in = NumberInFilter(name='id', lookup_expr='in')
    server_id = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    inner_ip = django_filters.CharFilter(lookup_expr='icontains')
    public_ip = django_filters.CharFilter(lookup_expr='icontains')
    certificate = django_filters.NumberFilter()
    os = django_filters.NumberFilter()
    support = django_filters.NumberFilter()
    region = django_filters.CharFilter(lookup_expr='icontains')
    server_info = django_filters.CharFilter(lookup_expr='icontains')
    remark = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Server
        fields = ['server_id', 'name', 'inner_ip', 'public_ip', 'certificate', 'os', 'support', 'region',
                  'server_info', 'remark']


class ScriptLogFilter(django_filters.FilterSet):
    """脚本日志过滤器"""
    script = django_filters.NumberFilter()

    class Meta:
        model = script_log
        fields = ['script']


class CronFilter(django_filters.FilterSet):
    """计划任务过滤器"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.NumberFilter()
    server = django_filters.NumberFilter()
    project = django_filters.CharFilter(lookup_expr='icontains')
    user = django_filters.CharFilter(lookup_expr='icontains')
    create_time = django_filters.DateFromToRangeFilter()
    status = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = cron
        fields = ['name', 'type', 'server', 'project', 'user', 'status']


class RevisionLogFilter(django_filters.FilterSet):
    """修改日志过滤器"""
    user = django_filters.NumberFilter()
    content_type = django_filters.NumberFilter()
    object_id = django_filters.NumberFilter()

    class Meta:
        model = RevisionLogs
        fields = ['user', 'content_type', 'object_id']


class SshOperationLogsFilter(django_filters.FilterSet):
    """脚本日志过滤器"""
    host = django_filters.NumberFilter()

    class Meta:
        model = SshOperationLogs
        fields = ['host']
