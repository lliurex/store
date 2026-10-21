#!/usr/bin/python3
import json
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame
from wdg.flowBar import QFlowBar
from random import shuffle
from lib import rss
from extras.constants import *

class suggestsBar(QFlowBar):
	ready=Signal()
	exception=Signal(str)
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.setFrameShape(QFrame.NoFrame)
		self.itemsPerPage=4
		self.spacing=20
		self.defaultSize=36
		self.overlay=False
		self.loadImgSync=True
		self.showScrollBar(True)
		self.feed="suggests"
	#def __init__

	def _thException(self,*args):
		self.exception.emit(*args)
	#def _thException

	def loadSuggests(self,apps):
		shuffle(apps)
		if apps==None or isinstance(apps,list)==False:
			return
		apps=apps[0:min(5,len(apps))]
		newApps={}
		while len(apps)>0:
			app=apps.pop()
			t=app["name"].strip()
			if app.get("hidden",False)==True or app.get("forbidden",False)==True or app.get("unavailable",False)==True:
				continue
			if app["name"].startswith("zero-lliurex"):
				continue
			if len(app["name"])>20:
				continue
			newApps[len(newApps)+len(self.content)]={"summary":"","metadata":app["id"],"img":app["icon"],"title":t}
		self.content.update(newApps)
		keys=list(self.content.keys())
		shuffle(keys)
		selectedContent={}
		for i in keys[0:min(10,len(keys))]:
			selectedContent[i]=self.content[i]
		bheight=self.defaultSize*2
		self.updateScreen(self.feed,selectedContent)
		self.table.setRowHeight(0,bheight-MARGIN)
		self.table.setFixedHeight(bheight+MARGIN*2)
		self.ready.emit()
	#def _endLoadData

