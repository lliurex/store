#!/usr/bin/python3
import json
from wdg.flowBar import QFlowBar
from lib import rss

class choiBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.rss=rss.rssParser()
		self.rss.choiceEnded.connect(self._loadData)
		self.itemsPerPage=3
		self.spacing=25
		self.defaultSize=64
	#def __init__(self,*args):

	def loadChoice(self):
		self.rss.feed="lliurexnet"
		self.overlay=False
		self.showScrollBar(True)
		self.rss.loadCache()
		self.rss.start()
	#def loadChoice

	def _loadData(self,*args):
		feed,content=args
		for idx,data in content.items():
			t=data.get("title")
			app=json.loads(self.rebost.showApp(data["title"]))
			if len(app)>0:
				data.update({"summary":app[0]["description"]})
		self.updateScreen(feed,content)
	#def _loadData
