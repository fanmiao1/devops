from django.contrib import admin
from .models import Protocol, Certificate, Support, Server, ServerGroup, cron, DetectWeb, DetectWebAlarmLogs


'''协议'''
@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 20
    ordering = ('-id',)
'''协议'''

'''凭证'''
@admin.register(Certificate)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'protocol', 'username', 'port')
    list_per_page = 20
    ordering = ('-id',)
'''凭证'''

'''服务商'''
@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_key_id', 'access_key_secret', 'remark')
    list_per_page = 20
    ordering = ('-id',)
'''服务商'''

'''服务器'''
@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'name', 'inner_ip', 'public_ip', 'os', 'certificate', 'support')
    list_per_page = 20
    ordering = ('-id',)
'''服务器'''

'''服务器分组'''
@admin.register(ServerGroup)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent_id')
    list_per_page = 20
    ordering = ('-id',)
'''服务器分组'''

'''计划任务'''
@admin.register(cron)
class CronAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 20
    ordering = ('-id',)
'''计划任务'''

'''Web检测'''
@admin.register(DetectWeb)
class DetectWebAdmin(admin.ModelAdmin):
    list_display = ('website','description','detect_count','last_detect_time')
    list_per_page = 20
    ordering = ('-id',)
'''Web检测'''

'''Web检测记录'''
@admin.register(DetectWebAlarmLogs)
class DetectWebAlarmLogsAdmin(admin.ModelAdmin):
    list_display = ('web','status_code','level','time')
    list_per_page = 20
    ordering = ('-id',)
'''Web检测记录'''
