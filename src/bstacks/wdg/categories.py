#!/usr/bin/python3
import json
from random import shuffle
from wdg.flowBar import QFlowBar
from lib import rss

class catsBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.itemsPerPage=4
		self.overlay=False
		self.simpleButtons=True
		self.spacing=10
	#def __init__(self,*args):

	def _getRgbColorFromCat(self,cat):
		rgb=0
		hcat=hash(cat)
		rgb=abs(hcat)
		b = (rgb >> 16) & 0xFF
		g = (rgb >> 8) & 0xFF
		r = rgb & 0xFF
		gamma=(r+g+b)/3
		if gamma>200: 
			r=min(255,r*0.8)
			g=min(255,g*0.8)
			b=min(255,b*0.8)
		return "#{:02X}{:02X}{:02X}".format(int(r),int(g),int(b))
	#def _getRgbColorFromCat

	def loadCategories(self):
		cats=self.rebost.getFreedesktopCategories()
		data={}
		idx=0
		rndCats=list(cats.keys())
		shuffle(rndCats)
		for cat in rndCats:
			hcolor=self._getRgbColorFromCat(cat)
			data[idx]={"title":cat.capitalize(),"img":hcolor,"summary":"","description":""}
			idx+=1
		self.updateScreen("cats",data)
	#def loadCategories

