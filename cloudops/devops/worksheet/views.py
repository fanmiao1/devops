#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   time    : 2018/4/2
#   author  : 谢育政
#   software: PyCharm

from django.shortcuts import render
from worksheet.models import *
from worksheet.forms import *
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from workflow.views import DateEncoder
from workflow.get_name_by_id import get_name_by_id
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from .wechatApi import *
from django.core.mail import EmailMultiAlternatives
import datetime,random,json,re,time
from devops import settings
from django.utils.timezone import utc
from django.utils.timezone import timedelta
from .worksheetCount import *
from .tasks import send_approval_email,new_worksheet_send_msg
from .getCurrentDomain import get_current_domain
from .sendWechatMessage import send_operator_wechat_message, send_receiver_wechat_message
import base64

REDIRECT_URL = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid=ww0f3efc2873ad11c3&' \
               'agentid=' + get_agentid() + '&state=STATE&redirect_uri=http://' + get_current_domain() + '/'

def get_userid(request,CODE):
    try:
        wechat_user_id = request.session['wechat_user_id']
    except KeyError:
        try:
            ACCESS_TOKEN = getAccesToken()['access_token']
            wechat_user_id = getUserID(CODE,ACCESS_TOKEN)['UserId']
            request.session['wechat_user_id'] = wechat_user_id
        except KeyError:
            alter = '该连接已过期，请重新从企业微信工作台进入该页面！'
            return render(request,'worksheet/alter.html',locals())
    return wechat_user_id

def qr_code(request,url='worksheet/'):
    appid = 'ww0f3efc2873ad11c3'
    agentid = get_agentid()
    redirect_uri = 'http://' + get_current_domain() + '/' + url
    return render(request, 'worksheet/wechat_login.html', locals())


# Create your views here.
def workder(request):
    try:
        remind = WorksheetRemind.objects.get(id = 1).remind
    except:
        remind = '请登记工单'
    CODE = request.GET.get('code')
    wechat_user_name = ''
    wechat_user_email = ''
    send_email_list = []
    if not CODE:
        return HttpResponseRedirect(REDIRECT_URL+'worksheet/')
    ACCESS_TOKEN = getAccesToken()['access_token']
    wechat_user_id = get_userid(request, CODE)
    the_url = request.path + '?code=' + CODE
    if request.method == "POST":
        workder_forms = WorkSheetForm(request.POST)
        try:
            wechat_user_info = getUserInfo(ACCESS_TOKEN, wechat_user_id)  # 获取微信用户信息
            wechat_user_name = wechat_user_info['name']  # 获取微信用户名字
            wechat_user_email = wechat_user_info['email']  # 获取微信用户邮箱
        except:
            alter = '该页面已过期, 请重新从企业微信进入!'
            return JsonResponse({'result': alter, 'code': 0})
        message = "请检查填写的内容！"
        approval_user_dict = {}
        if workder_forms.is_valid():  # 获取数据
            title = workder_forms.cleaned_data['title']
            have_power_change = workder_forms.cleaned_data['have_power_change']
            email = workder_forms.cleaned_data['email']
            file_form = workder_forms.cleaned_data['file']
            description = workder_forms.cleaned_data['description_desc']
            if have_power_change == 'True':
                if not email:
                    message = '请填写抄送邮箱'
                    return JsonResponse({'result': message, 'code': 0})
                send_email_list = email.split(';')
                if len(send_email_list) > 10:
                    message = '邮件最多只能抄送10人'
                    return JsonResponse({'result': message, 'code': 0})
                approval_user_list = GetDepartUserList(1, 1).userList()
                email_filter = EmailGroup.objects.values_list('email', flat=True)
                for send_email in send_email_list:
                    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", send_email) == None:
                        message = '您填写的抄送邮箱格式有误!'
                        return JsonResponse({'result': message, 'code': 0})
                    approval_user_id = ''
                    for i in approval_user_list:
                        if i['email'] == send_email:
                            approval_user_id = i['userid']
                            continue
                    if not approval_user_id:
                        message = send_email +'不存在，请填写公司内部人员邮箱'
                        return JsonResponse({'result': message, 'code': 0})
                    if send_email == wechat_user_email:
                        message = '不能抄送给自己'
                        return JsonResponse({'result': message, 'code': 0})
                    if send_email == 'itsupport@aukeys.com':
                        message = '不能抄送给「itsupport@aukeys.com」这个邮箱'
                        return JsonResponse({'result': message, 'code': 0})
                    if send_email == 'devops@aukeys.com':
                        message = '不能抄送给「devops@aukeys.com」这个邮箱'
                        return JsonResponse({'result': message, 'code': 0})
                    if send_email == 'aukeys@aukeys.com':
                        message = '不能抄送给「aukeys@aukeys.com」这个邮箱'
                        return JsonResponse({'result': message, 'code': 0})
                    if send_email in email_filter:
                        message = '此邮箱「'+ send_email +'」不属于个人，不能抄送'
                        return JsonResponse({'result': message, 'code': 0})
                    else:
                        approval_user_dict[send_email] = approval_user_id
            if not description:
                message = '请填写描述'
                return JsonResponse({'result': message, 'code': 0})

            the_wsid = autoid()   #生成工单ID
            new_worksheet = WorkSheet()
            new_worksheet.wsid = the_wsid
            new_worksheet.title = title
            if have_power_change == 'True':
                new_worksheet.email = email
                new_worksheet.status = 4
            else:
                new_worksheet.status = 1
            if settings.USE_TZ:
                the_now = datetime.datetime.utcnow().replace(tzinfo=utc)
            else:
                the_now = datetime.datetime.now()
            new_worksheet.have_power_change = have_power_change
            new_worksheet.submitter = wechat_user_name
            new_worksheet.submitter_userid = wechat_user_id
            new_worksheet.submitter_email = wechat_user_email
            new_worksheet.description = description
            new_worksheet.c_time = the_now
            new_worksheet.source = '网页'
            new_worksheet.save()
            new_worksheet_id = WorkSheet.objects.get(wsid=the_wsid)
            log_content = wechat_user_name + " " + '提交了工单'
            workder_oper_log_add(new_worksheet_id.id, log_content,the_now)
            new_desc = description
            if '<img' in description:
                for i in new_desc.split('<img'):
                    if 'src=\"/data/uploads/' in i:
                        try:
                            ws_file = WorksheetFile.objects.get(file=i.split('src=\"/data/uploads/')[1].split('\"')[0])
                            ws_file.worksheet_id = new_worksheet_id.id
                            ws_file.save()
                            new_desc = new_desc.replace(('<img' + i.split('>')[0] + '>'),'')
                        except:
                            continue
            new_worksheet_id.description = new_desc
            new_worksheet_id.save()
            if file_form != '':
                try:
                    for file_arr in json.loads(file_form):
                        try:
                            ws_file = WorksheetFile.objects.get(file='worksheet/'+str(file_arr['name']))
                            ws_file.worksheet_id = new_worksheet_id.id
                            ws_file.save()
                        except Exception as e:
                            print ('附件关联工单异常：'+str(e))
                            continue
                except Exception as e:
                    print('附件列表类型异常：'+str (e))
                    pass
            if have_power_change == 'True':
                send_approval_email.delay(
                    list(set(send_email_list)),wechat_user_name,title,new_desc,new_worksheet_id.id,approval_user_dict)
            else:
                new_worksheet_send_msg.delay(the_wsid,0)
            msg = '工单提交成功，我们会尽快处理，感谢你的支持与信任'
            BuildWechatMessage(wechat_user_id, msg).sendCard(the_wsid)
            messages.add_message(request, messages.SUCCESS, msg)
            return JsonResponse({'result': msg, 'the_wsid': the_wsid, 'code': 1})
        else:
            message = "请检查填写的内容！"
            return JsonResponse({'result': message, 'code': 0})
    workder_forms = WorkSheetForm()
    return render(request, 'worksheet/simple.html', {'workder_forms': workder_forms, 'remind': remind, 'the_url':the_url})


