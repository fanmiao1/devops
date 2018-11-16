# -*- coding: utf-8 -*-
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User, Group
from usercenter.permission import check_permission
from usercenter.build_message import build_message,send_message
from .comment import BuildComment
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from opscenter.models import cron
from database.models import Application
from .forms import *
from .compute_flow_count import *
from .get_name_by_id import get_name_by_id
import datetime
import operator
import json
from django.utils.timezone import timedelta
import os
from devops.settings import MEDIA_ROOT
from django.utils.timezone import utc
from devops import settings
from .serializers import *
from rest_framework import mixins, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class DateEncoder(json.JSONEncoder):
    '''
    重写构造json类，遇到日期特殊处理，其余的用内置
    '''
    def default(self, obj):
        try:
            if settings.USE_TZ:
                utc_dt = obj.replace(tzinfo=utc)
                obj = utc_dt.astimezone(datetime.timezone(timedelta(hours=8)))
        except:
            pass
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
             return json.JSONEncoder.default(self, obj)


'''  工作流  '''
''' 项目管理 '''

class ProjectAllList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """所有服务器列表(不分页)"""
    queryset = project.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    serializer_class = ProjectAllSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


@login_required
@check_permission
def project_manage_view(request):
    '''
    @author: Xieyz
    @note: 项目管理
    :param request:
    :return: 项目申请列表
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
            search = search.strip()
            all_records = project.objects.filter(Q(id__icontains=search) |
                                                 Q(applicant__username__icontains=search) |
                                                 Q(applicant__last_name__icontains=search[0],
                                                   applicant__first_name__icontains=search[1:]) |
                                                 Q(applicant__last_name__icontains=search[0:1],
                                                   applicant__first_name__icontains=search[2:]) |
                                                 Q(applicant__last_name__icontains=search) |
                                                 Q(applicant__first_name__icontains=search) |
                                                 Q(project__icontains=search))
            if search in '自建':
                all_records = project.objects.filter(source=1)
            elif search in '外购':
                all_records = project.objects.filter(source=0)
            elif search == '未审批':
                all_records = project.objects.filter(status=1)
            elif search == '执行中':
                all_records = project.objects.filter(status=9)
            elif search == '不通过':
                all_records = project.objects.filter(status=0)
            elif search == '项目经理审批通过':
                all_records = project.objects.filter(status=2)
            elif search == 'CTO审批通过':
                all_records = project.objects.filter(status=3)
            elif search == '采购审批通过':
                all_records = project.objects.filter(status=4)
        else:
            all_records = project.objects.all() # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'applicant', 'project', 'applicationtime', 'completiontime',
                               'status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)

                if order == 'asc':  # 如果排序是正向
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
            pageSize = 10  # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for list in pageinator.get_page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(list.applicant.id)
            except AttributeError:
                applicant = ''
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "applicant": applicant if applicant else "",
                "project": list.project if list.project else "",
                "source": list.get_source_display() if list.get_source_display() else "",
                "applicationtime": list.applicationtime if list.applicationtime else "",
                "approvaltime": list.approvaltime if list.approvaltime else "",
                "status": list.get_status_display() if list.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/project_manage.html')


@login_required
@check_permission
def project_add_view(request):
    '''
    @author: Xieyz
    @note: 项目添加
    :param request:
    :return:
    '''
    if request.method == "POST":
        project_add = ProjectForm(request.POST)
        if project_add.is_valid():
            data = project_add.cleaned_data
            project_name = data.get('project_name')
            project_name_english = data.get('project_name_english','')
            source = data.get('source')
            project_manager = data.get('project_manager')
            have_parent_project = data.get('have_parent_project',0)
            parent_project = data.get('parent_project')
            # project_group = data.get('project_group', '')
            project_desc = data.get('project_desc')
            project_status = data.get('project_status',1)
            if have_parent_project == 'True':
                if not parent_project:
                    errors = '请选择父项目!'
                    messages.add_message(request, messages.ERROR, errors)
                    return render(request, 'workflow/project_add.html', {'projectform': project_add})
            if not project_manager:
                errors = '请选择项目经理!'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/project_add.html', {'projectform': project_add})
            # 数据保存
            judge = project.objects.filter(project=project_name).exclude(status=0)
            if judge:  # 判断是否已存在该项目
                errors = '该项目已存在'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/project_add.html', {'projectform': project_add})
            else: # 如果项目不存在，执行数据保存
                projectform = project()
                projectform.applicant_id = request.user.id
                projectform.project = project_name
                projectform.project_english = project_name_english
                projectform.source = source
                projectform.have_parent_project = have_parent_project
                if have_parent_project == 'True':
                    projectform.parent_project = parent_project
                projectform.project_manager = project_manager
                projectform.group = ''
                projectform.describe = project_desc
                projectform.status = project_status
                projectform.save()

                # 添加项目经理到项目成员
                project_id = project.objects.only('id').get(project=project_name,status=project_status).id
                projectgroup = project_group()
                projectgroup.project_id = project_id
                projectgroup.user = project_manager
                projectgroup.user_type_id = Group.objects.get(name='项目经理').id
                projectgroup.save()

                # 更新日志
                update_logs = ProjectFlowLogs()
                update_logs.project_id = project_id
                update_logs.content = '项目申请：' + get_name_by_id.get_name(request.user.id) + '申请新建项目'
                update_logs.save()

                # 添加消息
                send_message(action = '项目创建', detail_id= project_id)
                messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
                return HttpResponseRedirect(reverse('project_manage'))
        else:
            messages.add_message(request, messages.ERROR, project_add.errors)
            return render(request, 'workflow/project_add.html', {'add_FormInput': project_add})
    else:
        projectform = ProjectForm()
    return render(request, 'workflow/project_add.html', {"projectform" : projectform})


@login_required
def project_delete(request,id):
    '''
    @author: Xieyz
    @note: 项目删除
    :param request:
    :return: 执行结果用字符串true/false代替
    '''
    del_judge_obj = project.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.applicant == request.user:
        project.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.applicant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def project_details_view(request, id):
    '''
    @author: Xieyz
    @note: 项目详情
    :param request:
    :return:
    '''
    if request.GET.get('comment'):
        BuildComment.project_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('project_details', args=[id]))
    po_manager = [] # 项目经理
    po_product_manager = [] # 产品经理
    po_development = [] # 开发人员
    po_test = [] # 测试人员
    po_operations = [] # 运维人员
    project_list = project.objects.filter(id = id)
    if not project_list:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('project_manage'))
    project_obj = project_group.objects.filter(project__id = id)
    for i in project_obj:
        try:
            if i.user_type.name == '项目经理':
                user_name = get_name_by_id.get_name(i.user.id)
                po_manager.append(user_name)
            elif i.user_type.name == '产品经理':
                user_name = get_name_by_id.get_name(i.user.id)
                po_product_manager.append(user_name)
            elif i.user_type.name == '开发人员':
                user_name = get_name_by_id.get_name(i.user.id)
                po_development.append(user_name)
            elif i.user_type.name == '测试人员':
                user_name = get_name_by_id.get_name(i.user.id)
                po_test.append(user_name)
            elif i.user_type.name == '运维人员':
                user_name = get_name_by_id.get_name(i.user.id)
                po_operations.append(user_name)
        except:
            continue
    flow_log = ProjectFlowLogs.objects.filter(project=id).order_by('-datetime')
    dict = {
        "list": project_list,
        "po_manager": po_manager,
        "po_product_manager": po_product_manager,
        "po_development": po_development,
        "po_test": po_test,
        "po_operations": po_operations,
        "flow_log" : flow_log,
        "comments" : ProjectApplyComment.objects.filter(project_id=id)
    }
    return(render(request, 'workflow/project_detail.html', dict))


@login_required
@check_permission
def project_approval_view(request, id, control):
    '''
    :param request: 项目审批
    :param id: project表的id
    :param control: 变量用作控制
    :return:
    '''
    approval = ''
    update_flow = project.objects.get(id=id)
    login_name = get_name_by_id.get_name(request.user.id)
    applicant_name = str(project.objects.only('applicant').get(id=id).applicant.username)
    if control == 2:
        if update_flow.project_manager.id != request.user.id:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        approval = '项目经理审批：'+ login_name + '审批通过'
        # 发送消息至cto
        send_message(action='项目创建审批', detail_id=id, adopt='通过', sector='cto')
    elif control == 3:
        judge_cto_control_variable = 0
        try:
            judge_cto_obj = Group.objects.get(name='cto').user_set.filter()
        except models.ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        for i in judge_cto_obj:
            if i.id == request.user.id:
                approval = 'CTO审批：' + login_name + '审批通过'
                judge_cto_control_variable = 1
                break
        if judge_cto_control_variable == 0:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        # 发送消息给采购部成员
        send_message(action = '项目创建审批', detail_id=id, adopt='通过', sector='采购部')
    elif control == 4:
        approval = '采购审批：' + login_name + '审批通过'
        # 发送消息给财务部成员
        send_message(action = '项目创建审批', detail_id=id, adopt='通过', sector='财务部')
    elif control == 9:
        update_flow.approvaltime = datetime.datetime.now()
        if update_flow.source == 0:
            approval = '财务审批：' + login_name + '审批通过'
        elif update_flow.source == 1:
            judge_cto_control_variable = 0
            try:

                judge_cto_obj = Group.objects.get(name='cto').user_set.filter()
            except models.ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect(request.session['login_from'])
            for i in judge_cto_obj:
                if i.id == request.user.id:
                    approval = 'CTO审批：' + login_name + '审批通过'
                    judge_cto_control_variable = 1
                    break
            if judge_cto_control_variable == 0:
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect(request.session['login_from'])
        # 发送消息
        send_message(action = '项目创建审批通过', detail_id=id)

    elif control == 0:
        if update_flow.status == 1:
            if update_flow.project_manager.id != request.user.id:
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect(request.session['login_from'])
        approval = '审批：'+ login_name +'审批不通过'
        send_message(action = '项目创建审批', detail_id=id, adopt='不通过')
        if request.GET.get('reject_comment'):
            BuildComment.project_apply_comment(id,'驳回意见: '+ request.GET.get('reject_comment'),request.user.id)
    update_flow.status = control
    update_flow.save()
    # 更新审批日志
    update_logs = ProjectFlowLogs()
    update_logs.project_id = id
    update_logs.content = approval
    update_logs.save()

    return HttpResponseRedirect('/flow/project_manage/project_details/' + str(id) + '/')


class project_details_info(object):
    '''
    项目详情：
    获取负责该项目的各个类型成员
    '''
    def __init__(self, user_id,type_name):
        self.user_id = user_id
        self.type_name = type_name

    def get_project_username(self):
        user_name = ''
        user_id_list = Group.objects.get(name=self.type_name)
        user_list = user_id_list.user_set.filter(id=self.user_id)
        for i in user_list:
            try:
                user_name = get_name_by_id.get_name(i.id)
            except AttributeError:
                user_name

        return user_name


@login_required
def delete_project_apply_comment(request,id):
    comment = ProjectApplyComment.objects.get(id=id)
    if request.user == comment.user:
        ProjectApplyComment.objects.filter(id=id).delete()
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})
''' 项目管理结束 '''


''' 项目成员变更 '''
@login_required
@check_permission
def project_member_manage_view(request):
    '''
    @author: Xieyz
    @note: 项目成员流
    :param request:
    :return: 项目成员申请列表
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        user_type_id = Group.objects.get(name='项目经理')
        if request.user.is_superuser:
            list_group = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id, user_type_id=user_type_id).values_list(
                              'project', flat=True)]
        if list_group:
            if search:  # 判断是否有搜索字
                search = '%s' % search
                search = search.strip()
                all_records = project_userflow.objects.filter((Q(id__icontains=search) |
                                                              Q(applicant__username__icontains=search) |
                                                             Q(applicant__last_name__icontains=search[0],
                                                               applicant__first_name__icontains=search[1:]) |
                                                             Q(applicant__last_name__icontains=search[0:1],
                                                               applicant__first_name__icontains=search[2:]) |
                                                              Q(applicant__last_name__icontains=search) |
                                                              Q(applicant__first_name__icontains=search) |
                                                              Q(project__project__icontains=search) |
                                                              Q(user_type__name__icontains=search) |
                                                              Q(add_user__icontains=search)) &
                                                              (Q(project_id__in=list_group) |
                                                               Q(applicant_id=request.user.id)))
                if search == '未审批':
                    all_records = project_userflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=1)
                elif search == '不通过':
                    all_records = project_userflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=0)
                elif search == '通过':
                    all_records = project_userflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=9)
            else:
                all_records = project_userflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id))  # must be wirte the line code here
        else:
            all_records = project_userflow.objects.filter(applicant_id=request.user.id)

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'applicant', 'project', 'user_type','add_user',
                               'applicationtime', 'completiontime','status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
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
        for project_member in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(project_member.applicant.id)
            except AttributeError:
                applicant = ''
            add_user_list = []
            remove_user_list = []
            try:
                if isinstance(eval(project_member.add_user)['添加成员'], dict):
                    if eval(project_member.add_user)['添加成员']:
                        for add_i in eval(project_member.add_user)['添加成员']:
                            try:
                                add_user_list.append(get_name_by_id.get_name(add_i))
                            except models.ObjectDoesNotExist:
                                continue
            except NameError:
                pass
            try:
                if isinstance(eval(project_member.add_user)['移出成员'], dict):
                    if eval(project_member.add_user)['移出成员']:
                        for remove_i in eval(project_member.add_user)['移出成员']:
                            try:
                                remove_user_list.append(get_name_by_id.get_name(remove_i))
                            except models.ObjectDoesNotExist:
                                continue
            except NameError:
                pass
            response_data['rows'].append({
                "id": project_member.id if project_member.id else "",
                "applicant": applicant if applicant else "",
                "project": project_member.project.project if project_member.project.project else "",
                "user_type": project_member.user_type.name if project_member.user_type.name else "",
                "add_user": add_user_list if add_user_list else "无",
                "remove_user": remove_user_list if remove_user_list else "无",
                "applicationtime": project_member.applicationtime if project_member.applicationtime else "",
                "execute_time": project_member.execute_time if project_member.execute_time else "",
                "status": project_member.get_status_display() if project_member.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/project_member_manage.html')


@login_required
@check_permission
def project_member_apply_view(request):
    '''
    @author: Xieyz
    @note: 项目成员申请
    :param request:
    :return:
    '''
    if request.method == "POST":
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return HttpResponseRedirect(reverse('project_member_apply'))
        add = ProjectUserForm(request.POST)
        if add.is_valid():
            # 数据获取
            data = add.cleaned_data
            project_id = data.get('project_name')
            change_user_list = request.POST.get('doublebox').split(",")
            if change_user_list == ['']:
                change_user_list = []
            user_type = data.get('project_user_type')
            desc = data.get('project_desc',)
            status = data.get('project_status',1)

            # # 判断是否重复申请(相同项目并相同成员类型,不能重复申请)
            judge_apply_list = project_userflow.objects.filter(
                project=project_id, user_type=user_type).exclude(Q(status=0) | Q(status=9))
            if judge_apply_list:
                # group_obj = Group.objects.get(id=user_type)
                messages.add_message(request, messages.ERROR,'该项目的【'+str(user_type)+'】申请还在审批中,请等待审批完成')
                return render(request, 'workflow/project_member_apply.html', {"projectform": ProjectUserForm() })

            # 申请修改前的成员列表
            old_project_user = project_group.objects.filter(
                project_id=project_id,user_type=user_type).values_list('user_id',flat=True)
            # 申请修改后的成员列表
            try:
                new_project_user = [int(i) for i in change_user_list]
            except ValueError:
                messages.add_message(request, messages.ERROR, '请选择需要添加或移出的成员')
                return render(request, 'workflow/project_member_apply.html', {"projectform": ProjectUserForm()})
            login_username = get_name_by_id.get_name(request.user.id)
            modify_project = str(project.objects.only('project').get(project=project_id,status=9).project)
            content_dict = {'申请人': login_username, '项目': modify_project,
                            '修改成员类型': user_type, '添加成员': [], '移出成员': []}
            dict_2 = {'添加成员':{}, '移出成员':{}}
            difference_list = list(set(old_project_user) ^ set(new_project_user))  # 原成员和修改后成员的差异列表
            if not difference_list:
                messages.add_message(request, messages.ERROR, '请选择需要添加或移出的成员')
                return render(request, 'workflow/project_member_apply.html', {"projectform": ProjectUserForm()})
            for difference in difference_list:
                try:
                    difference_user_obj = User.objects.get(id=difference)
                except TypeError:
                    messages.add_message(request, messages.ERROR, '请选择有效的用户')
                    return render(request, 'workflow/project_member_apply.html', {"projectform": ProjectUserForm()})
                user_name = get_name_by_id.get_name(difference)
                if difference in old_project_user:
                    content_dict['移出成员'].append(user_name)
                    dict_2['移出成员'][difference] = get_name_by_id.get_name(difference)
                else:
                    content_dict['添加成员'].append(user_name)
                    dict_2['添加成员'][difference] = get_name_by_id.get_name(difference)

            # 数据保存
            form = project_userflow()
            form.applicant_id = request.user.id
            form.project = project_id
            form.user_type = user_type
            form.add_user = dict_2
            form.describe = desc
            form.status = status
            form.save()

            # 保存日志
            project_userflow_id = project_userflow.objects.only('id').get(
                project=project_id, user_type=user_type, status=status).id
            update_logs = ProjectUserFlowLogs()
            update_logs.project_user_id = project_userflow_id
            update_logs.content = content_dict
            update_logs.save()
            # 发送消息
            send_message(action='项目成员申请', detail_id=project_userflow_id)
            messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
            return HttpResponseRedirect(reverse('project_member_manage'))
        else:
            messages.add_message(request, messages.ERROR,add.errors)
            return render(request, 'workflow/project_member_apply.html', {"projectform": ProjectUserForm()})
    else:
        projectform = ProjectUserForm()
    return render(request, 'workflow/project_member_apply.html', {"projectform" : projectform})


@login_required
def project_member_flow_delete(request, id):
    del_judge_obj = project_userflow.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.applicant == request.user:
        project_userflow.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.applicant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
def get_group_member(request,pid,gid):
    '''
    @author: Xieyz
    @note: 获取某类型的所有成员列表，和项目该类型的当前成员
    :param request:
    :param pid: 项目id
    :param gid: 成员类型id
    :return:
    '''
    user_id_list = project_group.objects.filter(project_id=pid,user_type_id=gid).values_list('user_id', flat=True)
    list1 = []
    list2_exclude = []
    for user_id in user_id_list:
        user_obj = User.objects.filter(groups__id=gid,id=user_id)
        for item in user_obj:
            # select_name = item.last_name+item.first_name if item.last_name+item.first_name else item.username
            list1.append([item.id, get_name_by_id.get_name(item.id)])
            list2_exclude.append(item.id)
    list2 = []
    all_group_user_list = Group.objects.get(id=gid).user_set.all()
    for item in all_group_user_list:
        # if item.id not in list2_exclude:
        # noselect_name = item.last_name+item.first_name if item.last_name+item.first_name else item.username
        list2.append([item.id, get_name_by_id.get_name(item.id)])
    return JsonResponse({'data1': list1,'data2':list2})


@login_required
@check_permission
def project_member_details_view(request,id):
    if request.GET.get('comment'):
        BuildComment.project_member_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('project_member_details', args=[id]))
    display = 0 # 控制是否显示审批按钮，0为不显示，不为0则显示
    project_userflow_list = project_userflow.objects.filter(id = id)
    if not project_userflow_list:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('project_member_manage'))
    usergroup = project_userflow.objects.get(id=id)
    project_manager = [get_name_by_id.get_name(id) for id in
                       project_group.objects.filter(project=usergroup.project,
                                                    user_type=Group.objects.get(name='项目经理')).values_list('user',
                                                                                                          flat=True)]
    flow_log = ProjectUserFlowLogs.objects.filter(project_user_id=id).order_by('-datetime')
    if usergroup.status == 1:
        display = usergroup.status
    dict = {
        "list": project_userflow_list,
        "display": display,
        "flow_log": flow_log,
        "comments": ProjectMemberApplyComment.objects.filter(project_userflow=id),
        "project_manager": project_manager,
    }
    return render(request, 'workflow/project_member_details.html', dict)


