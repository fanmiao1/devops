# -*- coding: utf-8 -*-
"""
@  time    : 2018/5/30
@  author  : Xieyz
@  software: PyCharm
"""
from rest_framework import serializers
from .models import GoodsType, Purchase


class GoodsTypeSerializer(serializers.ModelSerializer):
    """物品类型"""
    class Meta:
        model = GoodsType
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    """采购订单"""
    class Meta:
        model = Purchase
        fields = '__all__'


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """采购订单详情"""
    type = GoodsTypeSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'