def submit_success(request):
    return render(request,'worksheet/success.html')


def autoid():
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S") #生成当前时间
    randomNum = random.randint(0,100) #生成的随机整数n，其中0<=n<=100
    if randomNum <= 10:
        randomNum = str(0)+str(randomNum)
    uniqueNum = str(nowTime)+str(randomNum)
    return uniqueNum

@login_required
def workder_view(request,status, id=0):
    appointform = AppointForm()
    if status == 1:
        worksheet_classify_form = WorksheetClassifyForm()
    else:
        worksheet_classify_form2 = WorksheetClassifyForm()
    return render(request, 'worksheet/workder_list.html', locals())


@login_required
def get_workder_data(request, status):
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')
        search = request.POST.get('search')
        is_delay = request.POST.get('is_delay')
        print(is_delay)
        appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
        if search and is_delay:  # 判断是否有搜索字
            print('11111')
            search = '%s' % (search)
            search = search.strip()
            if request.user.is_superuser or '客服人员' in appoint_user_list:
                if status == 3:
                    all_record = WorkSheet.objects.filter((Q(status=3) | Q(status=0)),
                                                          (Q(wsid__icontains=search) |
                                                           Q(submitter__icontains=search) |
                                                           Q(title__icontains=search) |
                                                           Q(type__type_name__icontains=search) |
                                                           Q(receive_pepole__last_name__icontains=search[0],
                                                             receive_pepole__first_name__icontains=search[1:]) |
                                                           Q(receive_pepole__last_name__icontains=search[0:2],
                                                             receive_pepole__first_name__icontains=search[2:]) |
                                                           Q(operator__last_name__icontains=search[0],
                                                             operator__first_name__icontains=search[1:]) |
                                                           Q(operator__last_name__icontains=search[0:2],
                                                             operator__first_name__icontains=search[2:])),
                                                          is_delay=is_delay
                                                          )

                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(title__icontains=search), Q(status=1) | Q(status=4))
                else:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]) |
                                                          Q(operator__last_name__icontains=search[0],
                                                            operator__first_name__icontains=search[1:]) |
                                                          Q(operator__last_name__icontains=search[0:2],
                                                            operator__first_name__icontains=search[2:]), status=status,
                                                          is_delay=is_delay
                                                          )
            else:
                if status == 3:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]),
                                                          Q(status=3) | Q(status=0),
                                                          operator=request.user,
                                                          is_delay=is_delay)
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(title__icontains=search), Q(status=1) | Q(status=4),
                                                          operator=request.user)
                else:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]),
                                                          status=status,
                                                          operator=request.user,
                                                          is_delay=is_delay
                                                          )
        elif search and not is_delay:  # 判断是否有搜索字
            print('22222222')
            search = '%s' % (search)
            search = search.strip()
            if request.user.is_superuser or '客服人员' in appoint_user_list:
                if status == 3:
                    all_record = WorkSheet.objects.filter((Q(status=3) | Q(status=0)),
                                                          (Q(wsid__icontains=search) |
                                                           Q(submitter__icontains=search) |
                                                           Q(title__icontains=search) |
                                                           Q(type__type_name__icontains=search) |
                                                           Q(receive_pepole__last_name__icontains=search[0],
                                                             receive_pepole__first_name__icontains=search[1:]) |
                                                           Q(receive_pepole__last_name__icontains=search[0:2],
                                                             receive_pepole__first_name__icontains=search[2:]) |
                                                           Q(operator__last_name__icontains=search[0],
                                                             operator__first_name__icontains=search[1:]) |
                                                           Q(operator__last_name__icontains=search[0:2],
                                                             operator__first_name__icontains=search[2:]))
                                                          )

                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(title__icontains=search), Q(status=1) | Q(status=4))
                else:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]) |
                                                          Q(operator__last_name__icontains=search[0],
                                                            operator__first_name__icontains=search[1:]) |
                                                          Q(operator__last_name__icontains=search[0:2],
                                                            operator__first_name__icontains=search[2:]), status=status
                                                          )
            else:
                if status == 3:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]),
                                                          Q(status=3) | Q(status=0),
                                                          operator=request.user)
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(title__icontains=search), Q(status=1) | Q(status=4),
                                                          operator=request.user)
                else:
                    all_record = WorkSheet.objects.filter(Q(wsid__icontains=search) |
                                                          Q(submitter__icontains=search) |
                                                          Q(title__icontains=search) |
                                                          Q(type__type_name__icontains=search) |
                                                          Q(receive_pepole__last_name__icontains=search[0],
                                                            receive_pepole__first_name__icontains=search[1:]) |
                                                          Q(receive_pepole__last_name__icontains=search[0:2],
                                                            receive_pepole__first_name__icontains=search[2:]),
                                                          status=status,
                                                          operator=request.user
                                                          )
        elif not search and is_delay:
            print('333333')
            if request.user.is_superuser or '客服人员' in appoint_user_list:
                if status == 3:
                    all_record = WorkSheet.objects.filter((Q(status=3) | Q(status=0)), is_delay=is_delay)
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(status=1) | Q(status=4))
                else:
                    all_record = WorkSheet.objects.filter(status=status, is_delay=is_delay)
            else:
                if status == 3:
                    all_record = WorkSheet.objects.filter(Q(status=3) | Q(status=0), operator=request.user, is_delay=is_delay)
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(status=1) | Q(status=4), operator=request.user)
                else:
                    all_record = WorkSheet.objects.filter(status=status, operator=request.user, is_delay=is_delay)
        else:
            print('4444444')
            if request.user.is_superuser or '客服人员' in appoint_user_list:
                if status == 3:
                    all_record = WorkSheet.objects.filter(Q(status=3) | Q(status=0))
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(status=1) | Q(status=4))
                else:
                    all_record = WorkSheet.objects.filter(status=status)
            else:
                if status == 3:
                    all_record = WorkSheet.objects.filter(Q(status=3) | Q(status=0), operator=request.user)
                elif status == 1:
                    all_record = WorkSheet.objects.filter(Q(status=1) | Q(status=4), operator=request.user)
                else:
                    all_record = WorkSheet.objects.filter(status=status, operator=request.user)
        if status == 1:
            all_records = all_record.order_by('-id')
        elif status == 2:
            all_records = all_record.order_by('-a_time')
        else:
            all_records = all_record.order_by('-f_time')

        all_records_count = all_records.count()
        response_data = {'total': all_records_count, 'rows': []}
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
            unlook_count = WorksheetCommunicate.objects.filter(worksheet_id=list.id,service_look=0).count()
            try:
                operator = get_name_by_id.get_name(list.operator.id)
            except AttributeError:
                operator = ''
            try:
                receive_pepole = get_name_by_id.get_name(list.receive_pepole.id)
            except AttributeError:
                receive_pepole = ''
            response_data['rows'].append({
                "id": list.id if list.id else "",
                "wsid": list.wsid if list.wsid else "",
                "submitter": list.submitter if list.submitter else "",
                "title": list.title if list.title else "",
                "type": list.type.type_name if list.type else "",
                "submitter_email": list.submitter_email if list.submitter_email else "",
                "c_time": list.c_time if list.c_time else "",
                "receive_pepole" : receive_pepole if receive_pepole else "",
                "a_time": list.a_time if list.a_time else "",
                "deadline": list.deadline if list.deadline else "",
                "operator": operator if operator else "",
                "f_time": list.f_time if list.f_time else "",
                "status": list.get_status_display() if list.get_status_display() else "",
                "unlook_count": unlook_count if unlook_count else "",
                "is_delay": list.is_delay if list.is_delay else "",
            })
        return HttpResponse(json.dumps(response_data, cls=DateEncoder))


