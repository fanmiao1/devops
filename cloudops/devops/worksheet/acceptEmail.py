# -*- coding: UTF-8 -*-
from .wechatApi import *
from .models import WorkSheet,EmailWorksheetCount,WorksheetOperateLogs,EmailGroup
import poplib,datetime,random
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from .getCurrentDomain import get_current_domain
from .getReceiveEmail import get_receive_email
from .byte_hex_trans import byte_to_hex
import base64


GETEMAIL = get_receive_email()['email']
print (GETEMAIL)
def autoid():
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S") #生成当前时间
    randomNum = random.randint(0,100) #生成的随机整数n，其中0<=n<=100
    if randomNum <= 10:
        randomNum = str(0)+str(randomNum)
    uniqueNum = str(nowTime)+str(randomNum)
    return uniqueNum


def workder_oper_log_add(id,content):
    try:
        oper_logadd = WorksheetOperateLogs()
        oper_logadd.worksheet_id = id
        oper_logadd.content = content
        oper_logadd.save()
    except:
        error = str(id)+' 工单操作日志保存失败'
        print (error)
    else:
        return True

def conn_email(email,password,pop3_server,index):
    server = poplib.POP3(pop3_server)
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(password)
    resp, mails, octets = server.list()
    resp, lines, octets = server.retr(index)
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    msg = Parser().parsestr(msg_content)
    server.quit()
    return msg

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

# indent用于缩进显示:
def print_info(msg, indent=0):
    from devops.settings import MEDIA_ROOT
    part = ''
    result = {}
    result['to'] = msg['To'].split(',')
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            continue
    if indent == 0:
        result['cc_result'] = []
        try:
            cc_list = msg.get('Cc').split(',')
            for i in cc_list:
                result['cc_result'].append(i.split('<')[1].split('>')[0])
        except:
            pass
        for header in ['From', 'To', 'Subject']:

            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s' % (addr)
            result[header] = value
    import os
    tmp_dic = MEDIA_ROOT + '/tmp'
    tmp_dic_isExists = os.path.exists(tmp_dic)
    if not tmp_dic_isExists:
        os.makedirs(tmp_dic)
    img_type = ['FFD8FF', '89504E47', '47494638', '49492A00', '424D']
    result['text'] = ''
    result['file'] = []
    filename_list = []
    data_none = None
    for part in msg.walk():  # 遍历所有payload
        contenttype = part.get_content_type()
        filename = part.get_filename()
        if filename:
            # 保存附件
            data = part.get_payload(decode=True)
            if '=?utf-8?B?' in filename:
                filename = filename.split('=?utf-8?B?')[1].split('?=')[0]
                filename = str(base64.b64decode(filename),'utf-8')
            elif '=?GB2312?B?' in filename:
                filename = filename.split('=?GB2312?B?')[1].split('?=')[0]
                filename = str(base64.b64decode(filename),'gb2312')
            if '/' in filename:
                filename = filename.replace('/','')
            file_type = 1
            file_hex = byte_to_hex(data)[0:10]
            for i in img_type:
                if i in file_hex:
                    file_type = 0
                    break
                else:
                    continue
            filename_list.append(filename)
            if file_type == 0:
                if not filename.endswith(('.png', '.jpg', '.bmp', '.tif', '.gif')):
                    filename += '.jpg'
            file_path = MEDIA_ROOT + '/tmp/' + filename
            with open(file_path, 'wb') as fd:
                fd.write(data)
            url = "http://" + get_current_domain() + "/worksheet/ws_file/"+str(file_type)+"/"
            file_data = {"file": open(file_path, "rb")}
            r = requests.post(url, data_none, files=file_data)
            save_file_name = r.json()['name']
            result['file'].append('worksheet/'+str(save_file_name))
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        elif contenttype=='text/html':
            data = part.get_payload(decode=True)
            charset = part.get_content_charset('ios-8859-1')
            result['text'] += data.decode(charset)
            img_tag_li = result['text'].split('<img')
            for img_tab in img_tag_li:
                if 'src=\"' in img_tab and 'http://' in img_tab:
                    try:
                        save_file_path = img_tab.split('src=\"')[1].split('\"')[0]
                        print (save_file_path)
                        img = requests.get(save_file_path)
                        file_path = MEDIA_ROOT + '/tmp/ws_text_img'
                        with open(file_path, 'wb') as fd:
                            fd.write(img.content)
                        file_data = {"file": open(file_path, "rb")}
                        url = "http://" + get_current_domain() + "/worksheet/ws_file/0/"
                        r = requests.post(url, data_none, files=file_data)
                        save_file_name = r.json()['name']
                        result['text'] = result['text'].replace(save_file_path,'http://'+get_current_domain()+'/data/uploads/worksheet/'+str(save_file_name))
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except:
                                pass
                    except:
                        continue
    try:
        for i in result['text'].split('<img'):
            if 'src=' in i:
                for file_name in filename_list:
                    if file_name in  '<img' + i.split('>')[0] + '>':
                        result['text'] = result['text'].replace(('<img' + i.split('>')[0] + '>'), '')
    except:
        pass
    return result