@login_required
@check_permission
def project_member_approval_view(request, id, control):
    '''
    :param request: 项目成员申请审批
    :param id: project_userflow表的id
    :param control: 变量用作控制
    :return:
    '''
    approval = ''
    update_userflow = project_userflow.objects.get(id=id)
    project_manager = project_group.objects.filter(project=update_userflow.project,
                                                   user_type=Group.objects.get(name='项目经理')).values_list(
        'user', flat=True)
    if control == 9:
        if update_userflow.status == 9:
            messages.add_message(request, messages.ERROR, '已经审批通过，请勿重复审批')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        if not(request.user.id in project_manager or update_userflow.project.project_manager.id == request.user.id):
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        user_list = eval(update_userflow.add_user)
        add_user_list = user_list['添加成员']
        remove_user_list = user_list['移出成员']
        project = update_userflow.project
        for add_user in add_user_list:
            try:
                update_usergroup = project_group(user_id=add_user,project=project,user_type=update_userflow.user_type)
            except:
                continue
            else:
                update_usergroup.save()
        for remove_user in remove_user_list:
            try:
                remove_usergroup = project_group.objects.filter(
                    user_id=remove_user, project=project,user_type=update_userflow.user_type).delete()
            except:
                continue
        approval = '同意'
        update_userflow.execute_time = datetime.datetime.now()
        str_update_userflow = get_name_by_id.get_name(update_userflow.applicant.id)
        str_user_type = str(update_userflow.user_type)
        str_username = get_name_by_id.get_name(request.user.id)
        str_adduser = str(update_userflow.add_user)
        update_projectflow_logs = ProjectFlowLogs()
        update_projectflow_logs.project_id = update_userflow.project_id
        update_projectflow_logs.content = str_update_userflow + '申请变更' + str_user_type + ' ' + str_adduser + '，由'+ str_username + '审批通过.'
        update_projectflow_logs.save()

        # 发送消息
        send_message(action='项目成员申请审批通过', detail_id=id)

    elif control == 0:
        if update_userflow.status == 0:
            messages.add_message(request, messages.ERROR, '已经审批不通过，请勿重复审批')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        elif update_userflow.status == 9:
            messages.add_message(request, messages.ERROR, '已经审批通过，请勿重复审批')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        if not(request.user.id in project_manager or update_userflow.project.project_manager.id == request.user.id):
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        approval = '不同意'
        if request.GET.get('reject_comment'):
            BuildComment.project_member_apply_comment(id,'驳回意见: '+ request.GET.get('reject_comment'), request.user.id)
        # 发送消息
        send_message(action='项目成员申请审批', detail_id=id, adopt='不通过')

    update_userflow.status = control
    update_userflow.save()

    update_logs = ProjectUserFlowLogs()
    update_logs.project_user_id = id
    update_logs.content = '项目负责人审批：' + get_name_by_id.get_name(request.user.id) + approval
    update_logs.save()
    return HttpResponseRedirect(reverse('project_member_details',args=[id]))


