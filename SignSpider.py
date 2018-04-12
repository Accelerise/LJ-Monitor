# -*- coding: utf-8 -*-

import re
import urllib2
import cookielib
import random
import threading
from bs4 import BeautifulSoup
from extractor import extract_cj
from SQLiteWraper import SQLiteWraper, gen_chengjiao_insert_command
from common import hds, regions
from exception import writeWithLogFile, readWithLogFile

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#登录，不登录不能爬取三个月之内的数据
import LianJiaLogIn

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

exception_write = writeWithLogFile('sign_log.txt')
exception_read = readWithLogFile('sign_log.txt')

def search(pattern, content, group = 0):
    res = re.search(pattern, content)
    return res.group(group) if res else u'未知'

def chengjiao_spider(db_cj,xq_name,url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的成交记录
    """
    try:
        req = urllib2.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req,timeout=10).read()
        plain_text=unicode(source_code)#,errors='ignore')   
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exception_write('chengjiao_spider',xq_name,url_page)
        return
    except Exception,e:
        print e
        exception_write('chengjiao_spider',xq_name,url_page)
        return
    
    cj_list=soup.findAll('div',{'class':'info'})
    # print u'搜索到成交数量：' + str(cj_list.__len__())
    # print u'地址' + url_page
    for cj in cj_list:
        info_dict={}
        href=cj.find('a')
        if not href:
            continue
        url = href.attrs['href']
        info_dict.update({u'链接':url})
        info_dict.update({u'小区名称':xq_name})
        try:
            detail_req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
            # detail_source_code = opener.open(req, timeout=10).read()
            detail_source_code = urllib2.urlopen(detail_req,timeout=10).read()
            detail_plain_text=unicode(detail_source_code)
            extract_res = extract_cj(detail_plain_text)
            info_dict.update(extract_res)
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exception_write('chengjiao_spider',xq_name,url_page)
            continue
        except Exception,e:
            print e
            exception_write('chengjiao_spider',xq_name,url_page)
            continue 
        command=gen_chengjiao_insert_command(info_dict)
        db_cj.execute(command,1)

def xiaoqu_chengjiao_spider(db_cj,xq_name):
    """
    爬取小区成交记录
    """
    url=u"http://bj.lianjia.com/chengjiao/rs"+urllib2.quote(xq_name)+"/"
    try:
        req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req,timeout=10).read()
        plain_text=unicode(source_code)#,errors='ignore')   
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exception_write('xiaoqu_chengjiao_spider',xq_name,url)
        return
    except Exception,e:
        print e
        exception_write('xiaoqu_chengjiao_spider',xq_name,url)
        return
    content=soup.find('div',{'class':'page-box house-lst-page-box'})
    total_pages=0
    if content:
        d="d="+content.get('page-data')
        exec(d)
        total_pages=d['totalPage']
    
    # print u'总页数：' + str(total_pages)
    threads=[]
    for i in range(total_pages):
        url_page=u"http://bj.lianjia.com/chengjiao/pg%drs%s/" % (i+1,urllib2.quote(xq_name))
        t=threading.Thread(target=chengjiao_spider,args=(db_cj,xq_name,url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    
def do_xiaoqu_chengjiao_spider(db_xq,db_cj):
    """
    批量爬取小区成交记录
    """
    count=0
    xq_list=db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_chengjiao_spider(db_cj,xq[0])
        count+=1
        print 'have spidered %d xiaoqu' % count
    print 'done'




def exception_spider(db_cj):
    """
    重新爬取爬取异常的链接
    """
    count=0
    excep_list=exception_read()
    while excep_list:
        for excep in excep_list:
            excep=excep.strip()
            if excep=="":
                continue
            excep_name,xq_name,url=excep.split(" ",2)
            if excep_name=="chengjiao_spider":
                chengjiao_spider(db_cj,xq_name,url)
                count+=1
            elif excep_name=="xiaoqu_chengjiao_spider":
                xiaoqu_chengjiao_spider(db_cj,xq_name)
                count+=1
            else:
                print "wrong format"
            print "have spidered %d exception url" % count
        excep_list=exception_read()
    print 'all done ^_^'
    


if __name__=="__main__":
    command="create table if not exists xiaoqu (name TEXT primary key UNIQUE, regionb TEXT, regions TEXT, style TEXT, year TEXT)"
    db_xq=SQLiteWraper('lianjia-xq.db',command)
    
    command="create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    db_cj=SQLiteWraper('lianjia-detail-cj.db',command)

    #爬下所有小区里的成交信息
    do_xiaoqu_chengjiao_spider(db_xq,db_cj)
    
    #重新爬取爬取异常的链接
    exception_spider(db_cj)

