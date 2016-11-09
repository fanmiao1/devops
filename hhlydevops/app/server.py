
from flask import request,render_template, redirect,session
from app import app
from  dbutil import DB
import json


@app.route('/server')
def server():
   if not session.get('username',None):
        return redirect("/login")
   return  render_template('server/server.html',info = session)