@login_required
def get_project_manager(request, pid):
    '''
    项目成员申请页面，选择完项目后，获取到项目经理
    '''
    manager = project_group.objects.filter(project__id=pid, user_type=Group.objects.get(name='项目经理'))
    list1 = []
    for item in manager:
        list1.append([item.user.id, get_name_by_id.get_name(item.user.id)])
    return JsonResponse({'data': list1})


@login_required
def get_project_user(request,pid):
    '''
    项目成员申请页面，选择完成员类型后，获取到该类型的所有成员
    '''
    group = Group.objects.get(id=pid)
    userList = group.user_set.all()
    list1 = []
    for item in userList:
        list1.append([item.id, item.username])
    return JsonResponse({'data': list1})
''' 项目成员变更结束 '''


''' 计划任务变更 '''
@login_required
@check_permission
def cronflow_manage_view(request):
    '''
    @author: Xieyz
    @note: 计划任务工作流
    :param request:
    :return: 计划任务申请记录表
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        user_type_id = Group.objects.get(name='项目经理')
        if request.user.is_superuser:
            list_group = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id, user_type_id=user_type_id).values_list(
                              'project', flat=True)]
        if list_group:
            if search:  # 判断是否有搜索字
                search = '%s' % (search)
                search = search.strip()
                all_records = cronflow.objects.filter((Q(id__icontains=search) |
                                                       Q(applicant__username__icontains=search) |
                                                       Q(applicant__last_name__icontains=search[0],
                                                         applicant__first_name__icontains=search[1:]) |
                                                       Q(applicant__last_name__icontains=search[0:1],
                                                         applicant__first_name__icontains=search[2:]) |
                                                       Q(applicant__last_name__icontains=search) |
                                                       Q(applicant__first_name__icontains=search) |
                                                       Q(project__project__icontains=search)) &
                                                      (Q(project_id__in=list_group) | Q(applicant_id=request.user.id))
                                                      )
                if search == '待审批':
                    all_records = cronflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=1)
                elif search == '不通过':
                    all_records = cronflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=0)
                elif search == '待执行':
                    all_records = cronflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=2)
                elif search == '已执行添加':
                    all_records = cronflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id), status=9)
            else:
                all_records = cronflow.objects.filter(Q(project_id__in=list_group) | Q(applicant_id=request.user.id))  # must be wirte the line code here
        else:
            all_records = cronflow.objects.filter(applicant_id=request.user.id)  # must be wirte the line code here
        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'applicant', 'project', 'applicationtime', 'completiontime',
                               'status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
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
        for cron_flow in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(cron_flow.applicant.id)
            except AttributeError:
                applicant = ''
            response_data['rows'].append({
                "id": cron_flow.id if cron_flow.id else "",
                "applicant": applicant if applicant else "",
                "project": cron_flow.project.project if cron_flow.project else "",
                "applicationtime": cron_flow.applicationtime if cron_flow.applicationtime else "",
                "execute_time": cron_flow.execute_time if cron_flow.execute_time else "",
                "status": cron_flow.get_status_display() if cron_flow.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/cronflow_manage.html')


@login_required
@check_permission
def cronflow_add_view(request):
    '''
    @author: Xieyz
    @note: 计划任务申请
    :param request:
    :return:
    '''
    if request.method == "POST":
        add = CronFlowForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return render(request, 'workflow/cronflow_add.html', {"projectform": add})
        if add.is_valid():
            # 数据获取
            data = add.cleaned_data
            project = data.get('project_name')
            env = data.get('env')
            cron_time = data.get('cron_time')
            cron_order = data.get('cron_order')
            describe = data.get('describe')
            status = data.get('status',1)

            judge_cron_list = cron.objects.filter(order=cron_order,time=cron_time,project=project,environmental=env)
            if judge_cron_list:
                errors = '该计划任务已在项目中'
                messages.add_message(request,messages.ERROR,errors)
                return render(request, 'workflow/cronflow_add.html', {"projectform": add})

            judge_apply_flow = cronflow.objects.filter(
                project=project,environmental=env,cron_time=cron_time,cron_order=cron_order).exclude(Q(status=0) | Q(status=9))
            if judge_apply_flow:
                errors = '该计划任务已在申请列表中，请勿重复申请'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/cronflow_add.html', {"projectform": add})

            # 数据保存
            form = cronflow()
            form.applicant_id = request.user.id
            form.project = project
            form.cron_time = cron_time
            form.cron_order = cron_order
            form.environmental = env
            form.describe = describe
            form.status = status
            form.save()

            # 更新日志
            cronflow_id = cronflow.objects.only('id').get(
                project=project,environmental=env,cron_time=cron_time,cron_order=cron_order,status=status).id
            update_logs = cronflow_logs()
            update_logs.cronflow_id = cronflow_id
            update_logs.content = get_name_by_id.get_name(request.user.id) + '：申请添加计划任务'
            update_logs.save()

            # 发送消息
            send_message(action='计划任务申请', detail_id=cronflow_id)
            messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
            return HttpResponseRedirect(reverse('cronflow_manage'))
        else:
            messages.add_message(request, messages.ERROR, add.errors)
            return render(request, 'workflow/cronflow_add.html', {'projectform': add})
    else:
        cronflowform = CronFlowForm()
    return render(request, 'workflow/cronflow_add.html', {"projectform" : cronflowform})


@login_required
def cronflow_delete(request,id):
    del_judge_obj = cronflow.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.applicant == request.user:
        cronflow.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.applicant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def cronflow_details_view(request,id):
    if request.GET.get('comment'):
        BuildComment.cron_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('cronflow_details', args=[id]))
    display = 0 # 控制审批按钮，0为不显示，1位显示'通过'和'取消'按钮，2为显示'执行'按钮
    cronflow_list = cronflow.objects.filter(id = id)
    if not cronflow_list:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('cronflow_manage'))
    get_cronflow_status = cronflow.objects.get(id = id)
    project_manager = [get_name_by_id.get_name(id) for id in
                       project_group.objects.filter(project=get_cronflow_status.project,
                                                    user_type=Group.objects.get(name='项目经理')).values_list('user',
                                                                                                          flat=True)]
    cronflow_log = cronflow_logs.objects.filter(cronflow = id).order_by('-datetime')
    if get_cronflow_status.status == 1:
        display = 1
    if get_cronflow_status.status == 2:
        display = 2
    dict = {
        "list": cronflow_list,
        "display": display,
        "flow_log": cronflow_log,
        "comments": CronApplyComment.objects.filter(cronflow_id=id),
        "project_manager": project_manager,
    }
    return render(request, 'workflow/cronflow_details.html', dict)


@login_required
@check_permission
def cronflow_approval_view(request,id,control):
    '''
    @author: Xieyz
    @note: 计划任务审批
    :param request:
    :param id: cronflow表的id
    :param control: 变量用作控制
    :return:
    '''
    approval_content = ''
    login_name = get_name_by_id.get_name(request.user.id)
    update_flow = cronflow.objects.get(id=id)
    project_manager = project_group.objects.filter(project=update_flow.project,
                                                   user_type=Group.objects.get(name='项目经理')).values_list(
        'user', flat=True)
    if control == 2:
        if update_flow.application_status >= 2 or update_flow.application_status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect('/flow/cronflow_manage/cronflow_details/' + str(id) + '/')

        if not(request.user.id in project_manager or update_flow.project.project_manager.id == request.user.id):
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])

        # 批准后，添加进计划任务表
        update_cron = cron(
            time=update_flow.cron_time,
            order=update_flow.cron_order,
            describe=update_flow.describe,
            project=update_flow.project,
            environmental=update_flow.environmental,
            status='running',
        )
        update_cron.save()
        approval_content = '项目经理审批：' + login_name + '同意'

        # 发送消息
        send_message(action='计划任务申请审批通过', detail_id=id)

    elif control == 0:
        if update_flow.application_status >= 2 or update_flow.application_status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect('/flow/cronflow_manage/cronflow_details/' + str(id) + '/')

        if not(request.user.id in project_manager or update_flow.project.project_manager.id == request.user.id):
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        approval_content = '项目经理审批：' + login_name + '不同意'

        if request.GET.get('reject_comment'):
            BuildComment.cron_apply_comment(id, '驳回意见: ' + request.GET.get('reject_comment'), request.user.id)

        # 发送消息
        send_message(action='计划任务申请审批', detail_id=id, adopt='不通过')

    elif control == 9:
        # 判断是否为项目指定运维人员
        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_flow.project_id,user_type__name='运维人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的运维人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('cronflow_details', args=[id]))
        update_flow.execute_time = datetime.datetime.now()
        approval_content = login_name + ' 执行完成'

        # 发送消息
        send_message(action='添加计划任务完成', detail_id=id)
        messages.add_message(request, messages.SUCCESS, '执行成功！')

    update_flow.status = control
    update_flow.save()

    # 更新日志
    update_logs = cronflow_logs()
    update_logs.cronflow_id = id
    update_logs.content = approval_content
    update_logs.save()

    return HttpResponseRedirect('/flow/cronflow_manage/cronflow_details/' + str(id) + '/')
''' 计划任务变更结束 '''





''' 项目变更 '''
@login_required
@check_permission
def releaseflow_manage_view(request):
    '''
    @author: Zengws Xieyz
    @note: 项目变更工作流
    :param request:
    :return: 项目变更申请记录表
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        groups = []
        if request.user.is_superuser:
            groups = project.objects.filter(status=9).values_list('id', flat=True)
        else:
            list_group = [entry for entry in
                          project_group.objects.filter(user_id=request.user.id).values_list('project', flat=True)]
            for group in list_group:
                project_info = project.objects.get(id=group)
                groups.append(group)
                groups.append(project.objects.get(
                    project=project_info.parent_project).id) if project_info.have_parent_project else ''
                if not project_info.have_parent_project:
                    groups.extend([entry for entry in
                                   project.objects.filter(parent_project=project_info.project).values_list('id',
                                                                                                           flat=True)])
        list_group = list(set(groups))
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            search = search.strip()
            all_records = project_releaseflow.objects.filter((Q(applicant__username__icontains=search) |
                                                             Q(applicant__last_name__icontains=search[0],
                                                               applicant__first_name__icontains=search[1:]) |
                                                             Q(applicant__last_name__icontains=search[0:1],
                                                               applicant__first_name__icontains=search[2:]) |
                                                             Q(applicant__last_name__icontains=search) |
                                                             Q(applicant__first_name__icontains=search) |
                                                             Q(project__project__icontains=search) |
                                                             Q(title__icontains=search)) &
                                                             Q(project_id__in=list_group))
            if search in '普通':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, priority=0)
            elif search in '紧急':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, priority=1)
            if search == '待审批':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=1)
            elif search == '不通过':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=0)
            elif search == '测试审批通过':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=2)
            elif search == '项目经理审批通过':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=3)
            elif search == '待发布':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=4)
            elif search == '已发布':
                all_records = project_releaseflow.objects.filter(project_id__in=list_group, status=9)
        else:
            all_records = project_releaseflow.objects.filter(project_id__in=list_group)  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['applicant', 'project', 'title', 'applicationtime', 'completiontime',
                               'status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
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
        for releaseflow in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(releaseflow.applicant.id)
            except AttributeError:
                applicant = ''
            response_data['rows'].append({
                "id": releaseflow.id if releaseflow.id else "",
                "applicant": applicant if applicant else "",
                "project": releaseflow.project.project if releaseflow.project else "",
                "priority": releaseflow.get_priority_display() if releaseflow.get_priority_display() else "",
                "title": releaseflow.title if releaseflow.title else "",
                "version": releaseflow.version if releaseflow.version else "",
                "applicationtime": releaseflow.applicationtime if releaseflow.applicationtime else "",
                "release_time": releaseflow.release_time if releaseflow.release_time else "",
                "status": releaseflow.get_status_display() if releaseflow.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/releaseflow_manage.html')


@login_required
@check_permission
def releaseflow_add_view(request):
    '''
    @author: Zengws
    @note: 项目变更申请
    :param request:
    :return:
    '''
    if request.method == "POST":
        add = ReleaseFlowForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return render(request, 'workflow/releaseflow_add.html', {"projectform": add})
        if add.is_valid():
            # 数据获取
            data = add.cleaned_data
            project_name = data.get('project_name')
            test_approval = data.get('test_approval')
            version_number = data.get('version_number')
            priority = data.get('priority')
            type = data.get('type')
            title = data.get('title')
            describe = data.get('describe')
            status = data.get('status',1)

            judge = project_releaseflow.objects.filter(
                project=project_name,version=version_number).exclude(Q(status=0) | Q(status=9))
            if judge:
                errors = '该版本的变更已在申请列表中，请勿重复申请'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/releaseflow_add.html', {"projectform": add})
            # 数据保存
            form = project_releaseflow()
            form.applicant_id = request.user.id
            form.project_id = project_name
            form.test_approval = test_approval
            form.version = version_number
            form.priority = priority
            form.type = type
            form.title = title
            form.describe = describe
            form.status = status
            form.save()

            # 更新日志
            project_release_flow_id = project_releaseflow.objects.only('id').get(
                project_id=project_name, version=version_number, status=status).id
            update_logs = releaseflow_logs()
            update_logs.releaseflow_id = project_release_flow_id
            update_logs.content = get_name_by_id.get_name(request.user.id) + '：申请项目变更'
            update_logs.save()

            #发送消息
            send_message(action='项目变更申请', detail_id=project_release_flow_id)
            messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
            return HttpResponseRedirect(reverse('releaseflow_manage'))
        else:
            messages.add_message(request,messages.ERROR, add.errors)
            return render(request, 'workflow/releaseflow_add.html', {'projectform': add})
    else:
        releaseflowform = ReleaseFlowForm()
    return render(request, 'workflow/releaseflow_add.html', {"projectform" : releaseflowform})


@login_required
def releaseflow_delete(request, id):
    del_judge_obj = project_releaseflow.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.applicant == request.user:
        project_releaseflow.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.applicant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def releaseflow_details_view(request,id):
    '''
    @author: Zengws Xieyz
    @note: 项目变更内容查看
    :param request:
    :param id:
    :return:
    '''
    if request.method == "POST":
        getdataform = ReleaseTestReportForm(request.POST)
        getdataform.is_valid()
        data = getdataform.cleaned_data
        update_test_report = project_releaseflow.objects.get(id = id)
        update_test_report.testingreport = request.POST.get('releasetestreport')
        # 判断提交人是否为项目指定测试人员
        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_test_report.project_id,user_type__name='测试人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的测试人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        if not request.POST.get('releasetestreport').strip():
            messages.add_message(request, messages.WARNING, '测试报告提交不能为空!')
            return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        update_test_report.save() # 保存测试报告

        # 更新日志
        try:
            update_logs = releaseflow_logs()
            update_logs.releaseflow_id = id
            update_logs.content = Group.objects.get(user=request.user).name + ' ' + \
                                  get_name_by_id.get_name(request.user.id) + '：提交了测试报告'
            update_logs.save()
        except:
            update_logs = releaseflow_logs()
            update_logs.releaseflow_id = id
            update_logs.content = get_name_by_id.get_name(request.user.id) + '：提交了测试报告'
            update_logs.save()

    if request.GET.get('comment'):
        BuildComment.project_release_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
    display = 0 # 控制审批按钮，0为不显示，1位显示'通过'和'取消'按钮，2为显示'执行'按钮
    releaseflow_list = project_releaseflow.objects.filter(id = id)
    if not releaseflow_list:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('releaseflow_manage'))
    get_releaseflow_status = project_releaseflow.objects.get(id = id)
    project_manager = [get_name_by_id.get_name(id) for id in
                       project_group.objects.filter(project=get_releaseflow_status.project,
                                                    user_type=Group.objects.get(name='项目经理')).values_list('user',
                                                                                                          flat=True)]
    type_list = get_releaseflow_status.type
    type_name_list = "%s%s%s" % ('「Bug修复」' if '0' in type_list else '' , ' 「功能修复」' if '1' in type_list else '' , ' 「新功能增加」' if '2' in type_list else '')
    releaseflow_log = releaseflow_logs.objects.filter(releaseflow = id).order_by('-datetime')
    if get_releaseflow_status.status == 1:
        display = 1
        remind = '提交测试报告'
    else:
        remind = '查看测试报告'
    if get_releaseflow_status.status == 2:
        display = 2
    if get_releaseflow_status.status == 4:
        display = 3
    if get_releaseflow_status.status == 0:
        display = 9

    testingreport = project_releaseflow.objects.only('testingreport').get(id=id).testingreport
    releasetestreportform = ReleaseTestReportForm(   # 测试报告表单
    initial={
        'releasetestreport': testingreport,
    })
    # releasetestreportform = ReleaseTestReportForm()
    if not testingreport and not get_releaseflow_status.enclosure:  # 检查是否提交测试报告，如果没有提交，不能测试审批,0为没有提交，1为已提交
        do_test_approval = 0
    else:
        do_test_approval = 1
    dict = {
        "list": releaseflow_list,
        "type_name_list" : type_name_list,
        "display" : display,
        "remind" : remind,
        "flow_log": releaseflow_log,
        "form": releasetestreportform,
        "do_test_approval":do_test_approval,
        "comments": ProjectReleaseApplyComment.objects.filter(project_releaseflow_id=id),
        "id": id,
        "project_manager": project_manager,
    }

    return render(request, 'workflow/releaseflow_details.html', dict)



@login_required
def handle_upload(request,id):
    '''
   @author: Xieyz
   @note: 项目变更测试报告附件上传
   :param id: 项目变更工作流ID
   :return:
   '''
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if file_obj:   # 处理附件上传到方法
            try:
                project_releaseflow_obj = project_releaseflow.objects.get(id=id)
                # 判断提交人是否为项目指定测试人员
                try:
                    appoint_user_list = project_group.objects.filter(
                        project_id=project_releaseflow_obj.project.id, user_type__name='测试人员').values_list('user_id',
                                                                                                      flat=True)
                except:
                    pass
                else:
                    if request.user.id not in appoint_user_list:
                        return JsonResponse({'status':'error','title':'ERROR','result': '上传失败! 很抱歉，您不是负责该项目的测试人员，操作被拒绝!'})

                project_name = project_releaseflow_obj.project.project
                save_file_name = str(project_name) +'-'+str(project_releaseflow_obj.version)+'-测试报告.'+((file_obj.name)[::-1].split('.')[0])[::-1]
                file_type_list = ['docx','doc','dot','dotx','docm','dotm','xml','pdf']

                # 判断文件的类型
                if ((file_obj.name)[::-1].split('.')[0])[::-1] not in file_type_list:
                    return JsonResponse({'status':'error','title':'ERROR','result': '上传失败，请上传.docx或.pdf类型的文件!'})

                accessory_dir = os.path.join(MEDIA_ROOT, 'test_report_enclosure')
                if not os.path.isdir(accessory_dir):
                    os.mkdir(accessory_dir)
                upload_file = "%s/%s" % (accessory_dir, save_file_name)
                recv_size = 0
                with open(upload_file, 'wb') as new_file:
                    for chunk in file_obj.chunks():
                        new_file.write(chunk)
                project_releaseflow_obj.enclosure = save_file_name
                project_releaseflow_obj.save()
                update_logs = releaseflow_logs()
                update_logs.releaseflow_id = id
                update_logs.content = get_name_by_id.get_name(request.user.id) + '：上传了附件'
                update_logs.save()
                # messages.add_message(request,messages.SUCCESS, '上传附件成功！')
                return JsonResponse({'status':'success','title':'SUCCESS','result':'上传成功!'})
            except Exception as e:
                return JsonResponse({'status':'error','title':'ERROR','result': '上传失败! '+ str(e)})
        else:
            return JsonResponse({'status':'error','title':'ERROR','result': '上传失败，请选择一个文件!'})
    else:
        return JsonResponse({'status':'error','title':'ERROR','result': '上传失败！'})


@login_required
@check_permission
def releaseflow_approval_view(request,id,control):
    '''
    @author: Zengws, Xieyz
    :param request: 项目变更审批
    :param id: project_releaseflow表的id
    :param control: 变量用作控制
    :return:
    '''
    approval_content = ''
    login_name = get_name_by_id.get_name(request.user.id)
    update_flow = project_releaseflow.objects.get(id=id)
    gettestreport = project_releaseflow.objects.only('testingreport').get(id=id).testingreport
    project_manager = project_group.objects.filter(project=update_flow.project,
                                                   user_type=Group.objects.get(name='项目经理')).values_list(
        'user', flat=True)
    if control == 2:
        # 判断是否为项目指定测试人员
        if update_flow.status >= 2 or update_flow.status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_flow.project_id, user_type__name='测试人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的测试人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        if gettestreport or update_flow.priority == 1 or update_flow.enclosure:
            approval_content = login_name + '：测试审批通过'
        else:
            messages.add_message(request, messages.ERROR, '请提交测试报告!')
            return HttpResponseRedirect(reverse('releaseflow_details', args=(id,)))

        # 发送消息
        send_message(action='项目变更申请审批', detail_id=id, adopt='通过', sector='项目经理')

    if control == 4:
        if update_flow.status >= 4 or update_flow.status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        if not (request.user.id in project_manager or update_flow.project.project_manager.id == request.user.id):
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        approval_content = '项目负责人审批：'+ login_name +'同意'

        # 发送消息
        send_message(action='项目变更申请审批通过', detail_id=id)

    if control == 0:
        if update_flow.status == 2:
            approval_content = login_name + '：项目负责人不同意'
            if not (request.user.id in project_manager or update_flow.project.project_manager.id == request.user.id):
                messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
                request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
                return HttpResponseRedirect(request.session['login_from'])
        if update_flow.status == 1:
            try:
                appoint_user_list = project_group.objects.filter(
                    project_id=update_flow.project_id, user_type__name='测试人员').values_list('user_id', flat=True)
            except:
                pass
            else:
                if request.user.id not in appoint_user_list:
                    messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的测试人员, 操作被拒绝!')
                    return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        if request.GET.get('reject_comment'):
            approval_content = login_name + '：驳回申请'
            BuildComment.project_release_apply_comment(
                id, '驳回意见: ' + request.GET.get('reject_comment'), request.user.id)
        # 发送消息
        send_message(action='项目变更申请审批', detail_id=id, adopt='不通过')

    if control == 9:
        # 判断是否为项目指定运维人员
        if update_flow.status >= 9 or update_flow.status == 0:
            messages.add_message(request, messages.ERROR, '已经被审批！')
            return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))

        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_flow.project_id,user_type__name='运维人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的运维人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('releaseflow_details', args=[id]))
        update_flow.release_time = datetime.datetime.now()
        approval_content = login_name + '发布完成'

        # 发送消息
        send_message(action='项目变更执行完成', detail_id=id)
        messages.add_message(request, messages.SUCCESS, '执行成功！')

    update_flow.status = control
    update_flow.save()

    # 更新审批日志
    update_logs = releaseflow_logs()
    update_logs.releaseflow_id = id
    update_logs.content = approval_content
    update_logs.save()

    return HttpResponseRedirect(reverse('releaseflow_details', args=(id,)))
