# -*- coding: utf-8 -*-

import re
import urllib2
import cookielib
import random
import threading
from bs4 import BeautifulSoup
from extractor import extract_zf
from SQLiteWraper import SQLiteWraper, gen_hire_insert_command
from common import hds, regionsPinYin
from exception import writeWithLogFile, readWithLogFile

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# 登录，不登录不能爬取三个月之内的数据
import LianJiaLogIn

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

exception_write = writeWithLogFile('hire_log.txt')
exception_read = readWithLogFile('hire_log.txt')


def search(pattern, content, group=0):
    res = re.search(pattern, content)
    return res.group(group) if res else u'未知'


def hire_spider(db_zf, url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的成交记录
    """
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exception_write('hire_spider', url_page)
        return
    except Exception, e:
        print e
        exception_write('hire_spider', url_page)
        return

    hire_list = soup.findAll('div', {'class': 'info-panel'})
    for hire in hire_list:
        info_dict = {}
        href = hire.find('a')
        if not href:
            continue
        url = href.attrs['href']
        info_dict.update({u'链接': url})
        try:
            detail_req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
            # detail_source_code = opener.open(req, timeout=10).read()
            detail_source_code = urllib2.urlopen(detail_req, timeout=10).read()
            detail_plain_text = unicode(detail_source_code)
            extract_res = extract_zf(detail_plain_text)
            info_dict.update(extract_res)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exception_write('chengjiao_spider', url)
            continue
        except Exception, e:
            print e
            exception_write('chengjiao_spider', url)
            continue
        command = gen_hire_insert_command(info_dict)
        db_zf.execute(command, 1)

def exception_spider(db_zf):
    """
    重新爬取爬取异常的链接
    """
    count = 0
    excep_list = exception_read()
    while excep_list:
        for excep in excep_list:
            excep = excep.strip()
            if excep == "":
                continue
            excep_name, url = excep.split(" ", 2)
            if excep_name == "hire_spider":
                hire_spider(db_zf, url)
                count += 1
            else:
                print "wrong format"
            print "have spidered %d exception url" % count
        excep_list = exception_read()
    print 'all done ^_^'

def do_hire_spider(region='dongcheng'):
    """
    爬取大区域中的所有小区信息
    """
    url = u"http://bj.lianjia.com/zufang/" + region + "/"
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
    content = soup.find('div', {'class': 'page-box house-lst-page-box'})
    total_pages = 0
    if content:
        d = "d=" + content.get('page-data')
        exec (d)
        total_pages = d['totalPage']
    threads = []
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/zufang/%s/pg%d" % (region, i + 1)
        t = threading.Thread(target=hire_spider, args=(db_zf, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()




if __name__ == "__main__":

    command = "create table if not exists hire (href TEXT primary key UNIQUE, style TEXT, area TEXT, rent TEXT, rent_type TEXT,lng_lat TEXT)"
    db_zf = SQLiteWraper('lianjia-detail-zf.db', command)

    for region in regionsPinYin:
        do_hire_spider(region)

    # 重新爬取爬取异常的链接
    exception_spider(db_zf)

