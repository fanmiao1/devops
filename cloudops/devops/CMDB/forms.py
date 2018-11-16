# -*- coding: utf8 -*-
from django.contrib.auth.models import *
from django import forms
from .models import *
from django.db.models import Q


class FixedAssetsForm(forms.ModelForm):
    '''
    固定资产表单
    '''

    def __init__(self, *args, **kwargs):
        super(FixedAssetsForm, self).__init__(*args, **kwargs)
        null_true_list = ['purchased_date','overdue_insurance_date','applicant_date',
                          'cpu_model_number','memory_model_number','ext_ip',
                          'int_ip','os_version','hostname','disk_number','disk_size',
                          'raid_type','asset_manager','idc','describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = FixedAssets
        fields = '__all__'
        widgets = {
            'asset_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入资产编号(必填)'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'asset_brand': forms.Select(attrs={'class': 'form-control'}),
            'asset_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入型号(必填)'}),
            'asset_serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入设备序列号(必填)'}),
            'purchased_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '购买日期'}),
            'overdue_insurance_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '过保日期'}),
            'applicant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(必填)'}),
            'applicant_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '申请日期'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(必填)'}),

            'cpu_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入cpu型号'}),
            'cpu_kernel_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入核数'}),
            'memory_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内存型号'}),
            'memory_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '单位(G)'}),
            'ext_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'int_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OS版本'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '主机名'}),
            'disk_number':forms.TextInput(attrs={'class': 'form-control', 'placeholder': '磁盘个数'}),
            'disk_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '磁盘容量'}),
            'raid_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'raid类型'}),
            'asset_room_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '机房线路'}),
            'status': forms.RadioSelect(attrs={'class': 'flat'}),
            'asset_manager': forms.TextInput(attrs={'class': 'form-control'}),
            'idc': forms.TextInput(attrs={'class': 'form-control'}),
            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }


class NetworkDeviceForm(forms.ModelForm):
    '''
    网络设备表单
    '''

    def __init__(self, *args, **kwargs):
        super(NetworkDeviceForm, self).__init__(*args, **kwargs)
        null_true_list = ['purchased_date','applicant_date','port_num','port_type','memory','flash_memory','backplane_bandwidth',
                          'Packet_forwarding_rate','asset_manager','idc','describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = NetworkDevice
        fields = '__all__'
        widgets = {
            'asset_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入资产编号(必填)'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'asset_brand': forms.Select(attrs={'class': 'form-control'}),
            'asset_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入型号(必填)'}),
            'asset_serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入设备序列号(必填)'}),
            'purchased_date': forms.TextInput(attrs={'class': 'form-control input-group date', 'placeholder': '购买日期'}),
            'overdue_insurance_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '过保日期(必填)'}),
            'applicant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '申请人(必填)'}),
            'applicant_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '申请日期'}),

            'port_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入型号'}),
            'port_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入核数'}),
            'memory': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入型号'}),
            'flash_memory': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '单位(G)'}),
            'backplane_bandwidth': forms.TextInput(attrs={'class': 'form-control'}),
            'Packet_forwarding_rate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '包转发率'}),
            'manager_ip': forms.TextInput(attrs={'class': 'form-control'}),

            'status': forms.RadioSelect(attrs={'class': 'flat'}),
            'asset_manager': forms.TextInput(attrs={'class': 'form-control'}),
            'idc': forms.TextInput(attrs={'class': 'form-control'}),
            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }


class DomainForm(forms.ModelForm):
    '''
    域名表单
    '''

    def __init__(self, *args, **kwargs):
        super(DomainForm, self).__init__(*args, **kwargs)
        null_true_list = ['domain',
                          'platform_password',
                          'register_date',
                          'purchaser',
                          'contact_people',
                          'project_group',
                          'owner',
                          'manager_telephone',
                          'describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = Domain
        fields = '__all__'
        widgets = {
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入域名(必填)'}),
            'register_platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入注册平台(必填)'}),
            'platform_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入注册平台账号(必填)'}),
            'platform_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入注册平台密码'}),
            'register_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入注册日期'}),
            'purchaser': forms.TextInput(attrs={'class': 'form-control input-group date', 'placeholder': '请输入购买人'}),
            'contact_people': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入业务联系人'}),
            'project_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目组'}),

            'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入持有者'}),
            'bind_email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定的邮箱(必填)'}),
            'expire_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入到期日期(必填)'}),
            'manager_telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入联系人手机号码'}),
            'auto_renew': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.RadioSelect(attrs={'class': 'flat'}),

            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }


