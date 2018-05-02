# -*- coding: utf-8 -*-

import sqlite3
import threading
from SQLiteWraper import SQLiteWraper
from Tool import File

def testExtract():
    reader = File('../')
    page = reader.fileRead('experiment.html')
    from extractor import extract_cj, extract_es, extract_zf
    print extract_cj(page)
    print extract_es(page)
    print extract_zf(page)

def cleanDB():
    # command = "create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    # db_cj = SQLiteWraper('../lianjia-detail-cj.db', command)
    # chengjiaos = db_cj.fetchall("select href, area, unit_price, total_price from chengjiao")
    #
    # path = "../lianjia-detail-cj.db"
    # conn = sqlite3.connect(path)
    # cu = conn.cursor()
    #
    # for chengjiao in chengjiaos:
    #     href = chengjiao[0]
    #     area = chengjiao[1].replace(u"平米", "")
    #     unit_price = chengjiao[2].replace(u"元/平", "")
    #     total_price = chengjiao[3].replace(u"万", "")
    #     command = "UPDATE chengjiao SET area = '%s', unit_price = '%s', total_price = '%s' WHERE href = '%s'" % (area, unit_price, total_price, href)
    #     cu.execute(command)
    #
    # conn.commit()



    # command = "create table if not exists ershou (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    # db = SQLiteWraper('../lianjia-detail-es.db', command)

    command = "create table if not exists zufang (href TEXT primary key UNIQUE, style TEXT, area TEXT, rent TEXT, type TEXT,lng_lat TEXT)"
    db = SQLiteWraper('../lianjia-detail-zf.db', command)

    # ershous = db.fetchall("select href, area, unit_price, total_price from ershous")

    zufangs = db.fetchall("select href, area, rent from zufang")

    path = "../lianjia-detail-zf.db"
    conn = sqlite3.connect(path)
    cu = conn.cursor()

    for zufang in zufangs:
        href = zufang[0]
        area = zufang[1].replace(u"平米", "")
        # unit_price = ershou[2].replace(u"元/平", "")
        # total_price = ershou[3].replace(u"万", "")
        rent = zufang[2].replace(u"元/月", "")
        # command = "UPDATE ershou SET area = '%s', unit_price = '%s', total_price = '%s' WHERE href = '%s'" % (area, unit_price, total_price, href)
        command = "UPDATE zufang SET area = '%s', rent = '%s' WHERE href = '%s'" % (area, rent, href)
        cu.execute(command)

    conn.commit()

    prices = db.fetchall("select href, time_stamp, unit_price, total_price, rent from price")
    conn = sqlite3.connect(path)
    cu = conn.cursor()

    for price in prices:
        href = price[0]
        time_stamp = price[1]
        unit_price = price[2].replace(u"元/平", "")
        total_price = price[3].replace(u"万", "")
        rent = price[4].replace(u"元/月", "")
        command = "UPDATE price SET unit_price = '%s', total_price = '%s', rent = '%s' WHERE href = '%s' and time_stamp = '%s'" % (unit_price, total_price, rent, href, time_stamp)
        cu.execute(command)

    conn.commit()