from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from usercenter.permission import check_permission
from django.contrib import messages
from django.urls import reverse
from .forms import *
from django.core.paginator import Paginator
from django.contrib import auth
from django.db.models import Q
from .models import *
from workflow.models import *
from database.models import Application
from worksheet.models import WorkSheet
from workflow.views import DateEncoder
from workflow.get_name_by_id import get_name_by_id
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Permission as auth_permission
from django.contrib.contenttypes.models import ContentType
from django import forms
import json
import datetime
from worksheet.worksheetCount import GetWorksheetTotalCount
from workflow.compute_flow_count import get_workflow_total_count
from usercenter.getAllUser import get_all_user as getAllUser
from rest_framework import mixins
from rest_framework import generics
from .serializers import *
from lib.relative_time import time_span

class ClientOper(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


def get_group_list_by_user(request):
    id = request.POST.get('id', '')
    group_list = list(User.objects.get(id=int(id)).groups.values_list('id', flat=True))
    return JsonResponse({'group_list': group_list})


class CustomPasswordResetForm(PasswordResetForm):
    '''忘记密码功能 实现'邮箱未注册'的提示'''
    def clean_email(request):
        email = request.cleaned_data.get('email', '')

        if not User.objects.filter(email=email):
            raise forms.ValidationError('邮箱未注册')
        return email


class CustomPasswordResetView(PasswordResetView):
    # template_name = 'your_passd_reset.html'
    form_class = CustomPasswordResetForm


def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, '密码修改成功！')
    return HttpResponseRedirect(reverse('index'))


def password_reset_complete(request):
    messages.add_message(request, messages.SUCCESS, '密码重置成功！')
    return HttpResponseRedirect(reverse('login'))

def login(request):
    '''
    登录验证
    '''
    if request.method == 'GET':
        # 记住来源的url，如果没有则设置为首页('/')
        # request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
        request.session['login_from'] = '/'
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.session['login_from'])
        else:
            uf = UserForm()
            return render(request,'login.html', {'uf': uf})
    else:
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = request.POST.get('username', '')
            if username:
                username = username.strip()
            password = request.POST.get('password', '')
            user = auth.authenticate(username = username,password = password)
            if user is not None and user.is_active:
                auth.login(request, user)
                ''' 登录用户的可用菜单模块 '''
                request.session['menu_list'] = {}
                try:
                    get_module = SystemModule.objects.all()
                    for module in get_module:
                        try:
                            get_perm = Permission.objects.filter(Q(url=module.module_url) , Q(per_method=1))
                            if get_perm:
                                for i in get_perm:
                                    perm_name = i.name
                                    app_label = ContentType.objects.only('app_label').get(
                                        id=auth_permission.objects.only('content_type_id').get(
                                            codename=perm_name).content_type_id).app_label
                                    perm_str = app_label + '.' + perm_name
                                    if request.user.has_perm(perm_str):
                                        request.session['menu_list'][module.module_url] = module.module_name
                        except:
                            continue
                except:
                    pass
                ''' 登录用户的可用菜单模块 '''
                messages.add_message(request, messages.SUCCESS, 'logged in successfully!')
                try:
                    next_url  = request.GET['next']
                except:
                    pass
                else:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(request.session['login_from'])
            else:
                messages.add_message(request, messages.ERROR, "Sorry, that's not a valid username or password")
                return render(request, 'login.html', {'uf': uf})
        else:
            return render(request, 'login.html', {'uf': uf})


def logout(request):
    '''
    注销
    '''
    auth.logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def get_userinfo(request):
    '''
    @author: Xieyz
    @note: 获取用户信息
    :param request:
    :return:
    '''
    if 'username' in request.session:
        username = request.session['username']
        userid = request.session['userid']
        userinfo_dict = {
            'username' : username,
            'userid' : userid,
        }
        return render(request, 'head.html', userinfo_dict)





