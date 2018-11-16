from django.contrib import admin
from django.urls import path
from django.conf.urls import *
from database import views

# 数据库管理#
urlpatterns = [
    path('instances/', views.instances, name='instances'),
    path('rds/', views.rds, name='rds'),
    path('instances/<int:id>', views.instances, name='delete_instance'),
    path('instance/<int:id>', views.instance_detail, name='instance_detail'),
    path('instance/ops_info/<int:id>/', views.show_operation_log, name='show_operation_log'),
    path('instance/add', views.add_instance, name='add_instance'),
    path('instance/<int:id>/process/kill/<int:process_id>', views.instance_detail, name='kill_process'),
    path('instance/modify/<int:id>/', views.modify_instance, name='modify_instance'),
    path('instance/jump_queries_analyzing',views.jump_queries_analyzing, name='jump_queries_analyzing'),
    path('instance/jump_monitor', views.jump_monitor, name='jump_monitor'),
]

# 数据库变更#
urlpatterns += [
    path('instance/get_database/<int:instance_id>/', views.get_database, name='get_database'),
    path('instance/get_database_table/', views.get_database_table, name='get_database_table'),
    path('instance/get_user/<int:instance_id>/', views.get_user, name='get_user'),
    path('instance/get_instance/<int:project_id>/', views.get_project_instance, name='get_project_instance'),
    path('instance/get_project_user/<int:project_id>/', views.get_project_user, name='get_project_user'),
    path('instance/get_instance_dba/<int:instance_id>/', views.get_instance_dba, name='get_instance_dba'),
    path('instance/apply/new/user/', views.apply_new_user, name='apply_new_user'),
    path('instance/apply/privilege/', views.apply_privilege, name='apply_privilege'),
    path('instance/apply/sql/', views.apply_sql, name='apply_sql'),
    path('instance/release_flow/', views.database_release_flow_view, name='database_release_flow'),
    path('instance/release_flow/release_delete/<int:id>/', views.database_release_delete, name='database_release_delete'),
    path('instance/release_flow/release_detail/<int:id>/', views.database_release_detail_view,
         name='database_release_detail'),
    path('instance/release_flow/release_approval/<int:id>_<int:control>/', views.database_release_approval_view,
         name='database_release_approval'),
    path('instance/release_flow/release_ops_approval/<int:id>_<int:control>/', views.database_release_approval_view,
         name='database_release_ops_approval'),
    path('instance/release_flow/release_implement/<int:id>_<int:control>/', views.database_release_approval_view,
         name='database_release_implement'),
    path('instance/show_privileges/<int:id>/', views.show_privileges, name='show_privileges'),
    path('instance/show_privileges/<int:id>/<str:user>', views.show_privileges, name='database_delete_user'),
    path('instance/reset/passwd/<int:id>/<str:user>', views.reset_db_passwd, name='reset_db_passwd'),
    path('instance/get/privs/<int:id>/<str:user>', views.get_user_privilege, name='get_user_privilege'),
    path('instance/revoke/privs/<int:id>/', views.revoke_user_privilege, name='revoke_user_privilege'),
    path('instance/sql/review/', views.review_sql, name='review_sql'),
    path('instance/sql/search/', views.search_sql, name='search_sql'),
    path('instance/get_user/', views.get_project, name='get_project'),
]


# 数据库预警#
urlpatterns += [
    path('instance/sqlalert/', views.sql_alert, name='sql_alert'),
    path('instance/sqlalert/<int:id>/', views.sql_alert, name='delete_sql_alert'),
    path('instance/sqlalert/log/<int:id>/', views.sql_alert_log, name='sql_alert_log'),
    path('instance/sqlalert/add', views.apply_sql_alert, name='apply_sql_alert'),
    path('instance/sqlalert/release_detail/<int:id>/', views.sqlalert_detail, name='sql_alert_detail'),
    path('instance/sqlalert/release_detail/pm/<int:id>_<int:control>/', views.sqlalert_approval,
         name='sqlalert_manager_approval'),
    path('instance/sqlalert/release_detail/ops/<int:id>_<int:control>/', views.sqlalert_approval,
         name='sqlalert_dba_approval'),
    path('instance/sqlalert/release_detail/start/<int:id>_<int:control>/', views.sqlalert_enable,
         name='sqlalert_start_approval'),
    path('instance/sqlalert/release_detail/stop/<int:id>_<int:control>/', views.sqlalert_enable,
         name='sqlalert_stop_approval'),
    path('instance/sqlalert/onverify/<int:id>/', views.sqlalert_onverify,
         name='sqlalert_onverify'),
]

# 数据迁移 #
urlpatterns += [
    path('instance/datamigrate/', views.data_migrate, name='data_migrate'),
    path('instance/datamigrate/<int:id>/', views.data_migrate, name='delete_data_migrate'),
    path('instance/datamigrate/log/<int:id>/', views.data_migrate_log, name='data_migrate_log'),
    path('instance/datamigrate/add', views.apply_data_migrate, name='apply_data_migrate'),
    path('instance/datamigrate/release_detail/<int:id>/', views.datamigrate_detail, name='data_migrate_detail'),
    path('instance/datamigrate/reback/<int:id>/', views.datamigrate_reback, name='datamigrate_reback'),
    path('instance/datamigrate/release_detail/pm/<int:id>_<int:control>/', views.datamigrate_approval,
         name='datamigrate_manager_approval'),
    path('instance/datamigrate/release_detail/ops/<int:id>_<int:control>/', views.datamigrate_approval,
         name='datamigrate_dba_approval'),
    path('instance/datamigrate/release_detail/exec/<int:id>_<int:control>/', views.datamigrate_approval,
         name='datamigrate_exec_approval'),
    # path('instance/datamigrate/release_detail/start/<int:id>_<int:control>/', views.sqlalert_enable,
    #      name='sqlalert_start_approval'),
    # path('instance/datamigrate/onverify/<int:id>/', views.sqlalert_onverify,
    #      name='sqlalert_onverify'),
]


# 数据监控 #
urlpatterns += [
    path('instance/monitor/get_rds_perf/', views.aliyun_instance_monitordata, name='get_rds_perf'),
    # path('instance/monitor/get_local_perf/<int:id>/', views.collect_local_mysql, name='get_local_perf'),
    path('instance/monitor/get_monitor_data/', views.get_monitor_data, name='get_monitor_data'),
    path('instance/monitor/show_db_monitor/', views.MonitorDetailView.as_view(), name='show_db_monitor'),

]