def work_order_receive(request,status,id):
    try:
        worksheet_obj = WorkSheet.objects.get(id = id)
        go_url = "<a href='http://" + get_current_domain() + "/worksheet/work_order_record/detail/"+str(worksheet_obj.wsid)+"'>前往查看</a>"
        touser = worksheet_obj.submitter_userid
        result = ''
        send_wechat_messages = request.POST.get('send_wechat_messages')
        appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
        if status == 2:
            if '客服人员' not in appoint_user_list:
                error = '您没有权限作此操作!'
                return JsonResponse({'result': error, 'code': 0})

            type = request.POST.get('type','')
            deadline = request.POST.get('deadline')
            worksheet_obj.receive_pepole_id = request.user.id
            worksheet_obj.operator_id = request.user.id
            worksheet_obj.status = status
            worksheet_obj.type_id = int(type)
            worksheet_obj.deadline = deadline
            worksheet_obj.a_time=datetime.datetime.now()
            worksheet_obj.save()
            result = '工单受理成功!'
            # 发送消息
            message = '工单已经受理，我们会尽快处理，请耐心等待'
            BuildWechatMessage(touser, message).sendCard(worksheet_obj.wsid)
            # 添加日志
            log_content = get_name_by_id.get_name(request.user.id) + " " + '受理了工单'
            workder_oper_log_add(id,log_content)

        elif status == 3:
            if request.user.id != worksheet_obj.operator.id  and '客服人员' not in appoint_user_list:
                error = '您没有权限作此操作!'
                return JsonResponse({'result': error, 'code': 0})
            worksheet_obj.f_time = datetime.datetime.now()
            worksheet_obj.operator_id = request.user.id
            worksheet_obj.status = status
            worksheet_obj.save()
            result = '工单处理完成!'
            message = '工单已经处理完成，请反馈是否解决'
            BuildWechatMessage(touser,message).sendCard(worksheet_obj.wsid)
            # 添加日志
            log_content = get_name_by_id.get_name(request.user.id) + " " + '处理了工单'
            workder_oper_log_add(id,log_content)

        elif status == 0:
            result = '工单关闭成功!'
            worksheet_obj.status = status
            worksheet_obj.save()
            # 添加日志
            log_content = get_name_by_id.get_name(request.user.id) + " " + '关闭了工单'
            workder_oper_log_add(id,log_content)
            message = '工单已经关闭，感谢你的支持和理解'
            BuildWechatMessage(touser, message).sendCard(worksheet_obj.wsid)
        if send_wechat_messages:
            # 添加回复
            worksheet_add = WorksheetCommunicate()
            worksheet_add.worksheet_id = id
            worksheet_add.pepole = 1  # 1表示客服的消息
            worksheet_add.content = send_wechat_messages
            worksheet_add.service_look = 1
            worksheet_add.save()
            # 发送企业微信消息
            message = '工单有新的回复，请前往查看'
            BuildWechatMessage(touser, message).sendCard(worksheet_obj.wsid)
        return JsonResponse({'result': result, 'code':1})
    except Exception as e:
        print (str(e))
        error = '操作失败'
        return JsonResponse({'result': error, 'code':0}) 


