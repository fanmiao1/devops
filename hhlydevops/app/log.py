#coding:utf-8
from flask import request,render_template, redirect,session
from app import app
from  dbutil import DB
import json

@app.route('/log')
def log():
   if not session.get('username',None):
        return redirect("/login")
   return  render_template('log.html',info=session)

@app.route('/status')
def status():
   if not session.get('username',None):
        return redirect("/login")

   # 模拟的假数据，真实数据拼接成这个格式即可
   result = {
       'legend':['200','404','502'],
       'data':[{'name':'200','value':234},{'name':'404','value':300},{'name':'502','value':250}]
   }
   return  json.dumps(result)

@app.route('/map')
def map():
   if not session.get('username',None):
        return redirect("/login")
   return  render_template('map.html',info=session)

@app.route('/mapdata')
def mapdata():
   if not session.get('username',None):
        return redirect("/login")
   # 获取所有省份和对应的范围次数，由于是根据ip进行入库，多个ip可能属于同一个省份，故结果需要去重
   fields = ['province','count']
   data = DB().get_list('log_map',fields)   
   # print data
   # 相同省份的次数累加，最终结果res = {'北京':40,'上海':50,.....}
   res = {}
   for x in data:
       p_name = x['province']
       res[p_name]=res.get(p_name,0)+x['count']
   # print res

   # 将数据拼接为echart匹配的格式 [{'name':'北京','value':40},{'name':'上海','value':40},...]
   result = []
   for k,v in res.items():
       tmp={}
       tmp['name'],tmp['value']=k.rstrip('省市回维吾尔壮族自治区'),v
       result.append(tmp)
   print result
   mapdata = {'code':0,'result':result}
   return  json.dumps(mapdata)

