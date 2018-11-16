from django import forms
from django.contrib.auth.models import User
from .models import WorkSheetType

class WorkSheetForm(forms.Form):
    title = forms.CharField(
        label="标题", max_length=40,widget=forms.TextInput(
            attrs={'class': 'ivu-input',
                   'placeholder': u'请填写标题','oninput':'if(value.length>40)value=value.slice(0,40)'}))

    have_power_change = forms.CharField(
        label='是否需要抄送邮箱',required=False,error_messages={'required':''}, widget=forms.CheckboxInput(
            attrs={'class': 'js-switch'}))

    email = forms.CharField(
        label="抄送邮箱",required=False,widget=forms.TextInput(
            attrs={'class': 'ivu-input','placeholder': u'如有多个, 请用英文分号 ";" 分隔 !'}))

    file = forms.CharField(
        label="附件", required=False,widget=forms.TextInput(
            attrs={'class': 'form-control','style': 'display:none'}
        )
    )

    description_desc = forms.CharField(
        label="描述", required=False, widget=forms.Textarea(
            attrs={'class': 'form-control', 'id':'id_description', 'placeholder': u'请填写描述','style': 'display:none'}))


class AppointForm(forms.Form):
    user = forms.ModelChoiceField(
        label='指派给',required=False,queryset=User.objects.all(),empty_label="-- 选择指派的用户 --",to_field_name="id",
        widget=forms.Select(
            attrs={'id':'appoint_user', 'class':'selectpicker show-tick form-control',
                   'name':'appoint_user', 'data-live-search':'true'}))

    remark = forms.CharField(
        label="备注", required=False, widget=forms.Textarea(
            attrs={'class': 'form-control','placeholder': u'备注(选填)','rows':'5','cols':'20'}))


class WorksheetClassifyForm(forms.Form):
    type = forms.ModelChoiceField(
        label='归类', required=False, queryset=WorkSheetType.objects.all(), empty_label="-- 选择类型 --", to_field_name="id",
        widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control',
                   'name': 'classify', 'data-live-search': 'true'}))
    type2 = forms.ModelChoiceField(
        label='归类', required=False, queryset=WorkSheetType.objects.all(), empty_label="-- 选择类型 --", to_field_name="id",
        widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control',
                   'name': 'classify2', 'data-live-search': 'true'}))
    type3 = forms.ModelChoiceField(
        label='归类', required=False, queryset=WorkSheetType.objects.all(), empty_label="-- 选择类型 --", to_field_name="id",
        widget=forms.Select(
            attrs={'class': 'selectpicker show-tick form-control',
                   'name': 'classify3', 'data-live-search': 'true'}))