''' 项目变更结束 '''


''' 项目用户变更 '''
@login_required
@check_permission
def user_apply_flow_view(request):
    '''
    @author: Xieyz
    @note: 项目用户变更
    :param request:
    :param id:
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
            search = search.strip()
            all_records = ProjectUserApplyFlow.objects.filter(Q(id__icontains=search) |
                                                              Q(project__project__icontains=search) |
                                                              Q(user_name__icontains=search) |
                                                              Q(submitter__username__icontains=search) |
                                                              Q(submitter__last_name__icontains=search[0],
                                                                submitter__first_name__icontains=search[1:]) |
                                                              Q(submitter__last_name__icontains=search[0:1],
                                                                submitter__first_name__icontains=search[2:]) |
                                                              Q(submitter__last_name__icontains=search) |
                                                              Q(submitter__first_name__icontains=search) |
                                                              Q(user_group__icontains=search) |
                                                              Q(applicant__icontains=search) |
                                                              Q(remarks__icontains=search) |
                                                              Q(department__depart_name__icontains=search) |
                                                              Q(id__icontains=search))
            if search == '禁用':
                all_records = ProjectUserApplyFlow.objects.filter(is_active=0)
            elif search == '启用':
                all_records = ProjectUserApplyFlow.objects.filter(is_active=1)
            elif search in '添加用户':
                all_records = ProjectUserApplyFlow.objects.filter(type=0)
            elif search in '修改用户':
                all_records = ProjectUserApplyFlow.objects.filter(type=1)
            elif search == '待审批':
                all_records = ProjectUserApplyFlow.objects.filter(status=1)
            elif search == '不通过':
                all_records = ProjectUserApplyFlow.objects.filter(status=0)
            elif search == '待执行':
                all_records = ProjectUserApplyFlow.objects.filter(status=2)
            elif search == '执行完成':
                all_records = ProjectUserApplyFlow.objects.filter(status=9)
        else:
            all_records = ProjectUserApplyFlow.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['project', 'submitter','department','applicant','user_name','user_group','remarks','applicationtime','is_active','type','execute_time','status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
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
        for list in pageinator.page(pageNumber):
            try:
                submitter = get_name_by_id.get_name(list.submitter.id)
            except:
                submitter = ''
            try:
                department_name = list.department.depart_name
            except:
                department_name = ''
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "project": list.project.project if list.project.project else "",
                "department": department_name if department_name else "",
                "user_name": list.user_name if list.user_name else "",
                "user_group":list.user_group if list.user_group else "",
                "applicant": list.applicant if list.applicant else "",
                "submitter": submitter if submitter else "",
                "remarks": list.remarks if list.remarks else "",
                "is_active": list.get_is_active_display() if list.get_is_active_display() else "",
                "applicationtime": list.applicationtime if list.applicationtime else "",
                "execute_time": list.execute_time if list.execute_time else "",
                "type": list.get_type_display() if list.get_type_display() else "",
                "status": list.get_status_display() if list.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/user_apply_list.html')


@login_required
@check_permission
def user_apply_view(request):
    '''
    @author: Xieyz
    @note: 用户申请
    :param request:
    :return:
    '''
    if request.method == "POST":
        add = ProjectUserApplyForm(request.POST)
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return render(request, 'workflow/user_apply.html', {'projectform': add})
        if add.is_valid():
            data = add.cleaned_data
            project_name = data.get('project_name')
            department_id = data.get('department')
            group = data.get('group')
            remarks = data.get('remarks')
            user_name = data.get('user_name')
            is_active = data.get('is_active')
            name = data.get('name')
            email = data.get('email')
            status = data.get('status',1)

            # 数据保存
            judge_in_user = project_user.objects.filter(user_name=user_name,project=project_name)
            judge_in_email = project_user.objects.filter(email=email, project=project_name)
            judge_email_in_flow = ProjectUserApplyFlow.objects.filter(
                email=email, project=project_name).exclude(Q(status=0) | Q(status=3))
            judge_in_flow = ProjectUserApplyFlow.objects.filter(
                user_name=user_name, project=project_name).exclude(Q(status=0) | Q(status=3))
            if judge_in_user:
                errors = '该用户名已存在'
                messages.add_message(request,messages.ERROR,errors)
                return render(request, 'workflow/user_apply.html', {'projectform': add})
            elif judge_in_flow:  # 判断是否已存在
                errors = '该用户名已存在申请列表中, 审批中'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/user_apply.html', {'projectform': add})
            elif judge_in_email:
                errors = '该邮箱已存在'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/user_apply.html', {'projectform': add})
            if judge_email_in_flow:
                errors = '该邮箱已存在'
                messages.add_message(request, messages.ERROR, errors)
                return render(request, 'workflow/user_apply.html', {'projectform': add})
            else: # 如果用户不存在，执行数据保存
                group_dict = {'加入组': {group:authority_group.objects.only('group_name').get(id=group).group_name}}
                add_data_flow = ProjectUserApplyFlow()
                add_data_flow.project = project_name
                add_data_flow.department_id = department_id
                add_data_flow.user_group = group_dict
                add_data_flow.submitter_id = request.user.id
                add_data_flow.applicant = name
                add_data_flow.user_name = user_name
                add_data_flow.name = name
                add_data_flow.email = email
                add_data_flow.remarks = remarks
                add_data_flow.is_active = is_active
                add_data_flow.type = 0  # 0为添加用户，1为修改用户
                add_data_flow.status = status
                add_data_flow.save()

                # 更新日志
                project_user_apply_id = ProjectUserApplyFlow.objects.only('id').get(
                    user_name=user_name,project=project_name,status=status).id
                update_logs = ProjectUserApplyLogs()
                update_logs.user_apply_flow_id = project_user_apply_id
                update_logs.content = '用户申请：' + get_name_by_id.get_name(request.user.id) + '申请提交新建用户，申请用户名：' + user_name
                update_logs.save()

                # 发送消息
                send_message(action = '项目用户变更申请', detail_id = project_user_apply_id)
                messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
                return HttpResponseRedirect(reverse('user_apply_list'))
        else:
            messages.add_message(request, messages.ERROR, add.errors)
            return render(request, 'workflow/user_apply.html', {'projectform': add})
    else:
        projectform = ProjectUserApplyForm()
    return render(request, 'workflow/user_apply.html', {"projectform" : projectform})


@login_required
def user_apply_flow_delete(request,id):
    del_judge_obj = ProjectUserApplyFlow.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.submitter == request.user:
        ProjectUserApplyFlow.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.submitter != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:

            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def user_apply_details_view(request, id):
    '''
    @author: Xieyz
    @note: 项目用户申请详情
    :param request:
    :param id: ProjectUserApplyFlow表的id
    :return:
    '''
    if request.GET.get('comment'):
        BuildComment.project_user_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('user_apply_details', args=[id]))
    info = ProjectUserApplyFlow.objects.filter(id=id)
    if not info:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('user_apply_list'))
    log = ProjectUserApplyLogs.objects.filter(user_apply_flow_id=id).order_by('-datetime')

    detail = {
        "list": info,
        "flow_log": log,
        "comments": ProjectUserApplyComment.objects.filter(user_apply_flow_id=id),
    }
    return render(request, 'workflow/user_apply_detail.html', detail)


@login_required
@check_permission
def user_apply_approval_view(request,id,control):
    '''
    @author: Xieyz
    :param request: 项目用户申请审批
    :param id: ProjectUserApplyFlow表的id
    :param control: 变量用作控制
    :return:
    '''
    approval_content = ''
    login_name = get_name_by_id.get_name(request.user.id)
    update_flow = ProjectUserApplyFlow.objects.get(id=id)

    if control == 2:
        if update_flow.department.depart_director_id != request.user.id:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        update_flow.status = 2
        update_flow.save()
        approval_content = '审批：'+ login_name +'同意'

        send_message(action='项目用户变更申请审批通过', detail_id=id)

    if control == 0:
        if update_flow.department.depart_director_id != request.user.id:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        update_flow.status = 0
        update_flow.save()
        approval_content = '审批：'+ login_name + '不同意'

        if request.GET.get('reject_comment'):
            BuildComment.project_user_apply_comment(
                id, '驳回意见: ' + request.GET.get('reject_comment'), request.user.id)

        send_message(action='项目用户变更申请审批', detail_id=id, adopt='不通过')

    if control == 3:
        # 判断是否为项目指定运维人员
        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_flow.project_id,user_type__name='运维人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的运维人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('user_apply_details', args=[id]))
        if update_flow.type == 0:   # type为0表示添加用户
            approval_content = login_name + '执行添加用户'
            try:
                # 添加用户
                add_user = project_user()
                add_user.user_name = update_flow.user_name
                add_user.is_active = update_flow.is_active
                add_user.project = update_flow.project
                add_user.name = update_flow.name
                add_user.email = update_flow.email
                add_user.save()

            except:
                update_flow.status = 0
                update_flow.save()
                errors = '无法执行, 原因: 该用户已存在, 不能重复添加'
                update_logs = ProjectUserApplyLogs()
                update_logs.user_apply_flow_id = id
                update_logs.content = login_name +":"+ errors
                update_logs.save()
                messages.add_message(request, messages.ERROR, errors)
                return HttpResponseRedirect(reverse('user_apply_list'))

            # 更新用户日志
            get_user_id = project_user.objects.only('id').get(user_name=update_flow.user_name,
                                                              project=update_flow.project).id
            update_userlogs = UserChangeLogs()
            update_userlogs.user_id = get_user_id
            update_userlogs.content = str(update_flow.applicant) + '申请添加用户，由' +\
                                      str(update_flow.submitter) + \
                                      '提交，' + login_name + '执行添加'
            update_userlogs.save()

            # 添加组
            for key in eval(update_flow.user_group)['加入组']:
                add_group = user_group()
                add_group.user_name_id = project_user.objects.only('id').get(
                    user_name=update_flow.user_name,project=update_flow.project).id
                add_group.group_id = key
                add_group.save()

            # 发送消息
            send_message(action='项目用户变更完成', detail_id=id)

        if update_flow.type == 1:   # type为1表示修改用户
            approval_content = login_name + '执行修改用户'

            # 更新用户表
            update_user = project_user.objects.get(user_name=update_flow.user_name,project=update_flow.project)
            update_user.is_active = update_flow.is_active
            update_user.save()

            # 更新用户日志
            get_user_id = project_user.objects.only('id').get(user_name=update_flow.user_name,
                                                              project=update_flow.project).id
            update_userlogs = UserChangeLogs()
            update_userlogs.user_id = get_user_id
            update_userlogs.content = str(update_flow.applicant) + '申请修改用户，由' + \
                                      login_name + '执行修改'
            update_userlogs.save()

            # 更新组表
            add_dict = eval(update_flow.user_group)['加入组']
            if add_dict:   # 如果有申请加入组
                for key in add_dict:
                    user_group.objects.create(user_name_id=update_user.id, group_id=key)
            del_dict = eval(update_flow.user_group)['移出组']
            if del_dict:  # 如果有申请移出组
                for key in del_dict:
                    user_group.objects.filter(user_name_id=update_user.id, group_id=key).delete()

        # 更新状态
        update_flow.status = 3
        update_flow.execute_time = datetime.datetime.now()
        update_flow.save()
        messages.add_message(request, messages.SUCCESS, '执行成功！')
    # 更新审批日志
    update_logs = ProjectUserApplyLogs()
    update_logs.user_apply_flow_id = id
    update_logs.content = approval_content
    update_logs.save()

    return HttpResponseRedirect(reverse('user_apply_details',args=[id]))


@login_required
@check_permission
def user_modify_apply_view(request):
    '''
    @author: Xieyz
    @note: 申请修改用户
    :param request:
    :return:
    '''
    if request.method == "POST":
        if not request.POST.get('project_name'):
            messages.add_message(request, messages.ERROR,'请选择项目!')
            return HttpResponseRedirect(reverse('user_modify_apply'))
        add = ProjectUserModifyForm(request.POST)
        add.is_valid()
        data = add.cleaned_data
        project_name = data.get('project_name')
        department_id = data.get('department')
        user_name = data.get('user_name')
        applicant = data.get('applicant')
        group_data = request.POST.get('doublebox').split(",")
        if group_data == ['']:
            group_data = []
        remarks = data.get('remarks')
        is_active = data.get('is_active')
        user_name = user_name.strip()
        if not department_id:
            messages.add_message(request, messages.ERROR, '请选择部门')
            return HttpResponseRedirect(reverse('user_modify_apply'))

        old_group_list = user_group.objects.filter(
        group__project=project_name,user_name__user_name=user_name).values_list('group_id', flat=True)
        try:
            new_group_list = [int(i) for i in group_data]
        except ValueError:
            messages.add_message(request, messages.ERROR, '请选择有效的分组!')
            return HttpResponseRedirect(reverse('user_modify_apply'))

        content_dict = {'加入组':{},'移出组':{}}
        difference_list = list(set(old_group_list) ^ set(new_group_list))
        project_user_status = project_user.objects.only('is_active').get(project=project_name,user_name=user_name)
        if not difference_list and project_user_status.is_active == int(is_active):
            messages.add_message(request, messages.ERROR, '未作出任何改变, 请选择分组或者修改用户状态!')
            return HttpResponseRedirect(reverse('user_modify_apply'))
        for difference in difference_list:
            difference_obj = authority_group.objects.get(id=difference)
            if difference in old_group_list:
                content_dict['移出组'][difference] = difference_obj.group_name
            else:
                content_dict['加入组'][difference] = difference_obj.group_name

        # 数据保存
        judge_user = project_user.objects.filter(user_name=user_name,project=project_name)
        judge_in_flow = ProjectUserApplyFlow.objects.filter(user_name=user_name,project=project_name).exclude(Q(status=0)|Q(status=3))
        if not judge_user:
            errors = '该用户不存在'
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('user_modify_apply'))
        elif judge_in_flow:  # 判断是否已存在
            errors = '该用户名已存在申请列表中, 状态为审批中'
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('user_modify_apply'))
        else:
            add_data_flow = ProjectUserApplyFlow()
            add_data_flow.project = project_name
            add_data_flow.department_id = department_id
            add_data_flow.user_group = content_dict
            add_data_flow.submitter_id = request.user.id
            add_data_flow.applicant = applicant
            add_data_flow.user_name = user_name
            add_data_flow.remarks = remarks
            add_data_flow.is_active = is_active
            add_data_flow.type = 1  # 0为添加用户，1为修改用户
            add_data_flow.status = 1
            add_data_flow.save()

            # 更新日志
            project_user_apply_id = ProjectUserApplyFlow.objects.only('id').get(user_name=user_name,project=project_name,status=1).id
            update_logs = ProjectUserApplyLogs()
            update_logs.user_apply_flow_id = project_user_apply_id
            update_logs.content = get_name_by_id.get_name(request.user.id) + '申请修改用户：' + user_name
            update_logs.save()

            send_message(action='项目用户变更申请', detail_id=project_user_apply_id)
            messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
            return HttpResponseRedirect(reverse('user_apply_list'))
    else:
        projectform = ProjectUserModifyForm()
    return render(request, 'workflow/user_modify_apply.html', {"projectform" : projectform})


@login_required
def user_modify_apply_check_user(request,project_id,user):
    user = user.strip()
    try:
        user_obj = project_user.objects.get(user_name=user,project_id=project_id)
    except models.ObjectDoesNotExist:
        return JsonResponse({'data3': ['false']})
    if user_obj:
        group_id_list = user_group.objects.filter(
            group__project=project_id,user_name_id=user_obj.id).values_list('group_id', flat=True)
        list1 = []
        list2_exclude = []
        for user_group_id in group_id_list:
            user_group_obj = authority_group.objects.filter(id=user_group_id)
            for item in user_group_obj:
                list1.append([item.id, item.group_name])
                list2_exclude.append(item.id)
        list2 = []
        group_list = authority_group.objects.filter(project_id=project_id)
        for item in group_list:
            # if item.id not in list2_exclude:
            list2.append([item.id, item.group_name])
        list3 = []
        list3.append(user_obj.is_active)
        return JsonResponse({'data1': list1,'data2': list2,'data3':list3})
    else:
        return JsonResponse({'data3': ['false']})
''' 项目用户变更结束 '''


''' 项目用户权限变更 '''
@login_required
@check_permission
def project_authority_manage_view(request,id = 0):
    '''
    @author: Xieyz
    @note: 项目权限管理
    :param request:
    :return: 项目权限管理列表
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
            search = search.strip()
            all_records = authority_flow.objects.filter(Q(applicant__username__icontains=search) |
                                                        Q(applicant__last_name__icontains=search[0],
                                                          applicant__first_name__icontains=search[1:]) |
                                                        Q(applicant__last_name__icontains=search[0:1],
                                                          applicant__first_name__icontains=search[2:]) |
                                                        Q(applicant__last_name__icontains=search) |
                                                        Q(applicant__first_name__icontains=search) |
                                                        Q(project__project__icontains=search) |
                                                        Q(modify_user__user_name__icontains=search) |
                                                        Q(department__depart_name__icontains=search))

            if search == '待审批':
                all_records = ProjectUserApplyFlow.objects.filter(status=1)
            elif search == '不通过':
                all_records = ProjectUserApplyFlow.objects.filter(status=0)
            elif search == '待执行':
                all_records = ProjectUserApplyFlow.objects.filter(status=2)
            elif search == '权限变更完成':
                all_records = ProjectUserApplyFlow.objects.filter(status=3)
        else:
            all_records = authority_flow.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['applicant', 'project','department','modify_user','applicationtime', 'execute_time',
                               'status']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':  # 如果排序是反向
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
        for list in pageinator.page(pageNumber):
            try:
                applicant = get_name_by_id.get_name(list.applicant.id)
            except AttributeError:
                applicant = ''
            try:
                department_name = list.department.depart_name
            except:
                department_name = ''
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "applicant": applicant if applicant else "",
                "project": list.project.project if list.project else "",
                "department": department_name if department_name else "",
                "modify_user": list.modify_user.user_name if list.modify_user.user_name else "",
                "applicationtime": list.applicationtime if list.applicationtime else "",
                "execute_time": list.execute_time if list.execute_time else "",
                "status": list.get_status_display() if list.get_status_display() else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'workflow/project_authority_manage.html')


