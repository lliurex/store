#!/usr/bin/python3
import json
from random import shuffle
from wdg.flowBar import QFlowBar

class zmdsBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.zmdDir="/usr/share/zero-center/zmds"
		self.appDir="/usr/share/zero-center/applications"
		self.itemsPerPage=2
		self.overlay=True
		self.onlyImg=True
		self.spacing=10
	#def __init__(self,*args):

	def loadZomandos(self):
		zmds=json.loads(self.rebost.getAppsInCategory("zomando"))["zomando"]
		data={}
		idx=0
		rndZmds=zmds
		shuffle(rndZmds)
		for zmd in rndZmds:
			data[idx]={"title":zmd["name"].capitalize(),"img":zmd["icon"],"summary":zmd["summary"],"description":zmd["description"]}
			idx+=1
		self.updateScreen("zmds",data)
	#def loadCategories

