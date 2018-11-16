from django import forms
from .models import *
from workflow.models import project
from django.core.validators import RegexValidator


'''
@author: qingyw
@note: 「MySQL 数据库管理模块」 表单
'''


# def validate_instance(value):
#     if value == '--- 请选择 ---':
#         raise ValidationError(
#             _('%(value)s is not an even number'),
#             params={'value': value},
#             # _('请选择数据库实例'),
#         )


class InstanceForm(forms.Form):
    env = ((1, '生产环境'), (2, '测试环境'), (3, '开发环境'))

    server_ip = forms.CharField(label='服务器 IP', max_length=100, error_messages={
        'required': '请填写服务器 IP',
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'server_ip', 'placeholder': 'Server IP'}))

    instance_name = forms.CharField(label='实例名', max_length=20, error_messages={
        'required': '请填写实例名',
        'max_length': '实例名太长'
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'instance_name', 'placeholder': 'Instance Name'}))

    ops_user = forms.ModelChoiceField(label='运维DBA', required=True,
                                      queryset=Group.objects.get(name='运维DBA').user_set.all(), to_field_name="id",
                                      empty_label="-- 请选择类型 --", widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control', 'id': 'ops_user',
                   'placeholder': 'Ops User', 'data-live-search': 'true'}))

    project_name = forms.ModelChoiceField(label='所属项目',required=True,
                                          queryset=project.objects.filter(status=9), to_field_name="id",
                                          empty_label="-- 请选择类型 --", widget=forms.Select(
            attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control',
                   'name': 'project_name', 'data-live-search':'true'}))

    instance_type = forms.ModelChoiceField(label='类型',required=True, queryset=Category.objects.all(), to_field_name="id",
                                           empty_label="-- 请选择类型 --", widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control', 'id': 'instance_type',
                   'placeholder': 'Instance Type', 'data-live-search':'true'}))

    instance_username = forms.CharField(label='用户名', max_length=20, error_messages={
        'required': '请填写用户名',
        'max_length': '用户名太长'
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'instance_username', 'placeholder': 'Instance UserName'}))

    instance_password = forms.CharField(label='密码', error_messages={
        'required': '请填写密码'
    }, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'instance_password', 'placeholder': 'Instance Password',
        }))

    confirm_password = forms.CharField(label='确认密码', error_messages={
        'required': '确认密码'
    }, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password', 'placeholder': 'Confirm Password',
               }))

    instance_port = forms.IntegerField(label='端口', error_messages={
        'required': '请填写端口'
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'instance_port', 'placeholder': 'Instance Port'}))

    instance_env = forms.CharField(label='所属环境', widget=forms.Select(choices=env,
                                                                     attrs={
                                                                         'class': 'selectpicker show-tick form-control',
                                                                         'id': 'instance_env',
                                                                         'placeholder': 'Instance Env'}))


class ApplySQLForm(forms.Form):
    project_name = forms.CharField(label='项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))
    # project_name = forms.ModelChoiceField(label='项目', required=False,
    #                                       queryset=project.objects.filter(status=9),
    #                                       empty_label="-- 请选择项目 --", to_field_name="id", widget=forms.Select(
    #         attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control',
    #                'name': 'project_name', 'data-live-search': 'true'}))

    instance_name = forms.CharField(label='实例',  max_length=50, error_messages={
        'required': '请选择实例'
    },  widget=forms.Select(
        attrs={'id': 'instance_name', 'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'name': 'instance name'}))

    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'data-live-search': 'true', 'id': 'project_manager',
               'placeholder': 'Project Manager'}))

    ops_user = forms.CharField(label='运维DBA', max_length=50, error_messages={
        'required': '请选择运维DBA'
    }, widget=forms.Select(
        attrs={'id': 'ops_user', 'class': 'form-control', 'name': 'Ops User'}))
    # try:
    #     ops_manager = forms.ModelChoiceField(label='运维DBA审批', queryset=Group.objects.get(name='运维DBA').user_set.all(),
    #                                          initial=0, to_field_name="id", widget=forms.Select(
    #             attrs={'id': 'ops_manager', 'class': 'selectpicker show-tick form-control',
    #                    'name': 'Ops Manager', 'data-live-search':'true'}))
    # except:
    #     ops_manager = forms.CharField(label='运维DBA审批',widget=forms.Select(
    #             attrs={'id': 'ops_manager', 'class': 'selectpicker show-tick form-control'}))

    execute_sql = forms.CharField(label='执行 SQL', required=None, error_messages={
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'execute_sql', 'rows': '25',
               'placeholder': '多个 SQL 请使用 ; 隔开，且必须带数据库前缀， 如：UPDATE test.aukeyit SET rank = 1;'
               }))

    application_content = forms.CharField(label='申请说明', error_messages={
        'required': '请填写申请说明'
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'application_content', 'placeholder': '请详细描述此 SQL 用途'}))


