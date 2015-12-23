import sys, os
import urllib, urllib2
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import json
import requests
from bs4 import BeautifulSoup
from resources.lib import CMD
import thread
import datetime

base_url = sys.argv[0]

xbmc.log(str(sys))

addon_handle = int(sys.argv[1])
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'albums')

xbmc.log("addon_handle:"+str(addon_handle))
#Get web name
web = args.get('web', None)
command=args.get('command', None)

xbmc.log(str(args))
xbmc.log(xbmc.translatePath(addon.getAddonInfo('profile')))
#List Website

#Functions
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def addTumblrID():
	dialog = xbmcgui.Dialog()
	id=dialog.input('Enter Tumblr ID', type=xbmcgui.INPUT_ALPHANUM)
	tumblrIDs=xbmcaddon.Addon().getSetting("tumblrIDs")+id+";"
	xbmcaddon.Addon().setSetting("tumblrIDs",tumblrIDs)	
	li = xbmcgui.ListItem("Next")		
	
	#xbmc.log(args.get('addon_handle', None)[0])
	#xbmcplugin.addDirectoryItem(handle=int(args.get('addon_handle', None)[0]), url="", listitem=li, isFolder=True)	
	
def removeID(id):
	tumblrIDs=xbmcaddon.Addon().getSetting("tumblrIDs").split(";")
	newTumblrIDs=""
	for i in tumblrIDs:
		xbmc.log(str(i)+":"+str(id))
		if (i!=id)and(i!=""):
			newTumblrIDs=newTumblrIDs+i+";"
	xbmcaddon.Addon().setSetting("tumblrIDs",newTumblrIDs)		
	li = xbmcgui.ListItem("Next")		
	xbmcplugin.addDirectoryItem(handle=addon_handle, url="", listitem=li, isFolder=True)

def view(url, page):
	if page==1:
		li = xbmcgui.ListItem("Random")	
		url_next=build_url({"command":"view_random", "tumblrURL":url})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_next, listitem=li, isFolder=True)
	r = requests.get(url+'/page/'+str(page))
	html = r.text		
	soup = BeautifulSoup(html)		
	imgs=soup.findAll('img')
	urls=[]
	for img in imgs:
		img_src=img.get('src')
		if img_src.find('media.tumblr.com')>=0:
			if img_src.find('media.tumblr.com/avatar')==-1:
				urls.append(img_src)					
				
	#temp_path=xbmc.translatePath(addon.getAddonInfo('profile'))
	
	CMD.addDirectoryItem_Images(addon_handle, urls, xbmc.translatePath(addon.getAddonInfo('profile')))	
	
	li = xbmcgui.ListItem("Next(%s)" % str(page+1))	
	url_next=build_url({"command":"view", "tumblrURL":url, "page":str(page+1)})
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_next, listitem=li, isFolder=True)
	
	li = xbmcgui.ListItem("Next(%s)" % str(page+9))	
	url_next=build_url({"command":"view", "tumblrURL":url, "page":str(page+9)})
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_next, listitem=li, isFolder=True)

	
def view_random(url):
	urls=[]
	for i in range(1,20):	
		r = requests.get(url+'/random')
		html = r.text		
		soup = BeautifulSoup(html)		
		imgs=soup.findAll('img')			
		for img in imgs:
			img_src=img.get('src')
			if img_src.find('media.tumblr.com')>=0:
				if img_src.find('media.tumblr.com/avatar')==-1:
					urls.append(img_src)
	CMD.addDirectoryItem_Images(addon_handle, urls, xbmc.translatePath(addon.getAddonInfo('profile')))
	xbmc.log(str(urls))
	li = xbmcgui.ListItem("Random")	
	url_next=build_url({"command":"view_random", "tumblrURL":url})
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_next, listitem=li, isFolder=True)
	
	
def view_list_tumblr():
	xbmc.log(xbmcaddon.Addon().getSetting("tumblrIDs"))
	tumblrIDs=xbmcaddon.Addon().getSetting("tumblrIDs").split(";")
	xbmc.log(str(tumblrIDs))
	for id in tumblrIDs:
		if (id!=""):
			li = xbmcgui.ListItem(id)	
			li.setIconImage('https://api.tumblr.com/v2/blog/%s.tumblr.com/avatar' % id)
			url=build_url({"command":"view", "tumblrURL":'http://'+id+".tumblr.com", "page":"1"})
			li.addContextMenuItems([
				('Remove', 'XBMC.RunPlugin(%s)' % CMD.build_url(base_url,{'command':'remove','id':id}),)])
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
			
	li = xbmcgui.ListItem("Add")	
	url=build_url({"command":"addTumblrID","addon_handle":str(addon_handle)})
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
	xbmcplugin.endOfDirectory(addon_handle)			
#Main:
if command==None:
	view_list_tumblr()	
elif command!=None:
	if command[0]=='view':
		url=args.get('tumblrURL')[0]
		page=int(args.get('page')[0])
		view(url, page)
	elif command[0]=='view_random':
		url=args.get('tumblrURL')[0]
		view_random(url)
	elif command[0]=='addTumblrID':
		addTumblrID()		
		xbmc.executebuiltin("Container.Refresh")		
	elif command[0]=='remove':
		id=args.get('id')[0]
		removeID(id)	
		xbmc.executebuiltin("Container.Refresh")
	xbmc.executebuiltin('Container.SetViewMode(514)')
	xbmcplugin.endOfDirectory(addon_handle)		