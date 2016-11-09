#coding:utf-8
from flask import request,render_template, redirect,session
from . import app
#from db import * 
from  dbutil import DB
import json
import hashlib

salt = "aaaaa"

# 首页，个人中心
@app.route('/')
@app.route('/index')
def index():
   if not session.get('username',None):
        return redirect("/login")
   #result = getone({'name':session['username']})
   fields = ["id","name","name_cn","mobile","email","role","status"]
   where = {'name':session['username']}
   result = DB().get_one('users',fields,where)
   return  render_template('index.html',info=session,user=result)

# 用户列表
@app.route('/userlist')
def user_list():
    if not session.get('username',None):
        return redirect("/login")
    fields = ["id","name","name_cn","mobile","email","role","status"]
    #data = userlist(fields)
    data = DB().get_list('users',fields)
    return  render_template('userlist.html',users=data,info=session)

# 添加用户
@app.route("/add",methods=["GET","POST"])
def add_user():
    if not session.get('username',None):
        return redirect("/login")
    if request.method == "GET":
        return render_template("add.html",info=session)
    if request.method == "POST":
         data =  dict((k,v[0]) for k,v in dict(request.form).items())
         data['password'] = hashlib.md5(data['password']+salt).hexdigest()
         fields = ['name']
         where = {"name":data["name"]}
         if  DB().check('users',fields,where):
            return json.dumps({"code":1,"errmsg":"username is exist"})
         DB().create('users',data)
         return json.dumps({"code":0,"result":"add user success"})

# 删除用户
@app.route("/delete")
def del_user():
    if not session.get('username',None):
        return redirect("/login")
    id = request.args.get("id")
    where = {'id':id}
    DB().delete('users',where)
    return json.dumps({"code":0,"result":"delete user success"})

# 更新用户
@app.route('/update',methods=["GET","POST"])
def update():
    fields = ["id","name","name_cn","mobile","email","role","status"]
    if request.method == "GET":
        where = {'id':request.args.get("id")}
        userinfo = DB().get_one('users',fields,where)
        return json.dumps(userinfo)
    else:
        userinfo = dict((k,v[0]) for k,v in dict(request.form).items())
        DB().update('users',userinfo)
        return json.dumps({"code":0})


