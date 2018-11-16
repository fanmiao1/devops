from django.db import models
from django.contrib.auth.models import User,Group
import django.utils.timezone as timezone

class ModuleNameInfo(models.Model):
    module_name = models.CharField(u'模块中文名',max_length=128,null=True)
    build_number = models.IntegerField(u'构建号',null=True)
    build_user = models.ForeignKey(User,on_delete=models.SET_NULL,verbose_name='构建执行人',null=True)
    build_status = models.IntegerField(u'构建状态',null=True)
    start_time = models.DateTimeField(u'构建时间',auto_now_add=True)
    jenkins_env = models.IntegerField(u'构建环境',null=True)

    def __str__(self):
        return self.module_name

    class Meta:
        verbose_name_plural = '模块中文名'

class JenkinsConfig(models.Model):
    url = models.URLField(verbose_name='服务器URL')
    username = models.CharField(u'用户名',max_length=64,null=True)
    token = models.CharField(u'连接token',max_length=128,null=True)
    jenkins_id = models.IntegerField(u'记录ID',null=True)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name_plural = '服务器URL'
