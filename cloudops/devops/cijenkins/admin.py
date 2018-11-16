from django.contrib import admin
from .models import JenkinsConfig

'''资产'''
@admin.register(JenkinsConfig)
class JenkinsConfigAdmin(admin.ModelAdmin):
    list_display = ('url','username', 'token', 'jenkins_id')
    list_per_page = 20
    ordering = ('-id',)
'''资产'''