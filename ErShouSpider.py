# -*- coding: utf-8 -*-

from SQLiteWraper import SQLiteWraper, gen_ershou_insert_command
from extractor import extract_es
from SpiderGenerator import do_spider


if __name__ == "__main__":

    command = "create table if not exists ershou (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    db = SQLiteWraper('lianjia-detail-es.db', command)
    pre_conf = {
        "name": "ershou",
        "url_base": u"http://bj.lianjia.com/ershoufang/",
        "extract": extract_es,
        "gen_sql_command": gen_ershou_insert_command
    }
    do_spider(db, pre_conf)

