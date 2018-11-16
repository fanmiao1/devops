from .acceptEmail import *
from devops.celery import app
from .models import *
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import timedelta
from devops import settings
from .getCurrentDomain import get_current_domain
from .getReceiveEmail import get_receive_email
from .sendWechatMessage import send_operator_wechat_message, send_pm_wechat_message
import base64

@app.task
def check_email_count():
    print('开始检查邮箱。')
    receive_email = get_receive_email()
    email = receive_email['email']
    password = receive_email['email_password']
    pop3_server = 'imap.exmail.qq.com'
    server = poplib.POP3(pop3_server)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    resp, mails, octets = server.list()
    count = len(mails)
    server.quit()
    try:
        obj = EmailWorksheetCount.objects.get(id=1)
    except:
        obj_add = EmailWorksheetCount()
        obj_add.id = 1
        obj_add.count = 0
        obj_add.save()
        obj = EmailWorksheetCount.objects.get(id=1)
    old_count = obj.count
    if count > old_count:
        try:
            new_email_count = count - old_count
            print('有' + str(new_email_count) + '封新的邮件。')
        except:
            pass
        while count != old_count:
            result_dict = print_info(conn_email(email,password,pop3_server,old_count+1))
            email_submit_worksheet(result_dict['From'], result_dict['Subject'],
                                   result_dict['text'],result_dict['cc_result'],
                                   result_dict['file'],result_dict['to'])
            old_count += 1
    elif count < old_count:
        print (count)
        err = '请检查「itsupport@aukeys.com」邮箱收件箱中邮件数量是否和工单数据表「worksheet_emailworksheetcount」的数量相等！<br>' \
              '请保持邮件数量和数据库记录的数量相同，才能收取下一封新的邮件。'
        print (err)
        try:
            send_user_id = GetUserIdByEmail('xieyuzheng@aukeys.com', 1, 1).getUserId()
            BuildWechatMessage(send_user_id,err).send()
        except:
            pass
    else:
        print('没有新的邮件。')
        pass
    print('检查邮箱结束。')


@app.task
def check_worksheet_timeout():
    worksheet_obj = WorkSheet.objects.filter(status=3)
    for ws in worksheet_obj:
        if ws.f_time:
            if settings.USE_TZ:
                process_time = ws.f_time.astimezone(datetime.timezone(timedelta(hours=8))).replace(tzinfo=None)
            else:
                process_time = ws.f_time.replace(tzinfo=None)
            now = datetime.datetime.now()
            gap = now - process_time
            if gap.days > 7:
                update_ws = WorkSheet.objects.get(id = ws.id)
                update_ws.status = 0
                update_ws.result = 3
                update_ws.save()
                log = '工单自动关闭'
                WorksheetOperateLogs.objects.create(worksheet_id=ws.id,content=log)
                WorksheetCommunicate.objects.create(worksheet_id=ws.id, pepole=1, content=log, service_look=1)
            else:
                continue
        else:
            continue


@app.task
def check_worksheet_approval_timeout():
    worksheet_obj = WorkSheet.objects.filter(status=4)
    for ws in worksheet_obj:
        if settings.USE_TZ:
            process_time = ws.c_time.astimezone(datetime.timezone(timedelta(hours=8))).replace(tzinfo=None)
        else:
            process_time = ws.c_time.replace(tzinfo=None)
        now = datetime.datetime.now()
        gap = now - process_time
        if gap.days > 3:
            update_ws = WorkSheet.objects.get(id=ws.id)
            update_ws.status = 0
            update_ws.result = 3
            update_ws.save()
            log = '工单自动关闭'
            WorksheetOperateLogs.objects.create(worksheet_id=ws.id, content=log)
            WorksheetCommunicate.objects.create(worksheet_id=ws.id, pepole=1, content=log, service_look=1)
        elif gap.seconds / 60 / 60 > 10:
            msg = '有一个工单还未审批，请联系审批人审批，超过3天未审批的工单将自动关闭'
            BuildWechatMessage(ws.submitter_userid, msg).sendCard(ws.wsid)
        else:
            continue

# @app.task
# def send_approval_email(send_email_list,
#                         wechat_user_name,title,description,new_worksheet_id,approval_user_dict, *args, **kwargs):
#     pass

