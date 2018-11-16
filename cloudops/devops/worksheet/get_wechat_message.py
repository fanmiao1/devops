# coding: utf-8
# from django.http import HttpResponse
# from django.template import loader, Context
# from django.views.generic.base import View
from django.http import HttpResponse
import time,requests,random,string,struct
import hashlib,base64
from .WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import sys,json
from cryptography.fernet import Fernet
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .wechatApi import BuildWechatMessage,get_current_domain
from .sendWechatMessage import send_generic_message

@csrf_exempt
def wechat_auth(request):
    '''
    @author: Xieyz
    @note: 验证回调URL
    :param token: 票据
    :param timestamp: 时间戳
    :param encrypt: 密文
    :param nonce: 随机字符串
    :return: 安全签名
    '''
    sToken = 'AUKEYIT'
    sEncodingAESKey = 'rcZXUjshKCJF4UDGMBrb7ssPR5vUkRDdDckUiSAUKEY'
    sCorpID = 'ww0f3efc2873ad11c3'
    wxcpt=WXBizMsgCrypt.WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)

    data = request.GET
    sVerifyMsgSig = data.get('msg_signature','')
    sVerifyTimeStamp = data.get('timestamp','')
    sVerifyNonce = data.get('nonce','')

    if request.method == 'GET':
        sVerifyEchoStr = data.get('echostr','')
        ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
        if ret != 0:
            print ("ERR: VerifyURL ret: " + str(ret))
            sys.exit(1)
        return HttpResponse(sEchoStr.decode("utf8"))

    if request.method == 'POST':
        sReqData = request.body
        ret,sMsg=wxcpt.DecryptMsg(sReqData, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce)
        if ret != 0 :
            print ("ERR: DecryptMsg ret: " + str(ret))
            sys.exit(1)
        xml_tree = ET.fromstring(sMsg)
        result =''
        try:
            content = xml_tree.find("Content").text
            result = check_answer(content)
        except:
            pass
        finally:
            if type(result) == dict:
                user_id = xml_tree.find("FromUserName").text
                click_url = 'http://'+get_current_domain()+'/worksheet/answer_view/'+result['qid']+'/'
                send_generic_message(user_id, result['answer'], title=result['question'], url=click_url)
        return HttpResponse(ret)


def check_answer(qid):
    '''
    @author: Xieyz
    @note: 根据问题ID返回答案
    :param qid: 问题ID
    :return: 答案
    '''
    result = {'qid':qid}
    try:
        qid = int(qid)
        answer_obj = AutoReplyQuestion.objects.get(qid = qid)
        result['question'] = answer_obj.question
        result['answer'] = answer_obj.answer
    except:
        result['question'] = '问题编号不存在'
        result['answer'] = "根据提示发送正确的问题编号得到答案<br/><br/>" \
                 "-----------------------------<br/>" \
                 "回复编号“0”返回问题列表"
    return result

