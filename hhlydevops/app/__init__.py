#coding:utf-8
from flask import Flask
import sys
reload(sys)
sys.setdefaultencoding('utf8')      # 因为程序内部有中文参数，gunicorn直接调用这个文件的app,在入口把编码转好

app = Flask(__name__)

app.secret_key = "UIsadl;oi3&*(&9023sd"

import login
import demo
import idc
import cabinet
import server
import mem
import log
import cmd
import jobs
