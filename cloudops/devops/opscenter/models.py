from django.db import models
from django.contrib.auth.models import User, Group, ContentType
from django.core.validators import validate_comma_separated_integer_list


class SshOperationLogs(models.Model):
    """ssh用户行为日志"""
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='用户')
    host = models.ForeignKey(u'Server', on_delete=models.PROTECT, verbose_name='实例')
    operation_record = models.TextField(u'操作记录')
    time = models.DateTimeField(u'记录时间', auto_now_add=True)

    def __str__(self):
        return self.host

    class Meta:
        db_table = "opscenter_ssh_operation_logs"


class script(models.Model):
    """脚本"""
    script_name = models.CharField(u'脚本名称', max_length=100)
    script_desc = models.CharField(u'脚本描述', max_length=500)
    script_group = models.CharField(u'脚本分类', max_length=100)
    script_content = models.TextField(u'脚本内容')
    script_user = models.CharField(u'添加人', max_length=50)
    datetime = models.DateTimeField(u'添加时间', auto_now_add=True)

    def __str__(self):
        return self.script_name


class script_log(models.Model):
    """脚本日志"""
    script = models.ForeignKey('script', on_delete=models.CASCADE, verbose_name="执行脚本")
    script_result = models.CharField(u'执行结果', max_length=5000)
    script_user = models.CharField(u'执行人', max_length=50)
    datetime = models.DateTimeField(u'执行时间', auto_now_add=True)

    def __str__(self):
        return self.script_user


