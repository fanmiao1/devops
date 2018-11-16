from django.db import models
from django.contrib.auth.models import User
from opscenter.models import Support


class AssetType(models.Model):
    """资产类型"""
    name = models.CharField(u'类型名称', max_length=64, unique=True)
    customize_asset_field = models.TextField(u'定制资产字段', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "cmdb_asset_type"
        verbose_name = '资产类型'
        verbose_name_plural = verbose_name


class Supplier(models.Model):
    """供应商"""
    name = models.CharField(u'供应商名称', max_length=64)
    contact = models.CharField(u'联系人', max_length=64, null=True, blank=True)
    fixed_telephone = models.CharField(u'固定电话', max_length=16, null=True, blank=True)
    mobile_phone = models.CharField(u'手机号码', max_length=16, null=True, blank=True)
    address = models.CharField(u'地址', max_length=254, null=True, blank=True)
    email = models.EmailField(u'邮箱', null=True, blank=True)
    qq = models.CharField(u'qq', max_length=16, null=True, blank=True)
    remark = models.TextField(u'备注', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "cmdb_supplier"
        verbose_name = '供应商'
        verbose_name_plural = verbose_name


class Assets(models.Model):
    """资产"""
    STATUS_CHOICES = (
        (1, u'在库'),
        (2, u'借出'),
        (3, u'维修'),
        (4, u'报废'),
    )
    asset_id = models.CharField(u'资产编码', max_length=64, unique=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, verbose_name='资产类型',
                                   related_name='asset_type', null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='操作人',
                                      related_name='asset_operator', null=True, blank=True)
    operate_time = models.DateTimeField(u'操作时间', auto_now_add=True, null=True, blank=True)
    buy_time = models.DateField(u'采购日期', null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, verbose_name='供应商',
                                 related_name='supplier', null=True, blank=True)
    use_person = models.CharField(u'使用人', max_length=64, null=True)
    use_time = models.DateTimeField(u'领用时间', null=True)
    asset_info = models.TextField(u'资产信息', null=True, blank=True)
    status = models.IntegerField(u'资产状态', choices=STATUS_CHOICES)
    remark = models.TextField(u'备注', null=True, blank=True)

    def __str__(self):
        return self.asset_id

    class Meta:
        db_table = "cmdb_assets"
        verbose_name = '固定资产'
        verbose_name_plural = verbose_name


class Assetlogs(models.Model):
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE, verbose_name='资产')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='操作人',
                                 related_name='asset_log_operator', null=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "cmdb_asset_logs"
        verbose_name = '固定资产日志'
        verbose_name_plural = verbose_name


class AssetFlow(models.Model):
    """资产流动记录"""
    TYPE_CHOICES = (
        (1, u'入库'),
        (2, u'借出'),
        (3, u'还回'),
        (4, u'维修'),
        (5, u'报废'),
    )
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE, verbose_name='资产',
                              related_name='asset', null=True)
    hand_person = models.CharField(u'经手人', max_length=32, null=True)
    hand_person_email = models.EmailField(u'经手人邮箱', null=True)
    type = models.IntegerField(u'类型', choices=TYPE_CHOICES)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='操作人',
                                      related_name='asset_flow_operator', null=True)
    time = models.DateTimeField(u'时间',  null=True)
    remark = models.TextField(u'备注', null=True)

    def __str__(self):
        return self.asset.asset_id

    class Meta:
        db_table = "cmdb_asset_flow"
        verbose_name = '固定资产流动记录'
        verbose_name_plural = verbose_name


class DomainManage(models.Model):
    """域名管理"""
    STATUS_CHOICES = (
        (1, u'未使用'),
        (2, u'使用中'),
        (3, u'已过期')
    )
    domain = models.CharField(u'域名', max_length=64, null=True, blank=True)
    register_date = models.DateField(u'注册日期', null=True, blank=True)
    expire_date = models.DateField(u'到期日期', null=True, blank=True)
    is_auto_pay = models.BooleanField(u'是否自动续费', default=0)
    bisnis_responsible = models.CharField(u'业务负责人', max_length=32, null=True, blank=True)
    bisnis_responsible_email = models.EmailField(u'业务负责人邮箱', null=True, blank=True)
    register_support = models.ForeignKey(Support, on_delete=models.SET_NULL, verbose_name='注册服务商',
                                      related_name='domain_register_support', null=True)
    dns_support = models.ForeignKey(Support, on_delete=models.SET_NULL, verbose_name='域名解析服务商',
                                      related_name='domain_dns_support', null=True)
    dns_record = models.TextField(u'解析记录', null=True, blank=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES, default=1)
    remark = models.TextField(u'备注', null=True, blank=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True, null=True)
    is_delete = models.BooleanField(u'是否删除', default=0)

    def __str__(self):
        return self.domain

    class Meta:
        db_table = "cmdb_domain_manage"
        verbose_name = '域名管理'
        verbose_name_plural = verbose_name
