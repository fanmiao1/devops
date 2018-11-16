# -*- coding: utf8 -*-
from django.contrib.auth.models import *
from django import forms
from django.db.models import Q

class CronRevisionForm(forms.Form):
    '''
        计划任务修改表单
    '''
    env_select = (
        ('测试环境', u"测试环境"),
        ('开发环境', u"开发环境"),
        ('生产环境', u"生产环境"),
    )
    status_select = (
        ('running', u"启用"),
        ('disable', u"禁用"),
        ('delete', u"删除"),
    )
    cron_time = forms.CharField(label=u'运行时间', initial='class', widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    cron_order = forms.CharField(label=u'命令', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '命令'}))

    describe = forms.CharField(label='描述',max_length=1000,error_messages={
        'required': '请填写描述',
        'max_length': '描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Description'}))

    project_name = forms.CharField(label=u'项目', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '项目', 'readonly': 'readonly'}))


    env = forms.CharField(label=u'环境', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '环境', 'readonly': 'readonly'}))

    status = forms.ChoiceField(label='状态',widget=forms.Select(
        attrs={'class': 'form-control'}), choices=status_select)

class ScriptForm(forms.Form):
    '''
        项目增加表单
    '''
    group_select = [
        ('shell', 'shell'),('python','python'),('linuxyml','linuxyml'),('winyml','winyml'),('winps1','winps1'),
    ]
    # status_select = (
    #     ('新建', "新建"),
    #     ('运作中', "运作中"),
    #     ('完成', "完成"),
    # )
    script_name = forms.CharField(label='脚本名称',max_length=20,error_messages={
        'required': '请填写脚本名称',
        'max_length': '脚本名称太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputName', 'placeholder': 'Script_Name'}))

    script_desc = forms.CharField(label='脚本描述', max_length=1000, error_messages={
        'required': '请填写脚本描述',
        'max_length': '脚本描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Script_Desc'}))

    script_group = forms.CharField(label='脚本分类',
    widget=forms.Select(choices=group_select,attrs={'class': 'form-control', 'id': 'exampleInputGroup'}))

    script_content = forms.CharField(label='脚本内容', max_length=5000, error_messages={
        'required': '请填写脚本内容',
        'max_length': '脚本内容太长'
    }, widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputContent', 'placeholder': 'Script_content'}))

    script_user = forms.CharField(label='添加人', max_length=20, error_messages={
        'required': '请填写添加人',
        'max_length': '天加人太长'
    }, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputUser', 'placeholder': 'Script_User'}))

class Script_exec_Form(forms.Form):

    host_select = [
        ('10.1.2.166','10.1.2.166'),('10.1.2.167', '10.1.2.167'),('10.1.2.168','10.1.2.168'),('10.1.2.169','10.1.2.169')
    ]

    user_select = [
        (1, 'ubuntu'),(2,'root')
    ]

    script_name = forms.CharField(label='脚本名称',max_length=20,error_messages={
        'required': '请填写脚本名称',
        'max_length': '脚本名称太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputName', 'placeholder': 'Script_Name'}))

    script_desc = forms.CharField(label='脚本描述',max_length=1000,error_messages={
        'required': '请填写脚本描述',
        'max_length': '脚本描述太长'
    },widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputdesc', 'placeholder': 'Script_Desc'}))

    script_content = forms.CharField(label='脚本内容', max_length=5000, error_messages={
        'required': '请填写脚本内容',
        'max_length': '脚本内容太长'
    }, widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputContent', 'placeholder': 'Script_content'}))

    script_exec_host = forms.CharField(label='执行主机',
    widget = forms.Select(choices=host_select, attrs={'class': 'form-control', 'id': 'exampleInputGroup'}))

    script_exec_user = forms.CharField(label='执行用户',
    widget = forms.Select(choices=user_select, attrs={'class': 'form-control', 'id': 'exampleInputGroup'}))


class Script_exec_log_Form(forms.Form):


    script_name = forms.CharField(label='脚本名称',max_length=20,error_messages={
        'required': '请填写脚本名称',
        'max_length': '脚本名称太长'
    },widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputName', 'placeholder': 'Script_Name'}))

    script_result = forms.CharField(label='执行结果', max_length=5000, error_messages={
        'required': '请填写执行结果',
        'max_length': '执行结果太长'
    }, widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'exampleInputContent', 'placeholder': 'Script_result'}))

    script_exec_datetime = forms.CharField(label='执行主机',
    widget = forms.DateTimeField())

    script_exec_user = forms.CharField(label='执行用户',
    widget = forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputGroup'}))