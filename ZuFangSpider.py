# -*- coding: utf-8 -*-

from SQLiteWraper import SQLiteWraper, gen_zufang_insert_command
from extractor import extract_zf
from SpiderGenerator import do_spider


if __name__ == "__main__":

    command = "create table if not exists zufang (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, type TEXT,lng_lat TEXT)"
    db = SQLiteWraper('lianjia-detail-zf.db', command)
    pre_conf = {
        "name": "ershou",
        "url_base": u"http://bj.lianjia.com/zufang/",
        "extract": extract_zf,
        "gen_sql_command": gen_zufang_insert_command
    }
    do_spider(db, pre_conf)