class ApplyNewUserForm(forms.Form):
    privilege = (
        ('INSERT', 'insert'),
        ('DELETE', 'delete'),
        ('UPDATE', 'update'),
        ('SELECT', 'select'),
        ('CREATE', 'create'),
        ('INDEX', 'index'),
        ('ALTER', 'alter'),
        ('EVENT', 'event'),
        ('EXECUTE', 'execute'),
        ('CREATE VIEW', 'create view'),
        ('CREATE ROUTINE', 'create routine'),
        ('ALTER ROUTINE', 'alter routine'),
    )
    ip_seg = ((0, '请选择访问网段'), ('10.1.1.%', '10.1.1.%'), ('192.168.%', '192.168.%'), ('%', '%'))
    user_validator = RegexValidator(r'^[0-9a-zA-Z_]+$', "Can only contain Underline, Letters and Numbers.")
    project_name = forms.CharField(label='项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))

    instance_name = forms.CharField(label='实例', max_length=50, error_messages={
    }, widget=forms.Select(
        attrs={'id': 'instance_name', 'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'name': 'instance name'}))

    database_name = forms.CharField(label=u'数据库', required=True, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '', 'data-live-search': 'true',
               'id': 'database_name', 'placeholder': 'Database Name'}))

    table_name = forms.CharField(label=u'数据表', required=False, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '',
               'data-live-search': 'true', 'id': 'table_name', 'placeholder': 'Table Name'}))

    privileges = forms.CharField(label=u'申请权限：', widget=forms.SelectMultiple(
        choices=privilege,
        attrs={
            'class': 'selectpicker show-tick form-control',
            'data-actions-box': 'true',
            'multiple': '',
            'data-live-search': 'true',
            'id': 'privileges',
            'placeholder': 'privileges'}))

    ip_segment = forms.CharField(label=u'IP 网段',
                                 widget=forms.Select(choices=ip_seg,
                                                     attrs={'id': 'ip_segment',
                                                            'class': 'selectpicker show-tick form-control',
                                                            'name': 'ip_segment'}
                                                     ))

    username = forms.CharField(label=u'用户名', max_length=50, validators=[user_validator], error_messages={
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username', 'placeholder': 'userName', 'autocomplete': 'off'}))

    password = forms.CharField(label=u'密码', max_length=50, error_messages={
    }, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password', 'placeholder': 'password'}))

    confirm_password = forms.CharField(label='确认密码', error_messages={
        'required': '确认密码'
    }, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password', 'placeholder': 'Confirm Password',
               }))

    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'project_manager',
               'placeholder': 'Project Manager'}))

    ops_user = forms.CharField(label='运维DBA', max_length=50, error_messages={
        'required': '请选择运维DBA'
    }, widget=forms.Select(
        attrs={'id': 'ops_user', 'class': 'form-control', 'name': 'Ops User'}))
    application_content = forms.CharField(label=u'申请说明', error_messages={
        'required': '请填写申请说明'
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'application_content', 'placeholder': 'Application Content'}))


class ApplyPrivilegeForm(forms.Form):
    privilege = (
        ('INSERT', 'insert'),
        ('DELETE', 'delete'),
        ('UPDATE', 'update'),
        ('SELECT', 'select'),
        ('CREATE', 'create'),
        ('INDEX', 'index'),
        ('ALTER', 'alter'),
        ('EVENT', 'event'),
        ('EXECUTE', 'execute'),
        ('CREATE VIEW', 'create view'),
        ('CREATE ROUTINE', 'create routine'),
        ('ALTER ROUTINE', 'alter routine'),
    )
    project_name = forms.CharField(label='项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))

    instance_name = forms.CharField(label='实例', required=True, max_length=50, error_messages={
    }, widget=forms.Select(
        attrs={'id': 'instance_name', 'class': 'selectpicker show-tick form-control',
               'data-live-search': 'true', 'name': 'instance name'}))

    username = forms.CharField(label=u'数据库用户', error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '', 'data-live-search': 'true',
               'id': 'username', 'placeholder': 'username'}))

    database_name = forms.CharField(label=u'数据库', required=True, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '', 'data-live-search': 'true',
               'id': 'database_name', 'placeholder': 'Database Name'}))

    table_name = forms.CharField(label=u'数据表', required=False, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '',
               'data-live-search': 'true', 'id': 'table_name', 'placeholder': 'Table Name'}))

    privileges = forms.CharField(label=u'申请权限：', widget=forms.SelectMultiple(
        choices=privilege,
        attrs={
            'class': 'selectpicker show-tick form-control',
            'data-actions-box': 'true',
            'multiple': '',
            'data-live-search': 'true',
            'id': 'privileges',
            'placeholder': 'privileges'}))

    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'id': 'project_manager', 'placeholder': 'Project Manager'}))

    ops_user = forms.CharField(label='运维DBA', max_length=50, required=True, error_messages={
        'required': '请选择运维DBA'
    }, widget=forms.Select(
        attrs={'id': 'ops_user', 'class': 'form-control', 'name': 'Ops User'}))
    application_content = forms.CharField(label=u'申请说明', error_messages={
        'required': '请填写申请说明'
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'application_content', 'placeholder': 'Application Content'}))


