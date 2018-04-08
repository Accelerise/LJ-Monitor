#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from Tool import File
from lxml import etree
import re

propsMap = {
    u'户型': ur'\d室\d厅',
    u'面积': ur'[\d.]+平米',
    u'签约单价': ur'[\d.]+元/平',
    u'签约总价': ur'[\d.]+万',
    u'签约时间': ur'\d{4}\.\d{2}.\d{2}',
    u'经纬度': ur'resblockPosition:\'([\d.]+,[\d.]+)\''
}

propNames = propsMap.keys()

def regist_prop(name, rule):
    propsMap[name] = rule

def extract(page, originData={}):
    currentPropNames = [x for x in propNames]

    def get_prop(panel_text, propName):
        propRule = propsMap[propName]
        pattern = re.compile(propRule, re.S)
        match = pattern.search(panel_text)
        if match:
            if bool(match.groups()):
                return match.group(1)
            return match.group()
        return None

    def extract_props(childText, data):
        tmpPropNames = [x for x in currentPropNames]
        for propName in tmpPropNames:
            propValue = get_prop(childText, propName)
            if propValue:
                data[propName] = propValue
                currentPropNames.remove(propName)

    dom = etree.HTML(page)
    wrappers = dom.cssselect('.wrapper')
    scripts = dom.cssselect('script')
    data = originData.copy()
    for wrapper in wrappers:
        dom_text = wrapper.xpath('string(.)')
        extract_props(dom_text, data)
    for script in scripts:
        dom_text = script.xpath('string(.)')
        extract_props(dom_text, data)

    return data






