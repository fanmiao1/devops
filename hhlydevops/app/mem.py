#coding:utf-8
from flask import request,render_template, redirect,session
from app import app
from utils import mem_get
import json
import time

@app.route('/monitor')
def monitor():
   if not session.get('username',None):
        return redirect("/login")
   return  render_template('meminfo.html',info=session)

# 实时的监控系统信息，本例以内存为例，收集脚本在 utils工具包中
@app.route('/memdata')
def memdata():
   if not session.get('username',None):
        return redirect("/login")
   result = mem_get.getMem()   # 调用工具包中收集内存的脚本
   print result
   data = {'data':[]}
   for mem in result:
        data['data'].append({'name':mem.keys()[0],'value':mem.values()[0]})
   # 数据格式必须按照官方的来
   #   times = int(time.time())
   #   data = {'data':[{'name':times,'value':[times*1000,60]},{'name':times+100,'value':[times*1001,80]},{'name':times+1000,'value':[times*1005,70]},{'name':times+2000,'value':[times*1010,60]},{'name':times+1500,'value':[times*1020,70]}]}
   print data
   return json.dumps(data)
