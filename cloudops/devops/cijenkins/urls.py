from django.contrib import admin
from django.urls import path
from django.conf.urls import *
from cijenkins import views

urlpatterns = [
    path('job_manage_qa/<int:jenkins_env>', views.job_manage_views,
         name='job_manage_qa'),  # qa环境构建列表页
    path('job_manage_pro/<int:jenkins_env>', views.job_manage_views,
         name='job_manage_pro'), # pro环境构建列表页
    path('job_manage/job_details_qa/<int:jenkins_env>/<path:job_name>', views.job_details_views,
         name='job_details_qa'), # qa环境模块详情页
    path('job_manage/job_details_pro/<int:jenkins_env>/<path:job_name>', views.job_details_views,
         name='job_details_pro'), # pro环境模块详情页
    path('job_manage/job_deploy_qa/<int:jenkins_env>/<path:job_name>', views.job_deploy_views,
         name='job_deploy_qa'), # qa环境模块构建执行
    path('job_manage/job_deploy_pro/<int:jenkins_env>/<path:job_name>', views.job_deploy_views,
         name='job_deploy_pro'), # pro环境模块构建执行
    path('job_manage/cancel_build_qa/<int:jenkins_env>/<path:job_name>', views.cancel_build_views,
         name='cancel_build_qa'),  # qa环境执行停止构建
    path('job_manage/cancel_build_pro/<int:jenkins_env>/<path:job_name>', views.cancel_build_views,
         name='cancel_build_pro'),  # pro环境执行停止构建
    path('job_manage/console_qa/<int:jenkins_env>/<path:job_name>/<int:num_id>', views.console_output_views,
         name='console_qa'),  # qa环境控制台输出页
    path('job_manage/console_pro/<int:jenkins_env>/<path:job_name>/<int:num_id>', views.console_output_views,
         name='console_pro'),  # pro环境控制台输出页
    path('job_manage/rollback_qa/<int:jenkins_env>/<path:job_name>', views.job_rollback_views,
         name='job_rollback_qa'), # qa环境回滚操作页
    path('job_manage/rollback_pro/<int:jenkins_env>/<path:job_name>', views.job_rollback_views,
         name='job_rollback_pro'),  # pro环境回滚操作页
    path('job_manage/rollback_version_qa/<int:jenkins_env>/<path:job_name>', views.rollback_version_views,
         name='rollback_version_qa'),  # qa环境回滚执行
    path('job_manage/rollback_version_pro/<int:jenkins_env>/<path:job_name>', views.rollback_version_views,
         name='rollback_version_pro'),  # pro环境回滚执行
    path('job_manage/configure_qa/<int:jenkins_env>/<path:job_name>', views.job_configure_views,
         name='job_configure_qa'),  # qa环境修改svn配置页
    path('job_manage/configure_pro/<int:jenkins_env>/<path:job_name>', views.job_configure_views,
         name='job_configure_pro'),  # pro环境修改svn配置页
    path('job_manage/reconfig_qa/<int:jenkins_env>/<path:job_name>', views.job_reconfig_views,
         name='job_reconfig_qa'), # qa环境修改svn配置执行
    path('job_manage/reconfig_pro/<int:jenkins_env>/<path:job_name>', views.job_reconfig_views,
         name='job_reconfig_pro'),  # pro环境修改svn配置执行
]
