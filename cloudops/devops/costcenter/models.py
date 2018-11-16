from django.db import models


class GoodsType(models.Model):
    """物品类型"""
    name = models.CharField(u'名称', max_length=32)
    customize = models.TextField(u'定制字段', null=True, blank=True)
    is_delete = models.BooleanField(u'是否删除', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'物品类型'
        verbose_name_plural = verbose_name


class Purchase(models.Model):
    """采购订单"""
    STATUS_CHOICES = (
        (1, u'已申请'),
        (2, u'待审批'),
        (3, u'采购中'),
        (4, u'已开票'),
        (5, u'已完结')
    )
    PURCHASE_TYPE_CHOICES = (
        (1, u'新购'),
        (2, u'续费'),
        (3, u'升级')
    )
    applicant = models.CharField(u'申购人', max_length=32, null=True, blank=True)
    applicant_email = models.EmailField(u'申购人邮箱', null=True, blank=True)
    application_date = models.DateField(u'申购日期', null=True, blank=True)
    department_id = models.CharField(u'所属部门ID', max_length=64, null=True, blank=True)
    department = models.CharField(u'所属部门', max_length=64, null=True, blank=True)
    group = models.CharField(u'所属组', max_length=64, null=True, blank=True)
    approver = models.CharField(u'部门审批人', max_length=32, null=True, blank=True)
    approver_email = models.EmailField(u'部门审批人邮箱', null=True, blank=True)
    goods = models.CharField(u'申购物品', max_length=64)
    count = models.IntegerField(u'申购数量', default=1)
    unit_price = models.CharField(u'单价', max_length=16, null=True, blank=True)
    type = models.ForeignKey(GoodsType, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name=u'物品类型', related_name='purchase_type')
    standard = models.TextField(u'规格', null=True, blank=True)
    purchaser = models.CharField(u'采购人', max_length=32, null=True, blank=True)
    purchaser_email = models.EmailField(u'采购人邮箱', null=True, blank=True)
    purchase_date = models.DateField(u'采购日期', null=True, blank=True)
    purchase_type = models.IntegerField(u'采购类型', choices=PURCHASE_TYPE_CHOICES)
    total_price = models.FloatField(u'总价', null=True, blank=True)
    receiver = models.CharField(u'接收人', max_length=32, null=True, blank=True)
    receiver_email = models.EmailField(u'接收人邮箱', null=True, blank=True)
    receive_date = models.DateField(u'接收日期', null=True, blank=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES, default=1,
                                 help_text=" 1 已申请 2 待审批 3 采购中 4 已开票 5 已完结")
    other_info = models.TextField(u'其他信息', null=True, blank=True)
    remark = models.TextField(u'备注', null=True, blank=True)
    is_delete = models.BooleanField(u'是否删除', default=False)

    def __str__(self):
        return self.goods

    class Meta:
        verbose_name = u'采购订单'
        verbose_name_plural = verbose_name
