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

data = {}

def regist_prop(name, rule):
	propsMap[name] = rule

def get_prop(panelText, propName):
	propRule = propsMap[propName]
	pattern = re.compile(propRule, re.S)
	match = pattern.search(panelText)
	if match:
		if bool(match.groups()):
			return match.group(1)
		return match.group()
	return None

def extract_props(childText):
	global propNames
	tmpPropNames = [x for x in propNames]
	for propName in tmpPropNames:
		propValue = get_prop(childText, propName)
		if propValue:
			data[propName] = propValue
			propNames.remove(propName)

# writer = File('.')
# page = writer.fileRead('detail.html')
# dom = etree.HTML(page)
# wrappers = dom.cssselect('.wrapper')
# scripts = dom.cssselect('script')
# scriptTexts = [ script.xpath('string(.)') for script in scripts ]
# texts = [ wrapper.xpath('string(.)') for wrapper in wrappers ]


# def list_extract(page):
# 	global propNames, propsMap, data
# 	dom = etree.HTML(page)
# 	panels = dom.cssselect('div.info')
# 	count = 0
# 	result = []
# 	for panel in panels:
# 		children = panel.getchildren()
# 		propNames = propsMap.keys()
# 		data = {}
# 		subDoms = []
# 		for child in children:
# 			subDoms.append(child.getchildren())
# 		subDoms = [y for x in subDoms for y in x] 
# 		for subDom in subDoms:	
# 			subDomText = subDom.xpath('string(.)')
# 			extract_props(subDomText)
# 		if not propNames.__len__():
# 			count = count + 1
# 			result.append(data.copy())
# 	return result

def extract(page, originData={}):
	global propNames, propsMap, data
	dom = etree.HTML(page)
	wrappers = dom.cssselect('.wrapper')
	scripts = dom.cssselect('script')
	count = 0
	propNames = propsMap.keys()
	data = originData
	for wrapper in wrappers:
		domText = wrapper.xpath('string(.)')
		extract_props(domText)
	for script in scripts:
		domText = script.xpath('string(.)')
		extract_props(domText)

	return data



