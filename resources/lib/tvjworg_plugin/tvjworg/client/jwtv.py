# -*- coding: utf-8 -*-
"""
    Copyright (C) 2014-2016 ossierivera (plugin.video.tvjworg)
    Copyright (C) 2016-2018 plugin.video.youtube
    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import copy

import requests

import urllib,urllib2,urlparse,base64
import json
import web_pdb 

def get_best_video(file_ary, video_res):
	video_res = [1080,720,480,360,240][int(video_res)]	
	videos = []
	for x in file_ary:
		try:
			if int(x['label'][:-1]) > video_res: continue
        	except (ValueError, TypeError):
        		if int(x['frameHeight']) > video_res: continue
        	videos.append(x)
    	videos = sorted(videos, reverse=True)
    	#if subtitles == 'false': videos = [x for x in videos if x['subtitled'] == False]
    	if len(videos) == 0: return None
	return videos[0]


def get_video_metadata(file_ary, video_res, exclude_hidden=False):
    videoFiles = []
    for r in file_ary:
        video = get_best_video(r['files'], video_res)
        if video is None: continue

        sqr_img = ''
        wide_img = ''
        if 'sqr' in r['images']: sqr_img = r['images']['sqr'].get('md')
        elif 'cvr' in r['images']: sqr_img = r['images']['cvr'].get('md')
        if 'pnr' in r['images']: wide_img = r['images']['pnr'].get('md')

        if r.get('type') == 'audio': media_type = 'music'
        else: media_type = 'video'

        video_file = {'id': r['guid'], 'video': video['progressiveDownloadURL'], 'wide_img': wide_img, 'sqr_img': sqr_img, 'title': r.get('title'), 'dur': r.get('duration'), 'type': media_type}
	videoFiles.append(video_file)
    return videoFiles


def build_folders(subcat_ary, isStreaming):
	dirs = []
	for s in subcat_ary:
		fanart = ''
		image = ''
		if 'rph' in s['images']:
			image = s['images']['rph'].get('md')
		if 'pnr' in s['images']:
			fanart = s['images']['pnr'].get('md')	
		urilist = ['categories']
		if (isStreaming):
			urilist.append('streaming')
		urilist.append(s.get('key'))		
		#uri = context.create_uri(urilist)		
		#diritem = DirectoryItem(s.get('name'), uri,
		#		image, fanart)		
		item_hsh = {'type':'directory', 'title':s.get('name'), 'url':urilist, 'sqr_img':image, 'wide_img':fanart}		
		dirs.append(item_hsh)
	return dirs
 
def build_media_entries(file_ary, res):
	vids = []   
	video_res = res #context.get_settings().get_string('video_res')	 
	return get_video_metadata(file_ary, video_res)

def get_json(url):
	data = urllib2.urlopen(url).read().decode('utf-8')
	return json.loads(data)

def build_search_entries(result_ary):
	results = []		
	for r in result_ary:
        	if 'WebExclude' in r.get('tags'):
            			continue

        	title = r['displayTitle']
        	img = ""
		fanart = ""
 
    		for i in r.get('images'):
            		if i.get('size') == 'md' and i.get('type') == 'sqr':
                		img = i.get('url')
            		if i.get('size') == 'md' and i.get('type') == 'pnr':
                		fanart =  i.get('url')
				
		results.append ({'title':title, 'languageAgnosticNaturalKey':r['languageAgnosticNaturalKey'], 'fanart':fanart})
	return results
  
class JWTV(object):
    LOCAL_MAP = {'jw.api': 'https://data.jw-api.org/mediator/v1/categories/',
                 'jw.search.api': 'https://data.jw-api.org/search/query?',
                 'jw.token.api': 'https://tv.jw.org/tokens/web.jwt',
                 'jw.streaming.api': 'https://data.jw-api.org/mediator/v1/schedules/',
		 'jw.media-items.api': 'https://data.jw-api.org/mediator/v1/media-items/'
                 }
    def __init__(self, language='E', items_per_page=24):
	#self._jwt_token = jwt_token        
	self._language = language
	self._items_per_page = items_per_page

    def get_language(self):
        return self._language

    def set_language(self, language='E'):
	self._language = language    
 
    def get_sub_categories(self, options): #language, sub_level, isStreaming):
	language = ''
	sub_level = ''
	isStreaming = ''	
	if options['language']: 
		language = options['language']
	else:
		language = 'E'
	
	sub_level = options['sub_level']
	isStreaming = options['isStreaming']
	video_res = options['video_res']
		
	 
 	
	path = self.LOCAL_MAP['jw.api'] + language + '/' + sub_level + '/' + '?&detailed=1'
	info = self.perform_v1_request(path)
	result = []	
	if 'subcategories' in info['category']: 
		tmpdirs = build_folders(info['category']['subcategories'], isStreaming) # context
		result.extend(tmpdirs)

        if 'media' in info['category']: 
		tmpmedia = build_media_entries(info['category']['media'], video_res) #take care of the res problem
		result.extend(tmpmedia)
        return result



    def get_top_video_categories(self, language='E'):        
	path = self.LOCAL_MAP['jw.api'] + language + '?'	
	categories = self.perform_v1_request(path)
	result = []	
	for c in categories['categories']:
        	if 'WebExclude' not in c.get('tags', []):
       			cat_item = (c.get('name'),  c.get('key'))
			result.append(cat_item)
	return result

    def get_streaming_schedule(self, options):
	language = options['language']
	video_res = options ['video_res']
	sub_level = options['sub_level']
	path = self.LOCAL_MAP['jw.streaming.api'] + language + "/Streaming"
	info = self.perform_v1_request(path)
	time_pos = ''	
	results = []
	for s in info['category']['subcategories']:
        	if s['key'] == sub_level:
        		for item in get_video_metadata(s['media'], video_res):
		        	results.append(item)		
			time_pos = s['position']['time']
	return (time_pos, results)		        

	

    def perform_v1_request(self, url=''):
    	cats_raw = urllib2.urlopen(url).read().decode('utf-8')
	return json.loads(cats_raw)

    def get_jwt_token (self):	
	url = self.LOCAL_MAP['jw.token.api']
	token = urllib2.urlopen(url).read().decode('utf-8')
	return token

    def search(self, options):
	token = options['token']
	language = options['language']
	query = options['query']
	if not token:
		token = self.get_jwt_token()
	url = self.LOCAL_MAP['jw.search.api']
	query = urllib.urlencode({'q': query, 'lang': language, 'limit': 24})
	headers = {'Authorization': 'Bearer ' + token}
	try: 
		info = self.perform_v1_request(urllib2.Request(url + query, headers=headers))
                #return (token, info)
	except urllib2.HTTPError as e:
        	if e.code == 401:
			token = self.get_jwt_token()
                	headers = {'Authorization': 'Bearer ' + token}
                	info = self.perform_v1_request(urllib2.Request(url + query, headers=headers))
			#return (token, info)
            	else:
                	raise
	# have info and token
	results = []	
	if ('hits' in info):
		results.extend(build_search_entries(info['hits']))
		return (token, results)
	else:
		return (token, [])

    def get_media_item(self, options):
	language= options['language']
	video_key = options['video_key']
	video_res = options['video_res']	
	url = self.LOCAL_MAP['jw.media-items.api'] + language + '/' + video_key
	info = self.perform_v1_request(url)
	#web_pdb.set_trace()
	video = get_best_video (info['media'][0]['files'] , video_res)
	dct = {'title': info['media'][0]['title']}
	video.update(dct)
	return video
	