@app.task
def send_approval_email(send_email_list,
                        wechat_user_name,title,description,new_worksheet_id,approval_user_dict, *args, **kwargs):
    the_current_domain = get_current_domain()
    file = WorksheetFile.objects.filter(worksheet_id=new_worksheet_id)
    file_list = []
    for i in file:
        try:
            file_list.append('/data/uploads/'+str(i.file.name))
        except:
            continue
    email_filter = EmailGroup.objects.values_list('email', flat=True)
    for send in send_email_list:
        if send in email_filter:
            continue
        send_body =  """
<tbody>
  <tr>
    <td>
      <table align="center" border="0" cellpadding="0" cellspacing="0" width="600"
        style="border: none; border-collapse: collapse;">
        <tbody>
          <tr>
            <td style="padding: 10px 0; border: none; vertical-align: middle;"><strong style="font-size: 16px">深圳市傲基电子商务股份有限公司</strong>
            </td>
          </tr>
        </tbody>
      </table>
      <table align="center" border="0" cellpadding="0" cellspacing="0" width="600"
        style="border-collapse: collapse; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
        <tbody>
          <tr>
            <td>
              <table cellpadding="0" cellspacing="0" width="600" style="border: none; border-collapse: collapse;">
                <tbody>
                  <tr>
                    <td style="padding: 10px; background-color: #F8FAFE; border: none; font-size: 14px; font-weight: 500; border-bottom: 1px solid #e5e5e5;">有一条工单需要审批</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding: 10px; border: none;">
              <fieldset style="border: 1px solid #e5e5e5">
                <legend style="color: #114f8e">详情</legend>
                <div style="padding:5px; font-family:Tahoma,Arial,Roboto,”Droid Sans”,”Helvetica Neue”,”Droid Sans Fallback”,”Heiti SC”,”Hiragino Sans GB”,Simsun,sans-self;text-indent:21pt;"">
                  <p class="MsoNormal">user_name申请了工单，需要审批:</p>
                  <p>若有图片或附件，随附件发送，请查看是否有附件</p>
                  <p><b>申 请 人：</b>user_name</p>
                  <p><b>工单标题：</b>title</p>
                  <p><b>工单描述：</b>description</p>
                  <p><a style="text-decoration:none;" target="view_window" href="http://current_domain/worksheet/work_order_approval/yes_approval/">
                  <button style="background-color:#2db7f5;border-color:#2db7f5;color:#fff; padding:2px 7px 2px 7px;margin-right:20px;border-radius:4px;">同意</button></a>
                  <a style="text-decoration:none;" target="view_window" href="http://current_domain/worksheet/work_order_approval/no_approval/">
                    <button style="background-color:#ed3f14;border-color:#ed3f14;color:#fff; padding:2px 7px 2px 7px;border-radius:4px;">不同意</button>
                  </a>
                </p>
              </ul>
            </div>
          </fieldset>
        </td>
      </tr>
      <tr>
      <td>
              <table cellpadding="0" cellspacing="0" width="600" style="border: none; border-collapse: collapse;">
                <tbody>
                  <tr>
                    <td style="padding: 10px; background-color: #F8FAFE; border: none; font-size: 14px; font-weight: 500; border-bottom: 1px solid #e5e5e5;"><span color='#F4692E'>自由 分享 创新 拼搏</span></td>
                  </tr>
                </tbody>
              </table>
            </td>
      </tr>
    </tbody>
  </table>
</td>
</tr>
</tbody>
            """
        try:
            data = {
                "to": [send],
                "cc": [],
                "subject": "工单消息通知",
                "type": "text/html",
                "body": send_body.replace('wsid',str(new_worksheet_id)).replace(
                    'current_domain',the_current_domain).replace('user_name',wechat_user_name).replace(
                        'title',title).replace('description',description).replace(
                        'yes_approval', 'ZSYGPW'+base64.b64encode(('1_'+str(new_worksheet_id)+'_'+approval_user_dict[send]).encode(encoding="utf-8")).decode()).replace(
                        'no_approval', 'ZSYGPW'+base64.b64encode(('0_'+str(new_worksheet_id)+'_'+approval_user_dict[send]).encode(encoding="utf-8")).decode()),
                "attach": file_list
            }
            msges = (bytes(json.dumps(data), 'utf-8'))
            send_url = 'http://10.1.1.192:8011/api/v1/msg/email/'
            result = requests.post(send_url, data=msges)
        except Exception as _:
            continue


@app.task
def new_worksheet_send_msg(wsid,type):
    """
    :param wsid: 工单编号
    :param type: 1为工单审批完成, 0为新工单
    :return:
    """
    user_id_list = []
    chat_user_list = GetDepartUserList(1, 1).userList()
    user_obj = User.objects.filter(groups__name='客服人员')
    if user_obj.count() != 0:
        for i in user_obj:
            if i.email:
                for e in chat_user_list:
                    if e['email'] == i.email:
                        user_id_list.append(e['userid'])
            else:
                continue
    if user_id_list:
        try:
            to_user = "|".join(user_id_list)
            if type == 1:
                msg = '有一条新的工单审批完成，等待受理，请前往运维平台处理'
            else:
                msg = '有一条新的工单等待受理，请前往运维平台处理'
            BuildWechatMessage(to_user, msg).sendCard(wsid, 1)
        except Exception as e:
            print ('new worksheet notice abnormal, Error : ' + str(e))
            pass
    else:
        pass


@app.task
def cron_send_ops_message():
    """
    :return:
    """
    from workflow.get_name_by_id import get_name_by_id
    worksheet_obj = WorkSheet.objects.filter(status=2)

    for user in worksheet_obj:
        if user.is_delay:
            pm_message = get_name_by_id.get_name(
                user.operator_id) + '有一条待办工单<div class="highlight">已延期</div>，请协助督促处理！'
            message = '你有一条待办工单<div class="highlight">已延期</div>，请前往运维平台处理！'
            send_operator_wechat_message(user.id, message)
            send_pm_wechat_message(user.id, pm_message)

        else:
            message = '你有一条待办工单，请前往运维平台处理！'
            send_operator_wechat_message(user.id, message)


@app.task
def cron_check_delay():
    """
    :return:
    """
    from django.utils import timezone
    worksheet_obj = WorkSheet.objects.filter(status=2)
    for row in worksheet_obj:
        if row.deadline:
            if row.deadline.strftime("%Y-%m-%d") < timezone.now().strftime("%Y-%m-%d"):
                row.is_delay = 1
                row.save()


@app.task
def cron_sync_org():
    """
    :return:
    """
    from .wechatApi import GetWechatData
    from usercenter.models import Org
    org = GetWechatData().get_department_list()
    Org.objects.filter(id=1).update(org_data=org)
