# -*- coding: utf8 -*-
from django.contrib.auth.models import *
from django import forms
from .models import project
from django.db.models import Q


class ProjectForm(forms.Form):
    '''
        项目增加表单
    '''
    # group_select = [
    #     ('Default', 'Default'),
    # ]
    source_select = (
        (1, '自建'),
        (0, '外购'),
    )

    project_name = forms.CharField(label='项目名(中文)',max_length=20,error_messages={
        'required': '请填写项目名(中文)',
        'max_length': '项目名称太长'
    },widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'exampleInputName', 'placeholder': '填写项目名称'}))

    project_name_english = forms.CharField(label='项目名(英文)', max_length=20, required=False, error_messages={
        'required': '请填写项目名(英文)',
        'max_length': '项目名称太长'
    }, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'exampleInputNameEnglish', 'placeholder': 'Project Name (English)'}))

    have_parent_project = forms.CharField(label='是否有父项目',required=False,error_messages={'required':'请选择变更类型！'}, widget=forms.CheckboxInput(
        attrs={'class': 'js-switch'}))

    parent_project = forms.ModelChoiceField(
        label='父项目',required=False, queryset=project.objects.filter(status=9,have_parent_project=False).exclude(status=0),
        empty_label="-- 选择父项目 --", to_field_name="project",
        widget=forms.Select(
            attrs={'class': 'show-tick form-control', 'name': 'parent_project',
                   'id':'parent_project'}))

    source = forms.ChoiceField(
        label='项目来源', widget=forms.RadioSelect(attrs={'class': 'flat'}), choices = source_select)

    try:
        project_manager = forms.ModelChoiceField(
            label='项目经理',queryset=Group.objects.get(
                name='项目经理').user_set.all(),empty_label="-- 请选择 --",required=False,to_field_name="id",widget=forms.Select(
            attrs={'id':'exampleInputManage', 'class':'selectpicker show-tick form-control',
                   'name':'project_manager', 'data-live-search':'true'}))
    except:
        project_manager = forms.CharField(
            label='项目经理', widget=forms.TextInput(
                attrs={'id': 'exampleInputManage', 'class': 'selectpicker show-tick form-control'}))

    # project_group = forms.CharField(label='项目所在组',widget=forms.Select(
    #     choices=group_select,attrs={'class': 'form-control', 'id': 'exampleInputgroup'}))

    project_desc = forms.CharField(label='项目描述',required=False,error_messages={
        'required': '请填写项目描述',
        'max_length': '项目描述太长'
    },widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'exampleInputdesc', 'placeholder': 'Project Description'}))

    # project_status = forms.ChoiceField(label='',widget=forms.RadioSelect(
    #     attrs={'class': 'radio-inline', 'id': 'exampleInputstatus'}), choices=status_select)


class ProjectUserForm(forms.Form):
    '''
        项目成员变更表单
    '''
    project_name = forms.ModelChoiceField(
        label='项目 *',required=False,queryset=project.objects.filter(status=9),empty_label="-- 请选择项目 --",to_field_name="id",error_messages={
        'required': '请选择项目',
    },widget=forms.Select(
            attrs={'id':'project_name', 'class':'selectpicker show-tick form-control',
                   'name':'project_name', 'data-live-search':'true'}))
    try:
        project_user_type = forms.ModelChoiceField(
            label='成员类型 *', required=False, queryset=Group.objects.filter(
                Q(name='产品经理') | Q(name='开发人员') | Q(name='测试人员') | Q(name='运维人员') | Q(name='项目经理')),
            empty_label="-- 请选择成员类型 --",
            to_field_name="id",widget=forms.Select(
            attrs={'id':'project_user_type', 'class':'selectpicker show-tick form-control',
                   'name':'project_user_type', 'data-live-search':'true'}))
    except:
        project_user_type = forms.ModelChoiceField(
            label='成员类型 *',
            queryset=Group.objects.all(),required=False, empty_label="-- 请选择成员类型 --",
            to_field_name="id", widget=forms.Select(
                attrs={'id': 'project_user_type', 'class': 'selectpicker show-tick form-control',
                       'name': 'project_user_type', 'data-live-search': 'true'}))
    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'project_manager',
               'placeholder': 'Project Manager'}))

    # project_user = forms.CharField(label='添加成员', widget=forms.SelectMultiple(
    #     attrs={'class': 'form-control', 'id': 'project_user'}))
    # doublebox = forms.CharField(label='', required=False,widget=forms.Select(
    #     attrs={'class': 'demo', 'multiple': 'multiple', 'size': '10'}))

    project_desc = forms.CharField(label='提交描述',max_length=1000,required=False,error_messages={
        'max_length': '描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputdesc',
                                   'placeholder': 'Project Description'}))


