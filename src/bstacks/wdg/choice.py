#!/usr/bin/python3
import json
from PySide6.QtCore import Signal
from wdg.flowBar import QFlowBar
from random import shuffle
from lib import rss
from lib.threadLib import rebostQuery
from extras.constants import *

class choiBar(QFlowBar):
	ready=Signal()
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.rebostQuery=rebostQuery(rebost=self.rebost)
		self.rebostQuery.queryCompleted.connect(self._processQueryResult)
		self.rss=rss.rssParser()
		self.rss.choiceEnded.connect(self._beginLoadData)
		self.itemsPerPage=3
		self.spacing=15
		self.defaultSize=64
		self.overlay=False
		self.loadImgSync=True
		self.showScrollBar(True)
	#def __init__

	def loadChoice(self):
		self.rss.feed="lliurexnet"
		self.rss.start()
	#def loadChoice

	def _loadAppData(self,*args):
		self.content={}
		for idx,app in args[0].items():
			if len(app)==0:
				continue
			t=app[0]["name"].strip()
			self.content[t.replace(" ","")]={"summary":"","metadata":app[0]["id"],"img":app[0]["icon"],"title":t}
		self.rebostQuery.setQuery("search","lliurex")
		self.rebostQuery.start()
	#def _loadAppData

	def _endLoadData(self,*args):
		apps=args[0]
		shuffle(apps)
		cont=0
		while cont<3:
			for app in apps:
				if app.get("forbidden",False)==True or app.get("unavailable",False)==True:
					continue
				if app["name"].startswith("zero-lliurex"):
					continue
				if len(app["name"])>20:
					continue
				t=app["name"].strip()
				self.content[t.replace(" ","")]={"summary":"","metadata":app["id"],"img":app["icon"],"title":t}
				cont+=1
		keys=list(self.content.keys())
		shuffle(keys)
		selectedContent={}
		for i in keys[0:min(5,len(keys))]:
			selectedContent[i]=self.content[i]
		bheight=self.defaultSize*2
		self.table.setRowHeight(0,bheight-SPACING)
		self.table.setFixedHeight(bheight+MARGIN)
		self.updateScreen(self.feed,selectedContent)
		self.ready.emit()
	#def _endLoadData

	def _processQueryResult(self,*args):
		if self.rebostQuery.query=="showApps":
			self._loadAppData(*args)
		elif self.rebostQuery.query=="search":
			self._endLoadData(*args)
	#def _processQueryData

	def _beginLoadData(self,*args):
		#don't reload
		if self.rebostQuery.query=="search":
			return
		self.feed,self.content=args
		showApps=[]
		showApps=[title.get("title") for title in self.content.values()]
		self.rebostQuery.setQuery("showApps",showApps)
		self.rebostQuery.start()
	#def _beginLoadData
