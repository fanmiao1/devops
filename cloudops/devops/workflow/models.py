# Create your models here.
# from usercenter.models import Department
from django.db import models
from opscenter.models import Server, script
from django.contrib.auth.models import User, Group
from django.core.validators import validate_comma_separated_integer_list


class project(models.Model):
    SOURCE_CHOICES = (
        (0, '外购'),
        (1, '自建')
    )
    STATUS_CHOICES = (
        (0, '不通过'),
        (1, '未审批'),
        (2, '项目经理审批通过'),
        (3, 'CTO审批通过'),
        (4, '采购审批通过'),
        (5, '财务审批通过'),
        (9, '执行中')
    )
    applicant = models.ForeignKey(User,on_delete=models.SET_NULL, verbose_name='申请人',related_name='applicant_project',null=True)
    project = models.CharField(u'项目中文名',max_length=50)
    project_english = models.CharField(u'项目英文名', max_length=50, null=True)
    have_parent_project = models.BooleanField(u'是否有父项目',default=False)
    parent_project = models.CharField(u'父项目',max_length=50,null=True,blank=True,default='')
    project_manager = models.ForeignKey(User,on_delete=models.SET_NULL, verbose_name='项目经理',null=True)
    group = models.CharField(u'项目所属组', max_length=50)
    source = models.IntegerField(u'来源',choices=SOURCE_CHOICES)
    describe = models.TextField(u'描述')
    applicationtime = models.DateTimeField(u'申请时间',auto_now_add=True)
    approvaltime = models.DateTimeField(u'审批完成时间',null=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES)

    def __str__(self):
        return self.project

    class Meta:
        verbose_name_plural = "项目"


class Department(models.Model):
    depart_name = models.CharField(u'部门名称', max_length=100)
    project = models.ForeignKey(project,on_delete=models.CASCADE, verbose_name='项目')
    depart_director = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='部门负责人', null=True, blank=True)

    def __str__(self):
        return self.depart_name

    class Meta:
        verbose_name_plural = "部门"
        unique_together = ('depart_name', 'project')

class ProjectFlowLogs(models.Model):
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目申请记录')
    content = models.CharField(u'日志内容',max_length=500)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "workflow_project_flow_logs"


class project_group(models.Model):
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='负责项目')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, verbose_name='组成员')
    user_type = models.ForeignKey(Group, on_delete=models.CASCADE,null=True, verbose_name='成员类型')
    addtime = models.DateTimeField(u'添加时间',auto_now_add=True)

    def __str__(self):
        return str(self.project)


class project_userflow(models.Model):
    STATUS_CHOICES = (
        (0, '不通过'),
        (1, '未审批'),
        (9, '通过')
    )
    applicant = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='申请人',
                                  related_name='applicant_projectuser',null=True)
    project = models.ForeignKey(project,on_delete=models.CASCADE, verbose_name='项目')
    user_type = models.ForeignKey(Group,on_delete=models.CASCADE, verbose_name='成员类型')
    add_user = models.TextField(u'添加成员')
    describe = models.TextField(u'描述')
    applicationtime = models.DateTimeField(u'申请时间',auto_now_add=True)
    execute_time = models.DateTimeField(u'执行时间',null=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES)

    def __str__(self):
        return self.applicant


class ProjectUserFlowLogs(models.Model):
    project_user = models.ForeignKey(project_userflow, on_delete=models.CASCADE, verbose_name='成员申请记录')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "workflow_project_user_flow_logs"


class cronflow(models.Model):
    STATUS_CHOICES = (
        (0, u'不通过'),
        (1, u'待审批'),
        (2, u'待执行'),
        (9, u'已执行添加'),
    )
    applicant = models.ForeignKey(User,on_delete=models.CASCADE,null=True, verbose_name='申请人')
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    cron_time = models.CharField(u'时间', max_length=50)
    cron_order = models.CharField(u'命令', max_length=500)
    environmental = models.CharField(u'环境',max_length=100)
    # server_id = models.TextField(u'服务器ID', validators=[validate_comma_separated_integer_list])
    describe = models.TextField(u'描述')
    applicationtime = models.DateTimeField(u'申请时间', auto_now_add=True)
    execute_time = models.DateTimeField(u'执行时间', null=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES,help_text=u'0 不通过, 1 待审批, 2 待执行, 3 已执行添加')

    def __str__(self):
        return self.cron_order


class cronflow_logs(models.Model):
    cronflow = models.ForeignKey(cronflow, on_delete=models.CASCADE, verbose_name='计划任务申请记录')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content