def work_order_approval(request,approval):
    '''
    工单审批
    '''
    approval_de = base64.b64decode(approval[6:]).decode()
    status = int(approval_de.split('_')[0])
    id = int(approval_de.split('_')[1])
    user_id = approval_de.split('_')[2]
    try:
        worksheet_obj = WorkSheet.objects.get(id = id)
    except:
        alter = '此工单不存在！'
        return render(request, 'worksheet/alter.html', locals())
    log_content = ''
    contact_secret = get_contact_secret()
    ACCESS_TOKEN = getAccesToken(contact_secret)['access_token']
    wechat_user_info = getUserInfo(ACCESS_TOKEN, user_id)  # 获取微信用户信息
    wechat_user_name = wechat_user_info['name']  # 获取微信用户名字
    approval_pepole_email = worksheet_obj.email.split(';')
    if wechat_user_info['email'] not in approval_pepole_email:
        alter = '您不是该工单的审批人，不能进行此操作！'
        return render(request, 'worksheet/alter.html', locals())
    if worksheet_obj.status != 4:
        if worksheet_obj.status == 0:
            alter = '此工单已关闭！'
            return render(request, 'worksheet/alter.html', locals())
        approval_judge = 0
        oper_log_obj = WorksheetOperateLogs.objects.filter(worksheet_id=worksheet_obj.id)
        for i in oper_log_obj:
            if wechat_user_name + ' 审批了工单' in i.content:
                approval_judge = 1
                break
        if approval_judge == 0:
            alter = '审批完成！'
            if status == 0:
                worksheet_obj.status = status
                worksheet_obj.save()
                log_content = wechat_user_name + " " + '审批了工单，不同意'
                message = '你的工单已被「' + wechat_user_name + '」驳回'
                worksheet_comm_add = WorksheetCommunicate()
                worksheet_comm_add.worksheet_id = id
                worksheet_comm_add.pepole = 1  # 1表示客服的消息
                worksheet_comm_add.content = '已被 ' + wechat_user_name + ' 驳回'
                worksheet_comm_add.user_look = 0
                worksheet_comm_add.service_look = 1
                worksheet_comm_add.save()
                BuildWechatMessage(worksheet_obj.submitter_userid, message).sendCard(worksheet_obj.wsid)
            elif status == 1:
                log_content = wechat_user_name + " " + '审批了工单，同意'
                message = '你提交的工单已被「' + wechat_user_name + '」审批通过'
                BuildWechatMessage(worksheet_obj.submitter_userid, message).sendCard(worksheet_obj.wsid)
            workder_oper_log_add(id, log_content)
        else:
            alter = '你已审批过此工单！'
        return render(request, 'worksheet/alter.html', locals())
    go_url = "<a href='http://" + get_current_domain() + "/worksheet/work_order_record/detail/"+str(worksheet_obj.wsid)+"'>前往查看</a>"
    worksheet_obj.status = status
    worksheet_obj.p_time = datetime.datetime.now()
    to_user = worksheet_obj.submitter_userid
    if status == 1:
        worksheet_obj.save()
        log_content = wechat_user_name + " " + '审批了工单，同意'
        message = '「'+wechat_user_name+'」审批通过了你提交的工单'
        BuildWechatMessage(to_user, message).sendCard(worksheet_obj.wsid)
        new_worksheet_send_msg.delay(worksheet_obj.wsid,1)
    elif status == 0:
        worksheet_obj.result = 5
        worksheet_obj.save()
        log_content = wechat_user_name + " " + '审批了工单，不同意'
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = id
        worksheet_comm_add.pepole = 1  # 1表示客服的消息
        worksheet_comm_add.content = '已被 '+ wechat_user_name +' 驳回'
        worksheet_comm_add.user_look = 0
        worksheet_comm_add.service_look = 1
        worksheet_comm_add.save()
        message = '你的工单已被「'+wechat_user_name+'」驳回'
        BuildWechatMessage(to_user, message).sendCard(worksheet_obj.wsid)
    workder_oper_log_add(id,log_content)
    alter = '审批完成！'
    return render(request, 'worksheet/alter.html', locals())

@login_required
def work_order_appoint(request, id):
    if request.method == 'POST':
        appoint_user = request.POST.get('user')
        remark = request.POST.get('remark')
        if not appoint_user:
            error = '请选择指派用户'
            return JsonResponse({'result': error, 'code':0})
        try:
            worksheet_obj = WorkSheet.objects.get(id = id)
            appoint_user_list = Group.objects.filter(user=request.user).values_list('name',flat=True)
            if worksheet_obj.status == 1:
                if '客服人员' not in appoint_user_list:
                    error = '您不能指派!'
                    return JsonResponse({'result': error, 'code':0})
                type = request.POST.get('type', '')
                deadline = request.POST.get('deadline', '')
                worksheet_obj.type_id = int(type)
                worksheet_obj.status = 2
                worksheet_obj.deadline = deadline
                worksheet_obj.a_time = datetime.datetime.now()
                worksheet_obj.receive_pepole_id = request.user.id
                message = '工单已经受理，我们会尽快处理，请耐心等待'
                BuildWechatMessage(worksheet_obj.submitter_userid, message).sendCard(worksheet_obj.wsid)

            else:
                if not worksheet_obj.operator:
                    if request.user.id != worksheet_obj.receive_pepole_id and '客服人员' not in appoint_user_list:
                        error = '您不能指派!'
                        return JsonResponse({'result': error, 'code':0})
                else:
                    if request.user.id != worksheet_obj.operator_id and '客服人员' not in appoint_user_list:
                        error = '您不能指派!'
                        return JsonResponse({'result': error, 'code':0})

            # if request.user.id == int(appoint_user):
            #     error = '不能指派给自己!'
            #     return JsonResponse({'result': error, 'code':0})
            worksheet_obj.operator_id = appoint_user
            worksheet_obj.save()
        except:
            error = '操作失败'
            return JsonResponse({'result': error, 'code':0})
        else:
            # 添加日志
            log_content = get_name_by_id.get_name(request.user.id) + " " + '指派给' + " " + get_name_by_id.get_name(appoint_user)
            if remark:
                log_content = log_content + ", 备注: " +remark
            workder_oper_log_add(id,log_content)
            try:
                user_email = User.objects.only('email').get(id=appoint_user).email
                send_user_id = GetUserIdByEmail(user_email,1,1).getUserId()
            except:
                print ('Appoint Send Wechats Fail!')
                pass
            else:
                message = '收到一条工单的指派，请前往运维平台处理'
                BuildWechatMessage(send_user_id, message).sendCard(worksheet_obj.wsid, 2)
            result = '指派成功!'
            return JsonResponse({'result': result, 'code':1})