class CronFlowForm(forms.Form):
    '''
        计划任务工作流添加表单
    '''
    env_select = (
        ('开发环境', "开发环境"),
        ('测试环境', "测试环境"),
        ('生产环境', "生产环境"),
    )

    project_name = forms.ModelChoiceField(
        label='项目', required=False, queryset=project.objects.filter(status=9), empty_label="-- 选择项目 --", to_field_name="id",
        widget=forms.Select(
            attrs={'id':'project_name', 'class':'selectpicker show-tick form-control',
                   'name':'project_name', 'data-live-search':'true'}))

    env = forms.ChoiceField(label='环境',widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'id': 'exampleInputenv', 'data-live-search':'true'}), choices=env_select)

    # cron_time = forms.CharField(label=u'添加计划任务：', widget=forms.TextInput(
    #     attrs={'class': 'cron_time', 'id': 'cron_time', 'title':'点击修改时间',
    #            "data-target":"#myModal",'href':"cron_select","data-toggle":"modal"}))

    cron_time = forms.CharField(label=u'计划任务执行时间', max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'cron_time', 'title': '计划任务时间','placeholder': '填写计划任务执行时间'}))

    cron_order = forms.CharField(label=u'计划任务执行命令', max_length=500, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'cron_order','placeholder': '填写计划任务执行命令'}))

    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'id': 'project_manager',
               'placeholder': 'Project Manager','data-live-search':'true'}))

    describe = forms.CharField(label='描述',required=False,error_messages={
        'required': '请填写描述',
        'max_length': '描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputdesc',
                                   'placeholder': 'Project Description'}))


