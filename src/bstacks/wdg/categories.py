#!/usr/bin/python3
import json
from random import shuffle
from wdg.flowBar import QFlowBar
from lib import rss
from lib.helperLib import auxiliary

class catsBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.itemsPerPage=4
		self.overlay=False
		self.simpleButtons=True
		self.defaultSize=128
		self.spacing=10
		self.aux=auxiliary()
	#def __init__(self,*args):

	def loadCategories(self):
		cats=self.rebost.getFreedesktopCategories()
		data={}
		idx=0
		rndCats=list(cats.keys())
		shuffle(rndCats)
		for cat in rndCats:
			hcolor=self.aux.getRgbColorFromTxt(cat)
			data[idx]={"title":cat.capitalize(),"img":hcolor,"summary":"","description":""}
			idx+=1
		self.updateScreen("cats",data)
	#def loadCategories