# @login_required
# def page_not_found(request):
#     '''
#     @author: Xieyz
#     @note: 404报错页面
#     '''
#     return render(request,'404.html')
#
#
# @login_required
# def page_error(request):
#     '''
#     @author: Xieyz
#     @note: 500报错页面
#     '''
#     return render(request,'500.html')


@login_required
def index(request):
    '''
    @author: Xieyz
    @note: 首页
    '''
    try:
        count = {
            "worksheet_solve_of_me": WorkSheet.objects.filter(Q(status=3)|Q(status=0),operator=request.user).count(),
            "worksheet_total_count": GetWorksheetTotalCount().total_count(),
            "worksheet_solve_count": GetWorksheetTotalCount().solve_count(),
            "worksheet_close_count": GetWorksheetTotalCount().close_count(),
            "worksheet_process_count": GetWorksheetTotalCount().process_count(),
            "worksheet_solved_rate": round((GetWorksheetTotalCount().solved_complete_count()/
                                      GetWorksheetTotalCount().close_count())*100, 1),
            "worksheet_response_time_count": GetWorksheetTotalCount().response_time_count(),
            "worksheet_solve_time_count": GetWorksheetTotalCount().solve_time_count(),
            "workflow_total_count": get_workflow_total_count()
        }
    except Exception as e:
        print ("Index, Error : " + str(e))
        count = {}
    return render(request, 'dashboard.html', count)


@login_required
def group(request):
    '''
    @author: Xieyz
    @note: group
    '''
    return render(request,'group.html')


@login_required
def message_list_view(request,isread = 'all',id = 0):
    '''
    @author: Xieyz
    @note: 消息列表
    :param request:
    :return: 消息列表
    '''
    if id != 0:
        Message.objects.filter(id = id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功!')
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 每页显示多少行
        pageNumber = request.POST.get('pageNumber')
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            if isread == 'all':
                all_records = Message.objects.filter(Q(title__icontains=search) |
                                                     Q(type__icontains=search),
                                                     user_id=request.user.id)
            else:
                all_records = Message.objects.filter(Q(title__icontains=search) |
                                                     Q(type__icontains=search),
                                                     user_id=request.user.id,
                                                     status=isread)
        else:
            if isread == 'all':
                print(request.user.id)
                all_records = Message.objects.filter(user_id=request.user.id)
            else:
                all_records = Message.objects.filter(user_id=request.user.id,status=isread)

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['time','status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)

                if order == 'asc':  # 如果排序是正向
                    sort_column = '%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-time')
        all_records_count = all_records.count()

        if not pageSize:
            pageSize = 15  # 默认是每页15行的内容，与前端默认行数一致+
        if all_records_count:
            if int(all_records_count)%int(pageSize) == 0:
                if int(pageNumber) > int(all_records_count)/int(pageSize):
                    pageNumber = int(all_records_count)/int(pageSize)

        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        response_data = {'total': all_records_count, 'rows': []}
        for list in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "title": list.title if list.title else "",
                "time": list.time if list.time else "",
                "type": list.type if list.type else "",
                "status": list.get_status_display() if list.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'usercenter/message_list.html',{'isread':isread})


@login_required
def message_change_status(request):
    data = json.loads(request.body)
    for i in data:
        if i['status'] != '已读':
            Message.objects.filter(id=i['id']).update(status=1)
    return JsonResponse({'result': 'true'})


@login_required
def message_batch_delete(request):
    data = json.loads(request.body)
    for i in data:
        Message.objects.filter(id=i['id']).delete()
    return JsonResponse({'result': 'true'})


@login_required
def message_detail_view(request, id):
    '''
    @author: Xieyz
    @note: 消息详情
    :param request:
    :return:
    '''
    message_get = Message.objects.get(id=id)
    if message_get.status == 0:
        message_get.status = 1
        message_get.save()

    message_list = Message.objects.filter(id=id)
    dict = {
        "list": message_list,
    }
    return render(request, 'usercenter/message_detail.html', dict)


