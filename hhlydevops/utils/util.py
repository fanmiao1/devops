#/usr/bin/env python
#coding:utf-8
import logging
import logging.handlers

def WriteLog(log_name):
    log_file = "/tmp/test.log"
    log_level = logging.DEBUG
    # 定义日志格式
    format = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)2d]-%(funcName)s  %(levelname)s %(message)s')
    handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(format)
    # 实例化日志对象
    logger = logging.getLogger(log_name)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger                     #函数最终将实例化的logger对象返回，后面直接调用即可

#if __name__ == "__main__":
#    WriteLog('api').info('123')      # 模块内部直接调用函数。等价下面两行,下面的方法不推荐
    # writelog = WriteLog('api')
    # writelog.info('123')
