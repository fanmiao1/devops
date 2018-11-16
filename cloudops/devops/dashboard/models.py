from django.db import models

# Create your models here.

from django.db import models
from opscenter.models import Support
from django.contrib.auth.models import User, Group
# Create your models here.
'''
@author: qingyw
@note: 「dashboard 模块」 models
'''


class RDSInstance(models.Model):
    support_id = models.CharField(u'云平台账号id', max_length=20, help_text="SupportID")
    instance_id = models.CharField(u'实例id', max_length=50, help_text="InstanceID")
    instance_type = models.CharField(u'实例类型', max_length=50, help_text="InstanceType")
    instance_class = models.CharField(u'实例类别', max_length=100, help_text="InstanceClass")
    engine = models.CharField(u'引擎', max_length=100, help_text="Engine")
    engine_version = models.CharField(u'引擎版本', max_length=100, help_text="EngineVersion")
    region_id = models.CharField(u'实例region', max_length=100, help_text="RegionId")
    instance_description = models.CharField(u'实例描述', max_length=100, help_text="InstanceDesc")
    create_time = models.DateTimeField(u'创建时间', help_text="create_time")
    expire_time = models.DateTimeField(u'创建时间', help_text="expire_time")
    instance_status = models.CharField(u'实例状态', max_length=20, help_text="instance_status")

    def __str__(self):
        return self.instance_id

