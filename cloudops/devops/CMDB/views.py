import datetime
import re
import json
import time
import sys
import os
import xlrd

from django.db.models import Q
from django.contrib.auth.models import ContentType
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.core.paginator import Paginator
from django.utils.timezone import utc, timedelta
from django.views.generic import TemplateView, DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from devops.settings import MEDIA_ROOT

from database.models import Instance
from usercenter.permission import check_permission
from workflow.get_name_by_id import get_name_by_id
from workflow.views import DateEncoder
from usercenter.getAllUser import get_all_user as getAllUser
from worksheet.wechatApi import GetDepartUserList
from usercenter.models import Org
from lib.revision_log import change
from lib.pagination import MyPageNumberPagination
from .serializers import *
from usercenter.permission import check_object_perm
from .filter import *
from .models import *

## 自定义异常
class TaskError(Exception):
    pass

## 固定资产
@login_required
@check_permission
def fixed_asset_list(request):
    '''
    @author: 谢育政
    @note: 固定资产列表
    :param id: Assets表的id
    :return: Assets表的JSON格式数据
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        user_name = request.POST.get('user_name', '').strip()
        lend_time_input_name = request.POST.get('lend_time_input_name', '')
        buydata_search_input_name = request.POST.get('buydata_search_input_name', '')
        org_search_input_name = request.POST.get('org_search_input_name', '').strip()
        search_asset_id = request.POST.get('asset_id_input', '')
        all_records = Assets.objects.all()
        if sort_column:
            if sort_column in ['asset_id', 'asset_type','operator','operate_time','buy_time',
                               'supplier','use_person','use_time','status','remark']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
                    sort_column = '%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
        if search_asset_id:
            my_q = Q()
            for i in search_asset_id.split(','):
                my_q.add(Q(asset_id__icontains=i), Q.OR)
            all_records = all_records.filter(my_q)
        if request.POST.get('supplier_input'):
            my_q = Q()
            for i in request.POST.get('supplier_input').split(','):
                my_q.add(Q(supplier_id=int(i)), Q.OR)
            all_records = all_records.filter(my_q)

        if request.POST.get('type_input'):
            my_q = Q()
            for i in request.POST.get('type_input').split(','):
                my_q.add(Q(asset_type_id=int(i)), Q.OR)
            all_records = all_records.filter(my_q)

        if request.POST.get('status_input'):
            my_q = Q()
            for i in request.POST.get('status_input').split(','):
                my_q.add(Q(status=int(i)), Q.OR)
            all_records = all_records.filter(my_q)

        if request.POST.get('operator_input'):
            all_records = all_records.filter(operator__id=request.POST.get('operator_input'))

        if request.POST.get('asset_info_search_input'):
            for i in request.POST.get('asset_info_search_input').split('&'):
                all_records = all_records.filter(asset_info__icontains=i.strip())

        if buydata_search_input_name:
            if len(buydata_search_input_name.split('~')) == 2:
                start_buy_date, end_buy_date = buydata_search_input_name.split('~')
                startbuydate = datetime.datetime.strptime(start_buy_date.strip().replace('-', ','), '%Y,%m,%d')
                endbuydate = datetime.datetime.strptime(end_buy_date.strip().replace('-', ','), '%Y,%m,%d') + \
                              datetime.timedelta(days=1)
                all_records = all_records.filter(buy_time__range=(startbuydate, endbuydate))
            else:
                pass
        if user_name:
            all_records = all_records.filter(use_person__icontains=user_name)
        if len(lend_time_input_name.split('~')) == 2:
            start_lend_time, end_lend_time = lend_time_input_name.split('~')
            startlenddate = datetime.datetime.strptime(start_lend_time.strip().replace('-', ','), '%Y,%m,%d')
            endlenddate = datetime.datetime.strptime(end_lend_time.strip().replace('-', ','), '%Y,%m,%d') + \
                          datetime.timedelta(days=1)
            all_records = all_records.filter(use_time__range=(startlenddate, endlenddate))
        depart_user_list = []
        if org_search_input_name:
            try:
                org_obj = eval(Org.objects.only('org_data').get(oid=1).org_data)
                org_name_have = 0
                org_id = -1
                for i in org_obj:
                    if i['name'] == org_search_input_name:
                        org_id = int(i['id'])
                        org_name_have = 1
                        break
                    else:
                        continue
                if org_name_have == 1:
                    if org_id > 0:
                        user_li = GetDepartUserList(org_id, 1).userList()
                        for i in user_li:
                            depart_user_list.append(i['name'])
            except:
                pass
            all_records = all_records.filter(use_person__in=depart_user_list)
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        if not pageNumber:
            pageNumber = page
        try:
            pageinator.page(pageNumber)
        except:
            pageNumber = 1
        for list in pageinator.page(pageNumber):
            try:
                sn = eval(list.asset_info)['SN']
            except Exception as _:
                sn = ''
            response_data['rows'].append({
                "asset_id": list.asset_id if list.asset_id else "",
                "sn": sn if sn else "",
                "asset_type": list.asset_type.name if list.asset_type else "",
                "operator":  get_name_by_id.get_name(list.operator_id) if list.operator_id else "",
                "operate_time": list.operate_time if list.operate_time else "",
                "buy_time": list.buy_time if list.buy_time else "",
                "supplier": list.supplier.name if list.supplier else "",
                "use_person": list.use_person if list.use_person else "",
                "use_time": list.use_time.replace(tzinfo=utc).astimezone(
                    datetime.timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S") if list.use_time else "",
                "status": list.get_status_display() if list.status else "",
                "remark": list.remark[0:15]+("..." if len(list.remark) > 15 else "") if list.remark else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'cmdb/fixed_asset_list.html')

@login_required
@check_permission
def asset_type_list(request):
    '''
    @author: 谢育政
    @note: 资产类型列表
    :param id: AssetType表的id
    :return: AssetType表的JSON格式数据
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')
        all_records = AssetType.objects.all().order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        if not pageNumber:
            pageNumber = page
        for list in pageinator.page(pageNumber):
            response_data['rows'].append({
                "type_id": list.id if list.id else "",
                "name": list.name if list.name else "",
                "customize_asset_field": list.customize_asset_field if list.customize_asset_field else "",
            })
        return HttpResponse(json.dumps(response_data))
    return render(request, 'cmdb/fixed_asset_list.html')

