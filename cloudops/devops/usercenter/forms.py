from django import forms
from workflow.models import authority_group,project,project_user

class UserForm(forms.Form):
    '''
        用户登录表单
    '''
    username = forms.CharField(label='',max_length=100,widget=forms.TextInput(
        attrs={'id': 'username', 'class':'form-control text-sm', 'placeholder': 'User'}))
    password = forms.CharField(label='',widget=forms.PasswordInput(
        attrs={'id': 'password', 'class':'form-control text-sm', 'placeholder': 'Password'}))

class AuthorityGroupForm(forms.ModelForm):
    '''
    项目用户组增加/修改表单
    '''

    def __init__(self, *args, **kwargs):
        super(AuthorityGroupForm, self).__init__(*args, **kwargs)
        self.fields['project'].required =False
        self.fields['project'].queryset = project.objects.filter(status=9,have_parent_project=False)
        self.fields['project'].empty_label = "-- 请选择项目 --"
        self.fields['project'].to_field_name ="id"
    class Meta:
        model = authority_group
        fields = '__all__'
        widgets = {
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入组名称(必填)'}),
            'project': forms.Select(attrs={'class': 'selectpicker show-tick form-control',
                                           'id':'project_id', 'data-live-search':'true'}),
        }

class UserChangeForm(forms.ModelForm):
    '''
    项目用户增加/修改表单
    '''

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['email'].required = False
        self.fields['project'].required =False
        self.fields['project'].queryset = project.objects.filter(status=9,have_parent_project=False)
        self.fields['project'].empty_label = "-- 请选择项目 --"
        self.fields['project'].to_field_name ="id"

    class Meta:
        model = project_user
        fields = '__all__'
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名(必填)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'project': forms.Select(attrs={'class': 'selectpicker show-tick form-control', 'data-live-search':'true'}),
            'is_active': forms.RadioSelect(attrs={'class': 'flat'}),
        }