class DebriefingForm(forms.Form):
    """
    提交执行结果
    """
    content = forms.CharField(label='', error_messages={
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '25', 'placeholder': '请填写执行结果', 'id': 'debriefing'}))


class SQLForm(forms.Form):
    """
    查询/编辑 SQL
    """
    exec_sql = forms.CharField(label='', error_messages={
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '25', 'placeholder': '多个 SQL 请使用 ; 隔开', 'id': 'sqlform'}))


class rebackForm(forms.Form):
    """
    驳回表单
    """
    reback_reason = forms.CharField(label='', max_length=2000, error_messages={
    }, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请填写驳回意见', 'id': 'rebackform'}))


class SQLAlertForm(forms.Form):
    """
    SQL 预警表单
    """
    time_unit = (
        (1, u'SECONDS'),
        (2, u'MINUTES'),
        (3, u'HOURS'),
        (4, u'DAYS'),
    )
    interval_validator = RegexValidator(r'^[0-9]+$', "Can only contain Numbers.")
    title = forms.CharField(label='标题', error_messages={
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'title',
               'placeholder': '标题'
               }))
    project_name = forms.CharField(label='项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))

    instance_name = forms.CharField(label='实例', max_length=50, error_messages={
        'required': '请选择实例'
    }, widget=forms.Select(
        attrs={'id': 'instance_name', 'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'name': 'instance name'}))
    carbon_copy = forms.CharField(label=u'抄送人', required=False, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '', 'data-live-search': 'true',
               'id': 'carbon_copy', 'placeholder': 'cc'}))
    sql = forms.CharField(label='预警 SQL', error_messages={
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'sql', 'rows': '25',
               'placeholder': '请填写SQL'
               }))
    interval = forms.CharField(label='间隔时间', validators=[interval_validator], error_messages={
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'interval', 'placeholder': '间隔时间'
               }))
    interval_unit = forms.CharField(label='时间单位', error_messages={
    }, widget=forms.Select(choices=time_unit,
        attrs={'class': 'form-control', 'id': 'interval_unit', 'placeholder': '时间单位'
               }))
    application_content = forms.CharField(label='申请说明', error_messages={
        'required': '请填写申请说明'
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'application_content', 'placeholder': '请详细描述此 SQL 用途'}))


class DataMigrateForm(forms.Form):
    """
    数据迁移表单
    """
    export_data = ((0, '表结构'), (1, '表结构+数据'))
    new_db = ((1, '新建数据库'), )
    export_opt = ((3, '导出视图'), (0, '导出存储过程与函数'), (1, '导出定时事件'), (2, '迁移前备份目标端数据'))
    title = forms.CharField(label=u'标题', error_messages={
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'title',
               'placeholder': '标题'
               }))
    project_name = forms.CharField(label=u'项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))

    origin_instance = forms.CharField(label=u'源实例', required=True, error_messages={
        'required': '请选择实例'
    }, widget=forms.Select(
        attrs={'id': 'origin_instance', 'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'name': 'origin_instance'}))
    target_instance = forms.CharField(label=u'目标实例', required=True, error_messages={
        'required': '请选择实例'
    }, widget=forms.Select(
        attrs={'id': 'target_instance', 'class': 'selectpicker show-tick form-control', 'data-live-search': 'true',
               'name': 'target_instance'}))
    origin_db = forms.CharField(label=u'源数据库', required=True, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'multiple': '',
               'data-live-search': 'true', 'id': 'origin_db', 'placeholder': 'origin db'}))
    target_db = forms.CharField(label=u'目标数据库', required=False, error_messages={
    }, widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'data-live-search': 'true', 'id': 'target_db'}))
    origin_tab = forms.CharField(label=u'源数据库表', required=True, error_messages={
    }, widget=forms.SelectMultiple(
        attrs={'class': 'selectpicker show-tick form-control', 'data-actions-box': 'true', 'multiple': '',
               'data-live-search': 'true', 'id': 'origin_tab', 'placeholder': 'origin table'}))

    application_content = forms.CharField(label='申请说明', required=False, error_messages={
        'required': '请填写申请说明'
    }, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'application_content'}))
    is_export_data = forms.ChoiceField(
        label='导出方式', widget=forms.RadioSelect(attrs={'id': 'is_export_data', 'class': 'flat'}), choices=export_data)
    export_option = forms.CharField(label=u'导出选项', required=False, error_messages={
    }, widget=forms.CheckboxSelectMultiple(choices=export_opt,
                                           attrs={'id': 'export_option',
                                                  'class': 'js-switch',
                                                  'name': 'export_option'}))
