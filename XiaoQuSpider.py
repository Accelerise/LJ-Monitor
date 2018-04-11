# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urllib2
import random
from bs4 import BeautifulSoup
import threading
from SQLiteWraper import gen_xiaoqu_insert_command
from agent import hds

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def search(pattern, content, group=0):
    res = re.search(pattern, content)
    return res.group(group) if res else u'未知'


def xiaoqu_spider(db_xq, url_page=u"http://bj.lianjia.com/xiaoqu/pg1rs%E6%98%8C%E5%B9%B3/"):
    """
    爬取页面链接中的小区信息
    """
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exit(-1)
    except Exception, e:
        print e
        exit(-1)

    xiaoqu_list = soup.findAll('div', {'class': 'info'})
    for xq in xiaoqu_list:
        info_dict = {}
        info_dict.update({u'小区名称': xq.find('a').text})
        info_dict.update({u'大区域': xq.find('a', {'class': 'district'}).text})
        info_dict.update({u'小区域': xq.find('a', {'class': 'bizcircle'}).text})

        content = unicode(xq.find('div', {'class': 'positionInfo'}).text.strip())
        spacePattern = re.compile('\s')
        content = spacePattern.sub('', content)

        info_dict.update({u'小区户型': search(r"/([\s\S]*)/", content, 1)})
        info_dict.update({u'建造时间': search("\d{4}", content)})
        command = gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command, 1)


def do_xiaoqu_spider(db_xq, region=u"昌平"):
    """
    爬取大区域中的所有小区信息
    """
    url = u"http://bj.lianjia.com/xiaoqu/rs" + region + "/"
    try:
        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=5).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return
    except Exception, e:
        print e
        return
    d = "d=" + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    exec (d)
    total_pages = d['totalPage']

    threads = []
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/xiaoqu/pg%drs%s/" % (i + 1, region)
        t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print u"爬下了 %s 区全部的小区信息" % region