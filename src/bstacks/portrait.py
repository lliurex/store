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
from wdg.search import QSearch
from wdg.prgBar import QProgressImage 
from extras.i18n import *
from rebost import store

RSRC="/usr/share/store/rsrc"

class portrait(QStackedWindowItem):
	beginLoad=Signal("PyObject")
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
		self.previousPane=None
		self.currentPane=None
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

	def _showProgress(self,paneToLoad):
		self.currentPane=paneToLoad
		for pane in [self.paneHome,self.paneApps,self.paneDetails]:
			if pane.isVisible()==True:
				self.previousPane=pane
			pane.hide()
		if self.currentPane==self.paneApps:
			self.search.show()
			self.currentPane.show()
		else:
			self.prgBar.start()
			if self.currentPane==self.paneHome:
				self.search.hide()
	#def _showProgress

	def _stopProgress(self):
		if self.currentPane!=self.paneHome:
			self.search.show()
		if self.currentPane.isVisible()==False:
			self.currentPane.show()
		self.prgBar.stop()
	#def _stopProgress

	def _appsLoaded(self):
		self.stopLoad.emit()
	#def _appsLoaded

	def _loadCategory(self,*args):
		self.beginLoad.emit(self.paneApps)
		self.paneApps.load(args[0],category=True)
	#def _loadCategory

	def _detailsLoaded(self):
		self.paneHome.hide()
		self.paneApps.hide()
		self.paneDetails.show()
		self.stopLoad.emit()
	#def _detailssLoaded

	def _loadAppDetail(self,*args):
		self.beginLoad.emit(self.paneDetails)
		self.paneApps.blockSignals(True)
		self.paneDetails.load(args[0])
	#def _loadAppDetail

	def _loadAppDetailFromId(self,*args):
		self.beginLoad.emit(self.paneDetails)
		self.paneApps.blockSignals(True)
		self.paneDetails.loadFromId(args[0])
	#def _loadAppDetail

	def _goHome(self,*args):
		self.beginLoad.emit(self.paneHome)
		self.paneHome.show()
		self.search.hide()
		self.paneApps.hide()
		self.paneDetails.hide()
	#def _goHome

	def _searchApps(self,*args):
		if len(args[0])>1:
			if args[0]!=self.search.src.txtSearch.text():
				self.search.src.txtSearch.setText(args[0])
			self.beginLoad.emit(self.paneApps)
			self.paneApps.blockSignals(False)
			self.paneApps.load(args[0])
	#def _searchApps(self,*args):

	def _goPrevious(self,*args):
		self.previousPane.show()
		self.currentPane.hide()
		self.currentPane=self.previousPane
		if self.currentPane==self.paneApps:
			self.paneApps.blockSignals(False)
			self.previousPane=self.paneHome
		elif self.currentPane==self.paneHome:
			self.search.hide()
	#def _searchApps(self,*args):

	def _homePane(self):
		wdg=QHomePane(rebost=self.rebost)
		wdg.search.connect(self._searchApps)
		wdg.loadCategory.connect(self._loadCategory)
		wdg.requestInstall.connect(self._loadAppDetail)
		wdg.requestInstallFromId.connect(self._loadAppDetailFromId)
		return(wdg)
	#def _homePane

	def _appsPane(self):
		wdg=QAppsPane(rebost=self.rebost)
		wdg.requestInstall.connect(self._loadAppDetail)
		wdg.search.connect(self._searchApps)
		return(wdg)
	#def _appsPane

	def _detailsPane(self):
		wdg=QDetailsPane(rebost=self.rebost)
		wdg.search.connect(self._searchApps)
		return(wdg)
	#def _detailsPane

	def _defSearch(self):
		wdg=QSearch()
		wdg.requestSearch.connect(self._searchApps)
		wdg.goPrevious.connect(self._goPrevious)
		return(wdg)
	#def _defSearch

	def _defProgress(self):
		wdg=QProgressImage(self)
		wdg.inc=-1
		wdg.setImageFromFile(os.path.join(RSRC,"progressBar267x267.png"))
		wdg.lblInfo.hide()
		wdg.setAttribute(Qt.WA_StyledBackground, False)
		wdg.animation="bigger"
		return(wdg)
	#def _defProgress

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.hideControlButtons()
		self.oldCursor=self.cursor()
		self.search=self._defSearch()
		self.search.hide()
		lay.addWidget(self.search,0,0,1,self.layout().columnCount(),Qt.AlignCenter)
		self.paneHome=self._homePane()
		lay.addWidget(self.paneHome,1,0,1,self.layout().columnCount())
		self.paneApps=self._appsPane()
		self.paneApps.ready.connect(self._appsLoaded)
		self.paneApps.hide()
		lay.addWidget(self.paneApps,1,0,1,self.layout().columnCount())
		self.paneDetails=self._detailsPane()
		self.paneDetails.ready.connect(self._detailsLoaded)
		self.paneDetails.hide()
		lay.addWidget(self.paneDetails,1,0,1,self.layout().columnCount())
		self.prgBar=self._defProgress()
		self.prgBar.hide()
		lay.addWidget(self.prgBar,1,0,1,self.layout().columnCount())
	#def __initScreen__

	def updateScreen(self,addEnable=None):
		#self._rebost.wait()
		return
	#def _updateScreen
