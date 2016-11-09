#coding:utf-8
from flask import request,render_template, redirect,session
from app import app
from  dbutil import DB
import json

fields = ['id','name','name_cn','address','adminer','phone']

# 机房列表
@app.route('/idc')
def idc_list():
   if not session.get('username',None):
        return redirect("/login")
   data = DB().get_list('idc',fields)
   return  render_template('idc/idc.html',idcs=data,info=session)

# 添加机房
@app.route('/idcadd',methods = ['GET','POST'])
def idc_add():
   if not session.get('username',None):
        return redirect("/login")
   if request.method == 'POST':
       data = dict((k,v[0]) for k,v in dict(request.form).items())     
       where = {'name':data['name']}
       result = DB().check('idc',fields,where)
       if result:
           return json.dumps({'code':1,'errmsg':'idc name is exist'})
       else:
          data = DB().create('idc',data)
          return  json.dumps({'code':0,'result':'add idc success'})
   else:
      return  render_template('idc/idcadd.html',info=session)

# 删除机房,执行sql在生产环境中要判断下执行的结果，我这就不写了
@app.route('/idcdelete',methods=['POST'])
def idc_delete():
    if not session.get('username',None):
        return redirect("/login")
    id = request.form.get('id')
    where = {'id':id}
    DB().delete('idc',where)
    return json.dumps({'code':0,'result':'delete success!'})


# 更新机房,执行sql在生产环境中要判断下执行的结果，我这就不写了
@app.route('/idcupdate',methods=['GET','POST'])
def idc_update():
    if not session.get('username'):
	    return redirect('/login')
    if request.method == 'POST':
        data = dict((k,v[0]) for k,v in dict(request.form).items())
        DB().update('idc',data)
        return json.dumps({'code' :0,'result':'update completed!'})
    else:
        id = request.args.get('id' )
        where = {'id':id}
        idc_info = DB().get_one('idc',fields,where)
        return render_template('idc/idcupdate.html',idc=idc_info,info = session)
