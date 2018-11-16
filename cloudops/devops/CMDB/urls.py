from django.urls import path
from django.conf.urls import *
from django.contrib.auth.decorators import login_required

from CMDB import views


urlpatterns = [
    ## 资产管理

    ### 获取供应商
    path ('get_supplier', views.get_supplier, name='get_supplier'),

    ### 获取资产类型
    path('get_asset_type', views.get_asset_type, name='get_asset_type'),

    ### 编辑资产类型
    path('asset_type_change', views.asset_type_change, name='asset_type_change'),

    ### 删除资产类型
    path('asset_manage/fixed_asset/delete_asset_type/',views.delete_asset_type, name='delete_asset_type'),

    ### 编辑供应商
    path('supplier_change', views.supplier_change, name='supplier_change'),

    ### 删除供应商
    path('asset_manage/fixed_asset/delete_supplier/',views.delete_supplier, name='delete_supplier'),

    ### 获取组织结构
    path('get_org/', views.get_org, name='get_org'),

    ### 获取所有用户
    path('get_all_user/', views.get_all_user, name='get_all_user'),

    ### 获取企业微信用户
    path('get_wechat_user/',views.get_wechat_user, name='get_wechat_user'),

    ### 资产列表
    path('asset_manage/fixed_asset/fixed_asset_list/', views.fixed_asset_list, name='fixed_asset_list'),

    ### 资产类型列表
    path('asset_manage/fixed_asset/asset_type_list/', views.asset_type_list, name='asset_type_list'),

    ### 供应商列表
    path('asset_manage/fixed_asset/supplier_manage_list/', views.supplier_manage_list, name='supplier_manage_list'),

    ### 资产详情
    path('get_asset_detail/', views.get_asset_detail, name='get_asset_detail'),

    ### 资产添加
    path('asset_manage/fixed_asset/add_asset/',views.add_asset, name='add_asset'),

    ### 资产删除
    path('asset_manage/fixed_asset/delete_asset/',views.delete_asset, name='delete_asset'),

    ### 资产借出
    path('asset_manage/fixed_asset/asset_out/',views.asset_out, name='asset_out'),

    ### 资产归还
    path('asset_manage/fixed_asset/asset_back/',views.asset_back, name='asset_back'),

    ### 资产维修
    path('asset_manage/fixed_asset/asset_maintain/',views.asset_maintain, name='asset_maintain'),

    ### 资产报废
    path('asset_manage/fixed_asset/asset_scrap/', views.asset_scrap, name='asset_scrap'),

    ### 判断资产是否绑定供应商
    path('asset_manage/fixed_asset/judge_supplier/', views.judge_supplier, name='judge_supplier'),

    ### 判断归还人
    path('asset_manage/fixed_asset/judge_back_person/', views.judge_back_person, name='judge_back_person'),

    ### 获取资产定制字段
    path('asset_manage/fixed_asset/get_asset_field/', views.get_asset_field, name='get_asset_field'),

    ### 资产统计
    path('asset_manage/fixed_asset/asset_count/', views.asset_count, name='asset_count'),

    ### 资产导入
    path('asset_manage/fixed_asset/asset_import/', views.asset_import, name='asset_import'),

    ### 资产出入库记录导入
    path('asset_manage/fixed_asset/asset_flow_import/', views.asset_flow_import, name='asset_flow_import'),

    ### 自定义导出
    path('asset_manage/fixed_asset/custom_export/', views.custom_export, name='asset_custom_export'),

    ### 域名管理
    path('domain', login_required(views.DomainManageView.as_view()), name='domain_view'),
    path('domain/list/', views.DomainManageList.as_view(), name='domain_list'),
    path('domain/detail/<int:pk>/', views.DomainManageDetail.as_view(), name='domain_detail'),
    path('domain/get_amount', views.get_domain_amount, name='get_domain_amount'),  # 统计实例数量

    ### 固定资产Dashboard统计数据
    path('asset_amount', views.asset_amount, name='asset_amount'),
    path('daily_asset_flow_amount', views.daily_asset_flow_amount, name='daily_asset_flow_amount'),
]