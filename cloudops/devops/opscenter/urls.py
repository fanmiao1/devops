from django.urls import path
from opscenter import views
from django.contrib.auth.decorators import login_required
from .views import CertificateView, CertificateList, CertificateDetail, ProtocolList, ProtocolDetail, ServerView, \
    ServerList, ServerAllList, ServerDetail, SupportList, ServerDetailView, ServerGroupList, ServerGroupDetail, \
    RemoteExecView, AnsibleTaskList, AnsibleTaskDetail, ScriptList, ScriptDetail, ScriptView, ScriptLogList, \
    ScriptLogDetail, ScriptLogView, ScriptAllList, CronView, CronList, CronDetail, RevisionLogList, create_cron, \
    CronAllList, batch_delete, SshOperationLogsList, SshOperationLogsView

urlpatterns = [
    ## 修改日志
    path('revision_log/list/', RevisionLogList.as_view(), name='revision_log_list'),

    ## Ssh连接
    path('ssh_view/sid=<path:sid>/inoex=<path:inoex>/cid=<path:cid>/', views.SshView.as_view()),
    path('connect_ssh/',views.connect_ssh_view, name='connect_ssh'),
    path('check_connect/',views.check_connect,name='check_connect'),
    path('ssh_log_add/', SshOperationLogsList.as_view()),
    path('behavior_audit_view/<int:id>', login_required(SshOperationLogsView.as_view()), name='behavior_audit_view'),

    ## 凭证管理
    path('certificate', login_required(CertificateView.as_view()), name='cert_view'),
    path('certificate/list/', CertificateList.as_view(), name='cert_list'),
    path('certificate/detail/<int:pk>/', CertificateDetail.as_view(), name='cert_detail'),

    ## 协议管理
    path('protocol/list/', ProtocolList.as_view(), name='protocol_list'),
    path('protocol/detail/<int:pk>/', ProtocolDetail.as_view(), name='protocol_detail'),

    ## 服务商管理
    path('support/list/', SupportList.as_view(), name='support_list'),

    ## 服务器管理
    path('server', login_required(ServerView.as_view()), name='server_view'), # 实例列表视图
    path('server_detail/<int:pk>/', login_required(ServerDetailView.as_view()), name='server_detail_view'), # 实例详情视图
    path('server/list/', ServerList.as_view(), name='server_list'), # 服务器列表
    path('server/all/list/', ServerAllList.as_view(), name='server_all_list'), # 所有服务器列表(不分页)
    path('server/detail/<int:pk>/', ServerDetail.as_view(), name='server_detail'),
    path('server/status/list/', views.get_instances_status, name='get_instances_status'), # 获取实例状态
    path('server/desc/list/', views.get_instances_desc, name='get_instances_desc'), # 获取实例详情
    path('server/collect_instances', views.CollectInstances.as_view(), name='collect_instances'), # 收集实例
    path('server/region', views.get_region, name='get_region'),
    path('server/check_auto_renew', views.CheckAutoRenew.as_view(), name='check_auto_renew'),
    path('server/get_amount', views.get_server_amount, name='get_server_amount'), # 统计实例数量
    path('server/dashboard_asset_server_amount', views.dashboard_asset_server_amount, name='dashboard_asset_server_amount'),
    path('server/get_server_list_by_group', views.get_server_list_by_group, name='get_server_list_by_group'),
    path('server/get_server_group_list', views.get_server_group_list, name='get_server_group_list'),
    path('server/dashboard_server_monitor', views.dashboard_server_monitor, name='dashboard_server_monitor'),

    ## 服务器分组管理
    path('server_group/list/', ServerGroupList.as_view(), name='server_group'),
    path('server_group/detail/<int:pk>/', ServerGroupDetail.as_view(), name='server_group_detail'),

    ## 计划任务管理
    path('cron/', login_required(CronView.as_view()), name='cron_view'),
    path('cron/create_cron/', create_cron, name='create_cron'),
    path('cron/list/', CronList.as_view(),name='cron_list'),
    path('cron/all/list/', CronAllList.as_view(),name='cron_all_list'),
    path('cron/detail/<int:pk>/', CronDetail.as_view(), name='cron_detail'),
    path('cron/batch_delete/', batch_delete, name='batch_delete'),

    ## 推送监控信息API
    path('send_monitor_api', views.get_monitor_info_api, name='send_monitor_api'),
    path('get_redis_list', views.get_redis_list, name='get_redis_list'),
    path('get_mongo_list', views.get_mongo_list, name='get_mongo_list'),
    # path('get_cpu_info', views.get_cpu_info, name='get_cpu_info'),
    # path('get_memory_info', views.get_memory_info, name='get_memory_info'),
    path('get_classify_info', views.get_classify_info, name='get_classify_info'),
    path('get_io_info', views.get_io_info, name='get_io_info'),
    path('get_system_pids', views.get_system_pids, name='get_system_pids'),


    ## 脚本管理
    path('script/', login_required(ScriptView.as_view()), name='script_manage'),
    path('script/list/', ScriptList.as_view(), name='script_list'),
    path('script/detail/<int:pk>/', ScriptDetail.as_view(), name='script_detail'),
    path('script/all/list/', ScriptAllList.as_view(), name='script_all_list'),
    path('script/exec/', views.script_exec, name='script_exec'),
    path('script/exec/log/view/<int:id>/', login_required(ScriptLogView.as_view()), name='script_exec_log'),
    path('script/exec/log/list/', ScriptLogList.as_view(), name='script_exec_log_list'),
    path('script/exec/log/detail/<int:pk>/', ScriptLogDetail.as_view(), name='script_exec_log_detail'),

    ## Ansible任务
    path('remote_exec_view/', login_required(RemoteExecView.as_view()), name='remote_exec_view'),
    path('get_ansible_module', views.get_ansible_module, name='get_ansible_module'),
    path('ansible_exec', views.ansible_exec, name='ansible_exec'),
    path('ansible_task/list/', AnsibleTaskList.as_view(), name='ansible_task_list'),
    path('ansible_task/detail/<int:pk>/', AnsibleTaskDetail.as_view(), name='ansible_task_detail'),

    path('get_web_detect', views.get_web_detect, name='get_web_detect'),
]
