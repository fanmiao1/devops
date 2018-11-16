# Register your models here.
from django.contrib import admin
from .models import Permission,UserProfile,SystemModule,Org
from workflow.models import Department,project
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms import models,forms

'''
[修改用户输出显示]
在auth/models.py文件下User类下面添加：
def __str__(self):
    return self.last_name + self.first_name + '<' + self.username + '>'
'''

"""用户模块扩展"""
class ProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
"""用户模块扩展"""

'''修改Django后台标题和头部'''
admin.site.site_header = 'AUKEY 运维'
admin.site.site_title = 'AUKEY 运维'


'''修改部门表单样式'''
class DepartmentAdminForm(models.ModelForm):
    forms.model = Department

    def __init__(self, *args, **kwargs):
        super(DepartmentAdminForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = project.objects.filter(status=9)
        self.fields['project'].empty_label = "-- 请选择项目 --"
        self.fields['project'].to_field_name = "id"

    class Meta:
        model = Department
        fields = "__all__"


class DepartmentAdmin(admin.ModelAdmin):
    # filter_vertical = ('depart_director',)
    list_filter = ('depart_name', 'project')  # 过滤器
    form = DepartmentAdminForm
    list_display = ['depart_name', 'project', 'depart_director']


admin.site.register(Department,DepartmentAdmin)
'''修改部门表单样式'''

'''平台菜单模块'''
@admin.register(SystemModule)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_url')
    list_per_page = 20
    ordering = ('-id',)
'''平台菜单模块'''

'''平台权限'''
@admin.register(Permission)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('describe','name', 'url', 'per_method', 'argument_list')
    list_per_page = 20
    ordering = ('-id',)
'''平台权限'''

'''平台权限'''
@admin.register(Org)
class OrgAdmin(admin.ModelAdmin):
    list_display = ('name', 'oid')
    list_per_page = 20
    ordering = ('-id',)
'''平台权限'''
