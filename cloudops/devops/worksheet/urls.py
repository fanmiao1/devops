from django.contrib import admin
from django.urls import path
from django.conf.urls import *
from worksheet import views
from .get_wechat_message import *
from django.views.static import serve
from devops.settings import MEDIA_ROOT

urlpatterns = [
    path('ws_img/', views.ws_uploadIMG, name='ws_uploadIMG'),
    path('ws_file/<path:type>/', views.ws_uploadFILE, name='ws_uploadFILE'),
    path('up_bundfile/<path:type>/<path:id>/', views.up_bundfile, name='up_bundfile'),
    path('delete_wsfile/', views.delete_wsfile, name='delete_wsfile'),
    url(r'^data/uploads/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, }),
    path('', views.workder, name='work_order'),  # 提交工单页面
    path('submit_success', views.submit_success, name='submit_success'), # 工单提交成功页面
    path('api_get_message/', wechat_auth, name='api_get_message'), # 接收消息api
    path('list/<int:status>/', views.workder_view, name='work_order_list'),  # 后台工单列表页面
    path('list/<int:status>/<int:id>/', views.workder_view, name='work_order_list_id'),  # 后台工单列表页面
    path('data/<int:status>', views.get_workder_data, name='work_order_data'),  # 后台工单列表数据
    path('work_order_receive/<int:status>_<int:id>/', views.work_order_receive, name='work_order_receive'), # 工单受理功能
    path('work_order_appoint/<int:id>/', views.work_order_appoint, name='work_order_appoint'), # 工单指派功能
    path('get_work_order_detail/<int:id>', views.get_work_order_detail, name='get_work_order_detail'), # 工单详情数据
    path('work_order_reply_comm/<int:people>_<int:id>/', views.work_order_reply_comm, name='work_order_reply_comm'), # 工单沟通回复
    path('work_order_record/',views.work_order_record_view, name='work_order_record'), # 用户工单记录页面
    path('get_work_order_record_data/<path:wechat_user_id>/', views.get_workder_record_data, name='get_work_order_record_data'), # 用户工单记录列表数据
    path('work_order_record/detail/<path:wsid>/', views.workder_record_detail_view, name='work_order_record_detail'), # 用户工单记录详情
    path('work_order_approval/<path:approval>/', views.work_order_approval, name='work_order_approval'), # 工单审批功能
    path('work_order_close/<int:id>/',views.work_order_close, name='work_order_close'), # 关闭工单
    path('answer_view/<path:qid>/', views.answer_view, name='answer_view'), #  问题答案页面
    path('qr_code/url=<path:url>/', views.qr_code, name='qr_code'),  # 工单提交成功页面
    path('reopen_worksheet/<int:id>/', views.reopen_worksheet, name='reopen_worksheet'),
    path('edit_deadline/<int:id>/', views.edit_deadline, name='edit_deadline'),
    path('edit_type/<int:id>/', views.edit_type, name='edit_type'),
]