@login_required
def check_unread_message(request):
    unread_message_list = Message.objects.filter(user_id=request.user.id,status=0).order_by('-time')[:10]
    all_unread_count = Message.objects.filter(user_id=request.user.id,status=0).count()
    list1 = []
    for item in unread_message_list:
        list1.append([item.id, item.title, time_span(item.time)])
    list2 = [all_unread_count]
    return JsonResponse({'data': list1,'data2': list2})


@login_required
@check_permission
def project_authority_group_list_view(request,id = 0):
    '''
     @author: Xieyz
     @note: 项目权限组列表
     :param id: authority_group表的id
     :return: authority_group表的JSON格式数据
     '''
    if id != 0:
        authority_group.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功!')
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            all_records = authority_group.objects.filter(Q(id__icontains=search) |
                                                       Q(group_name__icontains=search) |
                                                       Q(project__project__icontains=search))
        else:
            all_records = authority_group.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['group_name', 'project']:
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':
                    sort_column = '%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('-id')
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
                "id": list.id if list.id else "",
                "group_name": list.group_name if list.group_name else "",
                "project": list.project.project if list.project.project else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'usercenter/project_authority_group_list.html')


@login_required
@check_permission
def project_authority_group_add(request):
    '''
    @author: Xieyz
    @note: 项目权限组添加
    :return: AuthorityGroupForm表单
    '''
    if request.method == "POST":
        change = AuthorityGroupForm(request.POST)
        if not request.POST.get('project'):
            messages.add_message(request, messages.ERROR, '请选择项目！')
            type = 'add'
            return render(request, 'usercenter/project_authority_group_change.html', {'form': change,'type':type})
        user_list = request.POST.getlist('doublebox')
        if change.is_valid():
            data = change.cleaned_data
            change.save()

            add_user_list = [int(i) for i in user_list]
            user_name_list = []
            if add_user_list:
                # 更新组和用户的关系表
                for user_id in add_user_list:
                    user_group_add = user_group()
                    user_group_add.group_id = authority_group.objects.only('id').get(
                        group_name=data.get('group_name'),project=data.get('project')).id
                    user_group_add.user_name_id = user_id
                    user_group_add.save()

                    user_name_list.append(project_user.objects.only('user_name').get(id=user_id).user_name)
            # 更新日志
            update_logs = AuthorityGroupChangeLogs()
            update_logs.group_id = authority_group.objects.only('id').get(group_name=data.get('group_name')).id
            update_logs.user_id = request.user.id
            update_logs.content = get_name_by_id.get_name(request.user.id) +'添加了新的用户组, 包含用户:'+ str(user_name_list)
            update_logs.save()

            messages.add_message(request, messages.SUCCESS, '添加用户组"' + data.get('group_name') + '",添加成功!')
            return HttpResponseRedirect(reverse('project_authority_group_list'))
        else:
            messages.add_message(request, messages.ERROR, change.errors)
            type = 'add'
            return render(request, 'usercenter/project_authority_group_change.html', {'form': change, 'type':type})
    else:
        form = AuthorityGroupForm()
        type = 'add'
    return render(request, 'usercenter/project_authority_group_change.html', locals())


@login_required
def get_all_project_user(request, pid):
    list1 = []
    obj = project_user.objects.filter(project_id=pid)
    for item in obj:
        list1.append([item.id, item.user_name])
    return JsonResponse({'data':list1})


