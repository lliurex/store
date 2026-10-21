#!/usr/bin/python3
import sys,time
from functools import partial
import os
import subprocess
import json
from PySide6.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHBoxLayout, QWidget,QVBoxLayout
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal
from QtExtraWidgets import QStackedWindowItem
from rebost import store 
from PySide6.QtWidgets import QApplication, QLineEdit,QLabel,QPushButton,QGridLayout,QHBoxLayout, QWidget,QVBoxLayout,QListWidget, \
							QListWidgetItem,QSizePolicy
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QStackedWindowItem
from wdg.btnRebost import QPushButtonRebostApp
from wdg.prgBar import QProgressImage 
from wdg.barButtons import QPushButtonBar
from wdg.barCategories import QToolBarCategories
from wdg.lblApp import QLabelRebostApp
from wdg.navCategories import QNavCategories
from wdg.wdgSearch import QSearch
import lib.helperLib as helper
from lib.libth import storeHelper,llxup
import extras.css as css
from extras.constants import *
from extras.i18n import *
import paneDetailView
import paneGlobalView
import paneHomeView
import paneErrorView

class portrait(QStackedWindowItem):
	requestGetApps=Signal(str)
	loadStart=Signal()
	loadStop=Signal()
	rebostToggled=Signal()
	def __init_stack__(self):
		self.init=False
		self.oldTime=0
		self.dbg=True
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.destroyed.connect(partial(portrait._onDestroy,self.__dict__))
		self.apps=[]
		self.helper=helper.appHelper()
		self.helper.procEnded.connect(self._procEnded)
		self.aux=helper.auxiliary()
		self.rc=store.client()
		self._referrerPane=None
		self._rebost=storeHelper(rc=self.rc)
		self._llxup=llxup()
		self._initThreads()
		self._initRegisters()
		self._initGUI()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Portrait: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
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

	def _initRegisters(self):
		#Catalogue related
		self.i18nCat={}
		self.oldCat=""
		self.catI18n={}
		self.apps={}
		self.appsToLoad=-1
		self.appsRaw=[]
		self.locked=True
		self._rebost.setAction("config")
		self._rebost.start()
		self.noChkNetwork=False
		self.isConnected=self.aux.chkNetwork()
		self.referrerBtn=None
	#def _initRegisters

	def _initThreads(self):
		self.requestGetApps.connect(self._getApps)
		self.loadStart.connect(self._progressShow)
		self.loadStop.connect(self._progressHide)
		self._llxup.chkEnded.connect(self._endGetUpgradables)
		self._rebost.lstEnded.connect(self._endLoadCategory)
		self._rebost.linEnded.connect(self._endLoadInstalled)
		self._rebost.srcEnded.connect(self._endSearchApps)
		self._rebost.rstEnded.connect(self._endReloadApps)
		self._rebost.cnfEnded.connect(self._endGetLockStatus)
		self._rebost.shwEnded.connect(self._loadFromArgs)
	#def _initThreads(self):

	def _initGUI(self):
		self.currentPane=None
		self.hideControlButtons()
		self.installingBtn=None
		self.oldCursor=self.cursor()
		self.setStyleSheet(css.portrait())
	#def _initGUI

	def _chkCategories(self,*args):
		if self.lstCategories.topLevelItemCount()<=0:
			self.lstCategories.load()
	#def _chkCategories

	def _endGetLockStatus(self,*args):
		self.locked,lockedUser=self.aux.getLockStatus(*args)
		if self.locked==False: #conf is unlocked, check groups 
			if lockedUser==True:
				self._unlockRebost()
		self.btnBar.setLocked(self.locked,lockedUser)
		self._debug("<-------- Rebost status acquired (lock {})".format(self.locked))
	#def _endGetLockStatus

	def _refreshBeforeInstall(self,app):
		install=False
		self._rebost.blockSignals(True)
		self._rebost.setAction("refreshApp",app["id"])
		app=json.loads(self._rebost._refreshApp())[0]
		self._rebost.blockSignals(False)
		if len(app["bundle"])>1:
			if "unknown" in app["bundle"]:
				app["bundle"].pop("unknown")
			install=True
			self.referrerBtn=self.installingBtn
			self.installingBtn=None
			self._installApp(self.referrerBtn,app)
		return(install)
	#def _refreshBeforeInstall

	def _installError(self,proc,app):
		if isinstance(proc,int)==False:
			if proc.returncode>1: #app is installed
				#pkexec ret values
				#127 -> Not authorized
				if proc.returncode==127:
					self.showMsg(title="LliureX Store",summary=app["name"],text=i18n.get("ERRUNAUTHORIZED"),icon=app["icon"],timeout=5000)
				else:
					self.showMsg(title="LliureX Store",summary=app["name"],text=i18n.get("ERRUNKNOWN"),icon=app["icon"],timeout=5000)
	#def _installError

	def _setInstallingState(self,app,state):
		app["state"]=state
		self._rebost.setAction("setAppState",app["id"],state)
		self._rebost.start()
		self._rebost.wait()
	#def _setInstallingState

	def _launchEpi(self,wdg,app,icon=""):
		#self.actionBtns.append(self.paneDetails.btn)
		if self.installingBtn!=None:
			self.showMsg(summary=i18n.get("ERRMORETHANONE",""),text=self.installingBtn.app["name"].capitalize(),timeout=4)
			return
		self.helper.runZmd(app,"",pxm=icon)
		self.installingBtn=wdg
	#def _launchEpi

	def _procEnded(self,*args):
		#self.installingBtn.updateScreen()
		app=args[0]
		self._rebost.blockSignals(True)
		self._rebost.setAction("refreshApp",app["id"])
		rapp=self._rebost._refreshApp(app["id"])
		rapp=self.aux.getAppFromString(rapp)
		self._rebost.blockSignals(False)
		bundle=self.helper.getInstalledBundle(rapp)#self._getInstalledBundle()
		if len(bundle)>0:
			self._setInstallingState(app,1)
		else:
			self._setInstallingState(app,2)
		if self._globalView.isVisible()==True:
			self._globalView.refreshBtnForApp(rapp)
		if self._detailView.isVisible()==True:
			self._detailView.refreshCmbForApp(rapp)
		self.installingBtn=None
	#def _procEnded

	def _progressShow(self):
		self.progress.start()
	#def _progressShow

	def _progressHide(self):
		self.progress.stop()
	#def _progressHide

	def _stopThreads(self,ignoreProgress=False):
		if self.appsToLoad==-1: #Init 
			exit
		self._rebost.blockSignals(True)
		self._rebost.requestInterruption()
		self._rebost.quit()
		self._rebost.wait()
		self._rebost.blockSignals(False)
		self._llxup.blockSignals(True)
		self._llxup.quit()
		self._llxup.wait()
		self._llxup.blockSignals(False)
		if ignoreProgress==False:
			self.loadStop.emit()
	#def _stopThreads

	def _closeEvent(self,*args):
		self._stopThreads()
	#def _closeEvent

	def keyPressEvent(self,*args):
		if self.searchBox.hasFocus()==False:
			self.searchBox.setFocus()
			if args[0].text().strip()!="":
				self.searchBox.setText(args[0].text().strip())
	#def keyPressEvent

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.box.setContentsMargins(0,0,0,0)
		self.box.setSpacing(0)
		self.sortAsc=False
		spacer=QLabel(" ")
		spacer.setAttribute(Qt.WA_StyledBackground, True)
		spacer.setStyleSheet("background:{};".format(COLOR_BACKGROUND_LIGHT))
		spacer.setFixedHeight(MARGIN*3)
		self.box.addWidget(spacer,0,1)
		self.navwdg=self._defNavigationPane()
		self.navwdg.setObjectName("wdg")
		self.box.addWidget(self.navwdg,0,0,5,1)
		self.searchBox=self._defSearch()
		self.box.addWidget(self.searchBox,1,1)
		spacer=QLabel(" ")
		spacer.setAttribute(Qt.WA_StyledBackground, True)
		spacer.setStyleSheet("background:{};".format(COLOR_BACKGROUND_LIGHT))
		spacer.setFixedHeight(MARGIN*4)
		self.box.addWidget(spacer,2,1)
		self.barCategories=self._defBarCategories()
		self.box.addWidget(self.barCategories,3,1,Qt.AlignTop)
		#self.barCategories.setMinimumHeight(MARGIN*6)
		self._homeView=self._getHomeViewPane()
		self.box.addWidget(self._homeView,4,1)
		self._globalView=self._getGlobalViewPane()
		self._globalView.hide()
		self.box.addWidget(self._globalView,4,1)
		self._detailView=self._getDetailViewPane()
		self.box.addWidget(self._detailView,4,1)
		self._detailView.hide()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		self.box.setColumnStretch(1,1)
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(1,0)
		self.box.setRowStretch(2,0)
		self.box.setRowStretch(3,0)
		self.box.setRowStretch(4,1)
		self.setObjectName("portrait")
		self._errorView=self._defError()
		self._errorView.setVisible(not(self.isConnected))
		self.box.addWidget(self._errorView,0,1,self.box.rowCount(),self.box.columnCount())
		self.progress=self._defProgress()
		self.progress.lblInfo.hide()
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
	#def __initScreen__

	def _defNavigationBar(self):
		wdg=QWidget()
		vbox=QVBoxLayout()
		wdg.setLayout(vbox)
		vbox.setContentsMargins(MARGIN*3,0,MARGIN*3,0)
		self.btnBar=QPushButtonBar()
		#self.certified=QPushButtonToggle()
		self.btnBar.toggleClicked.connect(self._unlockRebost)
		self.btnBar.homeClicked.connect(self._goHome)
		self.btnBar.installedClicked.connect(self._loadInstalled)
		self.btnBar.reloadClicked.connect(self._reloadApps)
		vbox.addWidget(self.btnBar,Qt.AlignCenter)
		self.lstCategories=QNavCategories(self._rebost)
		self.lstCategories.itemSelected.connect(self._loadCategory)
		vbox.addWidget(self.lstCategories,Qt.AlignTop|Qt.AlignCenter)
		vbox.setStretch(0,0)
		vbox.setStretch(1,2)
		vbox.setStretch(3,1)
		return(wdg)
	#def _defNavigationBar

	def _defBtnBar(self):
		wdg=QWidget()
		wdg.setObjectName("_defBtnBar")
		lay=QHBoxLayout()
		wdg.setLayout(lay)
		btnRefresh=self._defRefresh()
		btnRefresh.setObjectName("btnHome")
		lay.addWidget(btnRefresh,Qt.AlignRight)
		btnInst=self._defInst()
		btnInst.setObjectName("btnHome")
		lay.addWidget(btnInst,Qt.AlignLeft)
		btnRefresh.setFixedWidth(btnInst.sizeHint().width()+MARGIN)
		btnInst.setFixedWidth(btnInst.sizeHint().width()+MARGIN)
		return(wdg)
	#def _defBtnBar

	def _defBanner(self):
		lbl=QLabelRebostApp()
		lbl.setClickable(True)
		#lbl.setObjectName("banner")
		img=os.path.join(RSRC,"banner.svg")
		x=int(QApplication.primaryScreen().size().width()/6)
		y=int(x*9/16)
		pxm=QtGui.QPixmap(img).scaled(x,y,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		lbl.setPixmap(pxm)
		lbl.clicked.connect(self._goHome)
		return lbl
	#def _defBanner

	def _defNavigationPane(self):
		wdg=QWidget()
		#wdg.setObjectName("wdg")
		lay=QGridLayout()
		lay.setContentsMargins(0,MARGIN*3,0,0)
		wdg.setLayout(lay)
		self.sortAsc=False
		banner=self._defBanner()
		lay.addWidget(banner,0,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		_defBtnBar=self._defBtnBar()
		#lay.addWidget(_defBtnBar,1,0,1,1,Qt.AlignCenter)
		navBar=self._defNavigationBar()
		lay.addWidget(navBar,2,0,1,1)
		self.lblInfo=self._defInfo()
		if banner.pixmap().height()<90:
			lay.addWidget(self.lblInfo,0,0,1,1,Qt.AlignBottom)
		else:
			lay.addWidget(self.lblInfo,2,0,1,1,Qt.AlignBottom)
		navBar.setMinimumWidth(self.lblInfo.sizeHint().width())
		lay.setRowStretch(0,0)
		lay.setRowStretch(1,0)
		lay.setRowStretch(2,1)
		return(wdg)
	#def _defNavigationPane

	def _defBarCategories(self):
		wdg=QToolBarCategories()
		wdg.requestLoadCategory.connect(self._loadCategory)
		return(wdg)
	#def _defBarCategories

	def _unlockRebost(self,*args):
		self.resetScreen()
		self.loadStart.emit()
		self._rebost.setAction("lock")
		if self._rebost.isRunning():
			self._rebost.requestInterruption()
			self._rebost.wait()
		self._rebost.start()
		#self._rebost.wait()
		self._showPane(self._homeView)
		self.rebostToggled.emit()
		self.loadStop.emit()
	#def _unlockRebost

	def _defInst(self):
		btnInst=QPushButton(i18n.get("INSTALLED"))
		btnInst.clicked.connect(self._loadInstalled)
		btnInst.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		return(btnInst)
	#def _defInst

	def _defRefresh(self):
		btnRefresh=QPushButton(i18n.get("REFRESH"))
		btnRefresh.clicked.connect(self._reloadApps)
		btnRefresh.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		return(btnRefresh)
	#def _defRefresh

	def _launchLlxUp(self):
		self.parent.hide()
		subprocess.run(["pkexec","lliurex-up"])
		self.parent.show()
	#def _launchLlxUp

	def _defInfo(self):
		wdg=QPushButton(i18n.get("UPGRADES"))
		icn=QtGui.QIcon.fromTheme("lliurex-up")
		wdg.setIcon(icn)
		wdg.setObjectName("upgrades")
		wdg.clicked.connect(self._launchLlxUp)
		wdg.hide()
		wdg.setCursor(Qt.PointingHandCursor)
		return(wdg)
	#def _defInfo

	def _defError(self):
		pev=paneErrorView.paneErrorView()
		pev.requestLoadPortrait.connect(self._loadPortraitFromError)
		pev.setObjectName("errorMsg")
		return(pev)
	#def _defError

	def _resetSearch(self):
		self.searchBox.setText("")
		self.searchBox.setFocus()
	#def _resetSearch

	def _defSearch(self):
		wdg=QSearch()	
		wdg.setObjectName("wdgsearch")
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.requestSearch.connect(self._searchApps)
		return(wdg)
	#def _defSearch

	def _defProgress(self):
		wdg=QProgressImage(self)
		wdg.inc=-1
		wdg.setImageFromFile(os.path.join(RSRC,"progressBar267x267.png"))
		wdg.animation="pulsate"
		return(wdg)
	#def _defProgress

	def _getGlobalViewPane(self):
		gvp=paneGlobalView.paneGlobalView(self._rebost)
		gvp.requestLoadDetails.connect(self._loadGlobalDetails)
		gvp.requestInstallApp.connect(self._launchEpi)
		return(gvp)
	#def _getGlobalViewPane

	def _getDetailViewPane(self):
		dvp=paneDetailView.main(self._rebost)
		dvp.setObjectName("detailPanel")
		dvp.clickedBack.connect(self._returnFromDetail)
		dvp.loaded.connect(self._endLoadDetail)
		dvp.requestLoadTag.connect(self._loadTag)
		dvp.requestInstallApp.connect(self._launchEpi)
		return(dvp)
	#def _getDetailViewPane

	def _getHomeViewPane(self):
		hvp=paneHomeView.main(self._rebost)
		hvp.clickedApp.connect(self._loadHomeDetails)
		hvp.clickedCategory.connect(self._loadCategory)
		hvp.requestInstallApp.connect(self._launchEpi)
		return(hvp)
	#def _getHomeViewPane

	def _getApps(self,category="",installed=False):
		if category!="":
			self.resetScreen()
			self._globalView.getApps(category,installed)
	#def _getApps

	def _endGetUpgradables(self,*args):
		if args[0]==True:
			self.lblInfo.show()
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self._debug("Get available upgrades")
		self._llxup.start()
		#self._llxup.wait()
	#def _getUpgradables

	def _beginUpdate(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btnSettings.hide()
		if self.init==False:
			self.loadStart.emit()
		else:
			self._progressShow()
		self._homeView.hide()
	#def _beginUpdate

	def _endUpdate(self):
		self._return()
	#def _endUpdate

	def _goHome(self,*args,**kwargs):
		self._referrerPane=self._homeView
		self.resetScreen()
		self.lstCategories.unselectAll()
		self._showPane(self._homeView)
	#def _goHome

	def _reloadApps(self,*args,**kwargs):
		self._goHome()
		self.setCursor(Qt.WaitCursor)
		self.setDisabled(True)
		self._beginLoad()
		self._rebost.setAction("restart")
		self._rebost.blockSignals(False)
		self._rebost.start()
	#def _reloadApps

	def _endReloadApps(self,*args):
		self._debug("End reloading apps")
		self.loadStop.emit()
		self.setEnabled(True)
		self._goHome()
	#def _endReloadApps

	def _beginLoad(self,resetScreen=True):
		self.loadStart.emit()	
		#self._progressShow()
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.lstCategories.setEnabled(False)
		if resetScreen==False:
			self.softresetScreen()
		else:
			self.resetScreen()
		self.oldTime=time.time()
	#def _beginLoad

	def _loadInstalled(self):
		self._beginLoad()
		self._rebost.setAction("installed")
		self._rebost.blockSignals(False)
		self._rebost.start()
	#def _loadInstalled

	def _endLoadInstalled(self,*args):
		self.appsRaw=json.loads(args[0])
		self.apps=[]
		for app in self.appsRaw:
			#Discard zmds from list
			if app["bundle"].get("unknown","")!="":
				if app["bundle"].get("unknown")==app["name"]==app["pkgname"]:
					continue
			self.apps.append(app)
		#self.apps=self.appsRaw.copy()
		self._debug("End loading installed apps")
		self._showPane(self._globalView)
		self._endUpdate()
		self._globalView.loadApps(self.apps)
		self.oldTime=time.time()
	#def _endLoadInstalled

	def _searchApps(self,tag=""):
		if tag=="":
			txt=self.searchBox.text()
		else:
			txt=tag
		txt=txt.strip().removeprefix("\x08")
		if len(txt)==0:
			return
		else:
			self.lstCategories.unselectAll()
			self.barCategories.hide()
			self._beginLoad()
			self._rebost.setAction("search",txt)
			self._rebost.blockSignals(False)
			self._rebost.start()
	#def _searchApps

	def _endSearchApps(self,*args):
		self._debug("End loading category")
		self._showPane(self._globalView)
		self._endUpdate()
		self.appsRaw=[]
		self.appsRaw=json.loads(args[0])
		self.apps=self.appsRaw.copy()
		self._globalView.loadApps(self.apps)
		self.oldTime=time.time()
	#def _endSearchApps

	def _searchAppsBtn(self):
		txt=self.searchBox.text()
		self._searchApps(resetOld=False)
	#def _searchAppsBtn

	def _loadTag(self,*args):
		if len(args)>0:
			tag=args[0]
			self._beginLoad()
			self._searchApps(tag)
	#def _loadTag

	def _loadCategory(self,*args):
		cat=None
		flag=""
		if len(args)==0:
			cat=""
		elif isinstance(args[0],str):
			cat=args[0]
		if cat==None:
			return
		if time.time()-self.oldTime<MINTIME:
			return
		self.searchBox.setText("")
		self._beginLoad()
		self.requestGetApps.emit(cat)
	#def _loadCategory

	def _endLoadCategory(self,*args):
		self._debug("Load category end")
		self._showPane(self._globalView)
		self._endUpdate()
		self.appsRaw=[]
		appsRaw=json.loads(args[0])
		if isinstance(appsRaw,dict)==False:
			appsRaw={}
		for key,item in appsRaw.items():
			self.appsRaw.extend(item)
		self.apps=self.appsRaw.copy()
		self._globalView.loadApps(self.apps)
		self.oldTime=time.time()
	#def _endLoadCategory

	def _showPane(self,showPane):
		#if store was loaded from appstream showPane may be unassigned. Check
		if showPane==None:
			showPane=self._globalView
		for pane in [self._detailView,self._homeView,self._errorView,self._globalView]:
			if showPane==self._detailView and pane==self._globalView: #flowlayout goes crazy
				continue
			if showPane!=pane:
				pane.hide()
		showPane.show()
		showPane.setCursor(self.oldCursor)
		showPane.setFocus()
		self.lstCategories.setEnabled(True)
		if self._detailView.isVisible()==True:
			self.barCategories.populateCategories(self._detailView.app.get("categories",[]))
			self.barCategories.show()
		else:
			self.barCategories.hide()
		self.setCursor(self.oldCursor)
	#def _showPane

	def _endLoadDetail(self,*args,**kwargs):
		self.loadStop.emit()
		#self._progressHide()
		self._showPane(self._detailView)
		if self.progress.testAttribute(Qt.WA_StyledBackground)==True:
			self.progress.setAttribute(Qt.WA_StyledBackground, False)
			self.progress.lblInfo.hide()
			self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
	#def _endLoadDetail

	def _loadDetails(self,*args,**kwargs):
		self._beginLoad(resetScreen=False)
		icn=""
		app=""
		btn=None
		for arg in args:
			if isinstance(arg,tuple):
				for targ in arg:
					if isinstance(targ,QPushButtonRebostApp):
						icn=targ.iconUri.pixmap()
						self.referrerBtn=targ
						btn=targ
					elif isinstance(targ,dict) and len(targ)>0:
						app=targ
					elif hasattr(targ,"overlay"): #QPushInfoButton
						icn=targ.icon.pixmap()
						app={"id":targ.property("metadata")}
				break
			elif isinstance(arg,QPushButtonRebostApp):
				icn=arg.iconUri.pixmap()
				self.referrerBtn=arg
				btn=arg
			elif isinstance(arg,dict):
				app=arg.copy()
				break
		self._stopThreads(ignoreProgress=True)
		if app!="":
			self.parent.setWindowTitle("{} - {}".format(APPNAME,app.get("name","").capitalize()))
			self._detailView.setParms({"name":app.get("name",""),"id":app.get("id",""),"icon":icn,"btn":btn})
	#def _loadDetails(self,*args,**kwargs):

	def _loadGlobalDetails(self,*args,**kwargs):
		self._referrerPane=self._globalView
		self._loadDetails(args,kwargs)
	#def _loadGlobalDetails(self,*args,**kwargs):

	def _loadHomeDetails(self,*args,**kwargs):
		self._referrerPane=self._homeView
		self._loadDetails(args,kwargs)
	#def _loadHomeDetails(self,*args,**kwargs):

	def _loadPortraitFromError(self,*args,**kwargs):
		self.noChkNetwork=True
		self._goHome()
	#def _loadPortraitFromError

	def _loadFromArgs(self,*args,**kwargs):
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self._referrerPane=self._homeView
		jargs=json.loads(args[0])
		if len(jargs)>0:
			self._loadDetails(json.loads(args[0])[0],kwargs)
	#def _loadFromArgs

	def setParms(self,*args):
		appsedu=args[0]
		self._debug("** Detected parm on init **")
		if "://" in appsedu:
			self._beginLoad()
			self.lstCategories.setEnabled(False)
			self.progress.lblInfo.show()
			self.progress.setAttribute(Qt.WA_StyledBackground, True)
			self.box.addWidget(self.progress,0,0,self.box.rowCount(),self.box.columnCount())
			self._referrerPane=self._homeView
			self._stopThreads(ignoreProgress=True)
			pkgname=appsedu.split("://")[-1]
			self._referrerPane=self._detailView
			self._debug("Seeking for {}".format(pkgname))
			self._detailView.setParms(pkgname)
		else:
			#If categories are not populated load them
			self._chkCategories()
	#def setParms

	def _searchReferrerByName(self,name):
		for i in range(0,self._globalView.table.count()):
			wdg=self._globalView.table.itemAt(i).widget()
			if wdg.app["name"]==name:
				self.referrerBtn=wdg
				break
	#def _searchReferrerByName
	
	def _returnFromDetail(self,*args,**kwargs):
		if isinstance(self.referrerBtn,QPushButtonRebostApp):
			if self.referrerBtn.app["name"]!=args[1]["name"]:
				#Referrer doesn't match with last seen app. Search in table
				self._searchReferrerByName(args[1]["name"])
		if self._detailView.isVisible():
			if self._referrerPane==self._detailView:
				self._referrerPane=None
				self._showPane(self._homeView)
				if len(self._homeView.layout().children())==0:
					self._homeView.updateScreen()
			else:
				self._showPane(self._referrerPane)
		if args[1].get("state",0)>=7:
			if self.installingBtn==None:
				self.installingBtn=self.referrerBtn
		self.referrerBtn=None
		self._return(args,kwargs)
	#def _returnFromDetail

	def _return(self,*args,**kwargs):
		self.setCursor(self.oldCursor)
		self.parent.setWindowTitle("{}".format(APPNAME))
		self.loadStop.emit()
		#self._progressHide()
	#def _return

	def softresetScreen(self):
		self._stopThreads(ignoreProgress=True)
	#def resetScreen

	def resetScreen(self):
		self._stopThreads(ignoreProgress=True)
		self._globalView.loadAppsStop()
		self._globalView.table.clean()
	#def resetScreen

	def updateScreen(self,addEnable=None):
		#self._rebost.wait()
		if self.noChkNetwork!=True:
			if self.aux.chkNetwork()==False:
				self._endUpdate()
				self._showPane(self._errorView)
				self._stopThreads()
				return
		self._rebost.setAction("config")
		self._rebost.start()
		if self._referrerPane!=None:
			self._showPane(self._referrerPane)
		if self._detailView.isVisible():
			self._stopThreads()
		elif self._homeView.isVisible():
			if self.init==True:
				self._stopThreads()
			if len(self._homeView.layout().children())==0:
				self._homeView.updateScreen()
			self._endUpdate()
		self._getUpgradables()
	#def _updateScreen
