from flask import Flask
import os,logging
import util
app = Flask(__name__)

@app.route('/')
def hello_world():
    util.WriteLog('demo').info('nihao')
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9999,debug=True)
