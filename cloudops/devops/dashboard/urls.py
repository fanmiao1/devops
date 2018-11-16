from dashboard import views
from django.urls import path

# 数据库管理#
urlpatterns = [
    path('ali/instance/monitor', views.aliyun_instance_monitordata, name='aliyun_instance_monitordata'),

]