@login_required
@check_permission
def project_authority_group_modify(request,id):
    '''
    @author: Xieyz
    @note: 项目权限组修改
    :return: AuthorityGroupForm表单
    '''
    obj = authority_group.objects.get(id=id)
    if request.method == "POST":
        change = AuthorityGroupForm(request.POST,instance=obj)
        if not request.POST.get('project'):
            messages.add_message(request, messages.ERROR, '请选择项目！')
            return render(request, 'usercenter/project_authority_group_change.html', {'form': change,'type':type})
        if change.is_valid():
            data = change.cleaned_data

            # 更新日志
            update_logs = AuthorityGroupChangeLogs()
            update_logs.group_id = id
            update_logs.user_id = request.user.id
            update_logs.content = get_name_by_id.get_name(request.user.id) +'修改了用户组的信息'
            change.save()
            update_logs.save()

            messages.add_message(request, messages.SUCCESS, '修改用户组"' + data.get('group_name') + '"的信息,修改成功!')
            return HttpResponseRedirect(reverse('project_authority_group_list'))
        else:
            messages.add_message(request, messages.ERROR, change.errors)
            return render(request, 'usercenter/project_authority_group_change.html', {'form': change})
    else:
        form = AuthorityGroupForm(instance=obj)
    return render(request, 'usercenter/project_authority_group_change.html', locals())


@login_required
@check_permission
def project_authority_group_user_list_view(request, id = 0):
    '''
    @author: Xieyz
    @note: 模块管理页面
    :param request:
    :return: 模块列表
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')
        all_records = user_group.objects.filter(group_id=id)
        all_records = all_records.order_by('id')
        all_records_count = all_records.count()
        if not offset:
            offset = 0
        if not pageSize:
            pageSize = 10  # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for list in pageinator.page(pageNumber):
            user_obj = project_user.objects.get(id=list.user_name_id)
            response_data['rows'].append({
                "id": user_obj.id if user_obj.id else "",
                "user_name": user_obj.user_name if user_obj.user_name else "",
                "name": user_obj.name if user_obj.name else "",
                "is_active": user_obj.get_is_active_display() if user_obj.get_is_active_display() else "",
                "project": user_obj.project.project if user_obj.project.project else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    log = AuthorityGroupChangeLogs.objects.filter(group_id=id).order_by('-datetime')
    return render(request, 'usercenter/project_authority_group_user_list.html', {"id":id,"flow_log":log})


@login_required
def get_project_group_user(request, gid):
    '''
    @author: Xieyz
    @note: 获取所有该项目的用户列表，和组内的当前用户
    :param request:
    :param gid: 组id
    :return:
    '''
    user_id_list = user_group.objects.filter(group_id=gid).values_list('user_name_id', flat=True)
    list1 = []
    for user_id in user_id_list:
        obj = project_user.objects.filter(id=user_id)
        for item in obj:
            list1.append([item.id, str(item.user_name)+"<"+str(item.name)+">"])

    list2 = []
    list2_exclude = []
    for i in list1:
        list2_exclude.append(i[0])
    all_user_obj = project_user.objects.filter(project_id = authority_group.objects.only('project_id').get(id=gid).project_id)
    for item in all_user_obj:
        if item.id not in list2_exclude:
            list2.append([item.id, str(item.user_name)+"<"+str(item.name)+">"])
    return JsonResponse({'data1': list1,'data2':list2})


@login_required
@check_permission
def project_group_user_change(request, gid):
    '''
        @author: Xieyz
        @note: 用户添加或移出组
        :param request:
        :param gid: 组id
        :return:
        '''
    if request.method == "POST":
        modify_user_list = request.POST.getlist('doublebox')
        reduce_user = []
        increase_user = []
        old_user= user_group.objects.filter(group_id=gid).values_list('user_name_id', flat=True)
        new_user = [int(i) for i in modify_user_list]
        difference_list = list(set(old_user) ^ set(new_user))
        if not difference_list:
            messages.add_message(request, messages.ERROR, '未作出任何修改!')
            return HttpResponseRedirect(reverse('project_authority_group_user_list', args=[gid,]))
        for difference in difference_list:
            if difference in old_user:
                user_group.objects.filter(user_name_id=difference,group_id=gid).delete()
                reduce_user.append(str(project_user.objects.get(id = difference).user_name)+"<"+str(project_user.objects.get(id=difference).name)+">")
            else:
                add_user_group = user_group()
                add_user_group.group_id = gid
                add_user_group.user_name_id = difference
                add_user_group.save()
                increase_user.append(str(project_user.objects.get(id=difference).user_name)+"<"+str(project_user.objects.get(id=difference).name)+">")
        # 更新日志
        content_dict = {'添加用户': increase_user, '移出用户': reduce_user}
        update_logs = AuthorityGroupChangeLogs()
        update_logs.group_id = gid
        update_logs.user_id = request.user.id
        update_logs.content = get_name_by_id.get_name(request.user.id) +'操作: '+ str(content_dict)
        update_logs.save()
        messages.add_message(request, messages.SUCCESS, '操作成功!')
        return HttpResponseRedirect(reverse('project_authority_group_user_list', args=[gid,]))


# 用户管理
@login_required
@check_permission
def user_manage_view(request):
    '''
    @author: Xieyz
    @note: 项目用户管理
    :return:
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            all_records = project_user.objects.filter(Q(id__icontains=search) |
                                                      Q(name__icontains=search) |
                                                      Q(email__icontains=search) |
                                                      Q(project__project__icontains=search) |
                                                 Q(user_name__icontains=search))
        else:
            all_records = project_user.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['user_name', 'is_active','name','email']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
                    sort_column = '%s' % (sort_column)
                all_records = all_records.order_by(sort_column)
        else:
            all_records = all_records.order_by('id')
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
        for list in pageinator.page(pageNumber):
            # group_list = []
            # group_name = user_group.objects.values_list(
            #     'group__group_name',flat=True).filter(user_name_id=list.id)
            # for i in group_name:
            #     group_list.append(i)
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "user_name": list.user_name if list.user_name else "",
                "name": list.name if list.name else "",
                "email": list.email if list.email else "",
                "project_name":list.project.project if list.project.project else "",
                # "group_name": group_list if group_list else "",
                "is_active": list.get_is_active_display() if list.get_is_active_display() else "",
            })
        return HttpResponse(json.dumps(response_data))
    return render(request, 'usercenter/project_user_manage.html')


