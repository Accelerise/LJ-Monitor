#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from Tool import File
from lxml import etree
import re

styleRule = ur'(\d室\d厅(\d卫)?)|(\d房间(\d卫)?)'
sizeRule = ur'([\d.]+)平米'
unitPriceRule = ur'([\d.]+)元/平'
totalPriceRule = ur'([\d.]+)万'
signDateRule = ur'\d{4}\.\d{2}.\d{2}'
positionRule = ur'resblockPosition:\'([\d.]+,[\d.]+)\''
rentRule = ur'([\d.]+)\s+元/月'
hireType = ur'[整合]租'


cjPropsMap = {
    u'户型': styleRule,
    u'面积': sizeRule,
    u'签约单价': unitPriceRule,
    u'签约总价': totalPriceRule,
    u'签约时间': signDateRule,
    u'经纬度': positionRule
}

zfPropsMap = {
    u'户型': styleRule,
    u'面积': sizeRule,
    u'租金': rentRule,
    u'经纬度': positionRule,
    u'出租类型': hireType
}

esPropsMap = {
    u'户型': styleRule,
    u'面积': sizeRule,
    u'签约单价': unitPriceRule,
    u'签约总价': totalPriceRule,
    u'经纬度': positionRule
}

def get_prop(panel_text, propRule):
    pattern = re.compile(propRule, re.S)
    match = pattern.search(panel_text)
    if match:
        if bool(match.groups()):
            return ''.join(match.group(1).split())
        if bool(match.group()):
            return ''.join(match.group().split())
    return None

def extractUsingPropsMap(propsMap, domSelectors, isStrict=False):
    propsNames = propsMap.keys()
    def extract(page, originData={}):
        currentPropNames = [x for x in propsNames]

        def extract_props(childText, data):
            tmpPropNames = [x for x in currentPropNames]
            for propName in tmpPropNames:
                propRule = propsMap[propName]
                propValue = get_prop(childText, propRule)
                if propValue:
                    data[propName] = propValue
                    currentPropNames.remove(propName)

        dom = etree.HTML(page)
        data = originData.copy()
        for selector in domSelectors:
            panels = dom.cssselect(selector)
            for panel in panels:
                dom_text = panel.xpath('string(.)')
                extract_props(dom_text, data)
        if isStrict and len(currentPropNames) != 0:
            return None
        return data
    return extract

extract_cj = extractUsingPropsMap(cjPropsMap, ['.wrapper', 'script'], True)
extract_zf = extractUsingPropsMap(zfPropsMap, ['.overview', 'script'])
extract_es = extractUsingPropsMap(esPropsMap, ['.overview', 'script'])




