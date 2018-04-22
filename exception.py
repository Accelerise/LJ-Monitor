# -*- coding: utf-8 -*-

import threading
lock = threading.Lock()

def writeWithLogFile(file):
    def exception_write(fun_name, url):
        """
        写入异常信息到日志
        """
        lock.acquire()
        f = open(file, 'a')
        line = "%s %s\n" % (fun_name, url)
        f.write(line)
        f.close()
        lock.release()
    return exception_write

def readWithLogFile(file):
    def exception_read():
        """
        从日志中读取异常信息
        """
        lock.acquire()
        f = open(file, 'w+')
        lines = f.readlines()
        f.close()
        f = open(file, 'w')
        f.truncate()
        f.close()
        lock.release()
        return lines
    return exception_read