@login_required
@check_permission
def project_user_add(request):
    '''
    @author: Xieyz
    @note: 项目用户添加
    :return: UserChangeForm表单
    '''
    if request.method == "POST":
        change = UserChangeForm(request.POST)
        if not request.POST.get('project'):
            messages.add_message(request, messages.ERROR, '请选择项目！')
            return render(request, 'usercenter/project_user_change.html', {'form': change})
        if change.is_valid():
            data = change.cleaned_data
            change.save()

            # 更新日志
            try:
                update_logs = UserChangeLogs()
                update_logs.user_id = project_user.objects.only('id').get(user_name=data.get('user_name'),project_id=data.get('project')).id
                update_logs.content = get_name_by_id.get_name(request.user.id) +'添加了新的用户'
                update_logs.save()
            except:
                pass
            messages.add_message(request, messages.SUCCESS, '添加用户"' + data.get('user_name') + '",添加成功!')
            return HttpResponseRedirect(reverse('user_manage'))
        else:
            messages.add_message(request, messages.ERROR, change.errors)
            return render(request, 'usercenter/project_user_change.html', {'form': change})
    else:
        form = UserChangeForm()
    return render(request, 'usercenter/project_user_change.html', locals())


@login_required
def project_user_change_status(request, id, is_active):
    try:
        project_user.objects.filter(id=id).update(is_active=is_active)
        # 更新用户日志
        display = ''
        if is_active == 1:
            display = '启用'
        elif is_active == 0:
            display = '禁用'
        update_userlogs = UserChangeLogs()
        update_userlogs.user_id = id
        update_userlogs.content = get_name_by_id.get_name(request.user.id) + '修改用户状态为' + display
        update_userlogs.save()
        return JsonResponse({'result': 'true','project_user_id':id})
    except:
        return JsonResponse({'result': 'false'})


