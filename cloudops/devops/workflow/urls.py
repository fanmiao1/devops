from django.urls import path
from django.conf.urls import *
from workflow import views,comment
from django.conf import settings
from django.conf.urls.static import static
import devops.settings
from django.views.static import serve
from devops.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, }),
    # 工作流
    ## 项目管理
    path('project/all/list/', views.ProjectAllList.as_view(), name='all_project_list'),
    path('project_manage/', views.project_manage_view, name='project_manage'),
    path('project_manage/delete/<int:id>/', views.project_delete, name='project_manage_delete'),
    path('project_manage/project_add/', views.project_add_view, name='project_add'),
    path('project_manage/project_details/<int:id>/', views.project_details_view, name='project_details'),
    path('project_manage/project_details/delete_comment/<int:id>/', comment.delete_project_apply_comment,
         name='delete_project_apply_comment'),
    ### 项目经理审批
    path('project_manage/project_manager_approval/<int:id>_<int:control>/', views.project_approval_view,
         name='project_apply_project_manager_approval'),
    ### CTO审批
    path('project_manage/cto_approval/<int:id>_<int:control>/', views.project_approval_view,
         name='project_apply_cto_approval'),
    ### 采购审批
    path('project_manage/purchase_approval/<int:id>_<int:control>/', views.project_approval_view,
         name='project_apply_purchase_approval'),
    ### 财务审批
    path('project_manage/finance_approval/<int:id>_<int:control>/', views.project_approval_view,
         name='project_apply_finance_approval'),


    ## 项目变更
    path('releaseflow_manage/', views.releaseflow_manage_view,
         name='releaseflow_manage'),
    path('releaseflow_manage/delete/<int:id>/', views.releaseflow_delete,
         name='releaseflow_manage_delete'),
    path('releaseflow_manage/releaseflow_add/', views.releaseflow_add_view,
         name='releaseflow_add'),
    path('releaseflow_manage/releaseflow_details/<int:id>/', views.releaseflow_details_view,
         name='releaseflow_details'),
    path('releaseflow_manage/releaseflow_details/delete_comment/<int:id>/', comment.delete_project_release_apply_comment,
         name='delete_project_release_apply_comment'),
    ### 上传附件
    path('releaseflow_manage/releaseflow_details_post_annexes/<int:id>/', views.handle_upload,
         name='releaseflow_details_post_annexes'),
    ### 测试审批
    path('releaseflow_manage/test_approval_project_release/<int:id>_<int:control>/', views.releaseflow_approval_view,
         name='test_approval_project_release'),
    ### 项目经理审批
    path('releaseflow_manage/project_manager_approval_project_release/<int:id>_<int:control>/', views.releaseflow_approval_view,
         name='project_manager_approval_project_release'),
    ### 执行项目变更发布
    path('releaseflow_manage/implement_project_release/<int:id>_<int:control>/', views.releaseflow_approval_view,
         name='implement_project_release'),

    ## 项目成员变更
    path('project_member_manage/list/', views.project_member_manage_view,
         name='project_member_manage'),
    path('project_member_manage/delete/<int:id>/', views.project_member_flow_delete,
         name='project_member_manage_delete'),
    path('project_member_manage/apply/', views.project_member_apply_view,
         name='project_member_apply'),
    path('project_member_manage/details/<int:id>/', views.project_member_details_view,
         name='project_member_details'),
    path('project_member_manage/details/delete_comment/<int:id>/', comment.delete_project_member_apply_comment,
         name='delete_project_member_apply_comment'),
    ### 项目经理审批
    path('project_member_manage/approval/<int:id>_<int:control>/', views.project_member_approval_view,
         name='project_member_approval'),

    ## 计划任务变更
    path('cronflow_manage/',views.cronflow_manage_view,
         name='cronflow_manage'),
    path('cronflow_manage/cronflow_add/', views.cronflow_add_view,
         name='cronflow_add'),
    path('cronflow_manage/cronflow_details/<int:id>/', views.cronflow_details_view,
         name='cronflow_details'),
    path('cronflow_manage/cronflow_delete/<int:id>/', views.cronflow_delete,
         name='cronflow_delete'),
    path('cronflow_manage/cronflow_add/cron_select/', views.cron_select_view,
         name='cron_select'),
    path('cronflow_manage/cronflow_details/delete_comment/<int:id>/', comment.delete_cron_apply_comment,
         name='delete_cron_apply_comment'),
    ### 项目经理审批
    path('cronflow_manage/cronflow_approval/<int:id>_<int:control>/', views.cronflow_approval_view,
         name='cronflow_approval'),
    ### 执行计划任务变更
    path('cronflow_manage/cron_change_implement/<int:id>_<int:control>/', views.cronflow_approval_view,
         name='cron_change_implement'),

    ## 角色管理
    path('role_manage/',views.role_manage_view,name='role_manage'),
    path('role_manage/role_delete/<int:id>/',views.role_manage_view,name='role_delete'),
    path('role_manage/module_<int:id>/',views.role_module_list_view,name ='role_module_list'),
    path('role_add/',views.role_add_view,name='role_add'),
    path('role_manage/role_module_modify_<int:id>/',views.role_module_modify_view,name='role_module_modify'),
    path('get_all_module/<int:pid>/',views.get_all_module,name='get_all_module'),
    path('get_role_module_<int:id>/', views.get_role_module, name='get_role_module'),

    ## 权限管理
    path('module_manage/', views.module_manage_view, name='module_manage'),
    path('module_manage/module_delete/<int:id>/', views.module_manage_view, name='module_delete'),
    path('module_add/', views.module_add_view, name='module_add'),
    path('module_manage/module_modify_<path:id>/', views.module_modify_view, name='module_modify'),
    path('module_manage/module_change_history_<path:id>/', views.module_change_history_view, name='module_change_history'),


    ## 项目用户权限变更
    path('project_authority_manage/', views.project_authority_manage_view, name='project_authority_manage'),
    path('project_authority_manage/project_authority_delete/<int:id>/',views.project_role_delete, name='project_authority_delete'),
    path('project_authority_manage/project_authority_add/', views.project_authority_flow_add_view, name='project_authority_flow_add'),
    path('project_authority_manage/project_authority_details/<int:id>/',views.project_authority_details_view, name='project_authority_details'),
    path('project_authority_manage/project_authority_details/delete_comment/<int:id>/', comment.delete_project_user_authority_apply_comment,
         name='delete_project_user_authority_apply_comment'),
    ### 项目经理审批
    path('project_authority_manage/project_manager_project_authority_approval/<int:id>_<int:control>/', views.project_authority_approval_view,
         name='project_manager_project_authority_approval'),
    ### 执行用户权限变更
    path('project_authority_manage/project_authority_implement/<int:id>_<int:control>/', views.project_authority_approval_view,
         name='project_authority_implement'),

    ## 项目用户变更
    path('user_apply_list/', views.user_apply_flow_view, name='user_apply_list'),
    path('user_apply_list/user_apply/', views.user_apply_view, name='user_apply'),
    path('user_apply/delete/<int:id>', views.user_apply_flow_delete, name='user_apply_delete'),
    path('user_apply_list/user_modify_apply/', views.user_modify_apply_view, name='user_modify_apply'),
    path('user_apply_list/user_apply_details/<int:id>/', views.user_apply_details_view,
         name='user_apply_details'),
    path('user_apply_list/user_apply_details/delete_comment/<int:id>/', comment.delete_project_user_apply_comment,
         name='delete_project_user_apply_comment'),
    path('user_modify_apply_check_user_<int:project_id>_<path:user>/', views.user_modify_apply_check_user,
         name='user_modify_apply_check_user'),
    ### 项目经理审批
    path('user_apply_list/user_apply_approval/<int:id>_<int:control>/', views.user_apply_approval_view,
         name='user_apply_approval'),
    ### 执行用户添加/修改
    path('user_apply_list/user_operate_implement/<int:id>_<int:control>/', views.user_apply_approval_view,
         name='user_operate_implement'),

    ## 统计
    path('get_all_workflow_amount', views.get_all_workflow_amount, name='get_all_workflow_amount'),
    path('get_project_user_amount', views.get_project_user_amount, name='get_project_user_amount'),
    path('get_all_project', views.get_all_project, name='get_all_project'),
]
