# -*- coding: utf-8 -*-

import re
import urllib2
import cookielib
import random
import threading
from bs4 import BeautifulSoup
from extractor import extract_es
from SQLiteWraper import SQLiteWraper, gen_ershou_insert_command
from common import hds, regionsPinYin
from exception import writeWithLogFile, readWithLogFile

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# 登录，不登录不能爬取三个月之内的数据
import LianJiaLogIn

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

exception_write = writeWithLogFile('ershou_log.txt')
exception_read = readWithLogFile('ershou_log.txt')


def search(pattern, content, group=0):
    res = re.search(pattern, content)
    return res.group(group) if res else u'未知'


def ershou_spider(db_es, url_page=u"http://bj.lianjia.com/ershoufang/dongcheng/"):
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
        exception_write('ershou_spider', url_page)
        return
    except Exception, e:
        print e
        exception_write('ershou_spider', url_page)
        return

    ershou_list = soup.findAll('div', {'class': 'info-panel'})
    for ershou in ershou_list:
        info_dict = {}
        href = ershou.find('a')
        if not href:
            continue
        url = href.attrs['href']
        info_dict.update({u'链接': url})
        try:
            detail_req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
            # detail_source_code = opener.open(req, timeout=10).read()
            detail_source_code = urllib2.urlopen(detail_req, timeout=10).read()
            detail_plain_text = unicode(detail_source_code)
            extract_res = extract_es(detail_plain_text)
            info_dict.update(extract_res)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exception_write('chengjiao_spider', url)
            continue
        except Exception, e:
            print e
            exception_write('chengjiao_spider', url)
            continue
        command = gen_ershou_insert_command(info_dict)
        db_es.execute(command, 1)

def exception_spider(db_es):
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
            if excep_name == "ershou_spider":
                ershou_spider(db_es, url)
                count += 1
            else:
                print "wrong format"
            print "have spidered %d exception url" % count
        excep_list = exception_read()
    print 'all done ^_^'

def do_ershou_spider(db_es, region='dongcheng'):
    """
    爬取大区域中的所有小区信息
    """
    url = u"http://bj.lianjia.com/ershou/" + region + "/"
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
        url_page = u"http://bj.lianjia.com/ershou/%s/pg%d" % (region, i + 1)
        t = threading.Thread(target=ershou_spider, args=(db_es, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()




if __name__ == "__main__":

    command = "create table if not exists ershou (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    db_es = SQLiteWraper('lianjia-detail-es.db', command)

    count=0
    for region in regionsPinYin:
        do_ershou_spider(db_es, region)
        count = count + 1
        print 'have spidered %d region' % count

    # 重新爬取爬取异常的链接
    exception_spider(db_es)

