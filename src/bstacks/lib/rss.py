#!/usr/bin/python3
from PySide6.QtCore import Signal,QThread
import os,json,time
import feedparser
from bs4 import BeautifulSoup as bs
import urllib
from urllib.request import Request

class rssParser(QThread):
	appsEnded=Signal("PyObject","PyObject")
	blogEnded=Signal("PyObject","PyObject")
	recsEnded=Signal("PyObject","PyObject")
	choiceEnded=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.dbg=True
		self.rss={"blog":"https://portal.edu.gva.es/blogs/s1/lliurex/feed/",
				"appsedu":"https://portal.edu.gva.es/appsedu/feed/"}
		self.webpage={"lliurexnet":"https://portal.edu.gva.es/lliurex/va/",
				"receipts":"https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Receptes+LliureX+25"}
		self.feed="blog"
		self.cache=os.path.join(os.environ["HOME"],".cache","store","feeds")
		if os.path.exists(self.cache)==False:
			try:
				os.makedirs(self.cache)
			except:
				self.cache="/tmp/store"
				os.makedirs(self.cache)
		self._stop=False
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("rss: {}".format(msg))
	#def _debug

	def _fetchArticle(self,url):
		content=''
		req=Request(url)#, headers={'User-Agent':'Mozilla/5.0'})
		try:
			with urllib.request.urlopen(req,timeout=4) as f:
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
						if link==None:
							continue
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
					img=articleImg.get("src","")
					parsedFeeds[idx].update({"img":img})
					break
			if self._stop==True:
				break
		return parsedFeeds
	#def _getImgsForFeeds

	def run(self):
		feed=self.feed
		self.loadCache()
		parsedFeeds={}
		if feed in self.rss.keys():
			try:
				fparse=feedparser.parse(self.rss[feed])
			except Exception as e:
				print("Error parsing {}: {}".format(feed,e))
				fparse={}
			if len(fparse)>0:
				for item in fparse["items"]:
					if feed=="blog":
						idx=len(parsedFeeds)
						links=item.get("links",[""])[0]
						parsedFeeds.update({str(idx):{"type":feed,"title":item.get("title",""),"summary":item.get("summary",""),"link":links.href}})
					elif feed=="wiki":
						idx=len(parsedFeeds)
						links=item.get("links",[""])[0]
						parsedFeeds.update({str(idx):{"type":feed,"title":item.get("title",""),"summary":"","img":(0,0,0),"link":links.href}})
					else:
						lastApps=self._getLastApps(item.get("content"))
						for app,link in lastApps:
							idx=len(parsedFeeds)
							parsedFeeds.update({str(idx):{"type":feed,"title":app,"link":link}})
					if self._stop==True:
						break
			if len(parsedFeeds)>0 and feed!="wiki":
				parsedFeeds=self._getImgsForFeeds(parsedFeeds)
		elif self.feed in self.webpage.keys():
			rawcontent=self._fetchArticle(self.webpage[feed])
			bsContent=bs(rawcontent,"html.parser")
			if self.feed=="lliurexnet":
				carousel=bsContent.find_all("li",class_="glide__slide")
				idx=0
				for item in carousel:
					links=item.find("a",href=True)
					img=item.find("img")
					title=links["href"].removesuffix("/").split("/")[-1]
					parsedFeeds.update({str(idx):{"type":feed,"title":title,"link":links["href"],"img":img["src"]}})
					idx+=1
			else:
				entries=bsContent.find("ul",{"id":"drilldownmenu0"})
				idx=0
				for entry in entries:
					for li in entry.find_all("li",class_="menuLevel2"):
						if "dropdown" in li["class"]:
							continue
						links=entry.find_all("a",href=True)
						for link in links:
							print(link)
					links=entry.find("a",href=True)
					print("-----------------------------------------------------")
		self._emitContent(feed,parsedFeeds)
		self._writeCache(feed,parsedFeeds)
		self._stop=False
	#def run

	def _emitContent(self,feed,contents):
		if feed=="blog":
			self.blogEnded.emit(self.rss[feed],contents)
		elif feed=="receipts":
			self.recsEnded.emit(feed,contents)
		elif feed=="appsedu":
			self.appsEnded.emit(self.rss[feed],contents)
		elif feed=="lliurexnet":
			self.choiceEnded.emit(feed,contents)
	#def _emitContent

	def loadCache(self):
		self._debug("Cache: {}".format(self.cache))
		fCache=os.path.join(self.cache,self.feed)
		if os.path.exists(fCache):
			jcontent={}
			try:
				with open(fCache,"r") as f:
					jcontent=json.loads(f.read())
			except:
				print("Reading {}/{} error!!".format(self.cache,feed))
			else:
				if len(jcontent)>0:
					self._debug("Content for {0} loaded {1}".format(self.feed,fCache))
					self._emitContent(self.feed,jcontent)
	#def _loadCache

	def _writeCache(self,feed,content):
		if len(content)>0:
			try:
				with open(os.path.join(self.cache,feed),"w") as f:
					f.write(json.dumps(content))
			except Exception as e:
				print("Writing {}/{} error!!".format(self.cache,feed))
				print(e)
	#def _writeCach

	def stop(self):
		self._stop=True
#class rssParse

