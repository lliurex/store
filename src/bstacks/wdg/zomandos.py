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
		self.defaultSize=128
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