def work_order_close(request, id):
    appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
    if '客服人员' not in appoint_user_list:
        error = '你没有权限这么做!'
        return JsonResponse({'result': error, 'code': 0})
    if request.method == 'POST':
        remark = request.POST.get('remark')
        worksheet_obj = WorkSheet.objects.get(id=id)
        if worksheet_obj.status == 0:
            error = '该工单已经被关闭!'
            return JsonResponse({'result': error, 'code': 0})
        go_url = "<a href='http://" + get_current_domain() + "/worksheet/work_order_record/detail/" + str(worksheet_obj.wsid) + "'>前往查看</a>"
        to_user = worksheet_obj.submitter_userid
        try:
            now_time = datetime.datetime.now()
            worksheet_obj.status = 0
            if not worksheet_obj.a_time:
                worksheet_obj.a_time = now_time
                worksheet_obj.receive_pepole_id = request.user.id
            worksheet_obj.result = 4    # 4为客服关闭
            worksheet_obj.save()
            result = '工单关闭成功!'
            # 添加日志
            log_content = get_name_by_id.get_name(request.user.id) + " " + '关闭了工单'
            workder_oper_log_add(id, log_content)
            message = '客服人员关闭了工单，感谢你的支持与理解'
            BuildWechatMessage(to_user, message).sendCard(worksheet_obj.wsid)
            if remark:
                message = "客服人员关闭了工单, 关闭原因：" + remark
            WorksheetCommunicate.objects.create(worksheet_id=id, pepole=1, content=message, service_look=1)
            return JsonResponse({'result': result, 'code': 1})
        except:
            error = '操作失败'
            return JsonResponse({'result': error, 'code': 0})
    else:
        error = '操作失败'
        return JsonResponse({'result': error, 'code': 0})


def edit_deadline(request, id):
    from django.utils import timezone
    appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
    if '客服人员' not in appoint_user_list:
        error = '你没有该操作权限!'
        return JsonResponse({'result': error, 'code': 0})
    if request.method == 'POST':
        msg = request.POST.get('msg')
        deadline = request.POST.get('deadline')
        worksheet_obj = WorkSheet.objects.get(id=id)
        if worksheet_obj.status != 2:
            error = '该工单非待处理状态，不可修改!'
            return JsonResponse({'result': error, 'code': 0})
        if deadline < timezone.now().strftime("%Y-%m-%d"):
            error = '截止日期不能小于当前时间！'
            return JsonResponse({'result': error, 'code': 0})
        # go_url = "<a href='http://" + get_current_domain() + "/worksheet/work_order_record/detail/" + str(worksheet_obj.wsid) + "'>前往查看</a>"
        log_content = get_name_by_id.get_name(request.user.id) + " " + '将截止日期' + str(worksheet_obj.deadline) + '修改为' + deadline
        try:
            worksheet_obj.deadline = deadline
            worksheet_obj.save()
            result = '截止日期修改成功!'
            # 添加日志
            workder_oper_log_add(id, log_content)
            message = '客服人员修改截止日期为' + deadline
            send_operator_wechat_message(id, message)
            if msg:
                message = "客服人员修改了截止日期, 修改说明：" + msg
                WorksheetCommunicate.objects.create(worksheet_id=id, pepole=1, content=message, service_look=1)
            return JsonResponse({'result': result, 'code': 1})
        except:
            error = '操作失败'
            return JsonResponse({'result': error, 'code': 0})
    else:
        error = '操作失败'
        return JsonResponse({'result': error, 'code': 0})


def edit_type(request, id):
    from django.utils import timezone
    appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
    if '客服人员' not in appoint_user_list:
        error = '你没有该操作权限!'
        return JsonResponse({'result': error, 'code': 0})
    if request.method == 'POST':
        type_id = request.POST.get('type_id')
        worksheet_obj = WorkSheet.objects.get(id=id)
        if worksheet_obj.status == 1 or worksheet_obj.status == 4:
            error = '该工单待审批或未受理，不可修改!'
            return JsonResponse({'result': error, 'code': 0})
        log_content = get_name_by_id.get_name(request.user.id) + " " + '修改了工单归类'
        try:
            worksheet_obj.type_id = type_id
            worksheet_obj.save()
            result = '类别修改成功!'
            # 添加日志
            workder_oper_log_add(id, log_content)
            return JsonResponse({'result': result, 'code': 1})
        except:
            error = '操作失败'
            return JsonResponse({'result': error, 'code': 0})
    else:
        error = '操作失败'
        return JsonResponse({'result': error, 'code': 0})