class PrivateCloudForm(forms.ModelForm):
    '''
    私有云表单
    '''

    def __init__(self, *args, **kwargs):
        super(PrivateCloudForm, self).__init__(*args, **kwargs)
        null_true_list = ['cloud_type',
                          'host_account',
                          'host_password',
                          'create_date',
                          'physical_host_ip',
                          'physical_host_account',
                          'physical_host_password',
                          'project_group',
                          'ext_ip',
                          'os',
                          'hostname',
                          'disk_size',
                          'bandwidth',
                          'describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = PrivateCloudServer
        fields = '__all__'
        widgets = {
            'instance_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入实例名(必填)'}),
            'cloud_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入云类型'}),
            'host_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机账号'}),
            'host_password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机密码'}),
            'create_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入创建时间'}),
            'physical_host_ip': forms.TextInput(attrs={'class': 'form-control input-group date', 'placeholder': '请输入宿主机IP'}),
            'physical_host_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入宿主机账号'}),
            'physical_host_password': forms.TextInput(attrs={'class': 'form-control input-group date', 'placeholder': '请输入宿主机密码'}),
            'contact_people': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入对接人(必填)'}),
            'project_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入项目组'}),

            'cpu_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入CPU核数(必填)'}),
            'memory_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内存(G)(必填)'}),
            'ext_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入公网IP'}),
            'int_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内网IP(必填)'}),
            'os': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入操作系统'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机名'}),
            'disk_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入磁盘空间'}),
            'bandwidth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入带宽'}),

            'status': forms.RadioSelect(attrs={'class': 'flat'}),
            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }


class PublicCloudForm(forms.ModelForm):
    '''
    公有云表单
    '''

    def __init__(self, *args, **kwargs):
        super(PublicCloudForm, self).__init__(*args, **kwargs)
        null_true_list = ['platform',
                          'platform_password',
                          'host_account',
                          'host_password',
                          'create_date',
                          'project_group',
                          'area',
                          'int_ip',
                          'os',
                          'hostname',
                          'disk_size',
                          'bandwidth',
                          'describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = PublicCouldServer
        fields = '__all__'
        widgets = {
            'instance_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入实例名(必填)'}),
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入所在平台'}),
            'platform_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入平台账号(必填)'}),
            'platform_password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入平台密码'}),
            'host_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机账号'}),
            'host_password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机密码'}),
            'create_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入创建时间'}),
            'expire_date': forms.TextInput(attrs={'class': 'form-control input-group date', 'placeholder': '请输入到期时间(必填)'}),
            'applicant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入申请人(必填)'}),
            'project_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入项目组'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入所在区域'}),
            'contact_people': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入对接人(必填)'}),

            'cpu_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入CPU核数(必填)'}),
            'memory_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内存(G)(必填)'}),
            'ext_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入公网IP(必填)'}),
            'int_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内网IP'}),
            'os': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入操作系统'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入主机名'}),
            'disk_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入磁盘空间'}),
            'bandwidth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入带宽'}),

            'status': forms.RadioSelect(attrs={'class': 'flat'}),
            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }

class IdcForm(forms.ModelForm):
    '''
    idc表单
    '''

    def __init__(self, *args, **kwargs):
        super(IdcForm, self).__init__(*args, **kwargs)
        null_true_list = ['asset_brand',
                          'asset_model_number',
                          'use_date',
                          'project_group',
                          'cpu_model_number',
                          'cpu_kernel_num',
                          'memory_model_number',
                          'memory_size',
                          'ext_ip',
                          'int_ip',
                          'os_version',
                          'hostname',
                          'disk_number',
                          'disk_size',
                          'raid_type',
                          'server_room_temper',
                          'server_room_humidity',
                          'power_system',
                          'bandwidth',
                          'describe']
        for field_name in null_true_list:
            self.fields[field_name].required = False

    class Meta:
        model = Idc
        fields = '__all__'
        widgets = {
            'idc_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入idc位置(必填)'}),
            'rack_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入机房编号(必填)'}),
            'rack_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入机架号(必填)'}),
            'device_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入设备信息(必填)'}),
            'asset_brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入品牌'}),
            'asset_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入型号'}),
            'use_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '上架日期'}),
            'responsible': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入责任人(必填)'}),
            'project_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入项目组'}),

            'cpu_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入cpu型号'}),
            'cpu_kernel_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入核数'}),
            'memory_model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入内存型号'}),
            'memory_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '单位(G)'}),
            'ext_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'int_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OS版本'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '主机名'}),
            'disk_number':forms.TextInput(attrs={'class': 'form-control', 'placeholder': '磁盘个数'}),
            'disk_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '磁盘容量'}),
            'raid_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'raid类型'}),

            'status': forms.RadioSelect(attrs={'class': 'flat'}),
            'server_room_temper': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '机房温度'}),
            'server_room_humidity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '机房湿度'}),
            'power_system': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '电力系统'}),
            'bandwidth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '出口带宽'}),
            'describe': forms.Textarea(attrs={'class': 'form-control'})
        }