#!/usr/bin/python3
import os,sys
from functools import partial
from PySide6.QtWidgets import QApplication,QGridLayout,QPushButton
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal
from QtExtraWidgets import QStackedWindowItem
from home import QHomePane
from apps import QAppsPane
from details import QDetailsPane
from wdg.prgBar import QProgressImage 
from extras.i18n import *
from rebost import store

RSRC="/usr/share/store/rsrc"

class portrait(QStackedWindowItem):
	beginLoad=Signal()
	stopLoad=Signal()
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
		self.beginLoad.connect(self._showProgress)
		self.stopLoad.connect(self._stopProgress)
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

	def _showProgress(self):
		return
		self.prgBar.start()
	#def _showProgress

	def _stopProgress(self):
		self.prgBar.stop()
	#def _stopProgress

	def _searchApps(self,*args):
		self.beginLoad.emit()
		self.paneHome.hide()
		self.paneApps.show()
		self.paneApps.load(args[0])
	#def _searchApps(self,*args):

	def _loadCategory(self,*args):
		self.beginLoad.emit()
		self.paneApps.load(args[0],category=True)
	#def _loadCategory

	def _goHome(self,*args):
		self.paneHome.show()
		self.paneApps.hide()
		self.paneDetails.hide()
	#def _goHome

	def _homePane(self):
		wdg=QHomePane(rebost=self.rebost)
		wdg.search.connect(self._searchApps)
		wdg.loadCategory.connect(self._loadCategory)
		return(wdg)
	#def _homePane

	def _appsLoaded(self):
		self.paneHome.hide()
		self.paneDetails.hide()
		self.paneApps.show()
		self.stopLoad.emit()
	#def _appsLoaded

	def _installApp(self,*args):
		self.paneHome.hide()
		self.paneDetails.show()
		self.paneDetails.load(args[0])
		self.paneApps.hide()
	#def _installApp

	def _appsPane(self):
		wdg=QAppsPane(rebost=self.rebost)
		wdg.requestInstall.connect(self._installApp)
		return(wdg)
	#def _appsPane

	def _detailsPane(self):
		wdg=QDetailsPane(rebost=self.rebost)
		return(wdg)
	#def _detailsPane

	def _defProgress(self):
		wdg=QProgressImage(self)
		wdg.inc=-1
		wdg.setImageFromFile(os.path.join(RSRC,"progressBar267x267.png"))
		wdg.lblInfo.hide()
		#wdg.setAttribute(Qt.WA_StyledBackground, False)
		wdg.animation="bigger"
		wdg.animation="pulsate"
		return(wdg)
	#def _defProgress

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.hideControlButtons()
		self.oldCursor=self.cursor()
		self.paneHome=self._homePane()
		self.paneApps=self._appsPane()
		self.paneApps.ready.connect(self._appsLoaded)
		self.paneDetails=self._detailsPane()
		self.prgBar=self._defProgress()
		lay.addWidget(self.paneHome,1,0,1,self.layout().columnCount())
		lay.addWidget(self.paneApps,1,0,1,self.layout().columnCount())
		lay.addWidget(self.paneDetails,1,0,1,self.layout().columnCount())
		lay.addWidget(self.prgBar,1,0,1,self.layout().columnCount())
		self.prgBar.hide()
		self.paneApps.hide()
		self.paneDetails.hide()
	#def __initScreen__

	def updateScreen(self,addEnable=None):
		#self._rebost.wait()
		return
	#def _updateScreen
