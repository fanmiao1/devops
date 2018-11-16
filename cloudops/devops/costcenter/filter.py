# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/19
@  author  : XieYZ
@  software: PyCharm
"""
from .models import Purchase
import django_filters
from lib.number_in_filter import NumberInFilter

class PurchaseFilter(django_filters.FilterSet):
    """凭证过滤器"""
    id__in = NumberInFilter(name='id', lookup_expr='in')
    applicant = django_filters.CharFilter(lookup_expr='icontains')
    application_date = django_filters.DateFromToRangeFilter()
    department = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.CharFilter(lookup_expr='icontains')
    department_id__in = NumberInFilter(name='department_id', lookup_expr='in')
    type = django_filters.NumberFilter
    purchaser = django_filters.CharFilter(lookup_expr='icontains')
    purchase_type = django_filters.NumberFilter
    purchase_date = django_filters.DateFromToRangeFilter()
    goods = django_filters.CharFilter(lookup_expr='icontains')
    receiver = django_filters.CharFilter(lookup_expr='icontains')
    receive_date = django_filters.DateFromToRangeFilter()
    other_info = django_filters.CharFilter(lookup_expr='icontains')
    remark = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.NumberFilter

    class Meta:
        model = Purchase
        fields = ['id', 'applicant', 'application_date', 'department_id', 'type', 'purchaser', 'purchase_type',
                  'purchase_date', 'goods', 'receiver', 'receive_date', 'other_info', 'remark', 'status', 'department',
                  'group']