@login_required
def project_role_delete(request, id):
    del_judge_obj = authority_flow.objects.get(id=id)
    if del_judge_obj.status == 1 and del_judge_obj.applicant == request.user:
        authority_flow.objects.filter(id=id).delete()
        return JsonResponse({'result': 'true'})
    else:
        if del_judge_obj.status != 1:
            return JsonResponse({'result': '此状态不可删除！'})
        elif del_judge_obj.applicant != request.user:
            return JsonResponse({'result': '您没有权限删除这条记录！'})
        else:
            return JsonResponse({'result': '删除失败'})


@login_required
@check_permission
def project_authority_flow_add_view(request):
    '''
    @author: Xieyz
    @note: 项目用户权限申请
    :param request:
    :return:
    '''
    if request.method == "POST":
        add = ProjectAuthorityForm(request.POST)
        # 数据获取
        add.is_valid()
        data = add.cleaned_data
        project = data.get('project_name')
        department_id = data.get('department')
        modify_user = data.get('user')
        modify_authority_list = request.POST.get('doublebox').split(",")
        if modify_authority_list == ['']:
            modify_authority_list = []
        describe = data.get('describe')
        status = data.get('project_status',1)

        if not department_id or not modify_user:
            errors = '申请信息未填写完整!'
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('project_authority_flow_add'))

        judge = authority_flow.objects.filter(project=project,modify_user=modify_user).exclude(Q(status=0)|Q(status=3))
        if judge:
            errors = '该用户已申请权限修改，状态为未审批'
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('project_authority_flow_add'))

        # 数据保存
        old_authority = user_authority.objects.filter(user_name__id=modify_user).values_list('authority_name_id',
                                                                                             flat=True)
        new_authority = [int(i) for i in modify_authority_list]

        if not list(set(old_authority) ^ set(new_authority)):
            errors = '未作出任何修改,请选择角色!'
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('project_authority_flow_add'))

        form = authority_flow()
        form.applicant_id = request.user.id
        form.project = project
        form.department_id = department_id
        form.modify_user_id = modify_user
        form.old_authority = list(old_authority)
        form.new_authority = new_authority
        form.describe = describe
        form.status = status
        form.save()

        # 更新日志
        authority_flow_id = authority_flow.objects.only('id').get(project=project,modify_user=modify_user,status=status).id
        login_username = get_name_by_id.get_name(request.user.id)
        modify_username = str(project_user.objects.only('user_name').get(id=modify_user).user_name)
        content_dict = {'申请人':login_username, '修改用户':modify_username, '增加权限': [], '删除权限': []}
        difference_list = list(set(old_authority) ^ set(new_authority)) # 原权限和修改后权限的差异列表
        for difference in difference_list:
            authorityname = authority.objects.only('authority_name').get(id=difference).authority_name
            if difference in old_authority:
                content_dict['删除权限'].append(authorityname)
            else:
                content_dict['增加权限'].append(authorityname)
        update_logs = authorityflow_logs()
        update_logs.authority_flow_id = authority_flow_id
        update_logs.content = content_dict
        update_logs.save()

        # 发送消息
        send_message(action = '项目用户权限变更申请', detail_id = authority_flow_id)
        messages.add_message(request, messages.SUCCESS, '您的申请已提交, 等待审批')
        return HttpResponseRedirect(reverse('project_authority_manage'))
    else:
        projectform = ProjectAuthorityForm()
    return render(request, 'workflow/project_authority_flow_add.html', {"projectform" : projectform})


