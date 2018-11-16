import requests,json,urllib
from .models import WechatApp,WorkSheet
from .getCurrentDomain import get_current_domain

def get_agentid():
    try:
        agent_id = WechatApp.objects.only("agent_id").get(app_id=1).agent_id
    except:
        agent_id = '1000013'
    return agent_id

def get_corp_secret():
    try:
        corp_secret = WechatApp.objects.only('secret').get(app_id=1).secret
    except:
        corp_secret = 'EHnTerI6Yw0i_mCdKtwufW1RjWW9F_kwiTDv5rxzseQ'
    return corp_secret

def get_contact_secret():
    try:
        contact_secret = WechatApp.objects.only('contact_secret').get(app_id=1).get_contact_secret
    except:
        contact_secret = 'xWPfryWX7Fv1BcJSpivflpPQXC_v5iH0HY2zfu1soTA'
    return contact_secret


def getAccesToken(corp_secret=None):
    """
    @author: 谢育政
    @note: 获取Access_Token
    :param corp_secret: 企业微信应用的 Secret
    :param corp_id： 企业的CorpID
    :return: 返回字典，通过['access_token']取到Access_Token
    """
    corp_id = 'ww0f3efc2873ad11c3'
    if corp_secret == None:
        corp_secret = get_corp_secret()
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    payload = {'corpid': corp_id, 'corpsecret': corp_secret}
    response = requests.get(url, params=payload)
    return response.json()


def getUserID(CODE,ACCESS_TOKEN):
    """
    @author: 谢育政
    @note: 根据code和token获取用户ID
    :param CODE: 从企业微信提供api获取
    :param ACCESS_TOKEN: 从getAccesToken获取
    :return: 返回字典，通过['UserId']取到用户ID
    """
    payload = {'CODE': CODE, 'ACCESS_TOKEN': ACCESS_TOKEN}
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
    response = requests.get(url, params=payload)
    return response.json()


def getUserInfo(ACCESS_TOKEN,UserID):
    """
    @author: 谢育政
    @note: 获取用户详细信息
    :param ACCESS_TOKEN: 从getAccesToken获取
    :param UserID: 从getUserID获取
    :return: 返回字典如下
    {
       "errcode": 0,    //返回码
       "errmsg": "ok",    //对返回码的文本描述内容
       "userid": "zhangsan",    //成员UserID。对应管理端的帐号
       "name": "李四",    //成员名称
       "department": [1, 2],    //成员所属部门id列表
       "order": [1, 2],    //部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)
       "position": "后台工程师",    //职位信息
       "mobile": "15913215421",    //手机号码，第三方仅通讯录套件可获取
       "gender": "1",    //性别。0表示未定义，1表示男性，2表示女性
       "email": "zhangsan@gzdev.com",    //邮箱，第三方仅通讯录套件可获取
       "isleader": 1,    //	上级字段，标识是否为上级。
       "avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0",
        //	头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可
       "telephone": "020-123456",    //座机。第三方仅通讯录套件可获取
       "english_name": "jackzhang",    //英文名
       "extattr": {"attrs":[{"name":"爱好","value":"旅游"},{"name":"卡号","value":"1234567234"}]}，    //扩展属性，第三方仅通讯录套件可获取
       "status": 1,    //激活状态: 1=已激活，2=已禁用，4=未激活。已激活代表已激活企业微信或已关注微信插件。未激活代表既未激活企业微信又未关注微信插件。
       "qr_code":"https://open.work.weixin.qq.com/wwopen/userQRCode?vcode=xxx"    //员工个人二维码，扫描可添加为外部联系人；第三方暂不可获取
    }
    """
    payload = {'access_token': ACCESS_TOKEN,'userid': UserID}
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
    response = requests.get(url, params=payload)
    return response.json()


def constructMessages(touser,msg):
    """
    @author: 谢育政
    @note: 构建文本消息体
    :param touser: 收消息的用户id, 多个用户用"|"分隔
    :param msg: 发送的消息
    :return: 消息体
    """
    agentid = get_agentid()  # 工单测试应用id
    values = {
        "touser": touser,
        "msgtype": 'text',
        "agentid": agentid,
        "text": {'content': msg},
        "safe": 0
    }
    msges = (bytes(json.dumps(values), 'utf-8'))
    return msges


