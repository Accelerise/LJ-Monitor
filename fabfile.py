#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env, sudo, settings, hosts, cd, task, run, local, get
from fabric.contrib import files
from fabric.colors import green
from fabric.context_managers import shell_env
from fabric.operations import prompt
from fabric.colors import cyan

env.use_ssh_config = True
# 登录用户和主机名：
env.user = 'accelerise'

STAGES = {
    "production": {
        "cj_db": "~/Projects/LJ-Monitor/lianjia-detail-cj.db",
        "zf_db": "~/Projects/LJ-Monitor/lianjia-detail-zf.db",
        "es_db": "~/Projects/LJ-Monitor/lianjia-detail-es.db",
        "xq_db": "~/Projects/LJ-Monitor/lianjia-xq.db",
        "hosts": ["archer"]
    }
}
def stage_set(stage_name="test"):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)

stage_set('production')


def download(path):
    if files.exists(path):
        print 'downloading %s' % path
        get(path, './')

def getDB():
    # 下载数据库文件
    download(env.cj_db)
    download(env.zf_db)
    download(env.es_db)
    download(env.xq_db)

def deploy():
    # 重新加载 crontab 配置文件
    with settings(sudo_user="accelerise"):
        with cd('~/Projects/LJ-Monitor'):
            sudo("git reset --hard && git pull")
            sudo("/etc/init.d/cron reload")


