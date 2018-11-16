from django.contrib import admin
from .models import Supplier,AssetType,Assets
# Register your models here.

'''资产'''
@admin.register(Assets)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('asset_id','asset_type', 'operator', 'operate_time', 'buy_time','supplier','status','remark')
    list_per_page = 20
    ordering = ('-id',)
'''资产'''

'''资产类型'''
@admin.register(AssetType)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 20
    ordering = ('-id',)
'''资产类型'''

'''供应商'''
@admin.register(Supplier)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','contact', 'fixed_telephone', 'mobile_phone', 'address','email','qq','remark')
    list_per_page = 20
    ordering = ('-id',)
'''供应商'''