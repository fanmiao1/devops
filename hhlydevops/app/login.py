#coding:utf-8
from flask import request,render_template, redirect,session
from . import app
from dbutil import DB
import json
import hashlib

salt = "aaaaa"

# 登录功能
@app.route('/login', methods=["GET","POST"])
def login():
    # 用户第一次打开登录页面为GET请求，返回一个空的登录页
    if request.method == "GET":
        return render_template("login.html")
    # 如果用户点击按钮，提交post请求，表明已经填写了用户名和密码，则获取表单的值，然后判断用户密码是否正确
    # 如果不正确则输出错误信息到前端jQuery，如果正确则创建session，并返回正确码code到前端jquery
    if request.method == "POST":
        login_info =  dict((k,v[0]) for k,v in dict(request.form).items())
        login_info['password'] = hashlib.md5(login_info['password']+salt).hexdigest()   
        fields = ['name','password','role','status']
        where = {"name":login_info["name"]}
        result = DB().check('users',fields,where)
        if not result:
            return json.dumps({"code":1,"errmsg":"user is not exist"})
        if login_info["password"] != result['password']:
            return json.dumps({"code":1,"errmsg":"password error"})
        if  int(result['status']) == 1:
            return json.dumps({"code":1,"errmsg":"账户被锁定"})
        session["username"] = login_info["name"]
        session["role"] = result['role']
        return  json.dumps({"code":0,'result':'login success'})
      
# 退出功能      
@app.route("/logout/")
def logout():
    if session.get('username'):
        session.pop('role',None)
        session.pop('username', None)
    return redirect("/login")