@login_required
@check_permission
def project_authority_details_view(request,id):
    '''
    @author: Xieyz
    @note: 项目用户权限申请详情
    :param request:
    :param id:
    :return:
    '''
    if request.GET.get('comment'):
        BuildComment.project_user_authority_apply_comment(id, request.GET.get('comment'), request.user.id)
        return HttpResponseRedirect(reverse('project_authority_details', args=[id]))
    authority_info = authority_flow.objects.filter(id=id)
    if not authority_info:
        errors = '此记录不存在,或已被删除'
        messages.add_message(request,messages.ERROR,errors)
        return HttpResponseRedirect(reverse('project_authority_manage'))
    log = authorityflow_logs.objects.filter(authority_flow_id=id).order_by('-datetime')

    reduce_authority = []
    increase_authority = []
    new_authority = []
    get_authority = authority_flow.objects.get(id=id)
    difference_list = list(set(eval(get_authority.old_authority)) ^ set(eval(get_authority.new_authority)))  # 原权限和修改后权限的差异列表
    for difference in difference_list:
        authorityname = authority.objects.only('authority_name').get(id=difference).authority_name
        if difference in eval(get_authority.old_authority):
            reduce_authority.append(authorityname)
        else:
            increase_authority.append(authorityname)

    for auth_id in eval(get_authority.new_authority):
        new_authority.append(authority.objects.only('authority_name').get(id=auth_id).authority_name)

    instance_detail = {
        "list": authority_info,
        "flow_log": log,
        "reduce_authority" : reduce_authority,
        "increase_authority": increase_authority,
        "new_authority": new_authority,
        "comments": ProjectUserAuthorityApplyComment.objects.filter(authority_flow_id=id),
    }
    return render(request, 'workflow/project_authority_flow_details.html', instance_detail)


