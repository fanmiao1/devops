# _*_ coding: utf-8 _*_
from multiprocessing import current_process
import time
import datetime
import requests
import json
import sys
import os

from django.contrib.contenttypes.models import ContentType
from opscenter.models import script_log, cron, RevisionLogs, DetectWeb, DetectWebAlarmLogs
from devops.settings import SCRIPT_API, MODULE_API
from devops.celery import app
from usercenter.send_ws_message import Send
from devops.task_error import TaskError
from django.utils import timezone
import pycurl


@app.task
def run_ansible(resource, script_group, script_content, id, user):
    current_process()._config = {'semprefix': '/mp'}
    post_data = {}
    # postData['resource'] = resource
    # postData['script_type'] = script_group
    # postData['script_content'] = script_content
    # r = requests.post('http://127.0.0.1:8111/ans/', json=postData)

    post_data['resource'] = resource
    post_data['script_type'] = script_group
    post_data['script_content'] = script_content
    r = requests.post(SCRIPT_API, json=post_data)

    res = r.text
    script_logs = script_log()
    script_logs.script_result = res
    script_logs.script_id = id
    script_logs.datetime = datetime.datetime.now()
    script_logs.script_user = user
    script_logs.save()
    return res


@app.task
def run_ansible_module(resource, script_group, script_content, task_data, host, cookies):
    task_data['status'] = '执行中'
    task_data['exec_time'] = datetime.datetime.now()
    task_url = "http://{host}/opscenter/ansible_task/detail/{pk}/".format(host=host, pk=task_data['id'])
    try:
        task_response = requests.put(task_url, cookies=cookies, data=task_data)
    except Exception as _:
        err = '添加任务失败！'
        print(err)
        return err

    post_data = {}
    post_data['resource'] = resource
    post_data['script_type'] = script_group
    post_data['script_content'] = script_content
    r = requests.post(MODULE_API, json=post_data)

    res = r.text
    task_data['status'] = '完成'
    task_data['result'] = res
    task_data['complete_time'] = datetime.datetime.now()
    task_response = requests.put(task_url, cookies=cookies, data=task_data)
    return res


@app.task
def run_cron(resource, script_group, script_content, cron_id, user, os, change_status, data_type, content, file_path):
    current_process()._config = {'semprefix': '/mp'}
    true = 'true'
    false = 'false'
    null = 'null'
    now_cron_obj = cron.objects.get(id=cron_id)
    mkdir_a = 'path={path} state=directory'
    if os == 0:
        url = MODULE_API
        script_name = "/devops/{f}".format(f=now_cron_obj.name + '_' + str(cron_id))
        send_script_script_group = 'copy'
        mkdir_script_group = 'file'
        mkdir_a = mkdir_a.format(path='/devops')
    else:
        url = SCRIPT_API
        script_name = "c:/devops/{f}.exe".format(f=now_cron_obj.name + '_' + str(cron_id))
        send_script_script_group = 'win_copy'
        mkdir_script_group = 'win_file'
        mkdir_a = mkdir_a.format(path='c:\devops')
    if change_status == 'running':
        original_status = 'disable'
        if data_type != 0:
            mkdir_post_data = {}
            mkdir_post_data['resource'] = resource
            mkdir_post_data['script_type'] = mkdir_script_group
            mkdir_post_data['script_content'] = mkdir_a
            mkdir_r = requests.post(MODULE_API, json=mkdir_post_data)

            send_script_script_content = "src='{file_path}' dest={script_name}".format(
                file_path=file_path, script_name=script_name)
            send_script_post_data = {}
            send_script_post_data['resource'] = resource
            send_script_post_data['script_type'] = send_script_script_group
            send_script_post_data['script_content'] = send_script_script_content
            send_script_r = requests.post(MODULE_API, json=send_script_post_data)
    else:
        original_status = 'running'
    content_type_id = ContentType.objects.get(app_label=cron._meta.app_label, model=cron._meta.object_name)
    post_data = {}
    post_data['resource'] = resource
    post_data['script_type'] = script_group
    post_data['script_content'] = script_content
    r = requests.post(url, json=post_data)
    res = r.text
    dict_res = eval(res)

    try:
        if dict_res['status']:
            if dict_res['status'] == 'ERROR':
                cron.objects.filter(id=cron_id).update(status=original_status)
    except Exception as _:
        pass
    try:
        if os != 0:
            for i in dict_res['stats']:
                for ss in dict_res['stats'][i]:
                    dict_res = dict_res['stats'][i][ss]
        if not dict_res['ok']:
            cron.objects.filter(id=cron_id).update(status=original_status)
        else:
            cron.objects.filter(id=cron_id).update(status=change_status)
            same_cron_obj = cron.objects.filter(
                name=now_cron_obj.name, server=now_cron_obj.server, status='running').exclude(
                id=cron_id)
            for i in same_cron_obj:
                i.status = 'disable'
                i.save()
                RevisionLogs.objects.create(
                    content_type=content_type_id,
                    content='ID为{cron_id}的计划任务替换了该计划任务, 状态修改为：disable'.format(cron_id=cron_id),
                    object_id=i.id,
                    user=user
                )
    except Exception as _:
        pass
    RevisionLogs.objects.create(
        content_type=content_type_id,
        content=res,
        object_id=cron_id,
        user=user
    )
    data = {
        'target_type': 'group',
        'target': 'cron',
        'text': 'complete'
    }
    requests.post(url='http://codeops.aukeyit.com/websocket/send_ws_message/', data=data)
    return res