def constructCardMessages(touser, msg, wsid, type=0):
    import datetime
    agent_id = get_agentid()
    corp_secret = get_corp_secret()
    date_now = datetime.datetime.now().strftime("%Y年%m月%d日")
    ws_obj = WorkSheet.objects.get(wsid=wsid)
    ext = ''
    ext_before = ''
    title = ws_obj.title
    if len(title) > 12:
        title = title[0:12] + '......'
    if type == 0:
        ext = '<div>工单状态：'+ws_obj.get_status_display()+'</div>'
        # url = "http://"+get_current_domain()+"/worksheet/work_order_record/detail/"+wsid+"/"
        url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=ww0f3efc2873ad11c3&redirect_uri=http://"+get_current_domain()+"/worksheet/work_order_record/detail/"+wsid+"/&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect"
        btntxt = "详情"
    elif type == 1 or type == 2:
        ext_before = '<div>提交人：' + ws_obj.submitter + '</div>' + '<div>截止日期：' + str(ws_obj.deadline) + '</div>'
        url = "http://" + get_current_domain() + "/worksheet/list/"+str(type)+"/"+str(ws_obj.id)+"/"
        btntxt = "点击前往运维平台"
    else:
        ext_before = '<div>提交人：' + ws_obj.submitter + '</div>'
        url = "http://" + get_current_domain() + "/"
        btntxt = "点击前往运维平台"

    values = {
        "touser": touser,
        "msgtype": 'textcard',
        "textcard": {
            'title': '消息通知',
            'description': '<div class="gray">'+date_now+'</div>'\
                           '<div class="normal">'+msg+'</div> '\
                           '<br>'
                           +ext_before+\
                           '<div>工单标题：'+title+'</div>'\
                           '<div>工单编号：'+wsid+'</div>'\
                           +ext+ \
                           '<br>'
                           ' <div class="highlight">自由 分享 创新 拼搏</div>',
            "url": url,
            "btntxt": btntxt,
        },
        "agentid": int(agent_id),
        "corpid": "ww0f3efc2873ad11c3",
        "corpsecret": corp_secret,
    }
    msges = (bytes(json.dumps(values), 'utf-8'))
    return msges


def sendWeChatMessage(token, data):
    """
    @author: 谢育政
    @note: 发送企业微信API
    :param token: Token
    :param data: 发送的数据
    :return:
    """
    url = 'https://qyapi.weixin.qq.com'
    send_url = '%s/cgi-bin/message/send?access_token=%s' % (url, token)
    result = requests.post(send_url, data = data)

    if result.status_code == 200:
        return 'success'
    else:
      return 'Failed'


class BuildWechatMessage(object):
    """
    @author: 谢育政
    @note: 调用发送企业微信
    :param to_user： 发送到用户, 多个用 "|" 分隔
    :param data： 发送的文本
    """
    def __init__(self, to_user, data):
        self.to_user = to_user
        self.data = data

    def send(self):
        self.token = getAccesToken()['access_token']
        self.message_json = constructMessages(self.to_user,self.data)
        send_code = sendWeChatMessage(self.token, self.message_json)
        return send_code

    def sendCard(self, wsid, type = 0):
        self.card_message = constructCardMessages(self.to_user,self.data, wsid, type)
        send_url = 'http://10.1.1.192:8011/api/v1/msg/wechat/'
        result = requests.post(send_url, data=self.card_message)
        if result.status_code == 200:
            return 'Success'
        else:
            return 'Failed'


class GetUserAvatar(object):
    """
    @author: 谢育政
    @note: 获取用户头像
    :param user_id： 用户ID
    """
    def __init__(self, user_id):
        self.userid = user_id

    def UserAvatar(self):
        self.token = getAccesToken()['access_token']
        user_avatar = getUserInfo(self.token, self.userid)['avatar']
        return user_avatar


class GetDepartUserList(object):
    """
    @author: 谢育政
    @note: 获取部门用户列表
    :param department_id： 部门id
    :param fetch_child： 是否递归, 1/0
    """
    def __init__(self, department_id,fetch_child):
        self.department_id = department_id
        self.fetch_child = fetch_child
        self.contact_secret = get_contact_secret()

    def userList(self):
        self.token = getAccesToken(self.contact_secret)['access_token']
        self.url = 'https://qyapi.weixin.qq.com'
        self.send_url = '%s/cgi-bin/user/list' % (self.url)
        payload = {'access_token': self.token, 'department_id': self.department_id,'fetch_child':self.fetch_child}
        response = requests.get(self.send_url, params=payload)
        result = response.json()
        return result['userlist']


class GetUserIdByEmail(object):
    """
    @author: 谢育政
    @note: 根据邮箱获取用户ID
    :param department_id： 部门id
    :param fetch_child： 是否递归, 1/0
    """
    def __init__(self, email, department_id, fetch_child=0):
        self.email = email
        self.department_id = department_id
        self.fetch_child = fetch_child

    def getUserId(self):
        try:
            approval_user_list = GetDepartUserList(self.department_id, self.fetch_child).userList()
            approval_user_id =''
            for i in approval_user_list:
                if i['email'] == self.email:
                    approval_user_id = i['userid']
                    continue
            return approval_user_id
        except Exception as err:
            print ('Get user id fail: '+ str(err))
            return False


class GetWechatData(object):
    """
    @author: 谢育政
    @note: 获取企业微信数据
    """
    def __init__(self):
        self.contact_secret = get_contact_secret()
        self.url = 'https://qyapi.weixin.qq.com'
        self.token = getAccesToken(self.contact_secret)['access_token']

    def get_department_list(self, id=1):
        self.send_url = '%s/cgi-bin/department/list' % (self.url)
        payload = {'access_token': self.token, 'id': id}
        response = requests.get(self.send_url, params=payload)
        result = response.json()
        return result['department']
