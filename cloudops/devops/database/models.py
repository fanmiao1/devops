from django.db import models
from workflow.models import project
from opscenter.models import Support
from django.contrib.auth.models import User, Group
from django_celery_beat.models import PeriodicTask, IntervalSchedule
# Create your models here.
'''
@author: qingyw
@note: 「MySQL 数据库管理模块」 models
'''


class Category(models.Model):
    # TYPE_CHOICES = (
    # 	(1, u'MySQL'),
    # 	(2, u'SQL SERVER'),
    # 	(3, u'MongoDB'),
    # 	(4, u'Oracle'),
    # 	(5, u'金蝶数据库'),
    # 	(6, u'Redis'),
    # )
    cate_name = models.CharField(u'数据库', max_length=20, help_text="db type")
    createtime = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")

    def __str__(self):
        return self.cate_name


class Instance(models.Model):
    ENV_CHOICES = (
        (1, u'生产环境'),
        (2, u'测试环境'),
        (3, u'开发环境'),
    )
    server_ip = models.CharField(u'服务器IP', max_length=100, help_text="服务器IP 地址，转为数值型存储")
    instance_name = models.CharField(u'实例名', max_length=20, help_text="实例名")
    instance_env = models.IntegerField(u'所属环境', help_text="1 生产环境 2 测试环境 3 开发环境", choices=ENV_CHOICES)
    project = models.ForeignKey(project, on_delete=models.CASCADE,
                                      verbose_name="所属项目")
    instance_username = models.CharField('用户', max_length=20, help_text="数据库用户")
    instance_password = models.CharField(u'用户密码', max_length=100, help_text="数据库密码")
    instance_port = models.IntegerField(u'实例端口', help_text="实例端口")
    instance_type = models.ForeignKey(Category, on_delete=models.CASCADE,
                                      verbose_name="数据库类型：MySQL, SQL SERVER, MongoDB 等等 ")
    instance_role = models.CharField(u'实例角色', max_length=10, help_text="实例角色：主、从、主/从", null=True)
    createtime = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")
    ops_user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="运维人员")
    is_delete = models.IntegerField(u'是否删除', default=0, help_text="0 未删除 1 已删除")

    def __str__(self):
        return self.instance_name


class InstanceStruct(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, verbose_name='实例')
    main_host = models.CharField(u'主库IP', max_length=100, help_text="主库地址")
    main_port = models.IntegerField(u'主库端口', help_text="主库端口")
    subordinate_type = models.IntegerField(u'从库类型', help_text="从库类型：实时从库，延时从库")
    subordinate_delay = models.IntegerField(u'从库延迟', help_text="从库类型：实时从库，延时从库")
    createtime = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")
    updatetime = models.DateTimeField(u'更新时间', null=True, help_text="更新时间")


class Application(models.Model):
    APPLICATION_TYPE_CHOICES = (
        (1, u'申请权限'),
        (2, u'新建用户'),
        (3, u'执行SQL'),
    )
    APPLICATION_STATUS_CHOICES = (
        (0, u'驳回'),
        (1, u'待审批'),
        (2, u'项目经理审批通过'),
        (3, u'运维DBA审批通过'),
        (4, u'已执行'),
        (5, u'执行中'),
    )
    appliant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id', verbose_name='申请人')
    application_type = models.IntegerField(u'申请类型', help_text="申请类型 1 申请权限 2 新建用户 3 执行 SQL",
                                           choices=APPLICATION_TYPE_CHOICES)
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, verbose_name='实例ID')
    ops_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ops_manager_id', verbose_name='运维DBA')
    application_content = models.TextField(u'申请说明', help_text="申请说明")
    execute_sql = models.TextField(u'执行SQL', help_text="执行 SQL", default='')
    execute_result = models.TextField(u'执行结果', help_text="执行结果", default='')
    application_time = models.DateTimeField(u'申请时间', auto_now_add=True, help_text="申请时间")
    execute_time = models.DateTimeField(u'执行时间', null=True, help_text="执行时间")
    finished_time = models.DateTimeField(u'完成时间', null=True, help_text="完成时间")
    application_status = models.IntegerField(u'状态', default=1, help_text=" 0 驳回 1 待审批 2 项目经理审批通过 3 运维DBA审批通过 4 已执行",
                                             choices=APPLICATION_STATUS_CHOICES)
    reback_reason = models.CharField(u'驳回意见', max_length=2000, help_text="驳回意见", default='')
    review_result = models.TextField(u'校验结果', help_text="校验结果", default='')
    last_review_time = models.DateTimeField(u'最后校验时间',auto_now_add=True, help_text="最后校验时间")
    is_delete = models.IntegerField(u'是否删除', default=0, help_text="0 未删除 1 已删除")


