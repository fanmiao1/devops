#!/usr/bin/python
#coding:utf-8

from flask import render_template,request,redirect,session
from . import app
from  dbutil import DB
import json
import time

fields = ['id','apply_date','apply_type','apply_desc','deal_persion','status','deal_desc','deal_time','apply_persion']

@app.route("/jobadd/",methods=['GET','POST'])
def jobadd():
    if not session.get('username',None):
        return redirect("/login")
    if request.method == "POST":
        data = dict((k,v[0]) for k,v in dict(request.form).items())
        if not  data['apply_desc']:
             return json.dumps({'code':1,'errmsg':'job desc not null'})
        data['apply_date'] = time.strftime('%Y-%m-%d %H:%M')
        data['status'] , data['apply_persion'] = 0, session['username']
        DB().create('ops_jobs',data)
        '''sendemail'''
        #smtp_to = ['sa@yuanxin-inc.com']
        #send_info = '%s提交工单申请，运维同事请及时处理!'  % username  + '\n' + '工单申请描述\n' + data['apply_desc']
        #util.sendmail(app.config, smtp_to,'运维工单申请',send_info)
        return json.dumps({'code':0,'result':'创建工单成功!'})
    else:
	    return render_template('/jobs/jobsadd.html',info = session)

@app.route('/joblist/')
def joblist():
    if not session.get('username',None):
        return redirect("/login")
    where = {'status':['0','1']}
    jobs = DB().get_list('ops_jobs',fields,where)
    return render_template("/jobs/jobslist.html",jobs = jobs,info = session)

@app.route('/jobhistory/')
def jobhistory():
    if not session.get('username',None):
        return redirect("/login")
    jobs = DB().get_list('ops_jobs',fields)
    return render_template("/jobs/jobshistory.html",jobs = jobs,info = session)


@app.route('/jobdetail/')
def jobdetail():
    if not session.get('username',None):
        return redirect("/login")
    id = request.args.get('id')
    where = {'id':id}
    data = DB().get_one('ops_jobs',fields,where)
    if not data:
        result = {'code':1,'result':"信息查询失败"}
    else:
        data['apply_date']=str(data['apply_date'])
        data['deal_time']=str(data['deal_time'])
        result = {'code':0,'result':data}
    return json.dumps(result)


@app.route('/jobupdate/',methods=['GET','POST'])
def jobupdate():
    if not session.get('username',None):
        return redirect("/login")
    name = session['username']
    if request.method == "POST":
        data = dict((k,v[0]) for k,v in dict(request.form).items())
        data['status'] = 2
        data['deal_persion'] = name
        data['deal_time'] = time.strftime('%Y-%m-%d %H:%M')
        DB().update('ops_jobs',data)
        result = {'code':0,'result':"工单完成"}
        return json.dumps(result)
    else:
        id = request.args.get('id')
        data = {'id':id,'status':1,"deal_persion":name,'deal_time':time.strftime('%Y-%m-%d %H:%M')}
        DB().update('ops_jobs',data)
        result = {'code':0,'result':"工单处理中...."}
        return json.dumps(result)




