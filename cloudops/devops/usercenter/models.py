# Create your models here.
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import post_save
from workflow.models import Department

#==================扩展用户====================================
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部门', null=True, blank=True)

    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    """Create the UserProfile when a new User is saved"""
    if created:
        profile = UserProfile()
        profile.user = instance
        profile.save()

post_save.connect(create_user_profile, sender=User)
#==================扩展用户结束================================


class Permission(models.Model):
    """
    @author: Xieyz
    @note: 平台权限
    """
    chioces = (
        (1, 'GET'),
        (2, 'POST')
    )
    name = models.CharField("权限名称", max_length=64)
    url = models.CharField('URL名称', max_length=255)
    per_method = models.SmallIntegerField('请求方法', choices=chioces, default=1)
    argument_list = models.CharField('参数列表', max_length=255, help_text='多个参数之间用英文半角逗号隔开', blank=True, null=True)
    describe = models.CharField('描述', max_length=255)

    def __str__(self):
        return self.describe

    class Meta:
        verbose_name = '权限表'
        verbose_name_plural = verbose_name
        permissions = (
            ('views_project_details', '项目管理 - 查看项目详情'),
            ('actions_project_add', '项目管理 - 立项申请'),
            ('views_project_add', '项目管理 - 进入立项申请页面'),
            ('project_manager_approval_project_Apply', '项目经理审批 - (项目申请)'),
            ('views_releaseflow_add', '项目变更 - 进入申请项目变更页面'),
            ('views_releaseflow_details', '项目变更 - 查看项目变更详情'),
            ('project_manager_approval_project_release','项目经理审批 - (项目变更)'),
            ('views_project_user_add','项目成员变更 - 进入申请添加项目成员页面'),
            ('views_project_user_details','项目成员变更 - 查看项目成员申请详情'),
            ('project_manager_approval_project_user_apply','项目经理审批 - (项目成员变更申请)'),
            ('views_cron_apply', '计划任务变更 - 进入申请计划任务页面'),
            ('views_cron_apply_details', '计划任务变更 - 查看计划任务申请详情'),
            ('project_manager_approval_cron_apply','项目经理审批 - (计划任务申请)'),
            ('views_cron_list','计划任务管理 - 查看计划任务列表'),
            ('views_cron_details','计划任务管理 - 查看计划任务详情'),
            ('delete_cron','计划任务管理 - 删除计划任务'),
            ('revision_cron','计划任务管理 - 修改计划任务'),
            ('views_cron_revision_logs','计划任务管理 - 查看计划任务修改记录'),
            ('views_project_authority_flow_list','业务用户权限变更 - 查看用户权限变更工作流列表'),
            ('views_project_authority_apply','业务用户权限变更 - 进入申请业务用户权限变更页面'),
            ('action_project_authority_apply','业务用户权限变更 - 申请业务用户权限变更'),
            ('views_project_authority_detail','业务用户权限变更 - 查看用户权限变更详情'),
            ('project_manage_approval_authority_apply','部门负责人审批 - (业务用户权限变更申请)'),
            ('views_project_user_apply_list', '业务用户变更 - 查看业务用户申请列表'),
            ('views_project_user_add_apply', '业务用户变更 - 进入业务用户申请页面'),
            ('action_project_user_add_apply', '业务用户变更 - 业务用户申请添加'),
            ('views_project_user_modify_apply', '业务用户变更 - 进入业务用户修改页面'),
            ('action_project_user_modify_apply', '业务用户变更 - 业务用户申请修改'),
            ('views_project_user_apply_detail', '业务用户变更 - 查看业务用户申请详情'),
            ('project_manager_approval_user_apply', '部门负责人审批 - (业务用户变更申请)'),
            ('views_user_manage', '业务用户管理 - 查看业务用户列表'),
            ('views_user_detail', '业务用户管理 - 查看业务用户详情'),
            ('action_user_is_active', '业务用户管理 - 修改业务用户状态'),
            ('views_role_list', '业务角色管理 - 查看角色列表'),
            ('views_role_module_list', '业务角色管理 - 查看角色包含的权限列表'),
            ('views_role_add', '业务角色管理 - 进入添加角色页面'),
            ('action_role_add', '业务角色管理 - 添加角色'),
            ('views_role_module_modify', '业务角色管理 - 进入角色权限修改页面'),
            ('action_role_module_modify', '业务角色管理 - 角色权限修改'),
            ('views_module_list', '业务权限管理 - 查看所有权限列表'),
            ('views_module_add', '业务权限管理 - 进入添加权限页面'),
            ('action_module_add', '业务权限管理 - 添加权限'),
            ('views_module_modify', '业务权限管理 - 进入修改权限页面'),
            ('action_module_modify', '业务权限管理 - 修改权限'),
            ('views_module_change_history', '业务权限管理 - 查看权限修改记录'),
            ('cto_approval_project_apply','CTO审批 - (项目管理)项目申请'),
            ('purchase_approval_project_apply','采购审批 - (项目管理)项目申请'),
            ('finance_approval_project_apply','财务审批 - (项目管理)项目申请'),
            ('views_project_apply_list','项目管理 - 查看项目申请列表'),
            ('views_project_release_list','项目变更 - 查看项目变更申请列表'),
            ('views_project_member_apply_list','项目成员变更 - 查看项目成员变更列表'),
            ('views_cron_apply_list','计划任务变更 - 查看计划任务申请列表'),
            ('action_implement_user_authority_change','执行 - 业务用户权限变更'),
            ('action_implement_user_operate','执行 - 业务用户变更'),
            ('action_implement_cron_change','执行 - 计划任务变更'),
            ('action_project_user_add','项目成员变更 - 申请添加项目成员'),
            ('action_cron_apply','计划任务变更 - 申请计划任务'),
            ('action_releaseflow_add','项目变更 - 申请项目变更'),
            ('test_approval_project_release', '测试审批 - (项目变更)'),
            ('implement_project_release', '执行发布 - (项目变更)'),
            ('project_release_submit_test_report', '测试审批 - (项目变更-提交测试报告)'),
            ('views_database_release_list', '数据库变更 - 查看数据库变更列表'),
            ('views_apply_new_user', '数据库变更 - 进入申请用户页面'),
            ('action_apply_new_user', '数据库变更 - 申请用户'),
            ('views_apply_privilege', '数据库变更 - 进入申请授权页面'),
            ('action_apply_privilege', '数据库变更 - 申请授权'),
            ('views_apply_sql', '数据库变更 - 进入申请执行SQL页面'),
            ('action_apply_sql', '数据库变更 - 申请执行SQL'),
            ('action_review_sql', '数据库变更 - 校验SQL'),
            ('views_database_release_detail', '数据库变更 - 查看变更详情'),
            ('project_manager_approval_database_release_apply', '项目经理审批 - (数据库变更)'),
            ('operations_Manager_approval_database_release_apply', '运维DBA审批 - (数据库变更)'),
            ('views_instances', '数据库管理 - 查看实例列表'),
            ('action_delete_instance', '数据库管理 - 删除实例'),
            ('views_instance_detail', '数据库管理 - 查看实例详情'),
            ('views_add_instance', '数据库管理 - 进入添加实例页面'),
            ('action_add_instance', '数据库管理 - 添加实例'),
            ('views_modify_instance', '数据库管理 - 进入修改实例页面'),
            ('action_modify_instance', '数据库管理 - 修改实例'),
            ('project_user_add', '业务用户管理 - 业务用户添加'),
            ('project_user_modify', '业务用户管理 - 业务用户修改'),
            ('project_authority_group_list_view', '业务用户组管理 - 查看业务用户组列表'),
            ('project_authority_group_user_list_view', '业务用户组管理 -  查看业务用户组内成员列表'),
            ('project_authority_group_add', '业务用户组管理 - 添加组'),
            ('project_authority_group_modify', '业务用户组管理 - 修改组'),
            ('project_group_user_change', '业务用户组管理 - 修改组内用户'),
            ('project_authority_group_delete', '业务用户组管理 - 删除组'),
            ('views_show_privileges', '数据库管理 - 实例列表 - 查看用户权限'),
            ('views_delete_dbuser', '数据库管理 - 实例列表 - 用户权限 - 删除用户'),
            ('views_db_application_reback', '数据库变更 - 驳回数据库变更工作流'),
            ('jump_queries_analyzing','数据库管理 - 跳转到查询分析页面'),
            ('jump_monitor','数据库管理 - 跳转到监控页面'),
            ('database_release_implement','执行 - 数据库变更'),
            ('fixed_asset_manage','固定资产管理'),
            ('jenkins_qa', 'jenkins - qa环境'),
            ('jenkins_pro', 'jenkins - pro环境'),
            ('script_manage', '脚本管理'),
        )


