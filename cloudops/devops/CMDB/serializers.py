# -*- coding: utf-8 -*-
"""
@  time    : 2018/5/30
@  author  : Xieyz
@  software: PyCharm
"""
from rest_framework import serializers
from .models import DomainManage
from opscenter.serializers import SupportSerializer

class DomainManageSerializer(serializers.ModelSerializer):
    """域名管理"""
    class Meta:
        model = DomainManage
        fields = '__all__'


class DomainManageDetailSerializer(serializers.ModelSerializer):
    """域名管理详情"""
    register_support = SupportSerializer()
    dns_support = SupportSerializer()

    class Meta:
        model = DomainManage
        fields = '__all__'