@login_required
@check_permission
def project_user_modify(request,id):
    '''
    @author: Xieyz
    @note: 项目用户修改
    :return: UserChangeForm表单
    '''
    obj = project_user.objects.get(id=id)
    if request.method == "POST":
        change = UserChangeForm(request.POST,instance=obj)
        if not request.POST.get('project'):
            messages.add_message(request, messages.ERROR, '请选择项目！')
            return render(request, 'usercenter/project_user_change.html', {'form': change})
        if change.is_valid():
            data = change.cleaned_data

            # 更新日志
            update_logs = UserChangeLogs()
            update_logs.user_id = id
            update_logs.content = get_name_by_id.get_name(request.user.id) +'修改了用户的信息'
            change.save()
            update_logs.save()

            messages.add_message(request, messages.SUCCESS, '修改用户"' + data.get('user_name') + '"的信息,修改成功!')
            return HttpResponseRedirect(reverse('user_manage'))
        else:
            messages.add_message(request, messages.ERROR, change.errors)
            return render(request, 'usercenter/project_user_change.html', {'form': change})
    else:
        form = UserChangeForm(instance=obj)
    return render(request, 'usercenter/project_user_change.html', locals())


@login_required
@check_permission
def user_details_view(request, id):
    '''
    @author: Xieyz
    @note: 用户详情
    :param request:
    :param id: project_user表的id
    :return:
    '''
    info = project_user.objects.filter(id=id)
    log = UserChangeLogs.objects.filter(user_id=id).order_by('-datetime')
    group_info = user_group.objects.filter(user_name_id=id)
    user_role_info = user_authority.objects.filter(user_name_id=id)
    detail = {
        "list": info,
        "flow_log": log,
        "group_info": group_info,
        "user_role_info": user_role_info,
    }
    return render(request, 'usercenter/project_user_detail.html', detail)


@login_required
def get_all_user(request):
    """获取所有用户"""
    result = getAllUser()
    return JsonResponse({'result': result})