@login_required
@check_permission
def project_authority_approval_view(request, id, control):
    '''
    @author: Xieyz
    @note: 项目用户权限变更审批
    :param request:
    :param id: authority_flow表的id
    :param control: 变量用作控制
    :return:
    '''
    approval_content = ''
    login_name = get_name_by_id.get_name(request.user.id)
    update_flow = authority_flow.objects.get(id=id)

    if control == 0:
        if update_flow.department.depart_director_id != request.user.id:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        if request.GET.get('reject_comment'):
            BuildComment.project_user_authority_apply_comment(id,'驳回意见: '+ request.GET.get('reject_comment'),request.user.id)
        approval_content = '审批：' + login_name + '不同意'

        # 发送消息
        send_message(action = '项目用户权限变更申请审批', adopt = '不通过', detail_id = id)

    if control == 2:
        if update_flow.department.depart_director_id != request.user.id:
            messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(request.session['login_from'])
        approval_content = '部门负责人审批：' + login_name + '同意'

        # 发送消息
        send_message(action = '项目用户权限变更申请审批通过', detail_id = id)

    if control == 3:
        # 判断是否为项目指定运维人员
        try:
            appoint_user_list = project_group.objects.filter(
                project_id=update_flow.project_id,user_type__name='运维人员').values_list('user_id', flat=True)
        except:
            pass
        else:
            if request.user.id not in appoint_user_list:
                messages.add_message(request, messages.ERROR, '很抱歉, 您不是负责该项目的运维人员, 操作被拒绝!')
                return HttpResponseRedirect(reverse('project_authority_details', args=[id]))
        get_authority = authority_flow.objects.get(id=id)
        difference_list = list(
            set(eval(get_authority.old_authority)) ^ set(eval(get_authority.new_authority)))  # 原权限和修改后权限的差异列表
        for difference in difference_list:
            if difference in eval(get_authority.old_authority):
                user_authority.objects.filter(authority_name_id=difference,user_name_id=get_authority.modify_user.id).delete()
            else:
                add_user_authority = user_authority()
                add_user_authority.authority_name_id = difference
                add_user_authority.user_name_id = get_authority.modify_user.id
                add_user_authority.save()

        approval_content = login_name + '执行权限变更完成'
        update_flow.execute_time = datetime.datetime.now()

        # 发送消息
        send_message(action='项目用户权限变更完成', detail_id=id)
        messages.add_message(request, messages.SUCCESS, '执行成功！')
    # 更新审批日志
    update_flow.status = control
    update_flow.save()
    update_logs = authorityflow_logs()
    update_logs.authority_flow_id = id
    update_logs.content = approval_content
    update_logs.save()
    return HttpResponseRedirect('/flow/project_authority_manage/project_authority_details/' + str(id) + '/')


@login_required
def get_group(request,pid):
    '''
    @author: Xieyz
    @note: 项目用户权限申请，选择完项目后，获取该项目的所有组
    '''
    group_list = authority_group.objects.filter(project__id=pid)
    list1 = []  # 获取组
    for item in group_list:
        list1.append([item.id, item.group_name])

    department_obj = Department.objects.filter(project__id=pid)
    list2 = []  # 获取部门
    for item in department_obj:
        list2.append([item.id, item.depart_name])

    return JsonResponse({'data': list1,'data2': list2})


@login_required
def get_user(request,pid):
    '''
    @author: Xieyz
    @note: 项目用户权限申请，选择完组后，获取该项目的所有用户
    '''
    user_id_list = user_group.objects.filter(group__id=pid).values_list('user_name_id', flat=True)
    list1 = []
    for user_id in user_id_list:
        userlist = project_user.objects.filter(id = user_id)
        for item in userlist:
            list1.append([item.id, item.user_name])
    return JsonResponse({'data': list1})


@login_required
def get_user_authority(request,pid):
    '''
    @author: Xieyz
    @note: 获取所有权限列表，和用户的当前权限
    :param request:
    :param pid: 用户id
    :return:
    '''
    authority_id_list = user_authority.objects.filter(user_name__id=pid).values_list('authority_name_id', flat=True)
    list1 = []
    for user_authority_id in authority_id_list:
        user_authority_list = authority.objects.filter(id=user_authority_id)
        for item in user_authority_list:
            list1.append([item.id, item.authority_name])
    list2 = []
    list2_exclude = []
    for i in list1:
        list2_exclude.append(i[0])
    authority_list = authority.objects.filter(project_name = project_user.objects.only('project_id').get(id=pid).project_id)
    for item in authority_list:
        # if item.id not in list2_exclude:
        list2.append([item.id, item.authority_name])
    return JsonResponse({'data1': list1,'data2':list2})
''' 项目用户权限变更结束 '''


'''项目角色管理'''
@login_required
@check_permission
def role_manage_view(request,id = 0):
    '''
    @author: Xieyz
    @note: 角色列表视图
    :param request:
    :return: 角色列表
    '''
    if id != 0:
        authority.objects.filter(id=id).delete()
        messages.add_message(request, messages.Success,'删除角色成功！')
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            search = search.strip()
            all_records = authority.objects.filter(Q(id__icontains=search) |
                                                 Q(authority_name__icontains=search) |
                                                 Q(project_name__project__icontains=search))
        else:
            all_records = authority.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['authority_name', 'project_name']:
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':
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
            pageSize = 15  # 默认是每页10行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_records_count, 'rows': []}
        for list in pageinator.page(pageNumber):
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "authority_name": list.authority_name if list.authority_name else "",
                "project_name": list.project_name.project if list.project_name.project else "",
            })
        return HttpResponse(json.dumps(response_data))
    return render(request, 'usercenter/role_manage.html')


@login_required
@check_permission
def role_add_view(request):
    '''
     @author: Xieyz
     @note: 添加角色
     :param request:
     :return:
     '''
    if request.method == "POST":
        add = RoleAddForm(request.POST)
        if not request.POST.get('project_name'):
            errors = '请选择项目！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'usercenter/role_add.html', {'projectform': add})
        # 数据获取
        if add.is_valid():
            data = add.cleaned_data
            role_name = data.get('role_name')
            project_name = data.get('project_name')
            modify_module_list = request.POST.getlist('doublebox')

            judge = authority.objects.filter(authority_name=role_name,project_name=project_name)
            if judge:
                errors = '角色名已存在'
                messages.add_message(request, messages.SUCCESS, errors)
                return render(request, 'usercenter/role_add.html', {'projectform': add})

            # 数据保存
            module_list = [int(i) for i in modify_module_list]
            module_name = []

            # 更新角色表
            form = authority()
            form.authority_name = role_name
            form.project_name = project_name
            form.save()

            if module_list:
                # 更新角色和权限的关系表
                for module_id in module_list:
                    authority_module_add = authority_module()
                    authority_module_add.authority_id = authority.objects.only('id').get(authority_name=role_name,project_name=project_name).id
                    authority_module_add.module_id = module_id
                    authority_module_add.save()

                    module_name.append(Module.objects.only('module_name').get(id=module_id).module_name)

            # 更新日志
            update_logs = AuthorityChangeLogs()
            update_logs.authority_id = authority.objects.only('id').get(authority_name=role_name,project_name=project_name).id
            update_logs.content = get_name_by_id.get_name(request.user.id) + '新增了角色'+role_name+', 包含权限:'+ str(module_name)
            update_logs.save()
            messages.add_message(request, messages.SUCCESS, '添加角色成功！')
            return HttpResponseRedirect(reverse('role_manage'))
        else:
            messages.add_message(request,messages.ERROR,add.errors)
            return render(request, 'usercenter/role_add.html', {"projectform": add})
    else:
        form = RoleAddForm()
    return render(request, 'usercenter/role_add.html', {"projectform": form})


@login_required
@check_permission
def role_module_list_view(request, id = 0):
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
        search = request.POST.get('search')
        all_records = authority_module.objects.filter(authority_id=id)
        all_records = all_records.order_by('id')
        # if search:
        #     all_records_count = Module.objects.filter(
        #         Q(id__icontains=search) | Q(module_name__icontains=search) | Q(
        #             module_url__icontains=search)).values_list('id', flat=True).count()
        # else:
        #     all_records_count = all_records.count()
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
            module_list = Module.objects.get(id=list.module_id)
            # if search:
            #     search = '%s' % (search)
            #     search_moduleid_list = Module.objects.filter(
            #         Q(id__icontains=search) | Q(module_name__icontains=search) | Q(
            #             module_url__icontains=search)).values_list('id', flat=True)
            #     if module_list.id in search_moduleid_list:
            #         response_data['rows'].append({
            #             "id": module_list.id if module_list.id else "",
            #             "module_name": module_list.module_name if module_list.module_name else "",
            #             "module_url": module_list.module_url if module_list.module_url else "",
            #         })
            # else:
            #     response_data['rows'].append({
            #         "id": module_list.id if module_list.id else "",
            #         "module_name": module_list.module_name if module_list.module_name else "",
            #         "module_url": module_list.module_url if module_list.module_url else "",
            #     })
            response_data['rows'].append({
                "id": module_list.id if module_list.id else "",
                "module_name": module_list.module_name if module_list.module_name else "",
                "module_url": module_list.module_url if module_list.module_url else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    log = AuthorityChangeLogs.objects.filter(authority_id=id).order_by('-datetime')
    return render(request, 'usercenter/role_module_list.html', {"id":id,"flow_log":log})


@login_required
@check_permission
def role_module_modify_view(request,id):
    '''
     @author: Xieyz
     @note: 角色包含权限修改
     :param request:
     :return:
     '''
    if request.method == "POST":
        # 数据获取
        modify_module_list = request.POST.getlist('doublebox')

        # 数据保存
        reduce_module = []
        increase_module = []
        old_module = authority_module.objects.filter(authority__id=id).values_list('module_id', flat=True)
        new_module = [int(i) for i in modify_module_list]
        old_role_name = authority.objects.only('authority_name').get(id=id).authority_name
        new_role_name = request.POST['role_name']
        authority.objects.filter(id=id).update(authority_name=new_role_name)

        difference_list = list(set(old_module) ^ set(new_module))  # 原权限和修改后权限的差异列表
        for difference in difference_list:  # 循环差异列表，difference是module_id
            if difference in old_module:  # 如果module_id在修改前的authority_module关系表里面，表示authority中删除了这个module
                authority_module.objects.filter(module_id=difference,authority_id=id).delete()  # 执行删除authority_module关系表的记录
                reduce_module.append(Module.objects.get(id = difference).module_name)
            else:   # 如果module_id不在修改前的authority_module关系表里面，表示authority新增了一个module
                add_authority_module = authority_module()   # 执行新增一条authority_module关系表的记录
                add_authority_module.authority_id = id
                add_authority_module.module_id = difference
                add_authority_module.save()
                increase_module.append(Module.objects.get(id=difference).module_name)

        # 更新日志
        authority_li = authority.objects.get(id=id)
        update_logs = AuthorityChangeLogs()
        update_logs.authority_id = id
        update_logs.content = get_name_by_id.get_name(request.user.id) + '修改了角色，由：'+ old_role_name +'变更为：' + new_role_name +' ,增加了权限:'+ str(increase_module) + ', 删除了权限:' + str(reduce_module)
        update_logs.save()
        messages.add_message(request, messages.SUCCESS, '修改成功！')
        return HttpResponseRedirect(reverse('role_manage'))
    else:
        old_project = authority.objects.only('project_name').get(id=id).project_name.project
        old_role_name = authority.objects.only('authority_name').get(id=id).authority_name
        form = RoleModuleModifyForm(
            initial={
                "project":old_project,
                "role_name": old_role_name,
            }
        )
    return render(request, 'usercenter/role_module_modify.html', {"projectform": form,"id":id})


@login_required
def get_role_module(request,id):
    '''
    @author: Xieyz
    @note: 获取所有权限列表，和角色的当前权限
    :param request:
    :param pid: 用户id
    :return:
    '''
    module_id_list = authority_module.objects.filter(authority__id=id).values_list('module_id', flat=True)
    list1 = []
    for role_module_id in module_id_list:
        role_module_list = Module.objects.filter(id=role_module_id)
        for item in role_module_list:
            list1.append([item.id, item.module_name])

    list2 = []
    list2_exclude = []
    for i in list1:
        list2_exclude.append(i[0])
    module_list = Module.objects.filter(project = authority.objects.only('project_name_id').get(id=id).project_name_id)
    for item in module_list:
        if item.id not in list2_exclude:
            list2.append([item.id, item.module_name])
    return JsonResponse({'data1': list1,'data2':list2})
'''项目角色管理结束'''


'''项目模块（权限）管理'''
@login_required
@check_permission
def module_manage_view(request,id = 0):
    '''
    @author: Xieyz
    @note: 计划任务列表视图
    :param request:
    :return: 计划任务列表
    '''
    if id != 0:
        Module.objects.filter(id=id).delete()
        messages.add_message(request, messages.Success,'删除权限成功！')
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # 数据库中共有多少页
        search = request.POST.get('search')
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序
        if search:  # 判断是否有搜索字
            search = '%s' % (search)
            search = search.strip()
            all_records = Module.objects.filter(Q(id__icontains=search) |
                                                 Q(module_name__icontains=search) |
                                                 Q(module_url__icontains=search) |
                                                 Q(project__project__icontains=search))
        else:
            all_records = Module.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['module_name', 'module_url','project']:
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                if order == 'asc':
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
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "module_name": list.module_name if list.module_name else "",
                "module_url": list.module_url if list.module_url else "",
                "project": list.project.project if list.project.project else "",
            })
        return HttpResponse(json.dumps(response_data))
    return render(request, 'usercenter/module_manage.html')