class Message(models.Model):
    """
    @author: Xieyz
    @note: 平台消息中心
    """
    STATUS_CHOICES = (
        (0, '未读'),
        (1, '已读')
    )
    title = models.CharField(u'标题', max_length=100)
    content = models.CharField(u'内容', max_length=1000)
    url = models.CharField(u'url', max_length=200)
    time = models.DateTimeField(u'时间', null=True)
    type = models.CharField(u'消息类型',max_length=20)
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户')
    status = models.IntegerField(u'状态',choices=STATUS_CHOICES,help_text='0 未读 1 已读')

    def __str__(self):
        return self.title


class SystemModule(models.Model):
    """
    @author: Xieyz
    @note: 平台菜单模块
    """
    module_url = models.CharField(u'模块url', max_length=100)
    module_name = models.CharField(u'模块名称', max_length=100)

    class Meta:
        verbose_name = '平台菜单模块'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.module_name


class Org(models.Model):
    """
    @author: Xieyz
    @note: 组织结构
    """
    oid = models.IntegerField(u'oid')
    name = models.CharField(u'名称', max_length=100)
    org_data = models.TextField(u'组织结构数据')

    class Meta:
        verbose_name = '组织结构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Clients(models.Model):
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    channel_name = models.CharField(u'频道名称', max_length=256)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.channel_name
