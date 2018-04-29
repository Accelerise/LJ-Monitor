# -*- coding: utf-8 -*-

from SQLiteWraper import SQLiteWraper, gen_ershou_insert_command
from extractor import extract_es
from SpiderGenerator import do_spider
import sys, getopt

if __name__ == "__main__":

    command = "create table if not exists ershou (href TEXT primary key UNIQUE, style TEXT, area TEXT, unit_price TEXT, total_price TEXT,lng_lat TEXT)"
    db = SQLiteWraper('../lianjia-detail-es.db', command)
    command = "create table if not exists price (href TEXT, time_stamp INTEGER, unit_price TEXT, total_price TEXT, rent TEXT, PRIMARY KEY (href, time_stamp))"
    db.execute(command)
    opts, args = getopt.getopt(sys.argv[1:], "m:")
    mode = "entire"

    for op, value in opts:
        if op == "-m":
            if value == "inc":
                mode = "increment"
            if value == "spec":
                mode = "specific"
            if value == "ent":
                mode = "entire"

    pre_conf = {
        "name": "ershou",
        "url_base": u"http://bj.lianjia.com/ershoufang/",
        "extract": extract_es,
        "gen_sql_command": gen_ershou_insert_command,
        "mode": mode
    }
    do_spider(db, pre_conf)

