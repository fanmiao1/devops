# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/9
@  author  : Xieyz
@  software: PyCharm
"""
from rest_framework import serializers
from .models import Clients


class ClientSerializer(serializers.ModelSerializer):
    """频道"""
    class Meta:
        model = Clients
        fields = '__all__'
