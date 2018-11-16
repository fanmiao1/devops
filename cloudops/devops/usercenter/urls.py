from django.urls import path
from django.contrib import admin
from usercenter import views

urlpatterns = [
    # 消息中心
    path('message/all/', views.message_list_view,
         name='all_message'),
    path('message/isread/<int:isread>/', views.message_list_view,
         name='isread_message'),
    path('message/read/<int:isread>/', views.message_list_view,
         name='read_message'),
    path('message/detail/<int:id>/',views.message_detail_view,
         name='message_detail'),
    path('message/delete/<int:id>/',views.message_list_view,
         name='message_delete'),
    path('message/check_unread_message/',views.check_unread_message,
         name='check_unread_message'),
    path('message/message_change_status/',views.message_change_status,
         name='message_change_status'),
    path('message/message_batch_delete/',views.message_batch_delete,
         name='message_batch_delete'),

    # 项目用户组管理
    path('project_user_group_manage/list/', views.project_authority_group_list_view,
         name='project_authority_group_list'),
    path('project_user_group_manage/add/', views.project_authority_group_add,
         name='project_authority_group_add'),
    path('project_user_group_manage/modify/<int:id>/', views.project_authority_group_modify,
         name='project_authority_group_modify'),
    path('get_all_project_user_<int:pid>/', views.get_all_project_user,
         name='get_all_project_user'),
    path('get_project_group_user_<int:gid>/', views.get_project_group_user,
         name='get_project_group_user'),
    path('project_user_group_manage/user_list/<int:id>/', views.project_authority_group_user_list_view,
         name='project_authority_group_user_list'),
    path('project_group_user_change/<int:gid>/', views.project_group_user_change,
         name='project_group_user_change'),
    path('project_user_group_manage/delete/<int:id>/', views.project_authority_group_list_view,
         name='project_authority_group_delete'),

    ## 项目用户管理
    path('user_manage/', views.user_manage_view,
         name='user_manage'),
    path('user_manage/user_detail/<int:id>', views.user_details_view,
         name='user_detail'),
    path('user_manage/user_is_active/<int:id>_<int:is_active>/',views.project_user_change_status,
         name='user_is_active'),
    path('user_manage/add/', views.project_user_add,
         name='project_user_add'),
    path('user_manage/modify/<int:id>/', views.project_user_modify,
         name='project_user_modify'),
    path('get_group_list_by_user/', views.get_group_list_by_user,
         name='get_group_list_by_user'),

    ## WS频道操作
    path('client/add/', views.ClientOper.as_view()),
    path('client/delete/<int:pk>/', views.ClientOper.as_view()),
]