@login_required
@check_permission
def module_add_view(request):
    '''
     @author: Xieyz
     @note: 添加权限
     :param request:
     :return:
     '''
    if request.method == "POST":
        add = ModuleAddForm(request.POST)
        if not request.POST.get('project_name'):
            errors = '请选择项目！'
            messages.add_message(request, messages.ERROR, errors)
            return render(request, 'usercenter/module_change.html', {'projectform': add})
        # 数据获取
        if add.is_valid():
            data = add.cleaned_data
            project_name = data.get('project_name')
            module_name = data.get('module_name')
            module_url = data.get('module_url')

            judge = Module.objects.filter(module_name=module_name,project=project_name)
            if judge:
                errors = '权限名已存在'
                messages.add_message(request, messages.ERROR , errors)
                return render(request, 'usercenter/module_change.html', {'projectform': add})

            # 数据保存
            form = Module()
            form.project = project_name
            form.module_name = module_name
            form.module_url = module_url
            form.save()
            messages.add_message(request, messages.SUCCESS, '添加权限成功！')
            return HttpResponseRedirect(reverse('module_manage'))
        else:
            messages.add_message(request, messages.ERROR, add.errors)
            return render(request, 'usercenter/module_change.html', {'projectform': add})
    else:
        form = ModuleAddForm()
    return render(request, 'usercenter/module_change.html', {"projectform": form})


@login_required
@check_permission
def module_modify_view(request, id):
    '''
     @author: Xieyz
     @note: 修改权限URL
     :param request:
     :return:
     '''
    if request.method == "POST":
        add = ModuleModifyForm(request.POST)
        # 数据获取
        add.is_valid()
        data = add.cleaned_data
        module_url = data.get('module_url')
        module_name = data.get('module_name')

        old_module = str(Module.objects.only('module_url').get(id=id).module_url)
        old_module_name = Module.objects.only('module_name').get(id=id).module_name

        # 数据保存
        form = Module.objects.get(id=id)
        form.module_url = module_url
        form.module_name = module_name
        form.save()

        new_module = str(Module.objects.only('module_url').get(id=id).module_url)
        new_module_name = str(Module.objects.only('module_name').get(id=id).module_name)

        # 更新日志
        update_logs = ModuleChangeLogs()
        update_logs.module_id = id
        update_logs.content = get_name_by_id.get_name(request.user.id) + '修改了权限名称，由：' + old_module_name + ',修改为：' + new_module_name + '。修改了权限URL, 由:' + old_module + ', 修改为:' + new_module
        update_logs.save()
        messages.add_message(request, messages.SUCCESS, '修改权限成功！')
        return HttpResponseRedirect(reverse('module_manage'))
    else:
        old_project = Module.objects.only('project').get(id=id).project.project
        old_module_name = Module.objects.only('module_name').get(id=id).module_name
        old_module_url = Module.objects.only('module_url').get(id=id).module_url
        form = ModuleModifyForm(
            initial={
                "project":old_project,
                "module_name": old_module_name,
                "module_url": old_module_url
            }
        )
    return render(request, 'usercenter/module_change.html', {"projectform": form})


@login_required
def get_all_module(request,pid):
    list2 = []
    Module_list = Module.objects.filter(project_id=pid)
    for item in Module_list:
        list2.append([item.id, item.module_name])
    return JsonResponse({'data2':list2})


@login_required
@check_permission
def module_change_history_view(request,id):
    '''
    @author: Xieyz
    @note: 权限修改历史
    :param request:
    :return: 权限修改列表
    '''
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')
        all_records = ModuleChangeLogs.objects.filter(module_id=id).order_by('-id')
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
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "module": list.module.module_name if list.module.module_name else "",
                "content": list.content if list.content else "",
                "datetime": list.datetime if list.datetime else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'usercenter/module_change_logs.html', {"id":id})
'''项目模块（权限）管理结束'''

from django.views.decorators.csrf import csrf_exempt
'''富文本编辑器上传图片'''
@csrf_exempt
def uploadIMG(request):
    img = request.FILES.get('img')
    uploadimg = WorkFlowIMG()
    uploadimg.filename = img.name
    uploadimg.img = img
    uploadimg.save()
    return HttpResponse(
        "<script>top.$('.mce-btn.mce-open').parent().find('.mce-textbox').val('/media/%s').closest('.mce-window').find('.mce-primary').click();</script>" % uploadimg.img)


'''Cron表达式生成器页面'''
@login_required
def cron_select_view(request):
    '''
    获取cron生成器页面
    :param request:
    :return:
    '''
    return render(request, 'cron_select.html')


def workorder_chat_view(request):
    return render(request, 'workflow/workorder_chat.html')


'''获取工作流数量'''
@login_required
def get_flow_amount(request):
    start = request.POST.get('startdate')
    end = request.POST.get('enddate')
    startdate = start.strip().replace('-',',')
    startdate = datetime.datetime.strptime(startdate, '%Y,%m,%d')
    enddate = end.strip().replace('-',',')
    enddate = datetime.datetime.strptime(enddate, '%Y,%m,%d')
    date_list = []
    flow_count = []
    line_project_flow_count = []
    line_project_userflow_count = []
    line_cronflow_count = []
    line_project_releaseflow_count = []
    line_database_release_count = []
    for i in range((enddate - startdate).days + 1): # 循环计算日期范围内每天的工作流总数
        day = startdate + datetime.timedelta(days=i)
        project_flow_count = project.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        project_userflow_count = project_userflow.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        cronflow_count = cronflow.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        project_releaseflow_count = project_releaseflow.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        user_apply_flow_count = ProjectUserApplyFlow.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        authority_flow_count = authority_flow.objects.filter(applicationtime__range=(day,day+timedelta(days=1))).count()
        database_release_count = Application.objects.filter(application_time__range=(day,day+timedelta(days=1))).count()
        line_project_flow_count.append(int(('%d') % project_flow_count))
        line_project_userflow_count.append(int(('%d') % project_userflow_count))
        line_cronflow_count.append(int(('%d') % cronflow_count))
        line_project_releaseflow_count.append(int(('%d') % project_releaseflow_count))
        line_database_release_count.append(int(('%d') % database_release_count))
        flow_count.append(int(('%d') % (project_flow_count + project_userflow_count + cronflow_count +
            project_releaseflow_count +user_apply_flow_count + authority_flow_count + database_release_count)))

        date_list.append(day.strftime("%Y-%m-%d"))

    project_flow_count_dict = get_project_flow_count(startdate,enddate + datetime.timedelta(days=1))
    project_userflow_count_dict = get_project_userflow_count(startdate,enddate + datetime.timedelta(days=1))
    cronflow_count_dict = get_cronflow_count(startdate,enddate + datetime.timedelta(days=1))
    project_releaseflow_count_dict = get_project_releaseflow_count(startdate,enddate + datetime.timedelta(days=1))
    user_apply_flow_count_dict = get_user_apply_flow_count(startdate,enddate + datetime.timedelta(days=1))
    authority_flow_count_dict = get_authority_flow_count(startdate,enddate + datetime.timedelta(days=1))
    database_release_count_dict = get_database_release_count(startdate,enddate + datetime.timedelta(days=1))
    all_count = 0
    through_count = 0
    no_approval_count = 0
    no_through_count = 0
    for i in [project_flow_count_dict, project_userflow_count_dict, cronflow_count_dict,
                project_releaseflow_count_dict, user_apply_flow_count_dict, authority_flow_count_dict, database_release_count_dict]:
        all_count += i['all_count']
        through_count += i['through_count']
        no_approval_count += i['no_approval_count']
        no_through_count += i['no_through_count']
    return_dict = {
        'flow_count': flow_count,   # 日期范围内每天的工作流总数
        'line_project_flow_count': line_project_flow_count,
        'line_project_userflow_count': line_project_userflow_count,
        'line_project_releaseflow_count': line_project_releaseflow_count,
        'line_cronflow_count': line_cronflow_count,
        'line_database_release_count': line_database_release_count,
        'date_list':date_list,  # 日期列表
        'all_count': all_count,
        'through_count': through_count,
        'no_approval_count': no_approval_count,
        'no_through_count': no_through_count,
    }
    return JsonResponse(return_dict)

@login_required
def get_all_workflow_amount(request):
    project_flow_obj = project.objects.all()
    project_userflow_obj = project_userflow.objects.all()
    project_releaseflow_obj = project_releaseflow.objects.all()
    database_obj = Application.objects.all()
    cronflow_obj = cronflow.objects.all()
    result = {
        "project_flow_count": {
            "all": project_flow_obj.count(),
            "自建项目": project_flow_obj.filter(source=1).count(),
            "外购项目": project_flow_obj.filter(source=0).count(),
        },
        "project_userflow_count": {
            "all": project_userflow_obj.count(),
            "已完成": project_userflow_obj.filter(status=9).count(),
            "驳回": project_userflow_obj.filter(status=0).count()
        },
        "project_releaseflow_count": {
            "all": project_releaseflow_obj.count(),
            "已完成": project_releaseflow_obj.filter(status=9).count(),
            "驳回": project_releaseflow_obj.filter(status=0).count()
        },
        "database_release_count": {
            "all": database_obj.count(),
            "已完成": database_obj.filter(application_status=4).count(),
            "驳回": database_obj.filter(application_status=0).count()
        },
        "cronflow_count": {
            "all": cronflow_obj.count(),
            "已完成": cronflow_obj.filter(status=9).count(),
            "驳回": cronflow_obj.filter(status=0).count()
        }
    }
    return JsonResponse(result)

@login_required
def get_project_user_amount(request):
    project_id = request.GET.get('project_id')
    obj = project_group.objects.filter(project_id=project_id)
    type_count = {}
    data = []
    name_list = []
    for i in obj:
        try:
            type_count[i.user_type.name] += 1
        except KeyError:
            type_count[i.user_type.name] = 0
            type_count[i.user_type.name] += 1
    for v in type_count:
        name_list.append(v)
        data.append({'name': v, 'value': type_count[v]})
    result = {'name_list': name_list, 'data': data}
    return JsonResponse(result)


@login_required
def get_all_project(request):
    obj = project.objects.all()
    result = []
    for i in obj:
        result.append({'id': i.id, 'name': i.project})
    res = {'result': result}
    return JsonResponse(res)