def email_submit_worksheet(email,subject,content,cc,file,to):
    from .models import WorksheetFile
    try:
        obj = EmailWorksheetCount.objects.get(id=1)
    except:
        obj_add = EmailWorksheetCount()
        obj_add.id = 1
        obj_add.count = 1
        obj_add.save()
        obj = EmailWorksheetCount.objects.get(id=1)
    obj.count = obj.count + 1
    obj.save()
    if subject[0:3] == 'Re:' or subject[0:3] == '回复:':
        print('这是一封回复的邮件「'+str(subject)+'」，已被过滤！')
        return False
    if subject == '企业微信小助手' or subject[0:8] == '运维平台消息通知':
        print('这不是工单邮件，subject:「' + str(subject) + '」，已被过滤！')
        return False
    is_worksheet_email = 0
    for i in to:
        if GETEMAIL in i:
            is_worksheet_email = 1
            break
    if is_worksheet_email == 0:
        print('这是一封群发邮件「'+str(subject)+'」，已被过滤！')
        return False
    msg = ''
    try:
        user_id = GetUserIdByEmail(email, 1, 1).getUserId()
    except Exception as err:
        print('检测邮件「'+str(subject)+'」来源的用户企业微信user_id失败，失败原因：' + str(err))
        return False
    else:
        try:
            contact_secret = get_contact_secret()
            token = getAccesToken(contact_secret)['access_token']
            user_info = getUserInfo(token,user_id)
            user_name = user_info['name']
            the_wsid = autoid()
        except Exception as err:
            msg = '工单「'+str(subject)+'」提交失败，请通过「工单登记」提交工单'
            print ('检测邮件「'+str(subject)+'」来源企业微信用户信息失败，失败原因：' + str(err))
            return False
        else:
            try:
                worksheet_add = WorkSheet()
                if cc:
                    cc_str = ''
                    try:
                        cc_str = ";".join(cc)
                    except:
                        pass
                    worksheet_add.email = cc_str
                    worksheet_add.have_power_change = 1
                    worksheet_add.status = 4
                else:
                    worksheet_add.status = 1
                worksheet_add.wsid = the_wsid
                worksheet_add.title = subject
                worksheet_add.description = content
                worksheet_add.submitter = user_name
                worksheet_add.submitter_userid = user_id
                worksheet_add.submitter_email = email
                worksheet_add.source = '邮件'
                worksheet_add.save()
                new_worksheet_id = WorkSheet.objects.only('id').get(wsid=the_wsid).id
                try:
                    for i in file:
                        try:
                            ws_file = WorksheetFile.objects.get(file=i)
                            ws_file.worksheet_id = new_worksheet_id
                            ws_file.save()
                        except:
                            continue
                except:
                    pass
                if cc:
                    email_filter = EmailGroup.objects.values_list('email', flat=True)
                    if type(cc) == list:
                        try:
                            approval_user_list = GetDepartUserList(1, 1).userList()
                        except:
                            pass
                        else:
                            approval_user_dict = {}
                            judge_ten = 0
                            for cc_i in cc:
                                judge_ten += 1
                                if judge_ten > 10:
                                    break
                                if cc_i == GETEMAIL:
                                    continue
                                if cc_i in email_filter:
                                    continue
                                try:
                                    for i in approval_user_list:
                                        try:
                                            if i['email'] == cc_i:
                                                approval_user_dict[cc_i] = i['userid']
                                                continue
                                        except:
                                            continue
                                except:
                                    continue
                            from .tasks import send_approval_email
                            send_approval_email.delay(
                                cc, user_name, subject, content, new_worksheet_id, approval_user_dict)
                msg = '工单提交成功, 我们会尽快处理，感谢你的支持与信任'
            except Exception as err:
                print('邮件「'+str(subject)+'」转化成工单失败，失败原因：'+ str(err))
                return False
            else:
                try:
                    new_worksheet_id = WorkSheet.objects.only('id').get(wsid=the_wsid).id
                    log_content = user_name + " " + '提交了工单'
                    workder_oper_log_add(new_worksheet_id, log_content)
                except Exception as err:
                    print('邮件转化为工单，该工单的操作日志保存失败，失败原因：' + str(err))
            finally:
                BuildWechatMessage(user_id, msg).sendCard(the_wsid)
                from .tasks import new_worksheet_send_msg
                new_worksheet_send_msg.delay(the_wsid, 0)
            return True
