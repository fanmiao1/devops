#coding:utf-8
from flask import request,render_template, redirect,session
from app import app
from  dbutil import DB
import json

fields=['id','name','idc_id','u_num','power']
idc_fields = ['id','name']

# 机柜列表
'''
   机柜列表(关联了idc_id)的重点
   问题：
      机柜表里面存放了关联idc的id,而不是name, 如果不处理直接线上页面，idc这一列就是个数字，没有意义
   方案：
      1：查询机柜表数据的同时，也查询出机房表中id,name的对应值
      2：通过机柜表中的idc_id值和查机房表中查出来的id,name对比，如果id一致就将idc_id换成name
'''
@app.route('/cabinet')
def cabinet():
   if not session.get('username',None):
        return redirect("/login")
   idcs = DB().get_list('idc',idc_fields)   
   # print idcs   # [{'id': 7, 'name': 'hp'}, {'id': 1, 'name': 'syq'}]
   idcs = dict((idc['id'],idc['name'])  for idc in idcs)
   # print idcs     # {1: 'syq', 7: 'hp'}
   data = DB().get_list('cabinet',fields)
   # print data      # [{'idc_id': 2, 'u_num': '32U', 'id': 5, 'power': '20A', 'name': '005'}]
   # 重点！！！循环机柜表数据，并查询出idc_id是对比机房表信息，匹配就把idc_id 换位name,然后传到前端
   for x in data:
       if x['idc_id'] in idcs:
           x['idc_id'] = idcs[x['idc_id']]
   return  render_template('cabinet/cabinet.html',cabinets=data,info=session)

# 添加机柜
@app.route('/cabinetadd',methods = ['GET','POST'])
def cabinet_add():
   if not session.get('username',None):
        return redirect("/login")
   if request.method == 'POST':
       data = dict((k,v[0]) for k,v in dict(request.form).items())     
       print data
       where = {'name':data['name']}
       result = DB().check('cabinet',fields,where)
       if result:
           return json.dumps({'code':1,'errmsg':'cabinet name is exist'})
       else:
          data = DB().create('cabinet',data)
          return  json.dumps({'code':0,'result':'add cabinet success'})
   else:
      data = DB().get_list('idc',idc_fields)
      return  render_template('cabinet/cabinetadd.html',idcinfo=data,info=session)

# 删除机柜,执行sql在生产环境中要判断下执行的结果，我这就不写了
@app.route('/cabinetdelete',methods=['POST'])
def cabinet_delete():
    if not session.get('username',None):
        return redirect("/login")
    id = request.form.get('id')
    where = {'id':id}
    DB().delete('cabinet',where)
    return json.dumps({'code':0,'result':'delete success!'})


# 更新机柜,执行sql在生产环境中要判断下执行的结果，我这就不写了
'''
重点：
    1：更新数据关联的idc_id下拉菜单需要查询下机房表，然后将通过jinja2模块渲染，当然通过jQuery也行
    2：重点！！！渲染下拉菜单时，如何将该条数据已经选中的项展示出来呢？？？,两种方法jinja2模板 VS jQuery，
    本例采用了最简单的jinja2模板方式渲染，请看前端页面
'''
@app.route('/cabinetupdate',methods=['GET','POST'])
def cabinet_update():
    if not session.get('username'):
	    return redirect('/login')
    if request.method == 'POST':
        data = dict((k,v[0]) for k,v in dict(request.form).items())
        DB().update('cabinet',data)
        return json.dumps({'code' :0,'result':'update completed!'})
    else:
        id = request.args.get('id' )
        where = {'id':id}
        cabinet_info = DB().get_one('cabinet',fields,where)
        idcs = DB().get_list('idc',idc_fields)   
        return render_template('cabinet/cabinetupdate.html',cabinet=cabinet_info,idcs=idcs,info = session)
