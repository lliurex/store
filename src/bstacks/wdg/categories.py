#!/usr/bin/python3
import json
from random import shuffle
from wdg.flowBar import QFlowBar
from lib import rss
from lib.helperLib import auxiliary
import gettext
_ = gettext.gettext

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

	def loadCategories(self,cats=None):
		if cats==None:
			catsDict=self.rebost.getFreedesktopCategories()
			cats=list(catsDict.keys())
		shuffle(cats)
		data={}
		idx=0
		for cat in cats:
			hcolor=self.aux.getRgbColorFromTxt(cat)
			data[idx]={"title":_(cat).capitalize(),"img":hcolor,"summary":"","description":"","metadata":cat}
			idx+=1
		self.updateScreen("cats",data)
	#def loadCategories

