# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/24
@  author  : XieYZ
@  software: PyCharm
"""
from .models import DomainManage
import django_filters


class DomainFilter(django_filters.FilterSet):
    """凭证过滤器"""
    domain = django_filters.CharFilter(lookup_expr='icontains')
    register_date = django_filters.DateFromToRangeFilter()
    expire_date = django_filters.DateFromToRangeFilter()
    bisnis_responsible = django_filters.CharFilter(lookup_expr='icontains')
    is_auto_pay = django_filters.BooleanFilter()
    register_support = django_filters.NumberFilter
    dns_support = django_filters.NumberFilter
    status = django_filters.NumberFilter

    class Meta:
        model = DomainManage
        fields = ['domain', 'register_date', 'expire_date', 'bisnis_responsible', 'is_auto_pay', 'register_support',
         'dns_support', 'status']
