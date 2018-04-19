# -*- coding: utf-8 -*-

import re
import urllib2
import cookielib
import random
import threading
import json
from Bloom import Bloomfilter
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

modes = ["entire", "increment", "specific"]

def search(pattern, content, group=0):
    res = re.search(pattern, content)
    return res.group(group) if res else u'未知'


def do_spider(db, pre_conf):
    url_base = pre_conf['url_base']
    name = pre_conf['name']
    extract = pre_conf['extract']
    gen_sql_command = pre_conf['gen_sql_command']
    info_class_name = pre_conf.get('info_class_name', 'info')
    mode = pre_conf.get('mode', 'entire')

    list_spider_name = name + "_list_spider"
    detail_spider_name = name + "_detail_spider"
    exception_write = writeWithLogFile(name + '_log.txt')
    exception_read = readWithLogFile(name + '_log.txt')

    bf = Bloomfilter(10000000, 0.00001)


    def list_spider(list_url):
        try:
            req = urllib2.Request(list_url, headers=hds[random.randint(0, len(hds) - 1)])
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)  # ,errors='ignore')
            soup = BeautifulSoup(plain_text)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exception_write(list_spider_name, list_url)
            return
        except Exception, e:
            print e
            exception_write(list_spider_name, list_url)
            return

        item_list = soup.findAll('div', {'class': info_class_name})
        for item in item_list:
            href = item.find('a')
            if not href:
                continue
            url = href.attrs['href']
            if not bf.isContain(url):
                print "「%s」 is Contained!" % url
                detail_spider(url)
                bf.add(url)


    def detail_spider(url):
        info_dict = {u'链接': url}
        try:
            detail_req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
            # detail_source_code = opener.open(req, timeout=10).read()
            detail_source_code = urllib2.urlopen(detail_req, timeout=10).read()
            detail_plain_text = unicode(detail_source_code)
            extract_res = extract(detail_plain_text)
            info_dict.update(extract_res)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exception_write(detail_spider_name, url)
            return
        except Exception, e:
            print e
            exception_write(detail_spider_name, url)
            return
        print u"链接：%s" % url
        print info_dict
        command = gen_sql_command(info_dict)
        db.execute(command, 1)

    def region_spider(region):
        url = url_base + region + "/"
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
            d = json.loads(content.get('page-data'))
            total_pages = d['totalPage']
        threads = []
        for i in range(total_pages):
            list_url = u"%s%s/pg%d" % (url_base, region, i + 1)
            t = threading.Thread(target=list_spider, args=(list_url,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def exception_spider():
        count = 0
        excep_list = exception_read()
        while excep_list:
            for excep in excep_list:
                excep = excep.strip()
                if excep == "":
                    continue
                excep_name, url = excep.split(" ", 2)
                if excep_name == name + "_list_spider":
                    list_spider(url)
                    count += 1
                elif excep_name == name + "_detail_spider":
                    detail_spider(url)
                    count += 1
                else:
                    print "wrong format"
                print "have spidered %d exception url" % count
            excep_list = exception_read()
        print 'all done ^_^'

    spidered_urls = []

    if mode == "specific":
       for spidered_url in spidered_urls:
           detail_spider(spidered_url)
    else:
        if mode == "increment":
            spidered_urls = spidered_urls + db.fetchall("select href from " + name)
            for spidered_url in spidered_urls:
                bf.add(spidered_url[0])
        count = 0
        for region in regionsPinYin:
            region_spider(region)
            count = count + 1
            print '%s: have spidered %s region -- %d' % (name + "_spider", region, count)


    # 重新爬取爬取异常的链接
    exception_spider()



if __name__ == "__main__":

    command = "create table if not exists ershou (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    db = SQLiteWraper('lianjia-detail-es.db', command)
    pre_conf = {
        "name": "ershou",
        "url_base": u"http://bj.lianjia.com/ershoufang/",
        "extract": extract_es,
        "gen_sql_command": gen_ershou_insert_command,
        "mode": 'increment'
    }
    do_spider(db, pre_conf)
