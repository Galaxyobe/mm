# -*- coding: utf-8 -*-
"""
运行爬虫
"""

import os
import sys
import time

import psutil

import proxy.settings as settings
from proxy.commands.crawler import RunCrawler

project_path = os.path.abspath(settings.PROJECT_PATH)
pid_file = '%s/%s' % (project_path, settings.PID_NAME)


def run():
    """
    开始抓取
    """
    RunCrawler().start()


def set_pid(path):
    """
    设置pid
    把当前pid写入到path
    参数:
        @param path: pid文件路径
    返回:
        无
    """
    pid = os.getpid()
    with open(path, 'wb') as _file:
        text = str(pid) + ' #' + time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime(time.time()))
        _file.write(text)


def exists_pid(path):
    """
    检测pid
    检测path中的pid是否在运行
    参数:
        @param path: pid文件路径
    返回:
        无
    """
    with open(path, 'r') as _file:
        text = _file.readline()
        pid = int(text.split(' #')[0])
        return psutil.pid_exists(pid)


if __name__ == '__main__':
    if not os.path.exists(pid_file):
        set_pid(pid_file)
        run()
    else:
        if not exists_pid(pid_file):
            set_pid(pid_file)
            run()
        else:
            print '%s文件中的进程已运行' % pid_file
