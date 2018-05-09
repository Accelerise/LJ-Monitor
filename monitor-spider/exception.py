# -*- coding: utf-8 -*-

import threading
lock = threading.Lock()

def writeWithLogFile(file):
    def exception_write(fun_name, *args):
        """
        写入异常信息到日志
        """
        lock.acquire()
        f = open(file, 'a')
        line = fun_name
        for value in args:
            line = "%s %s" % (line, value)
        line = line + '\n'
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