class ReleaseFlowForm(forms.Form):
    '''
        项目变更工作流添加表单
    '''
    priority_select = (
        ('0', "普通"),
        ('1', "紧急"),
    )
    type_select = (
        (0, 'Bug修复'),
        (1, '功能维护'),
        (2, '新功能增加')
    )
    project_name = forms.CharField(label='项目', error_messages={
        'required': '请选择项目'
    }, widget=forms.Select(
        attrs={'id': 'project_name', 'class': 'selectpicker show-tick form-control', 'name': 'project_name'}))

    project_manager = forms.CharField(label=u'项目经理', max_length=50, error_messages={
        'required': '请选择项目经理'
    }, widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'id': 'project_manager',
               'placeholder': 'Project Manager','data-live-search':'true'}))

    # try:
    test_approval = forms.CharField(label='测试审批', widget=forms.TextInput(
        attrs={'class': 'form-control',
               'value':'测试组','readonly':'readonly'}))
    # except:
    #     test_approval = forms.CharField(label='测试审批', widget=forms.TextInput(
    #         attrs={'class': 'form-control', 'readonly': 'readonly'}))

    version_number = forms.CharField(
        label='版本号', required=True, widget=forms.TextInput(attrs={'class': 'form-control','maxlength':50}))

    priority = forms.ChoiceField(
        label='优先级', widget=forms.RadioSelect(attrs={'class': 'flat'}), choices = priority_select)

    type = forms.CharField(label='类型',error_messages={'required':'请选择变更类型！'}, widget=forms.CheckboxSelectMultiple(
        choices=type_select,attrs={'class': 'js-switch'}))

    title = forms.CharField(label='标题', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    describe = forms.CharField(label='发布内容', required=False,error_messages={
        'required': '请填写发布内容',
        'max_length': '信息太长'
    }, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Release Content'}))


class ReleaseTestReportForm(forms.Form):
    '''
        提交测试报告表单
    '''
    releasetestreport = forms.CharField(label='',max_length=2000,required=False,min_length=5,error_messages={
        'required': '请填写测试报告',
        'min_length': '测试审批报告太短',
        'max_length': '测试审批报告太长',
    },widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请填写测试报告','id':'releasetestreport'}))


class ProjectAuthorityForm(forms.Form):
    project_name = forms.ModelChoiceField(
        label='项目', required=False,queryset=project.objects.filter(status=9,have_parent_project=False), empty_label="-- 请选择项目 --", to_field_name="id",
        widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control', 'name': 'project_name',
                   'id':'project_name', 'data-live-search':'true'}))
    department = forms.CharField(label='部门',widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'department','data-live-search':'true'}))
    group = forms.CharField(label='组', widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'group','data-live-search':'true'}))
    user = forms.CharField(label='用户', widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'user','data-live-search':'true'}))
    describe = forms.CharField(label='描述',required=False,error_messages={
        'required': '请填写描述',
        'max_length': '项目描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}))


class ProjectUserApplyForm(forms.Form):
    '''
        项目用户申请表单
    '''
    IS_ACTIVE_CHOICES = (
        (0, u'禁用'),
        (1, u'启用'),
    )
    project_name = forms.ModelChoiceField(
        label='项目',required=False,queryset=project.objects.filter(status=9,have_parent_project=False),empty_label="-- 请选择项目 --",to_field_name="id",
        widget=forms.Select(
            attrs={'id':'project_name', 'class':'selectpicker show-tick form-control',
                   'name':'project_name', 'data-live-search':'true'}))

    department = forms.CharField(label='部门',error_messages={'required':'请选择部门！'},widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'department','data-live-search':'true'}))

    group = forms.CharField(label='组', error_messages={'required':'请选择组！'}, widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'group','data-live-search':'true'}))

    # applicant = forms.CharField(label='申请人', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请填写申请人的名字'}))

    user_name = forms.CharField(label='申请用户名', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请填写需要申请的用户名'}))

    name = forms.CharField(label='申请人姓名', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请填写申请人的姓名'}))

    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}))

    is_active = forms.ChoiceField(
        label='状态', widget=forms.RadioSelect(attrs={'class': 'flat'}), choices = IS_ACTIVE_CHOICES)

    remarks = forms.CharField(label='备注', widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': '如: 通过邮件申请'}), required=False)


class ProjectUserModifyForm(forms.Form):
    '''
        申请修改项目用户表单
    '''
    IS_ACTIVE_CHOICES = (
        (0, u'禁用'),
        (1, u'启用'),
    )

    project_name = forms.ModelChoiceField(
        label='用户所属的项目',required=False,queryset=project.objects.filter(status=9,have_parent_project=False),empty_label="-- 请选择项目 --",to_field_name="id",
        widget=forms.Select(
            attrs={'id':'project_name', 'class':'selectpicker show-tick form-control',
                   'name':'project_name', 'data-live-search':'true'}))

    user_name = forms.CharField(label='用户名', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请填写修改的用户名'}))

    applicant = forms.CharField(label='申请人', widget=forms.TextInput(attrs={'class': 'form-control'}))

    # email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': 'form-control'}))

    department = forms.CharField(label='部门', widget=forms.Select(
        attrs={'class': 'form-control selectpicker show-tick', 'id': 'department','data-live-search':'true'}))

    is_active = forms.ChoiceField(
        label='状态：',widget=forms.RadioSelect(attrs={'class': 'flat'}),choices = IS_ACTIVE_CHOICES)

    remarks = forms.CharField(label='备注', widget=forms.Textarea(attrs={'class': 'form-control'}),required = False)


class RoleAddForm(forms.Form):
    project_name = forms.ModelChoiceField(label='项目', required=False, queryset=project.objects.filter(status=9,have_parent_project=False),
                                          empty_label="-- 请选择项目 --", to_field_name="id", widget=forms.Select(
        attrs={'class': 'selectpicker show-tick form-control', 'name': 'project_name',
               'id':'project_name', 'data-live-search':'true'}))

    role_name = forms.CharField(label='角色名',max_length=100,error_messages={
        'required': '请填写角色名',
        'max_length': '角色名太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputName', 'placeholder': 'Role Name'}))

    doublebox = forms.CharField(label='',required=False,  widget=forms.Select(
        attrs={'class': 'demo', 'multiple': 'multiple', 'size': '10',}))


class RoleModuleModifyForm(forms.Form):
    project = forms.CharField(label='项目', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',"readonly":"readonly"}))

    role_name = forms.CharField(label='角色', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'}))

    doublebox = forms.CharField(label='', widget=forms.Select(
        attrs={'class': 'demo', 'multiple': 'multiple', 'size': '10',}))


class ModuleAddForm(forms.Form):
    project_name = forms.ModelChoiceField(
        label='项目', queryset=project.objects.filter(status=9,have_parent_project=False), empty_label="-- 请选择项目 --", to_field_name="id",
        required=False, widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control', 'name': 'project_name',
                   'id':'project_name', 'data-live-search':'true'}))

    module_name = forms.CharField(label='权限名称',max_length=100,error_messages={
        'required': '请填写权限名',
        'max_length': '权限名太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module Name'}))
    module_url = forms.CharField(label='权限url',max_length=500,error_messages={
        'required': '请填写权限URL',
        'max_length': '权限url太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module URL'}))


class ModuleModifyForm(forms.Form):
    project = forms.CharField(label='项目', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',"readonly":"readonly"}))

    module_name = forms.CharField(label='权限名', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'}))

    module_url = forms.CharField(label='权限url',max_length=500,error_messages={
        'required': '请填写权限URL',
        'max_length': '权限url太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module URL'}))