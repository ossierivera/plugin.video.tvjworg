# -*- coding: utf-8 -*-
"""
    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube
    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import copy

import requests

import urllib,urllib2,urlparse,base64
import json


def get_json(url):
	data = urllib2.urlopen(url).read().decode('utf-8')
	return json.loads(data)
  
class JWTV(object):
    LOCAL_MAP = {'jw.api': 'https://data.jw-api.org/mediator/v1/categories/',
                 'jw.search.api': 'https://data.jw-api.org/search/query?',
                 'jw.token.api': 'https://tv.jw.org/tokens/web.jwt',
                 'jw.streaming.api': 'https://data.jw-api.org/mediator/v1/schedules/',
		 'jw.media-items.api': 'https://data.jw-api.org/mediator/v1/media-items/'
                 }
    def __init__(self, jwt_token='', language='E', items_per_page=24):
	self._jwt_token = jwt_token        
	self._language = language
	self._items_per_page = items_per_page

    def get_language(self):
        return self._language

    def set_language(self, language='E'):
	self._language = language    
 
    def get_sub_categories(self, language, sub_level):
	path = self.LOCAL_MAP['jw.api'] + language + '/' + sub_level + '/' + '?&detailed=1'
	return self.perform_v1_request(path)
		

    def get_top_video_categories(self, language='E'):        
	path = self.LOCAL_MAP['jw.api'] + language + '?'	
	return self.perform_v1_request(path)
	

    def perform_v1_request(self, path='', language='E'):
	url = path + '/' + language + '?'
    	cats_raw = urllib2.urlopen(url).read().decode('utf-8')
	return json.loads(cats_raw)

    def get_jwt_token (self)
	if self._jwt_token == ''
		url = self.LOCAL_MAP['jw.token.api']
		token = urllib2.urlopen(url).read().decode('utf-8')
		self._jwt_token = token
	return self._jwt_token
