# -*- coding: utf-8 -*-

from SQLiteWraper import SQLiteWraper, gen_zufang_insert_command
from extractor import extract_zf
from SpiderGenerator import do_spider
import sys, getopt

if __name__ == "__main__":

    command = "create table if not exists zufang (href TEXT primary key UNIQUE, style TEXT, area TEXT, rent TEXT, type TEXT,lng_lat TEXT)"
    db = SQLiteWraper('../lianjia-detail-zf.db', command)
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
        "name": "zufang",
        "url_base": u"http://bj.lianjia.com/zufang/",
        "extract": extract_zf,
        "gen_sql_command": gen_zufang_insert_command,
        "info_class_name": "info-panel",
        "mode": mode
    }
    print pre_conf
    do_spider(db, pre_conf)

