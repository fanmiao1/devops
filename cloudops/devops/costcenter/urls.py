# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/19
@  author  : XieYZ
@  software: PyCharm
"""
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # 采购订单
    path('purchase', login_required(login_required(views.PurchaseView.as_view())), name='purchase_view'),
    path('purchase/list/', views.PurchaseList.as_view(), name='purchase_list'),
    path('purchase/detail/<int:pk>/', views.PurchaseDetail.as_view(), name='purchase_detail'),

    # 物品类型
    path('goods_type/list/', views.GoodsTypeList.as_view(), name='goods_type_list'),
    path('goods_type/detail/<int:pk>/', views.GoodsTypeDetail.as_view(), name='goods_type_detail'),

    # 统计
    path('amount_by_department', views.amount_by_department, name='amount_by_department'),
    path('amount_by_type', views.amount_by_type, name='amount_by_type'),
    path('amount_by_purchase_type', views.amount_by_purchase_type, name='amount_by_purchase_type'),
]