class InstanceLog(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, verbose_name='instance ID')
    content = models.TextField(u'更新内容', default='', help_text="更新内容")
    createtime = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")


class ApplicationLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name='application ID')
    content = models.TextField(u'更新内容', default='', help_text="更新内容")
    createtime = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")


class SQLAlert(models.Model):
    time_unit = (
        (1, u'seconds'),
        (2, u'minutes'),
        (3, u'hours'),
        (4, u'days'),
    )
    APPLICATION_STATUS_CHOICES = (
        (0, u'驳回'),
        (1, u'待审批'),
        (2, u'项目经理审批通过'),
        (3, u'运维DBA审批通过'),
        (4, u'启用'),
        (5, u'停用'),
    )

    class Meta:
        permissions = (
            ('sqlalert_dba_approval', '数据预警SQL-DBA 审批'),
            ('sqlalert_manager_approval', '数据预警SQL-项目经理审批'),
            ('sqlalert_start_approval', '数据预警SQL-启用预警SQL'),
            ('sqlalert_stop_approval', '数据预警SQL-停用预警SQL'),
            ('delete_sql_alert', '数据预警SQL-删除申请'),
            ('apply_sql_alert', '数据预警SQL-申请预警SQL'),
            ('sql_alert_detail', '数据预警SQL-查看详情'),
            ('sql_alert', '数据预警SQL-查看列表'),
        )

    title = models.TextField(u't标题', default='', help_text='标题')
    sql = models.TextField(u'预警SQL', default='', help_text="预警SQL")
    carbon_copy = models.CharField(u'抄送人', max_length=80, help_text="抄送人", default='')
    interval = models.IntegerField(u'执行间隔', default=0, help_text="执行间隔")
    interval_unit = models.IntegerField(u'时间单位', default=2, help_text="时间单位")
    start_time = models.DateTimeField(u'开始时间', auto_now_add=True, help_text="开始时间")
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, verbose_name='实例ID')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    application_time = models.DateTimeField(u'申请时间', auto_now_add=True, help_text="申请时间")
    application_content = models.TextField(u'申请说明', help_text="申请说明")
    application_status = models.IntegerField(u'状态', default=1, help_text=" 0 驳回 1 待审批 2 项目经理审批通过 3 运维DBA审批通过",
                                             choices=APPLICATION_STATUS_CHOICES)
    reback_reason = models.CharField(u'驳回意见', max_length=2000, help_text="驳回意见", default='')
    review_result = models.TextField(u'校验结果', help_text="校验结果", default='')
    last_review_time = models.DateTimeField(u'最后校验时间', auto_now_add=True, help_text="最后校验时间")
    is_delete = models.IntegerField(u'是否删除', default=0, help_text="0 未删除 1 已删除")
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL,
                                      verbose_name='定时任务')


class SQLAlertLog(models.Model):
    sql_alert = models.ForeignKey(SQLAlert, on_delete=models.CASCADE, verbose_name='SQL Alert ID')
    content = models.TextField(u'更新内容', default='', help_text="更新内容")
    create_time = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")