class Protocol(models.Model):
    """协议"""
    TYPE_CHOICES = (
        (0, u'密码'),
        (1, u'密钥')
    )
    name = models.CharField(u'协议名称', max_length=64)
    type = models.IntegerField(u'类型', choices=TYPE_CHOICES, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '协议'
        verbose_name_plural = verbose_name


class Certificate(models.Model):
    """凭证"""
    name = models.CharField(u'凭证名称', max_length=64)
    protocol = models.ForeignKey(Protocol, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='协议', related_name='cert_protocol')
    username = models.CharField(u'用户名', max_length=32, null=True, blank=True)
    port = models.IntegerField(u'端口', null=True, blank=True)
    key = models.TextField(u'Key', null=True, blank=True)
    remark = models.TextField(u'备注', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '凭证'
        verbose_name_plural = verbose_name


class Support(models.Model):
    """服务商"""
    TYPE_CHOICES = (
        (1, u'Aliyun'),
        (2, u'UCloud'),
        (3, u'Amazon')
    )
    name = models.CharField(u'服务商名称', max_length=64)
    access_key_id = models.CharField(u'Access Key ID', max_length=64, null=True, blank=True)
    access_key_secret = models.CharField(u'Access Key Secret', max_length=64, null=True, blank=True)
    type = models.IntegerField(u'类型', choices=TYPE_CHOICES, null=True, blank=True)
    remark = models.TextField(u'备注', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '服务商'
        verbose_name_plural = verbose_name


class Server(models.Model):
    """服务器"""
    OS_CHOICES = (
        (0, u'Linux'),
        (1, u'Windows'),
    )
    server_id = models.CharField(u'实例ID', max_length=32)
    name = models.CharField(u'实例名', max_length=64)
    inner_ip = models.GenericIPAddressField(u'私有IP', protocol='both', null=True, blank=True)
    public_ip = models.GenericIPAddressField(u'公网IP', protocol='both', null=True, blank=True)
    os = models.IntegerField(u'操作系统', choices=OS_CHOICES)
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='凭证', related_name='server_certificate')
    support = models.ForeignKey(Support, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='服务商', related_name='server_support')
    region = models.CharField(u'地域', max_length=64, null=True, blank=True)
    manager = models.CharField(u'管理员', max_length=64, null=True, blank=True)
    server_info = models.TextField(u'实例信息', null=True, blank=True)
    remark = models.TextField(u'备注', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = verbose_name


class ServerGroup(models.Model):
    """服务器分组"""
    name = models.CharField(u'组名', max_length=32)
    server = models.TextField(u'服务器', blank=False, null=True, validators=[validate_comma_separated_integer_list])
    parent_id = models.IntegerField(u'父组ID', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '服务器分组'
        verbose_name_plural = verbose_name


class Monitor(models.Model):
    """监控信息"""
    monitor_key = models.CharField(u'监控key', max_length=254)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)
    info = models.TextField(u'监控信息', null=True, blank=True)

    def __str__(self):
        return self.monitor_key

    class Meta:
        verbose_name = '监控信息'
        verbose_name_plural = verbose_name


class AnsibleTask(models.Model):
    """Ansible任务"""
    STATUS_CHOICES = (
        ('队列中', '队列中'),
        ('执行中', '执行中'),
        ('完成', '完成'),
    )
    server_id = models.TextField(u'服务器ID', validators=[validate_comma_separated_integer_list])
    server_name = models.TextField(u'服务器名称', blank=False, null=True)
    module = models.CharField(u'模块', max_length=128)
    parameter = models.TextField(u'参数', null=True, blank=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    exec_time = models.DateTimeField(u'执行时间', null=True, blank=True)
    complete_time = models.DateTimeField(u'完成时间', null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 verbose_name='操作人', related_name='oper_user', null=True)
    status = models.CharField(u'状态', max_length=32, choices=STATUS_CHOICES, default='队列中')
    error = models.TextField(u'错误列表', null=True, blank=True)
    result = models.TextField(u'结果', null=True, blank=True)

    def __str__(self):
        return self.parameter

    class Meta:
        db_table = "opscenter_ansible_task"
        verbose_name = 'Ansible任务'
        verbose_name_plural = verbose_name


class cron(models.Model):
    STATUS_CHOICE = (
        ('loading', u'请求中'),
        ('running', u'启用'),
        ('disable', u'禁用'),
        ('delete', u'删除')
    )
    TYPE_CHOICE = (
        (0, u'执行指令'),
        (1, u'执行脚本')
    )
    name = models.CharField(u'名称', max_length=48, default='default')
    type = models.IntegerField(u'类型', choices=TYPE_CHOICE, default=0)
    order = models.TextField(u'指令', null=True, blank=True)
    script = models.ForeignKey(script, verbose_name='脚本', on_delete=models.SET_NULL, null=True, blank=True)
    trigger = models.TextField(u'触发器', default=None)
    describe = models.TextField(u'描述', null=True, blank=True)
    project = models.CharField(u'项目', null=True, blank=True, max_length=48)
    server = models.ForeignKey(Server, verbose_name='实例', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.CharField(u'操作人', null=True, blank=True, max_length=48)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True, null=True)
    status = models.CharField(u'状态', max_length=7, choices=STATUS_CHOICE)

    def __str__(self):
        return self.name


class RevisionLogs(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Model', null=True, blank=True)
    content = models.TextField(u'修改内容')
    object_id = models.IntegerField(u'对象ID', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='修改人')
    datetime = models.DateTimeField(u'修改时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "opscenter_revision_logs"
        verbose_name = '修改日志'
        verbose_name_plural = verbose_name


class DetectWeb(models.Model):
    website = models.CharField(u'主页url', max_length=254)
    username = models.CharField(u'用户名', max_length=96, null=True, blank=True)
    password = models.CharField(u'密码', max_length=96, null=True, blank=True)
    username_element_name = models.CharField(u'用户名元素名称', max_length=24, null=True, blank=True)
    password_element_name = models.CharField(u'密码元素名称', max_length=24, null=True, blank=True)
    login_after_url = models.CharField(u'登录后跳转的url', max_length=96, null=True, blank=True)
    description = models.CharField(u'描述', max_length=50, null=True, blank=True)
    detect_count = models.IntegerField(u'监测次数', default=0)
    last_detect_time = models.DateTimeField(u'最后检测时间', null=True, blank=True)

    def __str__(self):
        return self.website

    class Meta:
        db_table = "opscenter_detect_web"
        verbose_name = '检测网站'
        verbose_name_plural = verbose_name


class DetectWebAlarmLogs(models.Model):
    web = models.ForeignKey(DetectWeb, verbose_name='检测的网站', on_delete=models.CASCADE, related_name='detect_web_log')
    status_code = models.IntegerField(u'状态码', null=True, blank=True)
    level = models.IntegerField(u'严重级别[1,9]', help_text='[1,3]-一般, [4,6]-较重, [7,8]-严重, [9]-特别严重',
                                null=True, blank=True)
    content = models.TextField(u'内容', null=True, blank=True)
    time = models.DateTimeField(u'时间', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.web.website

    class Meta:
        db_table = "opscenter_detect_web_logs"
        verbose_name = '检测网站问题记录'
        verbose_name_plural = verbose_name
