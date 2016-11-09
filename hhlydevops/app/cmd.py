#coding:utf-8
from flask import Flask, request,render_template,session
from . import app
from  ansible.runner import Runner
import os,json,urllib,sys,time


def ansible_cmd(pattern,module,args,forks):
	result = Runner(module_name = module,
			module_args = args,
			pattern = pattern,
			forks = forks).run()
	return  result

@app.route('/ansible')
def ansible():
   if not session.get('username',None):
        return redirect("/login")
   return render_template('ansible.html',info=session)

@app.route('/cmd',methods=['GET','POST'])
def cmd():
    if not session.get('username',None):
        return redirect("/login")
    name = session.get('username')
    cmd_time = time.strftime('%Y-%m-%d %H:%M:%S')
    pattern = request.args.get('pattern','all')
    module = request.args.get('module','shell')
    args = urllib.unquote(request.args.get('cmd','whoami'))
    if "rm" in args:
        return "卧槽，你竟然是坏淫！！！！"
    forks = request.args.get('forks',5)
    results = ansible_cmd(pattern,module,args,forks)
    record = "[%s] - %s - %s - %s\n" % (cmd_time,name,pattern,args)
    with open("/tmp/jobs.log",'a') as f:
        f.write(record)
    str = ""
    if results is None:
        print "NO host found"
        sys.exit(1)
    for (hostname,result)  in results['contacted'].items():
        if not "failed" in result and result['stdout'] != "":
            # print "%s | %s | success >>  \n %s" % (hostname,result['cmd'],result['stdout'])
            str += "%s | %s | success >>  \n %s \n" % (hostname,result['cmd'],result['stdout'])
        else:
            str += "%s | %s | FAILED  >>  \n %s \n" % (hostname,result['cmd'],result['stderr'])
    for (hostname,result) in results['dark'].items():
            str += "%s | SSH Error >> \n  %s \ n" % (hostname, result['msg'])
    return str

@app.route('/joblist')
def list():
    str = ''
    with open('/tmp/jobs.log') as f:
        # str = f.read()                     # 从头到尾读文件
        for line in reversed(f.readlines()): # 倒读
            # print line
            str +=line+"</br>"
    return str 