@login_required
def get_work_order_detail(request,id):
    worksheet_obj = WorkSheet.objects.get(id=id)
    WorksheetCommunicate.objects.filter(worksheet_id=id,service_look=0).update(service_look=1)
    worksheet_operatelogs_obj = WorksheetOperateLogs.objects.filter(worksheet__id=id).order_by("datetime")
    worksheet_comm_obj = WorksheetCommunicate.objects.filter(worksheet__id=id).order_by("datetime")
    log_list = []
    comm_list = []

    # 操作记录
    for log in worksheet_operatelogs_obj:
        log_list.append([log.datetime.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),log.content])

    # 沟通记录
    for comm in worksheet_comm_obj:
        comm_list.append([comm.get_pepole_display(),comm.content,comm.type,comm.datetime.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')])

    try:
        operator = get_name_by_id.get_name(worksheet_obj.operator.id)
    except AttributeError:
        operator = ''
    try:
        receive_pepole = get_name_by_id.get_name(worksheet_obj.receive_pepole.id)
    except AttributeError:
        receive_pepole = ''

    img = ''
    file = ''
    file_obj = WorksheetFile.objects.filter(worksheet_id=id)
    for i in file_obj:
        up_date = i.update_date.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if i.update_date else "",
        up_pp = i.update_pepole
        if i.file_type == 0:
            img += "<div class='demo-upload-list' title='上传者："+up_pp+"，时间："+str(up_date[0])+"'><img modal='zoomImg' src='/data/uploads/" + i.file.name + "' style='max-width:50px;'></div>"
        elif i.file_type == 1:
            file += "<span style='color:#999' title='上传者："+up_pp+"，时间："+str(up_date[0])+"'>（"+up_pp+"上传）</span>" \
                    "<span style='color:#999' title='上传者："+up_pp+"，时间："+str(up_date[0])+"'>"+i.filename+"</span>"\
                   "<a href='/data/uploads/"+i.file.name+"' download class='btn btn-link btn-xs' title='上传者："+up_pp+"，时间："+str(up_date[0])+"'>下载附件</a><br/>"
    worksheet_dict = {
        "id" : id,
        "wsid" : worksheet_obj.wsid if worksheet_obj.wsid else "",
        "title" : worksheet_obj.title if worksheet_obj.title else "",
        "description" : worksheet_obj.description if worksheet_obj.description else "",
        "img": img if img else "",
        "file": file if file else "",
        "source": worksheet_obj.source if worksheet_obj.source else "",
        "type": worksheet_obj.type.type_name if worksheet_obj.type else "",
        "submitter" : worksheet_obj.submitter if worksheet_obj.submitter else "",
        "submitter_email" : worksheet_obj.submitter_email if worksheet_obj.submitter_email else "",
        "email" : worksheet_obj.email if worksheet_obj.email else "",
        "status" : worksheet_obj.get_status_display() if worksheet_obj.get_status_display() else "",
        "receive_pepole" : receive_pepole if receive_pepole else "",
        "operator" : operator if operator else "",
        "c_time" : worksheet_obj.c_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if worksheet_obj.c_time else "",
        "p_time" : worksheet_obj.p_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if worksheet_obj.p_time else "",
        "a_time" : worksheet_obj.a_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if worksheet_obj.a_time else "",
        "f_time" : worksheet_obj.f_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if worksheet_obj.f_time else "",
        "deadline": worksheet_obj.deadline.strftime("%Y-%m-%d") if worksheet_obj.deadline else "",
        "result": worksheet_obj.get_result_display() if worksheet_obj.get_result_display() else "",
        "log_list": log_list,
        "comm_list":comm_list,
    }
    return JsonResponse(worksheet_dict)


def work_order_record_view(request):
    CODE = request.GET.get('code')
    if not CODE:
        return HttpResponseRedirect(REDIRECT_URL + 'worksheet/work_order_record/')
    wechat_user_id = get_userid(request,CODE)
    request.session['wechat_user_id'] = wechat_user_id
    if "<" in str(wechat_user_id) and ">" in str(wechat_user_id):
        return HttpResponseRedirect(REDIRECT_URL + 'worksheet/work_order_record/')
    return render(request, 'worksheet/workder_record2.html',{'wechat_user_id' : wechat_user_id})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_workder_record_data(request,wechat_user_id):
    itemIndex = request.POST.get('itemIndex')
    pageSize = request.POST.get('pageSize')
    pageNum = request.POST.get('pageNum')
    if itemIndex == '0':
        all_record = WorkSheet.objects.filter(Q(status=1)|Q(status=4),submitter_userid=wechat_user_id)
    elif itemIndex == '1':
        all_record = WorkSheet.objects.filter(status=2, submitter_userid=wechat_user_id)
    else:
        all_record = WorkSheet.objects.filter(Q(status=3)|Q(status=0),submitter_userid=wechat_user_id)
    all_records = all_record.order_by('-id')
    count = all_record.order_by('-id').count()
    if int(pageSize)*int(pageNum) - count >= int(pageSize):
        all_records = WorkSheet.objects.filter(status=999, submitter_userid=wechat_user_id)
    pageinator = Paginator(all_records, pageSize)
    result = {'result':[],'count':count}
    for list in pageinator.get_page(pageNum):
        result['result'].append({
            "wsid": list.wsid if list.wsid else "",
            "title": list.title if list.title else "",
            "c_time": list.c_time.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if list.c_time else "",
            "status": list.get_status_display() if list.get_status_display() else "",
        })
    return JsonResponse(result)


def workder_record_detail_view(request,wsid):
    request.session['from_url'] = request.META.get('HTTP_REFERER', '/')
    try:
        wechat_user_id = request.session['wechat_user_id']
    except:
        CODE = request.GET.get('code')
        if not CODE:
            return HttpResponseRedirect(REDIRECT_URL + 'worksheet/work_order_record/detail/' + wsid + '/')
        wechat_user_id = get_userid(request,CODE)
        request.session['wechat_user_id'] = wechat_user_id
    try:
        worksheet_obj = WorkSheet.objects.get(wsid = wsid)
        if worksheet_obj.submitter_userid != wechat_user_id:
            return HttpResponseRedirect(reverse('work_order_record'))
    except:
        alter = '此工单不存在'
        return render(request, 'worksheet/alter.html', locals())
    if request.method == 'POST':
        content = request.POST.get('comm')
        solve = request.POST.get('solve')
        if worksheet_obj.status == 3:
            if not solve:
                messages.add_message(request,messages.ERROR,'请选择是否解决')
                return HttpResponseRedirect(request.session['from_url'])
            worksheet_obj.status = 0
            worksheet_obj.result = solve
            worksheet_obj.save()
            solve_name = ''
            if solve == '1':
                solve_name = '已解决'
            elif solve == '2':
                solve_name = '未解决'
                message = '你有一条工单未解决，请及时登录处理！'
                send_receiver_wechat_message(worksheet_obj.id, message)
            log_content = '提交人关闭了工单'
            if solve_name:
                log_content = log_content + '，标记为：' + solve_name
            workder_oper_log_add(worksheet_obj.id, log_content)
        else:
            if not content:
                messages.add_message(request, messages.ERROR, '请填写回复')
                return HttpResponseRedirect(request.session['from_url'])
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = worksheet_obj.id
        worksheet_comm_add.pepole = 0 # 0表示用户的消息
        worksheet_comm_add.content = content
        worksheet_comm_add.user_look = 1
        worksheet_comm_add.service_look = 0
        if solve:
            worksheet_comm_add.type = 1

        worksheet_comm_add.save()
        message = '你要处理的工单有新的回复，请前往运维平台查看'
        send_operator_wechat_message(worksheet_obj.id, message)
        return HttpResponseRedirect(reverse('work_order_record_detail', args=[wsid]))
    img = ''
    file = ''
    file_obj = WorksheetFile.objects.filter(worksheet_id=worksheet_obj.id)
    for i in file_obj:
        up_date = i.update_date.replace(tzinfo=utc).astimezone(datetime.timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S") if i.update_date else "",
        if i.update_pepole == '用户':
            up_pp = '我'
        else:
            up_pp = '客服人员'
        if i.file_type == 0:
            img += "<div class='demo-upload-list' title='上传时间："+str(up_date[0])+"'><img src='/data/uploads/" + i.file.name + "' style='max-width:50px;'></div>"
        elif i.file_type == 1:
            file += "<span style='color:#999'>（上传时间："+str(up_date[0])+"）</span><span style='color:#999'>" + i.filename + "</span>" \
                    "<a href='/data/uploads/" + i.file.name + "' download class='btn btn-link btn-xs'>下载附件</a><br/>"
    worksheetcommunicate_obj = WorksheetCommunicate.objects.filter(worksheet__wsid=wsid).order_by('datetime')
    user_avatar = GetUserAvatar(worksheet_obj.submitter_userid).UserAvatar()
    WorksheetCommunicate.objects.filter(worksheet_id=worksheet_obj.id, user_look=0).update(user_look=1)
    return_dict = {
        'worksheet_obj':worksheet_obj,
        'worksheetcommunicate_obj':worksheetcommunicate_obj,
        'user_avatar':user_avatar,
        'img': img,
        'file': file
    }
    return render(request, 'worksheet/workder_record_detail.html',locals())


def work_order_reply_comm(request,people,id):
    try:
        comm_text = request.POST.get('comm_text')
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = id
        worksheet_comm_add.pepole = people  # 1表示客服的消息
        worksheet_comm_add.content = comm_text
        worksheet_comm_add.user_look = 0
        worksheet_comm_add.service_look = 1
        worksheet_comm_add.save()
        if people == 1: # 如果是客服的回复，通知提交人
            # 发送企业微信消息
            worksheet_obj = WorkSheet.objects.get(id=id)
            touser = worksheet_obj.submitter_userid
            # go_url = "<a href='http://" + get_current_domain() + "/worksheet/work_order_record/detail/" + str(
            #     worksheet_obj.wsid) + "'>前往查看</a>"
            message = '工单有新的回复，请前往查看'
            BuildWechatMessage(touser, message).sendCard(worksheet_obj.wsid)
    except Exception as e:
        print ('客服回复用户消息出现异常：' + str(e))
        error = '操作失败'
        return JsonResponse({'result': error, 'code': 0})
    else:
        result = '回复成功!'
        return JsonResponse({'result': result, 'code': 1})


def workder_oper_log_add(id,content,the_now=None):
    try:
        oper_logadd = WorksheetOperateLogs()
        oper_logadd.worksheet_id = id
        oper_logadd.content = content
        if datetime != None:
            oper_logadd.datetime = the_now
        oper_logadd.save()
    except:
        error = str(id)+u'工单操作日志保存失败'
        print(error)
    else:
        return True


'''获取工作流数量'''
def get_worksheet_amount(request):
    start = request.POST.get('start_date')
    end = request.POST.get('end_date')
    start_date = start.strip().replace('-',',')
    start_date = datetime.datetime.strptime(start_date, '%Y,%m,%d')
    end_date = end.strip().replace('-',',')
    end_date = datetime.datetime.strptime(end_date, '%Y,%m,%d')
    date_list = []
    day_count_list = []
    for i in range((end_date - start_date).days + 1):  # 循环计算日期范围内每天提交的工单总数
        day = start_date + datetime.timedelta(days=i)
        worksheet_count = WorkSheet.objects.filter(c_time__range=(day, day + timedelta(days=1))).count()
        day_count_list.append(int(('%d') % (worksheet_count)))
        date_list.append(day.strftime("%Y-%m-%d"))

    get_count = GetWorksheetCount(start_date,end_date + datetime.timedelta(days=1))
    total_count = get_count.worksheet_total_count()
    type_count = get_count.type_count()
    source_count = get_count.source_count(['邮件', '网页'])
    response_time_count = get_count.response_time_count()
    solve_time_count = get_count.solve_time_count()

    return_dict = {
        'day_count_list': day_count_list,   # 日期范围内每天提交的工单总数
        'date_list':date_list,  # 日期列表
        'total_count': total_count, # 日期范围内工单总数
        'response_time_count': response_time_count,
        'solve_time_count': solve_time_count,
        'source_count': source_count,
        'type_count': type_count
    }
    return JsonResponse(return_dict)


def answer_view(request, qid):
    from .get_wechat_message import check_answer
    ans = check_answer(qid)
    question = ans['question']
    answer = ans['answer']
    return render(request, 'worksheet/answer.html' ,locals())


'''富文本编辑器上传图片'''
@csrf_exempt
def ws_uploadIMG(request):
    result = {'name':[],'url':[]}
    img = request.FILES.getlist('img')
    for i in img:
        try:
            uploadimg = WorksheetFile()
            uploadimg.filename = i.name
            uploadimg.file = i
            uploadimg.file_type = 0
            uploadimg.save()
        except Exception as e:
            print ('上传图片「'+str(i.name)+'」失败：错误原因：' + str(e))
            continue
        try:
            re_name = str(uploadimg.file).split('worksheet/')[1]
        except:
            re_name = str(uploadimg.file)
        result['name'].append(re_name)
        result['url'].append("/data/uploads/%s" % uploadimg.file)
    return JsonResponse(result)


'''上传附件'''
@csrf_exempt
def ws_uploadFILE(request, type = 1):
    try:
        file = request.FILES.get('file')
        uploadimg = WorksheetFile()
        uploadimg.filename = file.name
        uploadimg.file = file
        uploadimg.file_type = type
        uploadimg.save()
    except Exception as e:
        print ('上传附件失败：错误原因：' + str(e))
        pass
    try:
        re_name = str(uploadimg.file).split('worksheet/')[1]
    except:
        re_name = str(uploadimg.file)
    return JsonResponse({"name":re_name, "url": "/data/uploads/%s" % uploadimg.file, })


'''上传工单附件'''
@csrf_exempt
def up_bundfile(request, type = 1, id = None):
    """
    :param request:
    :param type: 附件类型，0 图片， 1 文件
    :param id: 工单id
    :param pepole: 上传者，0 处理人/客服，1 用户
    :return:
    """
    wechat_user_id = request.session['wechat_user_id']
    try:
        ws_submiterid = WorkSheet.objects.get(id=id).submitter_userid
    except:
        ws_submiterid = 'none'
        return False
    if ws_submiterid != wechat_user_id:
        return False
    if id == None:
        return False
    try:
        file = request.FILES.get('file')
        uploadimg = WorksheetFile()
        uploadimg.filename = file.name
        uploadimg.file = file
        uploadimg.worksheet_id = id
        uploadimg.file_type = type
        uploadimg.save()
    except Exception as e:
        print ('上传附件失败：错误原因：' + str(e))
        return False
    try:
        re_name = str(uploadimg.file).split('worksheet/')[1]
    except:
        re_name = str(uploadimg.file)
    else:
        if str(type) != '1':
            content = "上传了图片：<div class='demo-upload-list'><img src='/data/uploads/" + str(uploadimg.file) + "' style='max-width:50px;'></div>"
        else:
            content = "上传了附件：<span style='color:#999'>" + str(uploadimg.filename) + "</span>"
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = id
        worksheet_comm_add.pepole = 0  # 0表示用户的消息
        worksheet_comm_add.content = content
        worksheet_comm_add.user_look = 1
        worksheet_comm_add.service_look = 0
        worksheet_comm_add.save()
        message = '你要处理的工单有新的回复，请前往运维平台查看'
        send_operator_wechat_message(id, message)
    return JsonResponse({"name":re_name, "url": "/data/uploads/%s" % uploadimg.file, })

'''删除附件'''
@csrf_exempt
def delete_wsfile(request):
    name = request.POST.get('file_name')
    wechat_user_id = request.session['wechat_user_id']
    try:
        obj = WorksheetFile.objects.get(file='worksheet/'+str(name))
        if obj.worksheet.submitter_userid != wechat_user_id:
            code = 0
            result = '撤回失败'
            return JsonResponse({"code": code, "result": result})
        else:
            del_filename = obj.filename
            del_fileid = obj.worksheet_id
    except:
        code = 0
        result = '撤回失败'
        return JsonResponse({"code": code, "result": result})

    try:
        WorksheetFile.objects.filter(file='worksheet/'+str(name)).delete()
    except:
        code = 0
        result = '撤回失败'
    else:
        code = 1
        result = '撤回成功'
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = del_fileid
        worksheet_comm_add.pepole = 0  # 0表示用户的消息
        worksheet_comm_add.content = "撤回了附件：<span style='color:#999'>" + str(del_filename) + "</span>"
        worksheet_comm_add.user_look = 1
        worksheet_comm_add.service_look = 0
        worksheet_comm_add.save()
    return JsonResponse({"code":code,"result":result})


@login_required
def reopen_worksheet(request,id):
    """
    重新打开工单
    :param request:
    :param id: 工单ID
    :return:
    """
    try:
        open_obj = WorkSheet.objects.get(id=id)
        appoint_user_list = Group.objects.filter(user=request.user).values_list('name', flat=True)
        if open_obj.status == 0 or open_obj.status == 3:
            if '客服人员' not in appoint_user_list and open_obj.operator_id != request.user.id and not request.user.is_superuser:
                result = '您没有权限作此操作!'
                return JsonResponse({'code': 0, 'result': result})
        else:
            result = '您没有权限作此操作!'
            return JsonResponse({'code': 0, 'result': result})
        open_obj.status = 2
        open_obj.receive_pepole_id = request.user.id
        open_obj.save()
    except:
        code = 0
        result = '重新打开工单失败'
    else:
        code = 1
        result = '重新打开了工单「'+str(open_obj.title)+'」'
        message = '你提交的工单已重新打开，返回待处理状态'
        BuildWechatMessage(open_obj.submitter_userid, message).sendCard(open_obj.wsid)
        log_content = get_name_by_id.get_name(request.user.id) + " " + '重新打开了工单'
        workder_oper_log_add(id, log_content)
        worksheet_comm_add = WorksheetCommunicate()
        worksheet_comm_add.worksheet_id = id
        worksheet_comm_add.pepole = 1  # 0表示用户的消息
        worksheet_comm_add.content = "客服人员重新打开了工单，返回待处理状态"
        worksheet_comm_add.user_look = 0
        worksheet_comm_add.service_look = 1
        worksheet_comm_add.save()
    return JsonResponse({"code":code,"result":result})