@login_required
@check_permission
def supplier_manage_list(request):
    '''
    @author: 谢育政
    @note: 供应商列表
    :param id: Supplier表的ID
    :return: Supplier表的JSON格式数据
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')
        all_records = Supplier.objects.all().order_by('-id')
        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_records_count
        if not pageSize:
            pageSize = 10  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        if not pageNumber:
            pageNumber = page
        for list in pageinator.page(pageNumber):
            response_data['rows'].append({
                "supplier_id": list.id if list.id else "",
                "name": list.name if list.name else "",
                "contact": list.contact if list.contact else "",
                "fixed_telephone": list.fixed_telephone if list.fixed_telephone else "",
                "mobile_phone": list.mobile_phone if list.mobile_phone else "",
                "address": list.address if list.address else "",
                "email": list.email if list.email else "",
                "qq": list.qq if list.qq else "",
                "remark": list.remark[0:15]+("..." if len(list.remark) > 15 else "") if list.remark else "",
            })
        return HttpResponse(json.dumps(response_data))
    return render(request, 'cmdb/fixed_asset_list.html')

@login_required
@check_permission
def add_asset(request):
    """编辑资产"""
    if request.method == 'POST':
        hidden_add_asset_id_input = request.POST.get('hidden_add_asset_id_input','')
        add_asset_id = request.POST.get('add_asset_name','').strip()
        add_asset_type = request.POST.get('add_asset_type','')
        add_status = request.POST.get('add_status_name','')
        add_supplier = request.POST.get('add_supplier_name','')
        add_buydate = request.POST.get('add_buydate_name','').strip()
        add_remark = request.POST.get('add_remark_name','').strip()
        fixed_field_list = ['add_asset_name', 'add_asset_type', 'add_status_name',
                            'add_supplier_name', 'add_buydate_name', 'add_remark_name','hidden_add_asset_id_input']
        add_asset_info = {}
        for i in request.POST:
            if i in fixed_field_list:
                continue
            else:
                add_asset_info[i] = request.POST.get(i,'')
        try:
            try:
                change_asset_obj = Assets.objects.get(asset_id = add_asset_id)
            except:
                content = '资产入库'
                change_asset_obj = Assets()
                change_asset_obj.asset_id = add_asset_id
                change_asset_obj.asset_type_id = int(add_asset_type)
                change_asset_obj.status = int(add_status)
                change_asset_obj.supplier_id = int(add_supplier) if add_supplier else None
                change_asset_obj.buy_time = add_buydate if add_buydate else None
                change_asset_obj.remark = add_remark if add_remark else None
                change_asset_obj.asset_info = add_asset_info if add_asset_info else None
            else:
                if not hidden_add_asset_id_input:
                    return JsonResponse({'code': 0, 'result': '资产编号已存在！'})
                else:
                    content = '资产修改：{old_info} 修改为 {new_info}'
                    old_info = {}
                    new_info = {}
                    status_dict = {'1': '在库', '2': '借出', '3': '维修', '4': '报废'}

                    if not change_asset_obj.asset_type_id:
                        old_asset_type = ''
                    else:
                        old_asset_type = change_asset_obj.asset_type_id
                    if str(old_asset_type) != add_asset_type:
                        old_info['资产类型'] = change_asset_obj.asset_type.name
                        new_info['资产类型'] = AssetType.objects.only('name').get(id=add_asset_type).name

                    if not change_asset_obj.status:
                        old_status = ''
                    else:
                        old_status = change_asset_obj.status
                    if str(old_status) != add_status:
                        old_info['资产状态'] = change_asset_obj.get_status_display()
                        new_info['资产状态'] = status_dict[str(add_status)]

                    if not change_asset_obj.supplier_id:
                        old_supplier = ''
                    else:
                        old_supplier = change_asset_obj.supplier_id
                    if str(old_supplier) != add_supplier:
                        old_info['供应商'] = change_asset_obj.supplier.name
                        new_info['供应商'] = Supplier.objects.only('name').get(id=add_supplier).name

                    if not change_asset_obj.buy_time:
                        old_buy_time = ''
                    else:
                        old_buy_time = change_asset_obj.buy_time.strftime('%Y-%m-%d')
                    if str(old_buy_time) != add_buydate:
                        old_info['采购日期'] = old_buy_time
                        new_info['采购日期'] = add_buydate

                    if not change_asset_obj.remark:
                        old_remark = ''
                    else:
                        old_remark = change_asset_obj.remark
                    if str(old_remark) != add_remark:
                        old_info['备注'] = old_remark
                        new_info['备注'] = add_remark

                    new_info_key_list = []
                    if add_asset_info:
                        for i in add_asset_info:
                            new_info_key_list.append(i)
                            try:
                                old_asset_i = eval(change_asset_obj.asset_info)[i]
                            except:
                                old_asset_i = ''
                            if add_asset_info[i] != old_asset_i:
                                old_info[i] = old_asset_i
                                new_info[i] = add_asset_info[i]
                    try:
                        for i in eval(change_asset_obj.asset_info):
                            if i not in new_info_key_list and eval(change_asset_obj.asset_info)[i]:
                                old_info[i] = eval(change_asset_obj.asset_info)[i]
                                new_info[i] = ''
                    except:
                        pass

                    if old_info and new_info:
                        content = content.format(old_info=old_info,new_info=new_info)
                    else:
                        code = 0
                        result = '没有作任何修改！'
                        return JsonResponse({'code': code, 'result': result})
                    change_asset_obj.asset_type_id = int(add_asset_type)
                    change_asset_obj.status = int(add_status)
                    change_asset_obj.supplier_id = int(add_supplier) if add_supplier else None
                    change_asset_obj.buy_time = add_buydate if add_buydate else None
                    change_asset_obj.remark = add_remark if add_remark else None
                    change_asset_obj.asset_info = add_asset_info if add_asset_info else None
            try:
                change_asset_obj.operator = request.user
                change_asset_obj.operate_time = datetime.datetime.now()
            except Exception as _:
                code = 0
                result = '登录已过期，请重新登录！'
                return JsonResponse({'code': code, 'result': result})
        except Exception as _:
            code = 0
            result = '操作失败，请检查输入框！'
            return JsonResponse({'code': code, 'result': result})
        else:
            change_asset_obj.save()
            try:
                if not hidden_add_asset_id_input:
                    # 资产流动记录保存
                    asset_flow_save(change_asset_obj.id, 1, request.user.id)
                # 日志保存
                asset_log_save(change_asset_obj.id, content, request.user.id)
            except Exception as _:
                pass
            code = 1
            result = '操作成功！'
            return JsonResponse({'code': code, 'result': result})


@login_required
@check_permission
def asset_import(request):
    """
    资产导入
    导入格式（必须按顺序写入到xls文件，第一行的标题如下）：
        资产编号、资产类型、资产状态、采购日期、供应商、使用人、领用时间、备注、其他（其他信息写在后面）
        【资产状态只能有4种：“在库”、“借出”、“维修”、“报废”。 不是这4种状态默认转换为“在库”】
    """
    file_obj = request.FILES.get('file')
    status_dict = {'在库': 1, '借出': 2, '维修': 3, '报废': 4}
    file_type_list = ['xls', 'xlsx']
    error_list = []
    # 判断文件的类型
    if ((file_obj.name)[::-1].split('.')[0])[::-1] not in file_type_list:
        return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '上传失败，请上传 .xls 或 .xlsx 类型的文件！'})
    else:
        # accessory_dir = os.path.join('e:/tmp_cmdb_import')
        accessory_dir = os.path.join(MEDIA_ROOT, 'tmp_cmdb_import')
        if not os.path.isdir(accessory_dir):
            os.mkdir(accessory_dir)
        upload_file = "%s/%s" % (accessory_dir, 'cmdb_import.'+((file_obj.name)[::-1].split('.')[0])[::-1])
        recv_size = 0
        with open(upload_file, 'wb') as new_file:
            for chunk in file_obj.chunks():
                new_file.write(chunk)
    workbook = xlrd.open_workbook(upload_file)
    book_sheet = workbook.sheet_by_index(0)
    n_rows = book_sheet.nrows
    row_number = len(book_sheet.row_values(0))
    if row_number < 6:
        return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '导入失败，表格格式错误！'})
    else:
        j_dict = {0: '资产编号', 1: '资产类型', 2: '资产状态', 3: '采购日期', 4: '供应商', 5: '使用人', 6:'领用时间', 7: '备注'}
        for i in range(len(j_dict)):
            if book_sheet.row_values(0)[i] != j_dict[i]:
                return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '第'+str(i+1)+'列的第一行标题有误！'})
    all_type = {}
    type_name = []
    type_obj = AssetType.objects.all()
    for i in type_obj:
        all_type[i.name] = i.id
        type_name.append(i.name)
    all_supplier = {}
    supplier_name = []
    supplier_obj = Supplier.objects.all()
    for i in supplier_obj:
        all_supplier[i.name] = i.id
        supplier_name.append(i.name)
    count = 0
    v = 0
    while v < n_rows:
        v += 1
        try:
            row_data = book_sheet.row_values(v)
            add_asset_obj = Assets()
            try:
                add_asset_obj.asset_id = row_data[0].strip()
            except Exception as _:
                add_asset_obj.asset_id = row_data[0]
            try:
                row_data_1 = row_data[1].strip()
            except Exception as _:
                row_data_1 = row_data[1]
            if row_data_1:
                if row_data_1 not in type_name:
                    add_type = AssetType.objects.create(name=row_data_1)
                    type_name.append(add_type.name)
                    all_type[add_type.name] = add_type.id
                add_asset_obj.asset_type_id = all_type[row_data_1]
            try:
                status = status_dict[row_data[2].strip()]
            except KeyError:
                status = 1
            add_asset_obj.status = status
            if str(row_data[3]) and row_data[3] != 'NULL':
                date = xlrd.xldate_as_tuple(row_data[3], 0)
                add_asset_obj.buy_time = datetime.datetime(*date)
            try:
                row_data_4 = row_data[4].strip()
            except Exception as _:
                row_data_4 = row_data[4]
            if row_data_4:
                if row_data_4 not in supplier_name:
                    add_supplier = Supplier.objects.create(name=row_data_4)
                    supplier_name.append(add_supplier.name)
                    all_supplier[add_supplier.name] = add_supplier.id
                add_asset_obj.supplier_id = all_supplier[row_data_4]

            if str(row_data[5]).strip() and row_data[5] != 'NULL':
                try:
                    add_asset_obj.use_person = row_data[5].strip()
                except Exception as _:
                    add_asset_obj.use_person = row_data[5]

            if str(row_data[6]) and row_data[6] != 'NULL':
                date = xlrd.xldate_as_tuple(row_data[6], 0)
                add_asset_obj.use_time = datetime.datetime(*date)

            if row_data[7].strip():
                try:
                    add_asset_obj.remark = row_data[7].strip()
                except Exception as _:
                    add_asset_obj.remark = row_data[7]
            if row_number > len(j_dict):
                asset_info_dict = {}
                for i in range(len(j_dict),row_number):
                    try:
                        the_data = row_data[i].strip()
                    except Exception as _:
                        the_data = row_data[i]
                    if the_data == 'NULL':
                        the_data = ''
                    asset_info_dict[book_sheet.row_values(0)[i]] = the_data
                add_asset_obj.asset_info = asset_info_dict
            add_asset_obj.operator = request.user
            try:
                add_asset_obj.save()
            except:
                continue
            else:
                count += 1
        except Exception as _:
            continue
    if os.path.exists(upload_file):
        try:
            os.remove(upload_file)
        except:
            pass
    return JsonResponse({'title': 'SUCCESS', 'result': '导入成功！', 'status': 'success'})

@login_required
@check_permission
def asset_flow_import(request):
    """
    资产出入记录导入
    导入格式（必须按顺序写入到xls文件，第一行的标题如下）：
        经手人、资产编号、类型、操作人、操作时间、备注
        【类型只能有5种：“入库”、“借出”、“还回”、“维修”、“报废”。 不是这5种状态默认转换为“入库”】
    """
    file_obj = request.FILES.get('file')
    type_dict = {'入库': 1, '借出': 2, '还回': 3, '维修': 4, '报废': 5}
    file_type_list = ['xls', 'xlsx']
    error_list = []
    # 判断文件的类型
    if ((file_obj.name)[::-1].split('.')[0])[::-1] not in file_type_list:
        return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '上传失败，请上传 .xls 或 .xlsx 类型的文件！'})
    else:
        # accessory_dir = os.path.join('e:/tmp_cmdb_import')
        accessory_dir = os.path.join(MEDIA_ROOT, 'tmp_cmdb_import')
        if not os.path.isdir(accessory_dir):
            os.mkdir(accessory_dir)
        upload_file = "%s/%s" % (accessory_dir, 'cmdb_import.'+((file_obj.name)[::-1].split('.')[0])[::-1])
        recv_size = 0
        with open(upload_file, 'wb') as new_file:
            for chunk in file_obj.chunks():
                new_file.write(chunk)
    workbook = xlrd.open_workbook(upload_file)
    book_sheet = workbook.sheet_by_index(0)
    n_rows = book_sheet.nrows
    row_number = len(book_sheet.row_values(0))
    if row_number < 6:
        return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '导入失败，表格格式错误！'})
    else:
        j_dict = {0: '经手人', 1: '资产编号', 2: '类型', 3: '操作人', 4: '操作时间', 5: '备注'}
        for i in range(6):
            if book_sheet.row_values(0)[i] != j_dict[i]:
                return JsonResponse({'status': 'error', 'title': 'ERROR', 'result': '第'+str(i+1)+'列的第一行标题有误！'})
    oper_name_id = request.user.id
    count = 0
    v = 0
    while v < n_rows:
        v += 1
        try:
            row_data = book_sheet.row_values(v)
            add_asset_obj = AssetFlow()
            try:
                add_asset_obj.hand_person = row_data[0].strip()
            except Exception as _:
                add_asset_obj.hand_person = row_data[0]
            try:
                row_data_1 = row_data[1].strip()
            except Exception as _:
                row_data_1 = row_data[1]
            try:
                the_asset_id = Assets.objects.only('id').get(asset_id=row_data_1).id
            except:
                continue
            else:
                add_asset_obj.asset_id = the_asset_id

            try:
                type = type_dict[row_data[2].strip()]
            except KeyError:
                type = 1
            add_asset_obj.type = type
            add_asset_obj.operator_id = oper_name_id

            if str(row_data[4]) and row_data[4] != 'NULL':
                date = xlrd.xldate_as_tuple(row_data[4], 0)
                add_asset_obj.time = datetime.datetime(*date)
                print (add_asset_obj.time)


            if row_data[5].strip():
                try:
                    add_asset_obj.remark = row_data[5].strip()
                except Exception as _:
                    add_asset_obj.remark = row_data[5]
            try:
                add_asset_obj.save()
            except:
                continue
            else:
                count += 1
        except Exception as _:
            continue
    if os.path.exists(upload_file):
        try:
            os.remove(upload_file)
        except:
            pass
    return JsonResponse({'title': 'SUCCESS', 'result': '导入成功！', 'status': 'success'})

@login_required
@check_permission
def delete_asset(request):
    """删除资产"""
    try:
        asset_id = request.POST.get('asset_id', '')
        if asset_id:
            try:
                Assets.objects.filter(asset_id = asset_id).delete()
            except Exception as _:
                raise TaskError('删除失败！')
            else:
                return JsonResponse({'code': 1, 'result': '删除成功！'})
        else:
            raise TaskError('此资产不存在！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def delete_asset_type(request):
    """删除资产类型"""
    try:
        type_id = request.POST.get('type_id', '')
        if type_id:
            try:
                asset_type_obj = AssetType.objects.get(id = type_id)
            except Exception as _:
                raise TaskError('此资产类型不存在！')
            if asset_type_obj.asset_type.all().count() > 0:
                raise TaskError('存在资产关联此类型，不能删除！')
            else:
                try:
                    AssetType.objects.filter(id=type_id).delete()
                except Exception as _:
                    raise TaskError('删除失败！')
                else:
                    return JsonResponse({'code': 1, 'result': '删除成功！'})
        else:
            raise TaskError('此资产类型不存在！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def delete_supplier(request):
    """删除供应商"""
    try:
        supplier_id = request.POST.get('supplier_id', '')
        if supplier_id:
            try:
                supplier_obj = Supplier.objects.get(id = supplier_id)
            except Exception as _:
                raise TaskError('此供应商不存在！')
            else:
                if supplier_obj.supplier.all().count() > 0:
                    raise TaskError('存在资产关联此供应商，不能删除！')
                else:
                    try:
                        Supplier.objects.filter(id=supplier_id).delete()
                    except:
                        raise TaskError('删除失败！')
                    else:
                        return JsonResponse({'code': 1, 'result': '删除成功！'})
        else:
            raise TaskError('此供应商不存在！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def asset_type_change(request):
    """编辑资产类型"""
    try:
        asset_type_id = request.POST.get('asset_form_type_name', '')
        asset_type_add_name = request.POST.get('asset_type_add_name', '').strip()
        my_field = request.POST.get('my_field', '')
        if not asset_type_add_name:
            raise TaskError('类型名称不能为空！')
        else:
            try:
                if not asset_type_id:
                    AssetType.objects.get(name=asset_type_add_name)
                else:
                    AssetType.objects.exclude(id=asset_type_id).get(name=asset_type_add_name)
            except Exception as _:
                try:
                    if not asset_type_id:
                        change_asset_type_obj = AssetType()
                    else:
                        change_asset_type_obj = AssetType.objects.get(id=asset_type_id)
                    change_asset_type_obj.name = asset_type_add_name
                    change_asset_type_obj.customize_asset_field = my_field
                    change_asset_type_obj.save()
                except Exception as _:
                    raise TaskError('操作失败！')
            else:
                raise TaskError('该类型名称已存在！')
            return JsonResponse({'code': 1, 'result': '操作成功！'})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def supplier_change(request):
    """编辑供应商"""
    try:
        change_supplier_id = request.POST.get('change_supplier_id_name', '')
        change_supplier_name = request.POST.get('change_supplier_name', '').strip()
        change_supplier_contact_name = request.POST.get('change_supplier_contact_name', '').strip()
        change_supplier_fixed_telephone_name = request.POST.get('change_supplier_fixed_telephone_name', '').strip()
        change_supplier_mobile_phone_name = request.POST.get('change_supplier_mobile_phone_name', '').strip()
        change_supplier_address_name = request.POST.get('change_supplier_address_name', '').strip()
        change_supplier_email_name = request.POST.get('change_supplier_email_name', '').strip()
        change_supplier_qq_name = request.POST.get('change_supplier_qq_name', '').strip()
        change_supplier_remark_name = request.POST.get('change_supplier_remark_name', '').strip()
        if not change_supplier_name:
            raise TaskError('供应商名称不能为空！')
        else:
            try:
                if not change_supplier_id:
                    Supplier.objects.get(name=change_supplier_name)
                else:
                    Supplier.objects.exclude(id=change_supplier_id).get(name=change_supplier_name)
            except Exception as _:
                try:
                    if not change_supplier_id:
                        change_asset_type_obj = Supplier()
                    else:
                        change_asset_type_obj = Supplier.objects.get(id=change_supplier_id)
                    change_asset_type_obj.name = change_supplier_name
                    change_asset_type_obj.contact = change_supplier_contact_name
                    change_asset_type_obj.fixed_telephone = change_supplier_fixed_telephone_name
                    change_asset_type_obj.mobile_phone = change_supplier_mobile_phone_name
                    change_asset_type_obj.address = change_supplier_address_name
                    change_asset_type_obj.email = change_supplier_email_name
                    change_asset_type_obj.qq = change_supplier_qq_name
                    change_asset_type_obj.remark = change_supplier_remark_name
                    change_asset_type_obj.save()
                except Exception as _:
                    raise TaskError('操作失败！')
            else:
                raise TaskError('该供应商名称已存在！')
            return JsonResponse({'code': 1, 'result': '操作成功！'})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def get_asset_detail(request):
    """资产详情"""
    try:
        asset_id = request.POST.get('asset_id', '').strip()
        if asset_id == '':
            raise TaskError('资产不存在！')
        try:
            asset_obj = Assets.objects.get(asset_id=asset_id)
        except Exception as _:
            raise TaskError('资产不存在！')
        else:
            flow_html = ''
            flow_obj = AssetFlow.objects.filter(asset_id=asset_obj.id).order_by('-time')
            start_html = '<div class="" role="tabpanel" data-example-id="togglable-tabs">'\
                      '<ul id="myTab" class="nav nav-tabs bar_tabs" role="tablist">' \
                      '<li role="presentation" class="active"><a href="#tab_content1_' + asset_id + '" role="tab" id="profile-tab" data-toggle="tab" aria-expanded="false">资产信息</a>' \
                      '</li>' \
                      '<li role="presentation" class =""><a href="#tab_content2_'+asset_id+'" id="home-tab" role="tab" data-toggle="tab" aria-expanded="true">出入记录</a> '\
                      '</li>'\
                      '<li role="presentation" class =""><a href="#tab_content3_'+asset_id+'" id="home-tab" role="tab" data-toggle="tab" aria-expanded="true">操作日志</a> '\
                      '</li>'\
                      '</ul>'\
                      '<div id="myTabContent" class="tab-content">'

            # 出入记录
            if flow_obj.count() > 0:
                flow_html = '<div role="tabpanel" class="tab-pane fade" id="tab_content2_'+asset_id+'" ' \
                            'aria-labelledby="home-tab"><div class="col-md-12">' \
                            '<table class="table table-striped table-bordered dt-responsive nowrap">' \
                            '<thead><tr><th>经手人</th><th>资产编号</th><th>类型</th>' \
                            '<th>操作人</th><th>操作时间</th><th>备注</th></tr></thead><tbody>'
                for i in flow_obj:
                    flow_html += ('<tr><td>' + (i.hand_person if i.hand_person else "")+'</td>'
                    '<td>'+(i.asset.asset_id if i.asset else "")+'</td>'
                    '<td>'+(i.get_type_display() if i.type else "")+'</td>'
                    '<td>'+(get_name_by_id.get_name(i.operator.id) if i.operator else "")+'</td>'
                    '<td>'+(i.time.replace(tzinfo=utc).astimezone(datetime.timezone(
                        timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S") if i.time else "")+'</td>'
                    '<td title="'+(i.remark if i.remark else "")+'" style="max-width:70px;">'+(
                        i.remark[0:15]+("..." if len(i.remark) > 15 else "") if i.remark else "")+'</td></tr>')
                flow_html += '</tbody></table></div></div>'
            else:
                flow_html += '<div role="tabpanel" class="tab-pane fade" id="tab_content2_'+asset_id+'" ' \
                             'aria-labelledby="home-tab">无出入记录</div>'

            # 操作日志
            log_obj = Assetlogs.objects.filter(asset_id=asset_obj.id).order_by('-datetime')
            if log_obj.count() > 0:
                log_html = '<div role="tabpanel" class="tab-pane fade" id="tab_content3_' + asset_id + '" ' \
                            'aria-labelledby="home-tab"><div class="col-md-12">' \
                            '<table class="table table-striped table-bordered dt-responsive nowrap">' \
                            '<thead><tr><th>操作人</th><th>操作时间</th><th>日志内容</th></tr></thead><tbody>'
                for i in log_obj:
                    log_html += (
                    '<tr><td>' + (get_name_by_id.get_name(i.operator.id) if i.operator else "") + '</td><td>' + (
                    i.datetime.replace(tzinfo=utc).astimezone(datetime.timezone(
                        timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S") if i.datetime else "") + '</td><td title="' + (
                    i.content if i.content else "") + '" style="max-width:800px;">' + (
                        i.content[0:200] + (
                        "..." if len(i.content) > 200 else "") if i.content else "") + '</td></tr>')
                log_html += '</tbody></table></div></div>'
            else:
                log_html = '<div role="tabpanel" class="tab-pane fade" id="tab_content3_' + asset_id + '" ' \
                           'aria-labelledby="home-tab">无操作日志</div>'
            flow_html += log_html

            # 资产信息
            if asset_obj.asset_info:
                asset_info = eval(asset_obj.asset_info)
                result = start_html+'<div role="tabpanel" class="tab-pane fade in active" id="tab_content1_'+str(asset_id)+'"' \
                                    ' aria-labelledby="profile-tab"><div class="col-md-12">'
                for key in asset_info.keys():
                    result += '<div style="" class="col-md-4 col-sm-6 col-xs-12"><b>'+str(key)+'：</b>' \
                               '<span>'+str(asset_info[key])+'</span></div>'
                result += '</div></div>' + flow_html + '</div></div>'
            else:
                flow_html += '<div role="tabpanel" class="tab-pane fade in active" id="tab_content1_'+asset_id+'" ' \
                             'aria-labelledby="profile-tab">无更多资产信息</div></div></div>'
                result = start_html+flow_html
            return JsonResponse({'code': 1, 'result': result})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def asset_out(request):
    """资产借出"""
    try:
        asset_out_name = request.POST.get('asset_out_name', '').strip()
        asset_use_person = request.POST.get('asset_use_person', '').strip()
        remark = request.POST.get('remark_out_name', '').strip()
        try:
            asset_obj = Assets.objects.get(asset_id=asset_out_name)
        except Exception as _:
            raise TaskError('资产编号不存在，请重新输入！')
        else:
            if asset_obj.status != 1:
                raise TaskError('操作失败，此资产目前为「'+asset_obj.get_status_display()+'」状态！')
            try:
                user_list = GetDepartUserList(1, 1).userList()
            except Exception as _:
                raise TaskError('领用人不存在，请重新输入！')
            else:
                asset_use_person_email = ''
                is_user = 0
                for i in user_list:
                    if asset_use_person == i['name']:
                        is_user = 1
                        asset_use_person_email = i['email']
                        break
                if is_user == 1:
                    # 资产状态修改（2为借出状态）
                    try:
                        asset_obj.status = 2
                        asset_obj.use_person = asset_use_person
                        asset_obj.use_time = datetime.datetime.now()
                        asset_obj.save()
                    except:
                        raise TaskError('操作失败！')
                    # 资产流动记录
                    asset_flow_save(asset_obj.id, 2, request.user.id, remark, asset_use_person, asset_use_person_email)
                    # 日志保存
                    asset_log_save(asset_obj.id, '资产借出', request.user.id)
                    return JsonResponse({'code': 1, 'result': '操作成功！'})
                else:
                    raise TaskError('领用人不存在，请重新输入！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def asset_back(request):
    """资产归还"""
    try:
        asset_back_name = request.POST.get('asset_back_name', '').strip()
        asset_back_person = request.POST.get('asset_back_person', '').strip()
        remark = request.POST.get('remark_back_name', '').strip()
        try:
            asset_obj = Assets.objects.get(asset_id=asset_back_name)
        except Exception as _:
            raise TaskError('资产编号不存在，请重新输入！')
        if not asset_back_person:
            raise TaskError('归还人不能为空！')
        else:
            if asset_obj.status == 1:
                raise TaskError('操作失败，此资产目前为「'+asset_obj.get_status_display()+'」状态！')
            # 资产状态修改（1为在库状态）
            try:
                asset_obj.status = 1
                asset_obj.use_person = None
                asset_obj.use_time = None
                asset_obj.save()
            except:
                raise TaskError('操作失败！')
            # 资产流动记录
            asset_flow_save(asset_obj.id, 3, request.user.id, remark, asset_back_person)
            # 日志保存
            asset_log_save(asset_obj.id, '资产归还', request.user.id)
            return JsonResponse({'code': 1, 'result': '操作成功！'})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})


@login_required
@check_permission
def asset_maintain(request):
    """资产维修"""
    try:
        asset_maintain_name = request.POST.get('asset_maintain_name', '').strip()
        asset_maintain_person = request.POST.get('asset_maintain_person', '').strip()
        remark = request.POST.get('remark_maintain_name', '').strip()
        try:
            asset_obj = Assets.objects.get(asset_id=asset_maintain_name)
        except Exception as _:
            raise TaskError('资产编号不存在，请重新输入！')
        else:
            if asset_obj.status != 1:
                raise TaskError('此资产目前为「'+asset_obj.get_status_display()+'」状态，不能维修！')
            if not asset_maintain_person:
                raise TaskError('维修方不能为空！')
            else:
                # 资产状态修改（3为维修状态）
                try:
                    asset_obj.status = 3
                    asset_obj.save()
                except:
                    raise TaskError('操作失败！')
                # 资产流动记录
                asset_flow_save(asset_obj.id, 4, request.user.id, remark, asset_maintain_person)
                # 日志保存
                asset_log_save(asset_obj.id, '资产维修', request.user.id)
                return JsonResponse({'code': 1, 'result': '操作成功！'})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
@check_permission
def asset_scrap(request):
    """资产报废"""
    try:
        asset_scrap_name = request.POST.get('asset_scrap_name', '').strip()
        remark = request.POST.get('remark_scrap_name', '').strip()
        try:
            asset_obj = Assets.objects.get(asset_id=asset_scrap_name)
        except Exception as _:
            raise TaskError('资产编号不存在，请重新输入！')
        else:
            if asset_obj.status != 1:
                raise TaskError('此资产目前为「'+asset_obj.get_status_display()+'」状态，不能报废！')
            else:
                # 资产状态修改（4为报废状态）
                try:
                    asset_obj.status = 4
                    asset_obj.save()
                except:
                    raise TaskError('操作失败！')
                # 资产流动记录
                asset_flow_save(asset_obj.id, 5, request.user.id, remark)
                # 日志保存
                asset_log_save(asset_obj.id, '资产报废', request.user.id)
                return JsonResponse({'code': 1, 'result': '操作成功！'})
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
def judge_back_person(request):
    """判断归还人"""
    try:
        asset_id = request.POST.get('asset_id', '').strip()
        if asset_id == '':
            raise TaskError('资产编号不能为空！')
        else:
            try:
                asset_obj = Assets.objects.get(asset_id = asset_id)
            except:
                raise TaskError('资产不存在')
            else:
                if asset_obj.status != 1:
                    if asset_obj.status == 3 or asset_obj.status == 2:
                        if asset_obj.status == 3:
                            flow_obj = AssetFlow.objects.filter(asset_id = asset_obj.id, type = 4)
                        else:
                            flow_obj = AssetFlow.objects.filter(asset_id=asset_obj.id, type=2)
                        if flow_obj.count() == 0:
                            return JsonResponse({'code': 1, 'result': ''})
                        else:
                            flow_last = flow_obj.order_by('-time')[0]
                            return JsonResponse({'code': 1, 'result': str(flow_last.hand_person)})
                    else:
                        return JsonResponse({'code': 1, 'result': ''})
                else:
                    raise TaskError('此资产不在维修状态！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
def judge_supplier(request):
    """判断供应商"""
    try:
        asset_id = request.POST.get('asset_id', '').strip()
        if asset_id == '':
            raise TaskError('资产编号不能为空！')
        else:
            try:
                asset_obj = Assets.objects.get(asset_id = asset_id)
            except:
                raise TaskError('此资产不存在！')
            else:
                if asset_obj.supplier:
                    return JsonResponse({'code': 1, 'result': asset_obj.supplier.name})
                else:
                    raise TaskError('此资产没有设定供应商信息！')
    except TaskError as e:
        return JsonResponse({'code': 0, 'result': str(e)})

@login_required
def get_asset_field(request):
    """获取资产定制字段"""
    try:
        type_id = request.POST.get('type_id', '')
        asset_id = request.POST.get('asset_id', '')
        if not type_id:
            raise TaskError('error')
        else:
            try:
                obj = AssetType.objects.get(id = int(type_id))
            except Exception as _:
                raise TaskError('error')
            else:
                the_asset_info = {}
                if asset_id:
                    try:
                        the_asset_info = eval(Assets.objects.only('asset_info').get(asset_id=asset_id).asset_info)
                    except:
                        the_asset_info = {}
                if not obj.customize_asset_field and not the_asset_info:
                    raise TaskError('error')
                else:
                    try:
                        field_list = (obj.customize_asset_field).split(",")
                    except Exception as _:
                        field_list = ''
                    return JsonResponse({'result': field_list, 'the_value': the_asset_info})
    except TaskError as _:
        return JsonResponse({'result': '', 'the_value': ''})

@login_required
@check_permission
def get_org(request):
    """获取组织结构"""
    try:
        data = eval(Org.objects.only('org_data').get(oid=1).org_data)
    except:
        data = []
    return JsonResponse({'result': data})

@login_required
@check_permission
def get_supplier(request):
    """获取所有供应商"""
    obj = Supplier.objects.all()
    result = []
    for i in obj:
        result.append({'value': i.id, 'name': i.name})
    return JsonResponse({'result':result})

@login_required
@check_permission
def get_asset_type(request):
    """获取所有资产类型"""
    obj = AssetType.objects.all()
    result = []
    for i in obj:
        result.append({'value': i.id, 'name': i.name})
    return JsonResponse({'result':result})

@login_required
@check_permission
def get_all_user(request):
    """获取所有用户"""
    result = getAllUser()
    return JsonResponse({'result': result})

@login_required
@check_permission
def get_wechat_user(request):
    """获取所有微信用户"""
    user_list = GetDepartUserList(1,1).userList()
    result = []
    for i in user_list:
        result.append({'value': i['email'], 'name': i['name']})
    return JsonResponse({'result': result})

def asset_flow_save(id, type, user_id, remark = None, use_person = None, use_person_email = None):
    """
    @note: 资产流动记录保存
    :param id: 资产ID
    :param user_id: 操作用户ID
    :param remark: 日志
    :param use_person: 领用人
    :param use_person_email: 领用人邮箱
    :return:
    """
    try:
        flow_obj = AssetFlow()
        flow_obj.asset_id = id
        flow_obj.hand_person = use_person
        flow_obj.hand_person_email = use_person_email
        flow_obj.type = type
        flow_obj.operator_id = user_id
        flow_obj.time = datetime.datetime.now()
        flow_obj.remark = remark
        flow_obj.save()
    except:
        code = 0
        alert = '日志保存失败'
    else:
        code = 1
        alert = '日志保存成功'
    return {'code': code, 'alert': alert}

def asset_log_save(id, content, user_id):
    """
    @note: 资产日志保存
    :param id: 资产ID
    :param content: 日志内容
    :param user_id: 操作用户ID
    :return:
    """
    try:
        log_obj = Assetlogs()
        log_obj.asset_id = id
        log_obj.content = content
        log_obj.operator_id = user_id
        log_obj.save()
    except:
        code = 0
        alert = '日志保存失败'
    else:
        code = 1
        alert = '日志保存成功'
    return {'code': code, 'alert': alert}

@login_required
def asset_count(request):
    """库存统计"""
    count = {}
    type_list = AssetType.objects.all()
    for type in type_list:
        count[type.name] = {}
        obj = AssetType.objects.get(id=type.id)
        count[type.name]['在库'] = obj.asset_type.filter(status=1).count()
        count[type.name]['借出'] = obj.asset_type.filter(status=2).count()
        count[type.name]['维修'] = obj.asset_type.filter(status=3).count()
        count[type.name]['报废'] = obj.asset_type.filter(status=4).count()
        count[type.name]['统计'] = count[type.name]['在库'] + count[type.name]['借出'] + count[type.name]['维修'] + \
                                 count[type.name]['报废']
    asset_c = Assets.objects.all()
    count['统计'] = {}
    count['统计']['在库'] = asset_c.filter(status=1).count()
    count['统计']['借出'] = asset_c.filter(status=2).count()
    count['统计']['维修'] = asset_c.filter(status=3).count()
    count['统计']['报废'] = asset_c.filter(status=4).count()
    count['统计']['统计'] = count['统计']['在库'] + count['统计']['借出'] + count['统计']['维修'] + count['统计']['报废']
    return JsonResponse({'result': count})


def get_database_instance_total():
    total = Instance.objects.all().count()
    return JsonResponse({'result':total})


def get_user_total():
    total = User.objects.all().count()
    return JsonResponse({'result':total})


def custom_export(request):
    """自定义导出"""
    asset_type = request.POST.get('type', '')
    field_lsit = request.POST.getlist('field', [])
    asset_field = []
    asset_field_verbose_name_dict = {}
    asset_field_verbose_name = []
    obj = Assets.objects.filter(asset_type=int(asset_type))
    for i in Assets._meta.fields:
        if i.name in field_lsit:
            try:
                asset_field_verbose_name.append(i.verbose_name)
                asset_field_verbose_name_dict[i.name] = i.verbose_name
                asset_field.append(i.name)
                field_lsit.remove(i.name)
            except Exception as _:
                continue
    data_list = []
    for v in obj:
        data = {}
        for b in asset_field:
            try:
                if b in ['asset_type', 'supplier']: 
                    str_value = eval("v.{field}.name".format(field=b))
                elif b == 'operator': 
                    str_value = get_name_by_id.get_name(id=eval("v.{field}.id".format(field=b)))
                elif b in ['operate_time', 'use_time']: 
                    str_value = eval("v.{field}".format(field=b)).replace(tzinfo=utc).astimezone(
                    datetime.timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S") if eval(
                    "v.{field}".format(field=b)) else ""
                elif b == 'buy_time':
                    str_value = eval("v.{field}".format(field=b)).strftime("%Y-%m-%d") if  eval(
                    "v.{field}".format(field=b)) else ""
                else: 
                    str_value = eval("v.{field}".format(field=b))
                data[asset_field_verbose_name_dict[b]] = str_value
            except Exception as _:
                try: data[asset_field_verbose_name_dict[b]] = ''
                except: data[b] = ''
                continue
        asset_info_dict = eval(v.asset_info)
        for j in field_lsit:
            try:
                data[j] = asset_info_dict[j]
            except Exception as _:
                data[j] = ''
                continue
        data_list.append(data)
    asset_field_verbose_name += field_lsit
    return JsonResponse({'result': {'data_list': data_list, 'field': asset_field_verbose_name}, 'code': 1})


class DomainManageView(TemplateView):
    """域名管理视图"""
    template_name = 'cmdb/domain_list.html'

    def get_context_data(self, **kwargs):
        context = super(DomainManageView, self).get_context_data(**kwargs)
        try:
            content_type_id = ContentType.objects.get(
                app_label=DomainManage._meta.app_label,
                model=DomainManage._meta.object_name
            ).id
            context['content_type_id'] = content_type_id
        except: pass
        return context


class DomainManageList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, DetailView):
    """域名管理列表、新增"""
    queryset = DomainManage.objects.all().exclude(is_delete=True).order_by('status', 'expire_date')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = DomainFilter
    pagination_class = MyPageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DomainManageDetailSerializer
        else:
            return DomainManageSerializer

    @check_object_perm(codename='CMDB.add_domainmanage')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='CMDB.add_domainmanage')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DomainManageDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """域名管理读取、更新、删除"""
    queryset = DomainManage.objects.all().exclude(is_delete=True)
    serializer_class = DomainManageSerializer

    @check_object_perm(codename='CMDB.add_domainmanage')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='CMDB.change_domainmanage')
    @change(choice={'status': 'STATUS_CHOICES'})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='CMDB.delete_domainmanage')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

@login_required
def get_domain_amount(request):
    obj = DomainManage.objects.all().exclude(is_delete=1)
    total = obj.count()
    run = obj.filter(status=2).count()
    date_list = obj.values_list('expire_date', flat=True)
    now_date = datetime.date.today()
    expired_at_once = 0
    expired = 0
    for i in date_list:
        try:
            gap = i - now_date
            if gap.days < 0:
                expired += 1
            elif gap.days <= 7:
                expired_at_once += 1
        except Exception:
            continue
    result = {
        "total": total,
        "run": run,
        "expired_at_once": expired_at_once,
        "expired": expired
    }
    return JsonResponse(result)

from opscenter.models import Server
from pandas import DataFrame
@login_required
def asset_amount(request):
    asset_obj = Assets.objects.all()
    computer_count = asset_obj.filter(asset_type__name='电脑').count()
    server_count = asset_obj.filter(asset_type__name='服务器').count()
    all_server_count = Server.objects.count()
    net_asset_count = asset_obj.filter(asset_type__name='网络设备').count()
    printer_count = asset_obj.filter(asset_type__name='打印机').count()
    domain_obj = DomainManage.objects.all().exclude(is_delete=1)
    domain_count = domain_obj.count()
    now_date = datetime.date.today()
    expired_at_once_data = []
    by_type_count = {}
    for i in domain_obj:
        if i.expire_date:
            try:
                gap = i.expire_date - now_date
                if 0 <= gap.days <= 7:
                    expired_at_once_data.append({
                        "domain": i.domain,
                        "support": i.register_support.name,
                        "expire_date": i.expire_date.strftime("%Y-%m-%d")
                    })
            except Exception:
                pass
        try:
            try:
                by_type_count[i.register_support.name] += 1
            except Exception:
                by_type_count[i.register_support.name] = 0
                by_type_count[i.register_support.name] += 1
        except Exception:
            pass
    pie_domain_by_type_data = []
    pie_domain_by_type_name_list = []
    for v in by_type_count:
        pie_domain_by_type_name_list.append(v)
        pie_domain_by_type_data.append({"name": v, "value": by_type_count[v]})
    if expired_at_once_data:
        expired_at_once_data = DataFrame(
            expired_at_once_data).sort_values(by='expire_date').values.tolist()
    result = {
        "computer_count": computer_count,
        "server_count": server_count,
        "all_server_count": all_server_count,
        "net_asset_count": net_asset_count,
        "printer_count": printer_count,
        "domain_count": domain_count,
        "pie_domain_by_type_name_list": pie_domain_by_type_name_list,
        "pie_domain_by_type_data": pie_domain_by_type_data,
        "expired_at_once_data": expired_at_once_data
    }
    return JsonResponse(result)

@login_required
def daily_asset_flow_amount(request):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    start_date = datetime.datetime.strptime(start.strip(), '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end.strip(), '%Y-%m-%d')
    flow_obj = AssetFlow.objects.all()
    date_list = []
    pie_flow_data = {"入库": 0, "借出": 0, "还回": 0, "维修": 0, "报废": 0}
    date_filter_1 = flow_obj.filter(time__range=(start_date, end_date))
    pie_flow_data["入库"] = date_filter_1.filter(type=1).count()
    pie_flow_data["借出"] = date_filter_1.filter(type=2).count()
    pie_flow_data["还回"] = date_filter_1.filter(type=3).count()
    pie_flow_data["维修"] = date_filter_1.filter(type=4).count()
    pie_flow_data["报废"] = date_filter_1.filter(type=5).count()
    line_in_count = []
    line_lend_count = []
    line_return_count = []
    line_maintain_count = []
    line_discard_count = []
    for i in range((end_date - start_date).days + 1): # 循环计算日期范围内每天的工作流总数
        day = start_date + datetime.timedelta(days=i)
        date_filter_2 = flow_obj.filter(time__range=(day, day + timedelta(days=1)))
        line_in_count.append(date_filter_2.filter(type=1).count())
        line_lend_count.append(date_filter_2.filter(type=2).count())
        line_return_count.append(date_filter_2.filter(type=3).count())
        line_maintain_count.append(date_filter_2.filter(type=4).count())
        line_discard_count.append(date_filter_2.filter(type=5).count())
        date_list.append(day.strftime("%Y-%m-%d"))
    result = {
        "pie_flow_data": pie_flow_data,
        "date_list": date_list,
        "line_in_count":line_in_count,
        "line_lend_count":line_lend_count,
        "line_return_count":line_return_count,
        "line_maintain_count":line_maintain_count,
        "line_discard_count":line_discard_count,
    }
    return JsonResponse(result)
