# -*- coding: utf-8 -*-
"""
    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import os
import sys
import json
import shutil
import socket
from base64 import b64decode
import urllib,urllib2,urlparse,base64
import web_pdb; 
	
from ..tvjworg.client import JWTV
from .. import kodion
from ..kodion.items import *
from ..kodion.impl.xbmc.xbmc_items import to_playback_item

import xbmc
import xbmcaddon																																																																																					
import xbmcvfs
import xbmcgui
import xbmcplugin
    
def get_json(url):
	data = urllib2.urlopen(url).read().decode('utf-8')
	return json.loads(data)

def get_best_video(file_ary, video_res):
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

    
def build_basic_listitem(file_data):
	vid = VideoItem(file_data['title'], file_data['video'], file_data['sqr_img'], file_data['wide_img']) #instead of sqr maybe can use wide
	vid.set_mediatype(file_data['type'])
	vid.set_duration_from_seconds(file_data['dur'])
	#xbmc.log(vid)	
	return vid




class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)
	self._client = JWTV( )
        
    def reset_client(self):
        self._client = None

    def get_client(self, context):
        if self._client is not None:
            return self._client
    	# return a new jwclient here   

    def on_root(self, context, re_match):
	language = context.get_settings().get_string('language', 'E')
	
    	categories = self._client.get_top_video_categories(language)

	result = []

    	for c in categories['categories']:
        	if 'WebExclude' not in c.get('tags', []):
       			cat_item = DirectoryItem(c.get('name'),  
                                      context.create_uri(['categories', c.get('key')]))
			result.append(cat_item)

	search_item = DirectoryItem('Search',  
                                      context.create_uri('search')) #params={'location': True})
    	
	result.append(search_item)

	return result

    def build_media_entries(self, context, file_ary):
	vids = []   
	video_res = context.get_settings().get_string('video_res')	 
	for v in get_video_metadata(file_ary, video_res):
		vids.append(build_basic_listitem(v))
	#xbmc.log(vids)        
	return vids
    


    @kodion.RegisterProviderPath('^/categories/(?P<sublevel>[^/]+)/$')
    def _on_sublevel(self, context, re_match):
        result = []
	sub_level = re_match.group('sublevel')
	isStreaming = False	
	if sub_level == "Streaming":
		isStreaming = True	
	language = context.get_settings().get_string('language', 'E')
	info = self._client.get_sub_categories(language, sub_level)
	if 'subcategories' in info['category']: 
		tmpdirs = self.build_folders(context, info['category']['subcategories'], isStreaming) # context
		result.extend(tmpdirs)

        if 'media' in info['category']: 
		tmpmedia = self.build_media_entries(context, info['category']['media']) #context
		result.extend(tmpmedia)
        return result
    
    @kodion.RegisterProviderPath('^/categories/streaming/(?P<sublevel>[^/]+)/$')
    def _on_streaming(self, context, re_match):
		#def get_video_metadata(file_ary, video_res, exclude_hidden=False):
	language = context.get_settings().get_string('language', 'E')
	info = get_json('https://data.jw-api.org/mediator/v1/schedules/' + language + '/Streaming')
	streammode = re_match.group('sublevel')
	video_res = context.get_settings().get_string('video_res')        
		
	for s in info['category']['subcategories']:
        	if s['key'] == streammode:
            		pl = xbmc.PlayList(1)
            		pl.clear()
            		for item in get_video_metadata(s['media'], video_res):
                		li = xbmcgui.ListItem(item['title'])
                		li.setArt({'icon': item['sqr_img'], 'thumb': item['sqr_img']})
                		pl.add(item['video'], li)
            		xbmc.Player().play(pl)
            		xbmc.Player().seekTime(s['position']['time'])
			return
	

    def build_folders(self, context, subcat_ary, isStreaming):
    	#isStreaming = mode[0] == 'Streaming'
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
		uri = context.create_uri(urilist)		
		diritem = DirectoryItem(s.get('name'), uri,
				image, fanart)		
		dirs.append(diritem)
	return dirs


    @kodion.RegisterProviderPath('^/search/$')
    def on_search(self, context, re_match):
    	kb = xbmc.Keyboard("", "-- Search -- ")
	kb.doModal()
	results = []
	if kb.isConfirmed():
        	search_string = kb.getText()
        	url = 'https://data.jw-api.org/search/query?'
        	query = urllib.urlencode({'q': search_string, 'lang': 'E', 'limit': 24})
        	headers = {'Authorization': 'Bearer ' + self.get_jwt_token(context)}
        	try:
            		info = get_json(urllib2.Request(url + query, headers=headers))
        	except urllib2.HTTPError as e:
            		if e.code == 401:
                		headers = {'Authorization': 'Bearer ' + self.get_jwt_token(context, True)}
                		info = get_json(urllib2.Request(url + query, headers=headers))
            		else:
                		raise
        	if 'hits' in info: 
				results.extend(self.build_search_entries(context, info['hits']))
	return results

    def build_search_entries(self, context, result_ary):
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

       		url = context.create_uri(['play', r['languageAgnosticNaturalKey'] ])
		viditem = VideoItem(title, url, img, fanart)
		results.append (viditem)
	return results

    def get_jwt_token(self, context, update=False):
    	token = context.get_settings().get_string('jwt_token', 'E')
    	if not token or update is True:
        	url = 'https://tv.jw.org/tokens/web.jwt'
       		token = urllib2.urlopen(url).read().decode('utf-8')
        	if token != '':
        	    context.get_settings().set_string('jwt_token', token)
	return token

 
    @kodion.RegisterProviderPath('^/play/(?P<video_key>[^/]+)/$')	
    def play_search_result(self, context, re_match):
    	video_key = re_match.group('video_key')
    	info = get_json('https://data.jw-api.org/mediator/v1/media-items/E/' + video_key)
	video_res = context.get_settings().get_string('video_res')    	
	video = get_best_video(info['media'][0]['files'], video_res)
	#vid = bool()    	
	if video:
		sqr_img = ''
		wide_img = ''
		r = info['media'][0]
		if 'sqr' in r['images']: sqr_img = r['images']['sqr'].get('md')
        	elif 'cvr' in r['images']: sqr_img = r['images']['cvr'].get('md')
        	if 'pnr' in r['images']: wide_img = r['images']['pnr'].get('md')
		return VideoItem(info['media'][0]['title'], video['progressiveDownloadURL'])

