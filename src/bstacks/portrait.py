#!/usr/bin/python3
import os,sys
from functools import partial
from PySide6.QtWidgets import QApplication,QGridLayout,QPushButton
from PySide6 import QtGui
from PySide6.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem
from home import QHomePane
from apps import QAppsPane
from wdg.topBar import QTopBar
from wdg.prgBar import QProgressImage 
from extras.i18n import *
from rebost import store

class portrait(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=True
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.rebost=store.client()
		self.destroyed.connect(partial(portrait._onDestroy,self.__dict__))
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		return
		selfDict["_rebost"].blockSignals(True)
		selfDict["_rebost"].requestInterruption()
		selfDict["_rebost"].quit()
		selfDict["_rebost"].wait()
		selfDict["_llxup"].blockSignals(True)
		selfDict["_llxup"].quit()
		selfDict["_llxup"].wait()
		selfDict["progress"].blockSignals(True)
		selfDict["progress"].stop()
	#def _onDestroy

	def _debug(self,msg):
		if self.dbg==True:
			print("Main: {}".format(msg))
	#def _debug

	def _chkNetwork(self):
		state=False
		if self.noChkNetwork==True:
			state=True
		else:
			state=helper.chkNetwork()
		return(state)
	#def _chkNetwork

	def _searchApps(self,*args):
		self.paneHome.hide()
		self.paneApps.setVisible(True)
		self.paneApps.load(args[0])
	#def _searchApps(self,*args):

	def _topBar(self):
		wdg=QTopBar()
		for chld in wdg.children():
			if isinstance(chld,QPushButton):
				chld.setText(i18n.get(chld.property("name"),chld.property("name")))
		wdg.loadHome.connect(self._goHome)
		wdg.loadNews.connect(print)
		wdg.loadRecs.connect(print)
		wdg.loadZmds.connect(print)
		wdg.loadCats.connect(print)
		return (wdg)
	#def _topBar

	def _goHome(self,*args):
		self.paneHome.show()
		self.paneApps.hide()

	def _homePane(self):
		wdg=QHomePane(rebost=self.rebost)
		wdg.search.connect(self._searchApps)
		return(wdg)
	#def _homePane

	def _appsPane(self):
		wdg=QAppsPane(rebost=self.rebost)
		return(wdg)
	#def _appsPane

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.hideControlButtons()
		self.oldCursor=self.cursor()
		self.paneHome=self._homePane()
		self.paneApps=self._appsPane()
		topBar=self._topBar()
		lay.addWidget(topBar,0,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		lay.addWidget(self.paneHome,1,0,1,self.layout().columnCount())
		lay.addWidget(self.paneApps,1,0,1,self.layout().columnCount())
		self.paneApps.hide()
	#def __initScreen__

	def _defProgress(self):
		wdg=QProgressImage(self)
		wdg.inc=-1
		wdg.setImageFromFile(os.path.join(RSRC,"progressBar267x267.png"))
		wdg.animation="bigger"
		wdg.animation="pulsate"
		return(wdg)
	#def _defProgress

	def updateScreen(self,addEnable=None):
		#self._rebost.wait()
		return
	#def _updateScreen
