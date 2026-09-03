#!/usr/bin/python3
import os,sys
from functools import partial
from PySide6.QtWidgets import QApplication,QGridLayout,QPushButton,QMessageBox
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal
from QtExtraWidgets import QStackedWindowItem
from home import QHomePane
from apps import QAppsPane
from details import QDetailsPane
from wdg.search import QSearch
from wdg.prgBar import QProgressImage 
from lib.helperLib import appHelper
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
		self.appHelper=appHelper()
		self.appHelper.procEnded.connect(self._procEnded)
		self.previousPane=[]
		self.currentPane=None
		self.beginLoad.connect(self._showProgress)
		self.stopLoad.connect(self._stopProgress)
		self.destroyed.connect(partial(portrait._onDestroy,self.__dict__))
		self.actionBtns=[]
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
		if self.currentPane!=None:
			if self.currentPane not in self.previousPane:
				self.previousPane.append(self.currentPane)
		self.currentPane=paneToLoad
		for pane in [self.paneHome,self.paneApps,self.paneDetails]:
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

	def _homeLoaded(self):
		self.paneHome.flowZmds.loadZomandos()
		self.stopLoad.emit()
		if self.paneDetails.isVisible()==True:
			self.currentPane=self.paneDetails
		else:
			self.currentPane=self.paneHome
	#def _homeLoaded

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
	#def _loadAppDetailFromId

	def _goHome(self,*args):
		self.beginLoad.emit(self.paneHome)
		self.paneHome.show()
		self.search.hide()
		self.paneApps.hide()
		self.paneDetails.hide()
	#def _goHome

	def _procEnded(self,*args):
		app=args[0]["id"]
		detailApp=self.paneDetails.app["id"]
		rapp=self.rebost.refreshApp(app)
		if app==detailApp:
			self.paneDetails.refreshApp(rapp)
		currentBtns=[]
		for btn in self.actionBtns:
			if hasattr(btn,"app"):
				if btn.app["id"]==app:
					btn.refreshApp(rapp)
					continue
			currentBtns.append(btn)
		self.actionsBtns=currentBtns
	#def _procEnded

	def _launchEpi(self,*args):
		self.actionBtns.append(self.paneDetails.btn)
		self.appHelper.runZmd(args[0],args[1],pxm=args[2])
	#def _launchEpi

	def _launchApp(self,*args):
		self.appHelper.runApp(args[0],args[1],pxm=args[2])
	#def _launchApp

	def _searchApps(self,*args):
		if len(args[0])>1:
			if args[0]!=self.search.src.txtSearch.text():
				self.search.src.txtSearch.setText(args[0])
			self.beginLoad.emit(self.paneApps)
			self.paneApps.blockSignals(False)
			self.paneApps.load(args[0].replace("#",""))
	#def _searchApps(self,*args):

	def _goPrevious(self,*args):
		if len(self.previousPane)>0:
			self.currentPane.hide()
			self.currentPane=self.previousPane.pop()
		if self.currentPane==self.paneApps:
			self.paneApps.blockSignals(False)
		elif self.currentPane==self.paneHome:
			self.search.hide()
		if self.currentPane==None:
			self.currentPane=self.paneHome
		self.currentPane.show()
	#def _goPrevious

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
		wdg.requestLaunch.connect(self._launchApp)
		wdg.requestInstall.connect(self._launchEpi)
		wdg.requestRemove.connect(self._launchEpi)
		wdg.search.connect(self._searchApps)
		wdg.loadCategory.connect(self._loadCategory)
		return(wdg)
	#def _detailsPane

	def keyPressEvent(self,*args):
		if self.search.hasFocus()==False:
			self.search.src.txtSearch.setFocus()
			if args[0].text().strip()!="":
				self.search.src.setText(args[0].text().strip())
	#def keyPressEvent

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

	def _rebostException(self,*args):
		self.prgBar.updateTimer.stop()
		dlg=QMessageBox()
		dlg.setIcon(QMessageBox.Critical)
		dlg.setText(i18n["ERRDBUS"])
		dlg.setWindowTitle("Botiga")
		dlg.exec_()
		sys.exit(1)
	#def _rebostException

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.hideControlButtons()
		self.oldCursor=self.cursor()
		self.search=self._defSearch()
		self.search.hide()
		lay.addWidget(self.search,0,0,1,self.layout().columnCount(),Qt.AlignCenter)
		self.prgBar=self._defProgress()
		lay.addWidget(self.prgBar,1,0,1,self.layout().columnCount())
		self.paneHome=self._homePane()
		self.paneHome.ready.connect(self._homeLoaded)
		self.paneHome.exception.connect(self._rebostException)
		lay.addWidget(self.paneHome,1,0,1,self.layout().columnCount())
		#self.paneHome.hide()
		self.paneApps=self._appsPane()
		self.paneApps.ready.connect(self._appsLoaded)
		self.paneApps.hide()
		lay.addWidget(self.paneApps,1,0,1,self.layout().columnCount())
		self.paneDetails=self._detailsPane()
		self.paneDetails.ready.connect(self._detailsLoaded)
		self.paneDetails.hide()
		lay.addWidget(self.paneDetails,1,0,1,self.layout().columnCount())
		self._showProgress(self.paneHome)
	#def __initScreen__

	def updateScreen(self,addEnable=None):
		self.paneHome.blockSignals(False) #Is blocked by stacked events, unblock or die
		self.paneHome.load()
		self.paneHome.blockSignals(False) #Is blocked by stacked events, unblock or die
		#self._rebost.wait()
		return
	#def _updateScreen
