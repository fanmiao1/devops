from django.contrib import admin
from .models import AutoReplyQuestion,WorkSheetType,WorksheetRemind,CurrentDomain,WechatApp,EmailGroup,\
    EmailWorksheetCount,WorksheetCommunicate,WorksheetOperateLogs,WorksheetFile,WorkSheet,ReceiveEmail


'''自动回复的问题和答案'''
@admin.register(AutoReplyQuestion)
class WorksheetQAAdmin(admin.ModelAdmin):
    list_display = ('qid','question', 'answer')
    list_per_page = 20
    ordering = ('-id',)
'''自动回复的问题和答案'''


'''工单类型'''
@admin.register(WorkSheetType)
class WorksheetTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    list_per_page = 20
    ordering = ('-id',)
'''工单类型'''


'''工单登记提示信息'''
@admin.register(WorksheetRemind)
class WorksheetRemindAdmin(admin.ModelAdmin):
    list_display = ('remind',)
    list_per_page = 20
    ordering = ('-id',)
'''工单登记提示信息'''


'''当前域名'''
@admin.register(CurrentDomain)
class CurrentDomainAdmin(admin.ModelAdmin):
    list_display = ('domain_id','domain')
    list_per_page = 20
    ordering = ('-id',)
'''当前域名'''


'''企业微信应用'''
@admin.register(WechatApp)
class WechatAppAdmin(admin.ModelAdmin):
    list_display = ('app_id','agent_id','secret','app')
    list_per_page = 20
    ordering = ('-id',)
'''企业微信应用'''


'''邮箱群组'''
@admin.register(EmailGroup)
class EmailGroupAdmin(admin.ModelAdmin):
    list_display = ('email_name','email')
    list_per_page = 20
    ordering = ('-id',)
'''邮箱群组'''


'''工单邮件数量'''
@admin.register(EmailWorksheetCount)
class EmailWorksheetCountAdmin(admin.ModelAdmin):
    list_display = ('id', 'count',)
    list_per_page = 20
    ordering = ('-id',)
'''工单邮件数量'''


'''工单'''
@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_filter = ('source', 'type', 'status')  # 过滤器
    list_display = ('wsid','title','source','submitter','type','have_power_change','c_time','status')
    list_per_page = 20
    ordering = ('-id',)
'''工单'''


'''工单接收邮箱'''
@admin.register(ReceiveEmail)
class ReceiveEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'email_id')
    list_per_page = 20
    ordering = ('-id',)
'''工单接收邮箱'''