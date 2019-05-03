# -*- coding: utf-8 -*-
"""
    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import os
import json
import shutil
import socket
from base64 import b64decode
import urllib,urllib2,urlparse,base64
import web_pdb; 
	

from .. import kodion
#from ..kodion.utils import strip_html_from_text, get_client_ip_address, is_httpd_live, find_video_id
from ..kodion.items import *



import xbmc
import xbmcaddon																																																																																					
import xbmcvfs

    
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

        	#if 'WebExclude' in r['tags']:
        	#    if exclude_hidden: continue
        	#    file_data = b64_encode_object(video_file)
        	#    video_file = {'id': None, 'video': build_url({'mode': 'ask_hidden', 'file_data': file_data}), 'wide_img': None,
        	#          'sqr_img': None, 'title': __language__(30013), 'dur': None}

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
	self._client = None
        
    #@staticmethod
    #def get_dev_config(context, addon_id, dev_configs):
        

    def reset_client(self):
        self._client = None

    def get_client(self, context):
        if self._client is not None:
            return self._client
    	# return a new jwclient here   

    def on_root(self, context, re_match):
	language = context.get_settings().get_string('language', 'E')
	url = 'https://data.jw-api.org/mediator/v1/categories/' + language + '?'
    	cats_raw = urllib2.urlopen(url).read().decode('utf-8')
    	categories = json.loads(cats_raw)

	result = []

    	for c in categories['categories']:
        	if 'WebExclude' not in c.get('tags', []):
       			cat_item = DirectoryItem(c.get('name'),  
                                      context.create_uri(['categories', c.get('key')]))
			result.append(cat_item)

	search_item = DirectoryItem('Search',  
                                      context.create_uri('search')) #params={'location': True})
    	
	result.append(search_item)

	languages_item = DirectoryItem('-- Set Language --',  
                                      context.create_uri('setlanguage')) #params={'location': True})
	result.append(languages_item)
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
        #self.set_content_type(context, kodion.constants.content_type.FILES)
        result = []
	sub_level = re_match.group('sublevel')
	language = context.get_settings().get_string('language', 'E')
	info = get_json('https://data.jw-api.org/mediator/v1/categories/' + language + '/' + sub_level + '?&detailed=1')
    
	#media = []
	#dirs = []
        if 'subcategories' in info['category']: 
		tmpdirs = self.build_folders(context, info['category']['subcategories']) # context
		result.extend(tmpdirs)

        if 'media' in info['category']: 
		tmpmedia = self.build_media_entries(context, info['category']['media']) #context
		result.extend(tmpmedia)
        
   
        #result.append(dirs)
	#xbmc.log("media")	
	#xbmc.log(media)
	#result.extend(dirs)	
	#result.extend(media)

	#web_pdb.set_trace()
	return result


    def build_folders(self, context, subcat_ary):
    	#isStreaming = mode[0] == 'Streaming'
	dirs = []
	for s in subcat_ary:
		fanart = ''
		image = ''
		if 'rph' in s['images']:
			image = s['images']['rph'].get('md')
		if 'pnr' in s['images']:
			fanart = s['images']['pnr'].get('md')	
		#web_pdb.set_trace()
		uri = context.create_uri(['categories', s.get('key')])		
		diritem = DirectoryItem(s.get('name'), uri,
				image, fanart)		
		dirs.append(diritem)
	return dirs










    
	


   #xbmcplugin.setContent(addon_handle, 'movies')

   

  
   
