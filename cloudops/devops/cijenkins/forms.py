from django import forms

class RollBackVersionForm(forms.Form):
    deploy_env = forms.CharField(label='回滚', widget=forms.TextInput(
        attrs={'class': 'form-control', 'value': 'rollback', 'readonly': 'readonly'}))
    version = forms.IntegerField(label='回滚版本号', error_messages={'required': '请填写回滚版本号'}, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'version', 'placeholder': 'Version Number'}))

class ReconfigJobForm(forms.Form):
    repository_url = forms.CharField(label='Repository URL',widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}
    ))
    new_repository_url = forms.URLField(label='New Repository URL',error_messages={'required': '请填写SVN地址'},widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'New Repository URL'}
    ))