from django.contrib import admin
from .models import project, project_group
# Register your models here.
@admin.register(project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'project_manager', 'source', 'applicationtime', 'approvaltime','status')
    list_per_page = 20
    ordering = ('-id',)

@admin.register(project_group)
class ProjectGroupAdmin(admin.ModelAdmin):
    search_fields = ('user__email',)
    list_display = ('project', 'user', 'user_type')
    list_filter = ('project', 'user_type')  # 过滤器
    list_per_page = 20
    ordering = ('-id',)