from devops.settings import MEDIA_ROOT
import os
class project_releaseflow(models.Model):
    enclosure_path = os.path.join(MEDIA_ROOT, 'test_report_enclosure')
    PRIORITY_CHOICE = (
        (0, u'普通'),
        (1, u'紧急'),
    )
    STATUS_CHOICES = (
        (0, '不通过'),
        (1, '待审批'),
        (2, '测试审批通过'),
        (3, '项目经理审批通过'),
        (4, '待发布'),
        (9, '已发布')
    )
    applicant = models.ForeignKey(User,on_delete=models.CASCADE,null=True, verbose_name='申请人')
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    title = models.CharField(u'标题', max_length=100)
    describe = models.TextField(u'发布内容')
    version = models.CharField(u'版本号', max_length=100)
    priority = models.IntegerField(u'优先级', choices=PRIORITY_CHOICE, default=0)
    type = models.CharField(u'类型', max_length=50, null=True,default='',validators=[validate_comma_separated_integer_list])
    testingreport = models.TextField(u'测试报告')
    enclosure = models.FilePathField(path=enclosure_path,recursive=True,blank=True,null=True)
    applicationtime = models.DateTimeField(u'申请时间', auto_now_add=True)
    release_time = models.DateTimeField(u'发布时间', null=True)
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES)

    def __str__(self):
        return self.title


class releaseflow_logs(models.Model):
    releaseflow = models.ForeignKey(project_releaseflow, on_delete=models.CASCADE, verbose_name='项目变更申请记录')
    content = models.CharField(u'日志内容',max_length=500)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content


class project_user(models.Model):
    IS_ACTIVE_CHOICES = (
        (0, u'禁用'),
        (1, u'启用'),
    )
    user_name = models.CharField(u'用户名', max_length=100)
    name = models.CharField(u'名字', max_length=24,null=True)
    email = models.EmailField(u'Email', null=True)
    is_active = models.IntegerField(u'是否启用',choices=IS_ACTIVE_CHOICES,default=1)
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name=u'项目名',related_name='user_project',null=True)

    class Meta:
        unique_together = ('user_name', 'project')

    def __str__(self):
        return self.user_name


class UserChangeLogs(models.Model):
    user = models.ForeignKey(project_user, on_delete=models.CASCADE, verbose_name='项目用户更新记录')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    class Meta:
        db_table = "workflow_user_change_logs"


class authority_group(models.Model):
    group_name = models.CharField(u'组名', max_length=100)
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name=u'项目名',related_name='group_project',null=True)

    class Meta:
        unique_together = ('group_name', 'project')

    def __str__(self):
        return self.group_name


class AuthorityGroupChangeLogs(models.Model):
    group = models.ForeignKey(authority_group, on_delete=models.CASCADE, verbose_name='组',null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    content = models.CharField(u'日志内容',max_length=500)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    class Meta:
        db_table = "workflow_authority_group_change_logs"


class user_group(models.Model):
    user_name = models.ForeignKey(project_user, on_delete=models.CASCADE, verbose_name= u'用户id')
    group = models.ForeignKey(authority_group, on_delete=models.CASCADE, verbose_name= u'组id')

    def __str__(self):
        return self.user_name


class authority(models.Model):
    '''
        角色表
    '''
    authority_name = models.CharField(u'角色名', max_length=100)
    project_name = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name=u'项目',related_name='authority_project',null=True)

    class Meta:
        unique_together = ('authority_name', 'project_name')

    def __str__(self):
        return self.authority_name


class AuthorityChangeLogs(models.Model):
    authority = models.ForeignKey(authority, on_delete=models.CASCADE, verbose_name='角色')
    content = models.CharField(u'日志内容',max_length=5000)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "workflow_authority_change_logs"


class Module(models.Model):
    '''
        模块表(权限表)
    '''
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name=u'项目',related_name='module_project',null=True)
    module_name = models.CharField(u'模块名称',max_length=100)
    module_url = models.CharField(u'模块url', max_length=200)

    def __str__(self):
        return self.module_name


class ModuleChangeLogs(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name='模块(权限)')
    content = models.CharField(u'日志内容',max_length=5000)
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "workflow_module_change_logs"


class authority_module(models.Model):
    authority = models.ForeignKey(authority, on_delete=models.CASCADE, verbose_name= u'角色id')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name= u'模块id')

    class Meta:
        unique_together = ('authority', 'module')


class user_authority(models.Model):
    authority_name = models.ForeignKey(authority, on_delete=models.CASCADE, verbose_name= u'权限id')
    user_name = models.ForeignKey(project_user, on_delete=models.CASCADE, verbose_name= u'用户id')

    def __str__(self):
        return self.authority_name


