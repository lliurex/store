#!/usr/bin/python3
import json
from random import shuffle
from wdg.flowTable import QFlowTable
from lib import rss
from lib.helperLib import auxiliary
from lib.threadLib import rebostQuery
import gettext
_ = gettext.gettext

class catsBar(QFlowTable):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowTable.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.rebostQuery=rebostQuery(rebost=self.rebost)
		self.rebostQuery.queryCompleted.connect(self._load)
		self.itemsPerPage=4
		self.overlay=False
		self.simpleButtons=True
		self.defaultSize=128
		self.spacing=10
		self.aux=auxiliary()
	#def __init__(self,*args):

	def _load(self,catsDict):
		cats=list(catsDict.keys())
		self._endLoad(cats)
	#def _load(self,catsDict):

	def _endLoad(self,cats):
		shuffle(cats)
		data={}
		idx=0
		for cat in cats:
			hcolor=self.aux.getRgbColorFromTxt(cat)
			data[idx]={"title":_(cat).capitalize(),"img":hcolor,"summary":"","description":"","metadata":cat}
			idx+=1
		self.updateScreen("cats",data)
	#def _load(self,cats)

	def loadCategories(self,cats=None):
		if cats==None:
			self.rebostQuery.setQuery("getFreedesktopCategories")
			self.rebostQuery.start()
		else:
			self._endLoad(cats)
		zmds=json.loads(self.rebost.getAppsInCategory("zomando"))["zomando"]
		data={}
		idx=0
		rndZmds=zmds
		shuffle(rndZmds)
		for zmd in rndZmds:
			summ=""
			if zmd["name"].lower() not in zmd["summary"].lower():
				summ=zmd["name"]
			if summ!="":
				summ+=": {}".format(zmd["summary"].capitalize())
			else:
				summ=zmd["summary"]
			if zmd["description"]!="" and summ==zmd["name"]:
				summ=zmd["description"].replace("\n","<br>").capitalize()
				
			data[idx]={"title":zmd["name"].capitalize(),
				"img":zmd["icon"],
				"summary":"<p align=\"left\"><strong>{}</p></strong>".format(summ.capitalize()),
				"description":"<p><strong>{}</p></strong>".format(zmd["description"]),
				"metadata":zmd["id"]
				}
			idx+=1
		self.updateScreen("zmds",data)
	#def loadCategories

