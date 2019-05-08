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
#import web_pdb 
    
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

     
class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)
	self._client = JWTV( )
        
    def reset_client(self):
        self._client = None

    def get_client(self, context):
        if self._client is not None:
            return self._client
    	self._client = JWTV()
	return self._client  

    def on_root(self, context, re_match):
	language = context.get_settings().get_string('language', 'E')
	
    	categories = self._client.get_top_video_categories(language)

	result = []
	for item in categories:
		search_item = DirectoryItem(item[0], context.create_uri(['categories', item[1]]))
		result.append(search_item)
	
	result.append(DirectoryItem('Search', context.create_uri(['search'])))
	
	return result
	

    @kodion.RegisterProviderPath('^/categories/(?P<sublevel>[^/]+)/$')
    def _on_sublevel(self, context, re_match):
        result = []
	sub_level = re_match.group('sublevel')
	isStreaming = False	
	if sub_level == "Streaming":
		isStreaming = True	
	language = context.get_settings().get_string('language', 'E')
	video_res = context.get_settings().get_string('video_res')	
	options = {'language':language, 'sub_level':sub_level, 'isStreaming':isStreaming, 'video_res':video_res  }
	info = self._client.get_sub_categories(options)
	
        result = []
	for itm in info:
		if itm['type'] == 'directory':
			result.append( DirectoryItem(itm['title'], context.create_uri(itm['url']), itm['sqr_img'], itm['wide_img']))			
		else:
			vid = VideoItem(itm['title'], itm['video'], itm['sqr_img'], itm['wide_img'])
			vid.set_mediatype(itm['type'])
			vid.set_duration_from_seconds(itm['dur']) 
			result.append(vid)
	return result
    
    @kodion.RegisterProviderPath('^/categories/streaming/(?P<sublevel>[^/]+)/$')
    def _on_streaming(self, context, re_match):
		
	language = context.get_settings().get_string('language', 'E')
	
	#info = self._client.get_streaming_schedule(language)	
	streammode = re_match.group('sublevel')
	video_res = context.get_settings().get_string('video_res') 

	options = {'language':language, 'video_res':video_res  , 'sub_level': streammode  }        

	(time_pos, info) = self._client.get_streaming_schedule(options)

	
	pl = xbmc.PlayList(1)
	pl.clear()
	for itm in info:
		li = xbmcgui.ListItem(itm['title'])
		li.setArt({'icon': itm['sqr_img'], 'thumb': itm['sqr_img']})
		pl.add(itm['video'], li)
	xbmc.Player().play(pl)
	xbmc.Player().seekTime(time_pos)
	return 
		
	
    @kodion.RegisterProviderPath('^/search/$')
    def on_search(self, context, re_match):
    	kb = xbmc.Keyboard("", "-- Search -- ")
	kb.doModal()
	results = []
	options = {}
	if kb.isConfirmed():
        	search_string = kb.getText()
		language = context.get_settings().get_string('language', 'E')
		token = context.get_settings().get_string('jwt_token')
		options['language'] = language
		options['token'] = token
		options['query'] = search_string
		(token, info) = self._client.search(options)
		context.get_settings().set_string('jwt_token', token)    	
		
        	for i in info:
			url = context.create_uri(['play', i['languageAgnosticNaturalKey']])
			viditem = VideoItem(i['title'], url, i['fanart'])
			results.append(viditem)

	return results



    @kodion.RegisterProviderPath('^/play/(?P<video_key>[^/]+)/$')	
    def play_search_result(self, context, re_match):
    	video_key = re_match.group('video_key')
	language = context.get_settings().get_string('language', 'E')
	#info = self._client.get_media_item(language, video_key)	
	video_res = context.get_settings().get_string('video_res')    	
	#video = get_best_video(info['media'][0]['files'], video_res)
	
	#web_pdb.set_trace()
	video = self._client.get_media_item({'language':language, 'video_res': video_res, 'video_key':video_key})   	
	context.log_notice("_______________")
	context.log_notice(video)	
	context.log_notice("________________")

	if video:
		#sqr_img = ''
		#wide_img = ''
		#r = info['media'][0]
		#if 'sqr' in r['images']: sqr_img = r['images']['sqr'].get('md')
        	#elif 'cvr' in r['images']: sqr_img = r['images']['cvr'].get('md')
        	#if 'pnr' in r['images']: wide_img = r['images']['pnr'].get('md')
		#context.log_notice(video['title'], video['progressiveDownloadURL'])
		return VideoItem(video['title'], video['progressiveDownloadURL'])