class DataMigrate(models.Model):
    APPLICATION_STATUS_CHOICES = (
        (0, u'驳回'),
        (1, u'待审批'),
        (2, u'项目经理审批通过'),
        (3, u'运维DBA审批通过'),
        (4, u'迁移中'),
        (5, u'已迁移'),
    )

    class Meta:
        permissions = (
            ('datamigrate_dba_approval', '数据迁移-运维DBA审批'),
            ('datamigrate_manager_approval', '数据迁移-项目经理审批'),
            ('datamigrate_exec_approval', '数据迁移-执行'),
            ('delete_data_migrate', '数据迁移-删除'),
            ('apply_data_migrate', '数据迁移-申请'),
            ('data_migrate_detail', '数据迁移-详情'),
            ('data_migrate', '数据迁移-列表'),
            ('datamigrate_reback', '数据迁移-驳回'),
        )
    title = models.TextField(u't标题', default='', help_text='标题')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    origin_instance = models.ForeignKey(Instance, related_name='origin_instance',  null=True, blank=True, on_delete=models.SET_NULL, verbose_name='源实例ID')
    target_instance = models.ForeignKey(Instance, related_name='target_instance', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='目标实例ID')
    origin_db = models.TextField(u'源数据库', help_text="抄送人", default='')
    target_db = models.TextField(u'目标数据库', help_text="抄送人", default='')
    origin_tab = models.TextField(u'源迁移表', help_text="抄送人", default='')
    is_new_db = models.IntegerField(u'是否新建数据库', default=0, help_text="是否新建数据库")
    is_export_data = models.IntegerField(u'是否迁移数据', default=0, help_text="是否迁移数据")
    is_export_view = models.IntegerField(u'是否迁移 view', default=0, help_text="是否迁移视图")
    is_export_routine = models.IntegerField(u'是否迁移 routine', default=0, help_text="是否迁移存储过程与函数")
    is_export_event = models.IntegerField(u'是否迁移 event', default=0, help_text="是否迁移定时任务")
    is_export_target = models.IntegerField(u'是否保存目标实例数据', default=0, help_text="是否保存目标实例数据")
    application_time = models.DateTimeField(u'申请时间', auto_now_add=True, help_text="申请时间")
    application_content = models.TextField(u'申请说明', help_text="申请说明")
    application_status = models.IntegerField(u'状态', default=1, help_text=" 0 驳回 1 待审批 2 项目经理审批通过 3 运维DBA审批通过",
                                             choices=APPLICATION_STATUS_CHOICES)
    execute_time = models.DateTimeField(u'执行时间', null=True, help_text="执行时间")
    finished_time = models.DateTimeField(u'完成时间', null=True, help_text="完成时间")
    is_delete = models.IntegerField(u'是否删除', default=0, help_text="0 未删除 1 已删除")


class DataMigrateLog(models.Model):
    data_migrate = models.ForeignKey(DataMigrate, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField(u'更新内容', default='', help_text="更新内容")
    create_time = models.DateTimeField(u'添加时间', auto_now_add=True, help_text="添加时间")


class RDSInstance(models.Model):
    support = models.ForeignKey(Support, null=True, blank=True, on_delete=models.SET_NULL)
    instance_id = models.CharField(u'实例id', max_length=50, help_text="InstanceID")
    instance_type = models.CharField(u'实例类型', max_length=50, help_text="InstanceType")
    instance_class = models.CharField(u'实例类别', max_length=100, help_text="InstanceClass")
    engine = models.CharField(u'引擎', max_length=100, help_text="Engine")
    engine_version = models.CharField(u'引擎版本', max_length=100, help_text="EngineVersion")
    region_id = models.CharField(u'实例region', max_length=100, help_text="RegionId")
    instance_description = models.CharField(u'实例描述', max_length=100, help_text="InstanceDesc")
    create_time = models.DateTimeField(u'创建时间', help_text="create_time")
    expire_time = models.DateTimeField(u'过期时间', null=True, help_text="expire_time")
    instance_status = models.CharField(u'实例状态', max_length=20, help_text="instance_status")

    def __str__(self):
        return self.instance_id


class Item(models.Model):
    db_key = models.CharField(u'db_key', max_length=50, help_text="db_key")
    key_type = models.IntegerField(u'key_type', default=1, help_text="1:db 2:os 3....")
    delta = models.IntegerField(u'delta', default=0, help_text="是否计算差值")


class History(models.Model):
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL, help_text="item id")
    instance_id = models.CharField(u'实例id', max_length=50, help_text="InstanceID")
    clock = models.DateTimeField(u'clock', help_text="clock")
    value = models.FloatField(u'value', default=0.00, help_text="监控值")
    delta_value = models.FloatField(u'delta_value', default=0.00, help_text="监控差值")

