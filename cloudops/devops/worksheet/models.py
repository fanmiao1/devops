from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list

# Create your models here.
class WorkSheetType(models.Model):
    type_name = models.CharField(u'工单类型名称', max_length=128)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = '工单类型'
        verbose_name_plural = '工单类型'
        db_table = 'worksheet_type'


class WorkSheet(models.Model):
    STATUS_CHOICES = (
        (0, '已关闭'),
        (4, '待审批'),
        (1, '未受理'),
        (2, '待处理'),
        (3, '已处理'),
    )
    RESULT_CHOICES = (
        (1, '已解决'),
        (2, '未解决'),
        (3, '自动关闭'),
        (4, '客服关闭'),
        (5, '审批不通过')
    )
    wsid = models.CharField(u'工单编号', max_length=32, unique=True)
    title = models.CharField(u'标题', max_length=128, blank=False)
    description = models.TextField(u'描述', null=True, blank=True)
    type = models.ForeignKey(WorkSheetType,on_delete=models.SET_NULL, verbose_name='工单类型',related_name='worksheet_type', null=True, blank=True)
    source = models.CharField(u'来源', max_length=32, null=True, blank=True)
    submitter = models.CharField(u'提交人', max_length=32,default='')
    submitter_userid = models.CharField(u'提交人', max_length=64,default='')
    submitter_email = models.CharField(u'提交人邮箱', max_length=128,default='')
    have_power_change = models.BooleanField(u'是否需要抄送邮箱',default=False)
    email = models.TextField(u'抄送邮箱', blank=False,null=True,default='',validators=[validate_comma_separated_integer_list])
    status = models.IntegerField(u'状态',choices=STATUS_CHOICES)
    c_time = models.DateTimeField(u'提交时间', auto_now_add=True)
    p_time = models.DateTimeField(u'审批时间', null=True, blank=True)
    a_time = models.DateTimeField(u'受理时间', null=True, blank=True)
    f_time = models.DateTimeField(u'处理时间', null=True, blank=True)
    deadline = models.DateField(u'截止日期', null=True, blank=True)
    is_delay = models.IntegerField(u'是否延期', default=0, help_text="0 未延期 1 已延期")
    receive_pepole = models.ForeignKey(User,on_delete=models.SET_NULL, verbose_name='受理人',related_name='receive_pepole',null=True, blank=True)
    operator = models.ForeignKey(User,on_delete=models.SET_NULL, verbose_name='处理人',related_name='operator',null=True, blank=True)
    result = models.IntegerField(u'结果', choices=RESULT_CHOICES,null=True,blank=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['wsid']
        verbose_name = '工单'
        verbose_name_plural = '工单'


class WorksheetFile(models.Model):
    CHOICES_TYPE = (
        (0, '图片'),
        (1, '文件')
    )
    worksheet =  models.ForeignKey(WorkSheet, on_delete=models.SET_NULL, null=True, verbose_name='工单')
    filename = models.CharField(u'文件名', max_length=255)
    file_type = models.IntegerField(u'文件类型', choices=CHOICES_TYPE)
    file = models.FileField(u'文件路径', upload_to='./worksheet')
    update_pepole = models.CharField(u'上传人', max_length=48, default='用户')
    update_date = models.DateTimeField('上传时间', auto_now_add=True, null=True)

    def __str__(self):
        return self.filename

    class Meta:
        verbose_name = '工单附件'
        verbose_name_plural = '工单附件'
        db_table = 'worksheet_file'


class WorksheetRemind(models.Model):
    remind = models.TextField(u'工单登记提示信息')

    def __str__(self):
        return self.remind

    class Meta:
        verbose_name = '工单登记提示信息'
        verbose_name_plural = '工单登记提示信息'
        db_table = 'worksheet_remind'


class WorksheetOperateLogs(models.Model):
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE, verbose_name='工单')
    content = models.TextField('内容')
    datetime = models.DateTimeField('时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '工单操作记录'
        verbose_name_plural = verbose_name
        db_table = 'worksheet_operate_logs'


class WorksheetCommunicate(models.Model):
    """
    工单沟通记录
    """
    PEPOLE_CHOICES = (
        (0, '用户'),
        (1, '客服'),
    )
    TYPE_CHOICES = (
        (0, '回复'),
        (1, '反馈'),
    )
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE, verbose_name='工单')
    pepole = models.IntegerField(u'发表人', choices=PEPOLE_CHOICES)
    content = models.TextField('内容')
    type = models.IntegerField('类型', choices=TYPE_CHOICES,default=0)
    datetime = models.DateTimeField('发表时间', auto_now_add=True)
    user_look = models.BooleanField(u'用户是否查看',default=False)
    service_look = models.BooleanField(u'客服是否查看',default=False)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '工单沟通记录'
        verbose_name_plural = verbose_name
        db_table = 'worksheet_communicate'


class AutoReplyQuestion(models.Model):
    """
    自动回复的问题对应答案
    """
    qid = models.IntegerField(u'问题ID', unique=True)
    question = models.CharField(u'问题', max_length=128)
    answer = models.TextField('答案')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = '工单系统企业微信自动回复'
        verbose_name_plural = verbose_name
        db_table = 'worksheet_auto_reply_question'


class EmailWorksheetCount(models.Model):
    count = models.IntegerField(u'数量', null=True)

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = '工单邮件数量(必须和工单接收邮箱的收件箱数量相同)'
        verbose_name_plural = verbose_name


class CurrentDomain(models.Model):
    domain_id = models.IntegerField(u'域名ID',unique=True)
    domain = models.CharField(u'域名', max_length=254)

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name = '当前域名'
        verbose_name_plural = verbose_name


class WechatApp(models.Model):
    app_id = models.IntegerField(u'应用ID',unique=True)
    agent_id = models.CharField(u'AgentId', max_length=254)
    secret = models.CharField(u'Secret', max_length=254)
    contact_secret = models.CharField(u'Contact_Secret', max_length=254, null=True)
    app = models.CharField(u'应用', max_length=254)

    def __str__(self):
        return self.app

    class Meta:
        verbose_name = '企业微信应用'
        verbose_name_plural = verbose_name


class EmailGroup(models.Model):
    email = models.CharField(u'邮箱', max_length=64, unique=True)
    email_name = models.CharField(u'邮箱归属', max_length=64)

    def __str__(self):
        return self.email_name

    class Meta:
        verbose_name = '邮箱群组'
        verbose_name_plural = verbose_name


class ReceiveEmail(models.Model):
    email_id = models.IntegerField(u'邮箱ID',unique=True)
    email = models.EmailField(u'邮箱', unique=True)
    email_password = models.CharField(u'邮箱密码', max_length=128, null=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = '工单接收邮箱'
        verbose_name_plural = verbose_name