# @login_required
def wait_process_message(request):
    # 待办
    result = []

    group_sp = project_group.objects.filter(user_id=request.user.id, project__status=1, user_type__name='项目经理')
    for i in group_sp:
        result.append({'title': '立项申请 - ' + i.project.project,
                       'time': i.project.applicationtime,
                       'type': '审批',
                       'url': '/flow/project_manage/project_details/' + str(i.project_id)})

    current_group_set = Group.objects.filter(user=request.user).values_list('name', flat=True)
    if 'cto' in current_group_set:
        p1 = project.objects.filter(status=2)
        for i in p1:
            result.append({'title': '立项申请 - ' + i.project,
                           'time': i.applicationtime,
                           'type': '审批',
                           'url': '/flow/project_manage/project_details/' + str(i.id)})

    if '采购部' in current_group_set:
        p1 = project.objects.filter(status=3)
        for i in p1:
            result.append({'title': '立项申请 - ' + i.project,
                           'time': i.applicationtime,
                           'type': '审批',
                           'url': '/flow/project_manage/project_details/' + str(i.id)})

    if '财务部' in current_group_set:
        p1 = project.objects.filter(status=4)
        for i in p1:
            result.append({'title': '立项申请 - ' + i.project,
                           'time': i.applicationtime,
                           'type': '审批',
                           'url': '/flow/project_manage/project_details/' + str(i.id)})

    project_userflow_ps = project_userflow.objects.filter(status=1)
    xmjl_sp = project_group.objects.filter(user_id=request.user.id, user_type__name='项目经理')
    for i in project_userflow_ps:
        for x in xmjl_sp:
            if i.project.id == x.project_id:
                result.append({'title': '项目成员变更审批',
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/project_member_manage/details/' + str(i.id)})
    ProjectUserApplyFlow_ps = ProjectUserApplyFlow.objects.filter(status=1)
    p2 = Department.objects.filter(depart_director_id=request.user.id)
    for i in ProjectUserApplyFlow_ps:
        for x in p2:
            if i.project.id == x.project_id:
                result.append({'title': '业务用户变更审批',
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/user_apply_list/user_apply_details/'+str(i.id)})

    ywry_sp = project_group.objects.filter(user_id=request.user.id, user_type__name='运维人员')
    ProjectUserApplyFlow_ps2 = ProjectUserApplyFlow.objects.filter(status=2)
    for i in ProjectUserApplyFlow_ps2:
        for x in ywry_sp:
            if i.project.id == x.project_id:
                result.append({'title': '业务用户变更执行',
                               'time': i.applicationtime,
                               'type': '执行',
                               'url': '/flow/user_apply_list/user_apply_details/'+str(i.id)})

    authority_flow_ps = authority_flow.objects.filter(status=1)
    for i in authority_flow_ps:
        for x in p2:
            if i.project.id == x.project_id:
                result.append({'title': '业务用户权限变更审批',
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/project_authority_manage/project_authority_details/' + str(i.id)})

    authority_flow_ps2 = authority_flow.objects.filter(status=2)
    for i in authority_flow_ps2:
        for x in ywry_sp:
            if i.project.id == x.project_id:
                result.append({'title': '业务用户权限变更执行',
                               'time': i.applicationtime,
                               'type': '执行',
                               'url': '/flow/project_authority_manage/project_authority_details/' + str(i.id)})

    csry_ps = project_group.objects.filter(user_id=request.user.id, user_type__name='测试人员')
    project_releaseflow_ps = project_releaseflow.objects.filter(status=1)
    for i in project_releaseflow_ps:
        for x in csry_ps:
            if i.project.id == x.project_id:
                result.append({'title': '项目变更 - ' + i.title,
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/releaseflow_manage/releaseflow_details/' + str(i.id)})

    project_releaseflow_ps2 = project_releaseflow.objects.filter(status=2)
    for i in project_releaseflow_ps2:
        for x in xmjl_sp:
            if i.project.id == x.project_id:
                result.append({'title': '项目变更 - ' + i.title,
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/releaseflow_manage/releaseflow_details/' + str(i.id)})

    project_releaseflow_ps3 = project_releaseflow.objects.filter(status=3)
    for i in project_releaseflow_ps3:
        for x in ywry_sp:
            if i.project.id == x.project_id:
                result.append({'title': '项目变更 - ' + i.title,
                               'time': i.applicationtime,
                               'type': '执行',
                               'url': '/flow/releaseflow_manage/releaseflow_details/' + str(i.id)})

    cronflow_ps = cronflow.objects.filter(status=1)
    for i in cronflow_ps:
        for x in xmjl_sp:
            if i.project.id == x.project_id:
                result.append({'title': '计划任务变更 - ' + i.cron_time+' '+i.cron_order,
                               'time': i.applicationtime,
                               'type': '审批',
                               'url': '/flow/cronflow_manage/cronflow_details/' + str(i.id)})

    cronflow_ps2 = cronflow.objects.filter(status=2)
    for i in cronflow_ps2:
        for x in ywry_sp:
            if i.project.id == x.project_id:
                result.append({'title': '计划任务变更 - ' + i.cron_time+' '+i.cron_order,
                               'time': i.applicationtime,
                               'type': '执行',
                               'url': '/flow/cronflow_manage/cronflow_details/' + str(i.id)})

    database_app_ps = Application.objects.filter(application_status=1,is_delete=0)
    for i in database_app_ps:
        for x in xmjl_sp:
            if i.project.id == x.project_id:
                result.append({'title': '数据库变更 - ' + i.project.project + ' - ' + i.instance.instance_name + ' - ' + i.get_application_type_display(),
                               'time': i.application_time,
                               'type': '审批',
                               'url': '/database/instance/release_flow/release_detail/'+str(i.id)})

    database_app_ps2 = Application.objects.filter(application_status=2, instance__ops_user_id=request.user.id,is_delete=0)
    for i in database_app_ps2:
        result.append({'title': '数据库变更 - ' + i.project.project + ' - ' + i.instance.instance_name + ' - ' + i.get_application_type_display(),
                       'time': i.application_time,
                       'type': '审批',
                       'url': '/database/instance/release_flow/release_detail/'+str(i.id)})

    database_app_ps3 = Application.objects.filter(application_status=3, instance__ops_user_id=request.user.id,is_delete=0)
    for i in database_app_ps3:
        result.append({'title': '数据库变更 - ' + i.project.project + ' - ' + i.instance.instance_name + ' - ' + i.get_application_type_display(),
                       'time': i.application_time,
                       'type': '执行',
                       'url': '/database/instance/release_flow/release_detail/'+str(i.id)})
    result.sort(key=lambda x: x["time"],reverse=True)

    # 我的申请记录
    result2 = []
    project_app_record = project.objects.filter(applicant_id=request.user.id).order_by('-applicationtime')
    for i in project_app_record:
        result2.append({'title': i.project,
                        'url': '/flow/project_manage/project_details/' + str(i.id),
                        'type': '立项申请',
                        'app_time': i.applicationtime})
    project_userflow_app_record = project_userflow.objects.filter(applicant_id=request.user.id).order_by('-applicationtime')
    for i in project_userflow_app_record:
        result2.append({'title': '申请项目成员变更',
                        'url': '/flow/project_member_manage/details/' + str(i.id),
                        'type': '项目成员变更',
                        'app_time': i.applicationtime})
    cronflow_app_record = cronflow.objects.filter(applicant_id=request.user.id).order_by('-applicationtime')
    for i in cronflow_app_record:
        result2.append({'title': i.cron_time+' '+i.cron_order,
                        'url': '/flow/cronflow_manage/cronflow_details/' + str(i.id),
                        'type': '计划任务变更',
                        'app_time': i.applicationtime})
    project_releaseflow_app_record = project_releaseflow.objects.filter(applicant_id=request.user.id).order_by('-applicationtime')
    for i in project_releaseflow_app_record:
        result2.append({'title': i.title,
                        'url': '/flow/releaseflow_manage/releaseflow_details/' + str(i.id),
                        'type': '项目变更',
                        'app_time': i.applicationtime})
    authority_flow_app_record = authority_flow.objects.filter(applicant_id=request.user.id).order_by('-applicationtime')
    for i in authority_flow_app_record:
        result2.append({'title': '申请业务用户权限变更',
                        'url': '/flow/project_authority_manage/project_authority_details/' + str(i.id),
                        'type': '业务用户权限变更',
                        'app_time': i.applicationtime})
    user_apply_flow_app_record = ProjectUserApplyFlow.objects.filter(submitter_id=request.user.id).order_by('-applicationtime')
    for i in user_apply_flow_app_record:
        result2.append({'title': '申请业务用户变更',
                        'url': '/flow/user_apply_list/user_apply_details/'+str(i.id),
                        'type': '业务用户变更',
                        'app_time': i.applicationtime})
    database_app_record = Application.objects.filter(appliant_id=request.user.id,is_delete=0).order_by('-application_time')
    for i in database_app_record:
        result2.append({'title': i.project.project + ' - ' + i.instance.instance_name + ' - ' + i.get_application_type_display(),
                        'url': '/database/instance/release_flow/release_detail/'+str(i.id),
                        'type': '数据库变更',
                        'app_time': i.application_time})
    result2.sort(key=lambda x: x["app_time"],reverse=True)
    result2 = result2[:8]

    # 我要处理的工单
    result3 = []
    wait_process_worksheet = WorkSheet.objects.filter(status=2, operator_id = request.user.id).order_by('c_time')
    for i in wait_process_worksheet:
        result3.append({'title':i.title, 'url':'/worksheet/list/2/'+str(i.id)+'/'})
    return JsonResponse({'code': 1, 'result': result, 'result2': result2, 'result3': result3})
