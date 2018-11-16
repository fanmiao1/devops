# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/27
@  author  : Xieyz
@  software: PyCharm
"""
from rest_framework import serializers
from .models import project


class ProjectAllSerializer(serializers.ModelSerializer):
    """用户"""
    class Meta:
        model = project
        fields = '__all__'
