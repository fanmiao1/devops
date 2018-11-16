# -*- coding: utf-8 -*-
"""
@  time    : 2018/5/30
@  author  : Xieyz
@  software: PyCharm
"""
from rest_framework import serializers
from django.contrib.auth.models import User, ContentType
from .models import Certificate, Protocol, Server, Support, ServerGroup, AnsibleTask, script, script_log, cron, \
    RevisionLogs, SshOperationLogs
from workflow.serializers import ProjectAllSerializer

class UserSerializer(serializers.ModelSerializer):
    """用户"""
    class Meta:
        model = User
        fields = '__all__'


class ProtocolSerializer(serializers.ModelSerializer):
    """协议"""
    class Meta:
        model = Protocol
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    """凭证"""
    class Meta:
        model = Certificate
        fields = '__all__'


class ProtocolDetailSerializer(serializers.ModelSerializer):
    """协议详情"""
    cert_protocol = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Protocol
        fields = '__all__'


class CertificateDetailSerializer(serializers.ModelSerializer):
    """凭证详情"""
    protocol = ProtocolSerializer()

    class Meta:
        model = Certificate
        fields = '__all__'


class SupportSerializer(serializers.ModelSerializer):
    """服务商"""
    class Meta:
        model = Support
        fields = '__all__'


class ServerSerializer(serializers.ModelSerializer):
    """服务器"""
    class Meta:
        model = Server
        fields = '__all__'


class ServerDetailSerializer(serializers.ModelSerializer):
    """服务器详情"""
    certificate = CertificateSerializer()
    support = SupportSerializer()

    class Meta:
        model = Server
        fields = '__all__'


class ServerGroupSerializer(serializers.ModelSerializer):
    """服务器分组"""
    class Meta:
        model = ServerGroup
        fields = '__all__'


class AnsibleTaskSerializer(serializers.ModelSerializer):
    """Ansible任务"""
    class Meta:
        model = AnsibleTask
        fields = '__all__'


class AnsibleTaskDetailSerializer(serializers.ModelSerializer):
    """Ansible任务详情"""
    operator = UserSerializer()

    class Meta:
        model = AnsibleTask
        fields = '__all__'


class ScriptSerializer(serializers.ModelSerializer):
    """脚本"""
    class Meta:
        model = script
        fields = '__all__'


class ScriptLogSerializer(serializers.ModelSerializer):
    """脚本日志"""
    class Meta:
        model = script_log
        fields = '__all__'


class CronSerializer(serializers.ModelSerializer):
    """计划任务"""
    class Meta:
        model = cron
        fields = '__all__'


class CronDetailSerializer(serializers.ModelSerializer):
    """计划任务详情"""
    script = ScriptSerializer()
    server = ServerSerializer()

    class Meta:
        model = cron
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = '__all__'


class RevisionLogSerializer(serializers.ModelSerializer):
    """计划任务修改日志"""
    user = UserSerializer()
    content_type = ContentTypeSerializer()

    class Meta:
        model = RevisionLogs
        fields = '__all__'


class SshOperationLogsSerializer(serializers.ModelSerializer):
    """Ssh行为日志"""

    class Meta:
        model = SshOperationLogs
        fields = '__all__'


class SshOperationLogsDetailSerializer(serializers.ModelSerializer):
    """Ssh行为日志详情"""
    user = UserSerializer()
    host = ServerSerializer()

    class Meta:
        model = SshOperationLogs
        fields = '__all__'
