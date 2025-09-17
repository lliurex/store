#!/usr/bin/python3
from PySide6.QtCore import Signal,QThread
import feedparser
from bs4 import BeautifulSoup as bs
import urllib
from urllib.request import Request

class rssParser(QThread):
	rssEnded=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.dbg=True
		self.rss={"blog":"https://portal.edu.gva.es/blogs/s1/lliurex/feed/",
				"appsedu":"https://portal.edu.gva.es/appsedu/feed/"}
		self.feed="blog"
		self._stop=False
	#def __init__

	def _fetchArticle(self,url):
		content=''
		req=Request(url, headers={'User-Agent':'Mozilla/5.0'})
		try:
			with urllib.request.urlopen(req,timeout=2) as f:
				content=(f.read().decode('utf-8'))
		except Exception as e:
			print("Couldn't fetch {}".format(url))
			print("{}".format(e))
		return(content)
	#def _fetchCatalogue

	def _getLastApps(self,contents):
		lastApps=[]
		for content in contents:
			bsContent=bs(content.get("value","html.parser"),features="lxml")
			for strong in bsContent.find_all("strong", text="LliureX"):
				if strong==None:
					continue
				for ul in strong.parent.next_siblings:
					if ul.text.strip()=="":
						continue
					for li in ul.find_all("li"):
						link=li.find("a")
						lastApps.append((li.text.split("(")[0].strip(),link.get("href","")))
						if len(lastApps)>5:
							break
					break
					if len(lastApps)>5:
						break
				if self._stop==True:
					lastApps=[]
					break
				if len(lastApps)>5:
					break
			if len(lastApps)>5:
				break
		return(lastApps)
	#def _getLastApps

	def _getImgsForFeeds(self,parsedFeeds):
		for idx in parsedFeeds.keys():
			url=parsedFeeds[idx].get("link","")
			if url!="":
				rawcontent=self._fetchArticle(url)
				bscontent=bs(rawcontent,"html.parser")
				articleInfo=bscontent.find_all("div",class_="imagen-destacada")
				for info in articleInfo:
					articleImg=info.find("img")
					parsedFeeds[idx].update({"img":articleImg["src"]})
					break
			if self._stop==True:
				break
		return parsedFeeds
	#def _getImgsForFeeds

	def run(self):
		feed=self.feed
		parsedFeeds={}
		if feed in self.rss.keys():
			try:
				fparse=feedparser.parse(self.rss[feed])
			except Exception as e:
				print("Error: {}".format(e))
				fparse={}
			if len(fparse)>0:
				for item in fparse["items"]:
					if feed=="blog":
						idx=len(parsedFeeds)
						links=item.get("links",[""])[0]
						parsedFeeds.update({idx:{"type":feed,"title":item.get("title",""),"link":links.href}})
					else:
						lastApps=self._getLastApps(item.get("content"))
						for app,link in lastApps:
							idx=len(parsedFeeds)
							parsedFeeds.update({idx:{"type":feed,"title":app,"link":link}})
					if self._stop==True:
						break
		if len(parsedFeeds)>0:
			parsedFeeds=self._getImgsForFeeds(parsedFeeds)
		self.rssEnded.emit(self.rss[feed],parsedFeeds)
		self._stop=False
	#def run

	def stop(self):
		self._stop=True
#class rssParse

