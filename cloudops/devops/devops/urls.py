"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import *
from workflow import views
from usercenter.views import login,logout,index,group,CustomPasswordResetView,password_change_done,\
    password_reset_complete,wait_process_message, get_all_user
from django.views.static import serve
from devops.settings import MEDIA_ROOT
from django.views.generic import RedirectView
from worksheet.views import get_worksheet_amount
from django.views.generic import TemplateView
from lib.get_wechat_department_userlist import detail_userlist
from lib.get_wechat_department_list import department_list
from rest_framework_jwt.views import obtain_jwt_token
# from rest_framework import routers
# from opscenter.urls import opscenter_url
# from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
# router = routers.DefaultRouter()
# all_url = {}
# all_url.update(opscenter_url)
# for k, v in all_url.items():
#     router.register(k, v)
# handler404 = "usercenter.views.page_not_found"
# handler500 = "usercenter.views.page_error"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('jwt_auth/', obtain_jwt_token),
    path('login/',login,name='login'),
    path('logout/', logout,name='logout'),
    path('', index),
    path('index/', index, name='index'),
    path('group/', group, name='group'),
    path('favicon.ico',RedirectView.as_view(url='/static/images/favicon.ico')),
    path('accounts/password_change/', auth_views.password_change,name='password_change'),
    path('accounts/password_change/done/', password_change_done,name='password_change_done'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(),name='password_reset'),
    path('accounts/password_reset/done/', auth_views.password_reset_done,name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.password_reset_confirm,name='password_reset_confirm'),
    path('accounts/reset/done/', password_reset_complete,name='password_reset_complete'),
    path('get_flow_amount/', views.get_flow_amount,name='get_flow_amount'),  # 统计工作流
    path('get_worksheet_amount/', get_worksheet_amount,name='get_worksheet_amount'),  # 统计工单
    path('get_wait_process_message/', wait_process_message, name='get_wait_process_message'),  # 待办
    path('get_all_user/', get_all_user, name='get_all_user'),  # 获取所有用户
    path('get_wechat_detail_userlist/', detail_userlist, name='get_wechat_detail_userlist'),  # 获取企业微信部门用户列表
    path('get_wechat_department_list/', department_list, name='get_wechat_department_list'),  # 获取企业微信部门列表
    # 企业微信js-sdk
    path('WW_verify_x8jZ3ijX1wZctHZz.txt',TemplateView.as_view(template_name="WW_verify_x8jZ3ijX1wZctHZz.txt")),

    # 图片上传
    url(r'uploadIMG/', views.uploadIMG, name='uploadIMG'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, }),
    url(r'^data/uploads/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, }),

    # 用于二/三级联动
    path('get_project_manager_<int:pid>/', views.get_project_manager),
    path('get_group_user_<int:pid>_<int:gid>/', views.get_group_member),
    path('get_group_<int:pid>/',views.get_group),
    path('get_user_<int:pid>/',views.get_user),
    path('get_user_authority_<int:pid>/',views.get_user_authority),

    # 工作流
    path('flow/',include('workflow.urls')),

    # 数据库管理
    path('database/',include('database.urls')),

    # 用户中心
    path('usercenter/',include('usercenter.urls')),

    # CMDB
    path('cmdb/', include('CMDB.urls')),

    # 操作中心
    path('opscenter/', include('opscenter.urls')),

    # 工单系统
    path('worksheet/', include('worksheet.urls')),

    # 费用中心
    path('costcenter/', include('costcenter.urls')),

	# jenkins构建
    path('cijenkins/', include('cijenkins.urls')),

    # path(r'my_api/', include(router.urls)),
    # path(r'api-auth/', obtain_jwt_token),
]
