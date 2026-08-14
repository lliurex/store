#!/usr/bin/python3
import json
from wdg.flowBar import QFlowBar
from random import shuffle
from lib import rss
from extras.constants import *

class choiBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.rss=rss.rssParser()
		self.rss.choiceEnded.connect(self._loadData)
		self.itemsPerPage=3
		self.spacing=15
		self.defaultSize=64
		self.overlay=False
		self.showScrollBar(True)
	#def __init__

	def loadChoice(self):
		self.rss.feed="lliurexnet"
		self.rss.start()
	#def loadChoice

	def _loadData(self,*args):
		feed,content=args
		appContent={}
		for idx,data in content.items():
			t=data.get("title")
			app=json.loads(self.rebost.showApp(data["title"]))
			if len(app)>0:
				data.update({"summary":"","metadata":app[0]["id"],"img":app[0]["icon"]})
				appContent[len(appContent)]=data
		cont=0
		apps=json.loads(self.rebost.searchApp("lliurex"))
		shuffle(apps)
		while cont<3:
			for app in apps:
				if app.get("forbidden",False)==True or app.get("unavailable",False)==True:
					continue
				if app["name"].startswith("zero-lliurex"):
					continue
				if len(app["name"])>20:
					continue
				appContent[len(appContent)]={"summary":"","metadata":app["id"],"img":app["icon"],"title":app["name"].strip()}
				cont+=1
		keys=list(appContent.keys())
		shuffle(keys)
		selectedContent={}
		for i in keys[0:min(5,len(keys))]:
			selectedContent[i]=appContent[i]
		bheight=self.defaultSize*2
		self.table.setRowHeight(0,bheight-SPACING)
		self.table.setFixedHeight(bheight+MARGIN)
		self.updateScreen(feed,selectedContent)
	#def _loadData