class authority_flow(models.Model):

    APPLICATION_STATUS_CHOICES=(
        (0, u'不通过'),
        (1, u'待审批'),
        (2, u'待执行'),
        (3, u'权限变更完成'),
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name= u'申请人')
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name=u'项目')
    modify_user = models.ForeignKey(project_user, on_delete=models.CASCADE, verbose_name=u'要修改的用户')
    department = models.ForeignKey(Department,on_delete=models.CASCADE, verbose_name=u'部门',null=True)
    old_authority = models.TextField(u'原权限', null=True)
    new_authority = models.TextField(u'修改后的权限', null=True)
    describe = models.TextField(u'描述', null=True)
    applicationtime = models.DateTimeField(u'申请时间', auto_now_add=True)
    execute_time = models.DateTimeField(u'执行时间', null=True, help_text="执行时间")
    status = models.IntegerField(u'状态',  choices=APPLICATION_STATUS_CHOICES,
                              help_text=u'0 不通过, 1 待审批, 2 待执行, 3 已执行')

    def __str__(self):
        return self.project


class authorityflow_logs(models.Model):
    authority_flow = models.ForeignKey(authority_flow, on_delete=models.CASCADE, verbose_name='权限修改申请记录')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content


class ProjectUserApplyFlow(models.Model):
    IS_ACTIVE_CHOICES = (
        (0, u'禁用'),
        (1, u'启用'),
    )
    TYPE_CHOICES = (
        (0, u'添加用户'),
        (1, u'修改用户'),
    )
    STATUS_CHOICES=(
        (0, u'不通过'),
        (1, u'待审批'),
        (2, u'待执行'),
        (3, u'执行完成'),
    )
    project = models.ForeignKey(project, on_delete=models.CASCADE, verbose_name='项目')
    submitter = models.ForeignKey(User, on_delete=models.CASCADE,null=True, verbose_name= u'提交人')
    applicant = models.CharField(u'申请人', max_length=50)
    user_name = models.CharField(u'用户名', max_length=50)
    name = models.CharField(u'姓名', max_length=50,null=True)
    email = models.EmailField(u'Email',null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=u'部门', null=True)
    user_group = models.TextField(u'分配组', null=True)
    remarks = models.TextField(u'备注', null=True)
    is_active = models.IntegerField(u'是否启用',choices=IS_ACTIVE_CHOICES,default=1)
    applicationtime = models.DateTimeField(u'申请时间', auto_now_add=True)
    execute_time = models.DateTimeField(u'执行时间', null=True, help_text="执行时间")
    type = models.IntegerField(u'类型',choices=TYPE_CHOICES,null=True)
    status = models.IntegerField(u'状态',choices=STATUS_CHOICES)

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = "workflow_project_user_apply_flow"


class ProjectUserApplyLogs(models.Model):
    user_apply_flow = models.ForeignKey(ProjectUserApplyFlow, on_delete=models.CASCADE, verbose_name='项目用户申请记录')
    content = models.TextField(u'日志内容')
    datetime = models.DateTimeField(u'时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "workflow_project_user_apply_logs"


class WorkFlowIMG(models.Model):
    filename = models.CharField(max_length=200, blank=True, null=True)
    img  = models.ImageField(upload_to = './img')

    def __str__(self):
        return self.filename

    class Meta:
        db_table = "workflow_img"


class ProjectApplyComment(models.Model):
    """
    项目申请沟通记录
    """
    project = models.ForeignKey(project,on_delete=models.CASCADE,verbose_name='项目ID')
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def  __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_project_apply_comment'


class ProjectMemberApplyComment(models.Model):
    """
    项目成员变更申请沟通记录
    """
    project_userflow = models.ForeignKey(project_userflow,on_delete=models.CASCADE,verbose_name='项目成员申请工作流ID')
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def  __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_project_member_apply_comment'


class ProjectUserApplyComment(models.Model):
    """
    项目用户变更申请沟通记录
    """
    user_apply_flow = models.ForeignKey(ProjectUserApplyFlow, on_delete=models.CASCADE, verbose_name='项目用户申请工作流ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_project_user_apply_comment'


class ProjectUserAuthorityApplyComment(models.Model):
    """
    项目用户权限变更申请沟通记录
    """
    authority_flow = models.ForeignKey(authority_flow, on_delete=models.CASCADE, verbose_name='项目用户权限申请工作流ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_project_user_authority_apply_comment'


class ProjectReleaseApplyComment(models.Model):
    """
    项目变更申请沟通记录
    """
    project_releaseflow = models.ForeignKey(project_releaseflow, on_delete=models.CASCADE, verbose_name='项目变更申请工作流ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_project_release_apply_comment'


class CronApplyComment(models.Model):
    """
    项目变更申请沟通记录
    """
    cronflow = models.ForeignKey(cronflow, on_delete=models.CASCADE, verbose_name='计划任务申请工作流ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='用户')
    content = models.TextField('内容')
    datetime = models.DateTimeField('发表时间', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'workflow_cron_apply_comment'