@app.task
def web_quality():
    detect_obj = DetectWeb.objects.all()
    for i in detect_obj:
        content = ""
        code = None
        i.detect_count += 1
        i.last_detect_time = timezone.now()
        i.save()
        try:
            i.detect_count += 1
            url = i.website   #探测的目标URL
            c = pycurl.Curl()   #创建一个Curl对象
            c.setopt(pycurl.URL,url)    #定义请求的URL常量

            try:
                c.perform_rb()
            except Exception as e:
                content += "主页异常: "+str(e)
                raise TaskError(content)
                continue

            NAMELOOKUP_TIME = c.getinfo(c.NAMELOOKUP_TIME)  # 获取DNS解析时间
            CONNECT_TIME = c.getinfo(c.CONNECT_TIME)  # 获取建立连接时间
            PRETRANSFER_TIME = c.getinfo(c.PRETRANSFER_TIME)  # 获取从建立连接到准备传输所消耗的时间
            STARTTRANSFER_TIME = c.getinfo(c.STARTTRANSFER_TIME)  # 获取从建立连接到传输开始消耗的时间
            TOTAL_TIME = c.getinfo(c.TOTAL_TIME)  # 获取传输的总时间
            HTTP_CODE = c.getinfo(c.HTTP_CODE)  # 获取HTTP状态码
            SIZE_DOWNLOAD = c.getinfo(c.SIZE_DOWNLOAD)  # 获取下载数据包的大小
            HEADER_SIZE = c.getinfo(c.HEADER_SIZE)  # 获取HTTP头部大小
            SPEED_DOWNLOAD = c.getinfo(c.SPEED_DOWNLOAD)  # 获取平均下载速度

            # 输出相关数据
            code = int(HTTP_CODE)
            content += ("主页状态码：%s" % (HTTP_CODE))
            content += ("\nDNS解析时间：%.2f ms" % (NAMELOOKUP_TIME * 1000))
            content += ("\n建立连接时间：%.2f ms" % (CONNECT_TIME * 1000))
            content += ("\n准备传输时间：%.2f ms" % (PRETRANSFER_TIME * 1000))
            content += ("\n传输开始时间：%.2f ms" % (STARTTRANSFER_TIME * 1000))
            content += ("\n传输结束总时间：%.2f ms" % (TOTAL_TIME * 1000))
            content += ("\n下载数据包大小：%d bytes/s" % (SIZE_DOWNLOAD))
            content += ("\nHTTP头部大小：%d bytes/s" % (HEADER_SIZE))
            content += ("\n平均下载速度：%d bytes/s" % (SPEED_DOWNLOAD))

            if i.login_after_url and i.username and i.password:
                request = "{username_element_name}={username}&{password_element_name}={password}".format(
                    username_element_name=i.username_element_name,
                    username=i.username,
                    password_element_name=i.password_element_name,
                    password=i.password,
                )
                c.setopt(pycurl.CONNECTTIMEOUT,5)   #定义请求连接的等待时间
                c.setopt(pycurl.TIMEOUT,5)      #定义请求超时时间
                c.setopt(pycurl.NOPROGRESS,1)       #屏蔽下载进度条
                c.setopt(pycurl.FORBID_REUSE,1)     #完成交互后强制断开连接，不重用
                c.setopt(pycurl.MAXREDIRS,1)        #指定HTTP重定向的最大数为1
                c.setopt(pycurl.DNS_CACHE_TIMEOUT,30)       #设置保存DNS信息的时间为30秒
                c.setopt(pycurl.POSTFIELDS, request)
                c.setopt(pycurl.COOKIEFILE, '')

                try:
                    c.perform()
                except Exception as e:
                    content += ("登录异常: "+str(e))
                    raise TaskError(content)
                    continue

                c.setopt(pycurl.URL, i.login_after_url)
                c.setopt(pycurl.HTTPGET, 1)

                try:
                    c.perform_rb()
                except Exception as e:
                    content += ("登录异常: "+str(e))
                    raise TaskError(content)
                    continue

                login_after_code = c.getinfo(c.HTTP_CODE)
                content += ("\n登录后跳转状态码: %s" % (login_after_code))
            c.close()

        except TaskError as err:
            c.close()
            content = str(err)
        log = DetectWebAlarmLogs()
        log.web = i
        log.content = content
        log.status_code = code
        log.save()
