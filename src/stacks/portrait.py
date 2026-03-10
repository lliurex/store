#!/usr/bin/python3
import sys,time,signal,time
from functools import partial
import os,grp
import subprocess
import json
import dbus
import dbus.mainloop.glib
from PySide6.QtWidgets import QApplication, QLineEdit,QLabel,QPushButton,QGridLayout,QHBoxLayout, QWidget,QVBoxLayout,QListWidget, \
							QCheckBox,QListWidgetItem,QSizePolicy
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QEvent#,QTimer
from QtExtraWidgets import QStackedWindowItem
from rebost import store 
from libth import storeHelper,llxup
from btnRebost import QPushButtonRebostApp
from prgBar import QProgressImage
from barButtons import QPushButtonBar
from barCategories import QToolBarCategories
from lblApp import QLabelRebostApp
import libhelper
import exehelper
import paneDetailView
import paneGlobalView
import paneHomeView
import paneErrorView
import css
from constants import *

import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"ALL":_("All"),
	"AVAILABLE":_("Available"),
	"CATEGORIESDSC":_("Filter by category"),
	"CERTIFIED":_("Certified by Appsedu"),
	"CONFIG":_("Portrait"),
	"DESC":_("Navigate through all applications"),
	"ERRNOTFOUND":_("Could not open"),
	"ERRLAUNCH":_("Error opening"),
	"ERRMORETHANONE":_("There's another action in progress"),
	"ERRUNAUTHORIZED":_("Authorization is required"),
	"ERRSYSTEMAPP":_("System apps can't be removed"),
	"ERRUNKNOWN":_("Unknown error"),
	"FILTERS":_("Filters"),
	"FILTERSDSC":_("Filter by formats and states"),
	"HOME":_("Home"),
	"HOMEDSC":_("Main page"),
	"INSTALLED":_("Installed"),
	"LLXUP":_("Launch LliurexUp"),
	"MENU":_("Show applications"),
	"NEWDATA":_("Updating info"),
	"OPEN":_("Z·Install"),
	"REFRESH":_("Reload Apps"),
	"REMOVE":_("Remove"),
	"SEARCH":_("Search"),
	"SORTDSC":_("Sort alphabetically"),
	"TOOLTIP":_("Portrait"),
	"UPGRADABLE":_("Upgradables"),
	"UPGRADES":_("There're upgrades available"),
	"CHK_NETWORK":_("Store was unable to get information from internet"),
	"OPN_NETWORK":_("Open network settings")
	}

class portrait(QStackedWindowItem):
	requestGetApps=Signal(str)
	loadStart=Signal()
	loadStop=Signal()
	rebostToggled=Signal()
	def __init_stack__(self):
		self.init=False
		self.minTime=1
		self.oldTime=0
		self.dbg=True
		self.enabled=True
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.destroyed.connect(partial(portrait._onDestroy,self.__dict__))
		self.pendingApps={}
		self.apps=[]
		self.helper=libhelper.helper()
		#self.updateTimer=QTimer()
		#self.updateTimer.timeout.connect(QApplication.processEvents)
		self.rc=store.client()
		self._referrerPane=None
		self._rebost=storeHelper(rc=self.rc)
		self._llxup=llxup()
		self.runapp=exehelper.appLauncher()
		self.runapp.runEnded.connect(self._endRunApp)
		self.zmd=exehelper.zmdLauncher()
		self.zmd.zmdEnded.connect(self._endRunApp)
		self._initThreads()
		self._initRegisters()
		self._initGUI()
		#DBUS loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		#DBUS connections
		bus=dbus.SystemBus()
		objbus=bus.get_object("net.lliurex.rebost","/net/lliurex/rebost")
	#	objbus.connect_to_signal("beginUpdateSignal",self._beginUpdate,dbus_interface="net.lliurex.rebost")
	#	(self.locked,self.userLocked)=self._rebost.isLocked()
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
		self.appsLoaded=0
		self.appsSeen=[]
		self.appsRaw=[]
		self.locked=True
		self._rebost.setAction("config")
		self._rebost.start()
		#self._rebost.wait()
		self.stopAdding=False
		self.filters={"installed":False}
		self.loading=False
		self.categoriesTree={}
		self.chkUpdates=False
		self.noChkNetwork=False
		self.isConnected=self._chkNetwork()
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
		#self._rebost.lckEnded.connect(self._endLock)
		self._rebost.rstEnded.connect(self._endReloadApps)
		#self._rebost.staEnded.connect(self._endGetLockStatus)
		self._rebost.cnfEnded.connect(self._endGetLockStatus)
		self._rebost.catEnded.connect(self._populateCategories)
		self._rebost.shwEnded.connect(self._loadFromArgs)
	#def _initThreads(self):

	def _initGUI(self):
		self.hideControlButtons()
		self.referersHistory={}
		self.referersShowed={}
		self.installingBtn=None
		self.refererApp=None
		self.oldCursor=self.cursor()
		self.refresh=True
		self.released=True
		self.maxCol=5
		self.setStyleSheet(css.portrait())
	#def _initGUI

	def _chkNetwork(self):
		state=False
		if self.noChkNetwork==True:
			state=True
		else:
			bus=dbus.SystemBus()
			try:
				objbus=bus.get_object("org.freedesktop.NetworkManager","/org/freedesktop/NetworkManager")
				proxbus=dbus.Interface(objbus,"org.freedesktop.NetworkManager")
				status=proxbus.state()
			except Exception as e:
				self._debug("Chk network: {}".format(e))
				state=True
			else:
				if status==70:
					state=True
		return(state)
	#def _chkNetwork

	def _chkUserGroup(self):
		lockedUser=False
		grpData=grp.getgrnam("sudo")
		if grpData.gr_gid not in os.getgroups():
			userlocked=True
		return(lockedUser)
	#def _chkUserGroup(self):

	def _chkCategories(self,*args):
		if self.lstCategories.count()<=0:
			self._rebost.blockSignals(False)
			self._rebost.setAction("getCategories")
			self._rebost.start()
			#self._rebost.wait()
	#def _chkCategories

	def _endGetLockStatus(self,*args):
		jconfig=args[0]
		self.locked=jconfig.get("onlyVerified",False)
		lockedUser=self._chkUserGroup()
		if not isinstance(self.locked,bool):
			if int(self.locked)==0:
				self.locked=False
			else:
				self.locked=True
		if self.locked==False: #conf is unlocked, check groups 
			if lockedUser==True:
				self._unlockRebost()
		self.btnBar.setLocked(self.locked,lockedUser)
		self._debug("<-------- Rebost status acquired (lock {})".format(self.locked))
		self._chkCategories()
		self.prgCat.stop()
		self.prgCat.hide()
	#def _endGetLockStatus

	def _endLock(self,*args):
		pass
		#self._endRestart()
	#def _endLock

	def _endRestart(self,*args):
		self.loadStop.emit()
		self._goHome()
	#def _endRestart

	def _endRunApp(self,*args):
		self.setCursor(self.oldCursor)
		proc=None
		if len(args)>0:
			if isinstance(args[0],dict):
				app=args[0]
			if len(args)==2:
				proc=args[1]
		else:
			return
		if proc!=None:
			if isinstance(proc,int)==False:
				if proc.returncode>1: #app is installed
					#pkexec ret values
					#127 -> Not authorized
					if proc.returncode==127:
						self.showMsg(title="LliureX Store",summary=app["name"],text=i18n.get("ERRUNAUTHORIZED"),icon=app["icon"],timeout=5000)
					else:
						self.showMsg(title="LliureX Store",summary=app["name"],text=i18n.get("ERRUNKNOWN"),icon=app["icon"],timeout=5000)
		self._rebost.setAction("refreshApp",app["id"])
		app=json.loads(self._rebost._refreshApp())[0]
		self._rebost.setAction("setAppState",app["id"],0)
		self._rebost.start()
		self._rebost.wait()
		app["state"]=0 #App is in "normal" state
		if self.installingBtn!=None:
			oldReferrer=self.referrerBtn
			self.referrerBtn=self.installingBtn
			self._returnFromDetail(None,app)
			self.referrerBtn=oldReferrer
			self.installingBtn=None
		elif self._detailView.isVisible():
			self._detailView.endInstall(app)
	#def _endRunApp

	def _setInstallingState(self,app,state):
		app["state"]=state
		self._rebost.setAction("setAppState",app["id"],state)
		self._rebost.start()
		self._rebost.wait()
		return(app)
	#def _setInstallingState

	def _installApp(self,*args): #(btn,app,[bundle])
		if self.installingBtn!=None:
			self.showMsg(summary=i18n.get("ERRMORETHANONE",""),text=self.installingBtn.app["name"].capitalize(),timeout=4)
			return
		wdg=args[0]
		app=args[1]
		bundle=""
		if len(args)>2:
			bundle=args[2]
		else:
			if hasattr(wdg,"instBundle"):
				if len(wdg.instBundle)>0:
					bundle=wdg.instBundle
			if len(bundle)==0:
				priority=self.helper.getBundlesByPriority(app)
				idx=list(priority.keys())
				idx.sort()
				bundle=priority[idx[0]].split(" ")[0]
		if bundle=="epi":
			bundle="unknown"
		pkg=app.get('id')
		try:
			if pkg!="":
				installer=str(self.rc.getExternalInstaller())
				if installer!="":
					state=7
					if isinstance(wdg,QPushButtonRebostApp):
						self.installingBtn=wdg
						if wdg.btn.text()==i18n["REMOVE"]:
							state=8
					elif hasattr(wdg,"text"):
						if wdg.text()==i18n["REMOVE"]:
							state=8
					if bundle=="webapp":
						details=self.helper.getAppseduDetails(app["homepage"])
						app["bundle"]["webapp"]=details["url"]
						self.runapp.setUrl(app)
						self.runapp.start()
					elif bundle!="unknown":
						self._setInstallingState(app,state)
						self.runapp.setArgs(app,[installer,pkg,bundle])
						self.runapp.start()
					else:
						self.zmd.setApp(app)
						self.zmd.start()
		except Exception as e:
			print(e)
		return
	#def _installApp

	def _progressShow(self):
	#	self.updateTimer.start(1)
		self.progress.start()
	#def _progressShow

	def _progressHide(self):
		self.progress.stop()
		#self.prgCat.stop()
		#self.prgCat.hide()
		#self.updateTimer.stop()
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
		spacer.setFixedHeight(int(MARGIN)*3)
		self.box.addWidget(spacer,0,1)
		navwdg=self._defNavigationPane()
		navwdg.setObjectName("wdg")
		self.box.addWidget(navwdg,0,0,5,1)
		self.searchwdg=self._defSearch()
		self.box.addWidget(self.searchwdg,1,1)
		spacer=QLabel(" ")
		spacer.setAttribute(Qt.WA_StyledBackground, True)
		spacer.setStyleSheet("background:{};".format(COLOR_BACKGROUND_LIGHT))
		spacer.setFixedHeight(int(MARGIN)*4)
		self.box.addWidget(spacer,2,1)
		self.barCategories=self._defBarCategories()
		self.box.addWidget(self.barCategories,3,1,Qt.AlignTop)
		#self.barCategories.setMinimumHeight(int(MARGIN)*6)
		self._homeView=self._getHomeViewPane()
		self.box.addWidget(self._homeView,4,1)
		self._globalView=self._getGlobalViewPane()
		self._globalView.hide()
		self.box.addWidget(self._globalView,4,1)
		self._detailView=self._getDetailViewPane()
		self.box.addWidget(self._detailView,4,1)
		self._detailView.hide()
		self.prgCat=QProgressImage(self)
		self.prgCat.sleepSeconds=55
		self.prgCat.setColor(COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_DARKEST)
		self.prgCat.lblInfo.setWordWrap(True)
		self.box.addWidget(self.prgCat,0,0,5,2)
		self.prgCat.start()
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
		vbox.setContentsMargins(int(MARGIN)*3,0,int(MARGIN)*3,0)
		self.btnBar=QPushButtonBar()
		#self.certified=QPushButtonToggle()
		self.btnBar.toggleClicked.connect(self._unlockRebost)
		self.btnBar.homeClicked.connect(self._goHome)
		self.btnBar.installedClicked.connect(self._loadInstalled)
		self.btnBar.reloadClicked.connect(self._reloadApps)
		vbox.addWidget(self.btnBar,Qt.AlignCenter)
		self.lstCategories=QListWidget()
		self.lstCategories.setObjectName("lstCategories")
		self.lstCategories.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lstCategories.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		vbox.addWidget(self.lstCategories,Qt.AlignTop|Qt.AlignCenter)
		self.lstCategories.setMinimumHeight(int(ICON_SIZE/3))
		self.lstCategories.setFixedWidth(wdg.sizeHint().width()-int(MARGIN)*3)
		self.lstCategories.currentItemChanged.connect(self._decoreLstCategories)
		self.lstCategories.itemActivated.connect(self._loadCategory)
		self.lstCategories.itemClicked.connect(self._loadCategory)
		self.lstCategories.hide()
		self.lblInfo=self._defInfo()
		vbox.addWidget(self.lblInfo,Qt.Alignment(-1))
		vbox.setStretch(0,0)
		vbox.setStretch(1,2)
		vbox.setStretch(3,1)
		wdg.setMinimumWidth(self.lblInfo.sizeHint().width())
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
		btnRefresh.setFixedWidth(btnInst.sizeHint().width()+int(MARGIN))
		btnInst.setFixedWidth(btnInst.sizeHint().width()+int(MARGIN))
		return(wdg)
	#def _defBtnBar

	def _defBanner(self):
		lbl=QLabelRebostApp()
		lbl.setClickable(True)
		#lbl.setObjectName("banner")
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","banner.svg")
		pxm=QtGui.QPixmap(img).scaled(172,64,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		lbl.setPixmap(pxm)
		lbl.clicked.connect(self._goHome)
		return lbl
	#def _defBanner

	def _defNavigationPane(self):
		wdg=QWidget()
		#wdg.setObjectName("wdg")
		lay=QGridLayout()
		lay.setContentsMargins(0,int(MARGIN)*3,0,0)
		wdg.setLayout(lay)
		self.sortAsc=False
		banner=self._defBanner()
		lay.addWidget(banner,0,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		_defBtnBar=self._defBtnBar()
		#lay.addWidget(_defBtnBar,1,0,1,1,Qt.AlignCenter)
		navBar=self._defNavigationBar()
		lay.addWidget(navBar,2,0,1,1)
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
		#QApplication.processEvents()
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
	
	def setBtnSearchIcon(self,icn=""):
		if icn!="":
			icn=QtGui.QIcon(os.path.join(RSRC,"{}.png".format(icn)))
		if len(self.searchBox.text())>0:
			icn=QtGui.QIcon(os.path.join(RSRC,"cancel.png"))
		else:
			icn=QtGui.QIcon(os.path.join(RSRC,"search.png"))
		self.btnSearch.setIcon(icn)
	#def setBtnSearchIcon

	def _changeSearchAppsBtnIcon(self):
		if len(self.searchBox.text())>0:
			self.setBtnSearchIcon("cancel")
		else:
			self.setBtnSearchIcon("search")
	#def _changeSearchAppsBtnIcon(self):

	def _resetSearch(self):
		self.searchBox.setText("")
		self.searchBox.setFocus()
	#def _resetSearch

	def _defSearch(self):
		wdgParent=QWidget()
		layParent=QHBoxLayout(wdgParent)
		wdgParent.setObjectName("wdgsearch")
		wdgParent.setAttribute(Qt.WA_StyledBackground, True)
		wdg=QWidget()
		wdg.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.setObjectName("wsearch")
		self.searchBox=QLineEdit()
		font=self.searchBox.font()
		font.setPointSize(font.pointSize()+2)
		self.searchBox.setFont(font)
		self.searchBox.setObjectName("search")
		lay=QHBoxLayout()
		lay.setSpacing(0)
		self.btnSearch=QPushButton()
		self.btnSearch.setObjectName("bsearch")
		icn=QtGui.QIcon(os.path.join(RSRC,"search.png"))
		self.btnSearch.setIcon(icn)
		self.btnSearch.setMinimumSize(int(ICON_SIZE/4),int(ICON_SIZE/4))
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.btnSearch.setIconSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		self.searchBox.returnPressed.connect(self._searchApps)
		self.searchBox.textChanged.connect(self._changeSearchAppsBtnIcon)
		self.btnSearch.clicked.connect(self._resetSearch)
		lay.addWidget(self.searchBox)#,Qt.AlignCenter|Qt.AlignCenter)
		lay.addWidget(self.btnSearch)
		wdg.setLayout(lay)
		wdg.setMaximumWidth(450)
		layParent.addWidget(wdg)
		return(wdgParent)
	#def _defSearch

	def _defProgress(self):
		wdg=QProgressImage(self)
		wdg.inc=-1
		wdg.setImageFromFile(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","progressBar267x267.png"))
		wdg.animation="bigger"
		wdg.animation="pulsate"
		return(wdg)
	#def _defProgress

	def _getGlobalViewPane(self):
		gvp=paneGlobalView.paneGlobalView(self._rebost)
		gvp.requestLoadDetails.connect(self._loadGlobalDetails)
		gvp.requestInstallApp.connect(self._installApp)
		return(gvp)
	#def _getGlobalViewPane

	def _getDetailViewPane(self):
		dvp=paneDetailView.main(self._rebost)
		dvp.setObjectName("detailPanel")
		dvp.clickedBack.connect(self._returnFromDetail)
		dvp.loaded.connect(self._endLoadDetail)
		dvp.requestLoadTag.connect(self._loadTag)
		dvp.requestInstallApp.connect(self._installApp)
		return(dvp)
	#def _getDetailViewPane

	def _getHomeViewPane(self):
		hvp=paneHomeView.main(self._rebost)
		hvp.clickedApp.connect(self._loadHomeDetails)
		hvp.clickedCategory.connect(self._loadCategory)
		hvp.requestInstallApp.connect(self._installApp)
		hvp.loaded.connect(self._chkCategories)
		self.rebostToggled.connect(hvp.reloadAppsedu)
		return(hvp)
	#def _getHomeViewPane

	def _populateCategories(self,cats):
		self.prgCat.stop()
		self.prgCat.hide()
		self.lstCategories.show()
		self.lstCategories.clear()
		self.lstCategories.setSizeAdjustPolicy(self.lstCategories.SizeAdjustPolicy.AdjustToContents)
		self.i18nCat={}
		self.catI18n={}
		self.categoriesTree=cats
		seenCats={}
		#Sort categories
		masterCategories=[]
		for mastercat,subcats in self.categoriesTree.items():
			#if cat.islower() it's a category from system without appstream info 
			cats=[]
			cats.append(mastercat)
			cats.extend(subcats)
			for cat in cats:
				if _(cat).capitalize() in self.i18nCat.keys() or cat.islower():
					continue
				if _(cat).capitalize() in self.i18nCat.keys() or cat.islower():
					continue

				self.i18nCat[_(cat).capitalize()]=cat
				self.catI18n[cat]=_(cat)
			masterCategories.append(_(mastercat).capitalize())
		masterCategories.sort()
		lowercats=[]
		font=self.lstCategories.font()
		font.setPointSize(font.pointSize()+2)
		for cat in masterCategories:
			if cat.lower() not in lowercats:
				self.lstCategories.addItem(" · {}".format(cat))
				item=self.lstCategories.item(self.lstCategories.count()-1)
				if item!=None:
					item.setToolTip(cat)
					item.setFont(font)
				lowercats.append(cat.lower())
	#def _populateCategories

	def _getApps(self,category="",installed=False):
		if category!="":
			self.resetScreen()
			category=self.i18nCat.get(category,category)
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
		self.stopAdding=True
		self._homeView.hide()
	#def _beginUpdate

	def _endUpdate(self):
		self._return()
	#def _endUpdate

	def _goHome(self,*args,**kwargs):
		self._referrerPane=self._homeView
		self.lstCategories.setCurrentRow(-1)
		self.resetScreen()
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
		self.loading=False
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
		self.loading=False
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
		self.lstCategories.setCurrentRow(-1)
		if len(txt)==0:
			return
		else:
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

	def _decoreLstCategories(self,*args):
		if isinstance(args[0],QListWidgetItem):
			font=args[0].font()
			font.setBold(True)
			args[0].setFont(font)
		if len(args)>1:
			if isinstance(args[1],QListWidgetItem):
				font=args[1].font()
				font.setBold(False)
				args[1].setFont(font)
	#def _decoreLstCategories

	def _getRawCategory(self,cat):
		if cat=="":
			if self.lstCategories.count()!=0:
				i18ncat=self.lstCategories.currentItem().text().replace(" · ","")
			else:
				i18ncat=""
		else:
			if isinstance(cat,str):
				i18ncat=cat.replace(" · ","")
			elif isinstance(cat,QListWidgetItem):
				i18ncat=cat.text().replace(" · ","")
			elif cat!=None:
				i18ncat=cat.text().replace(" · ","")
			flag=Qt.MatchFlags(Qt.MatchFlag.MatchContains)
			items=self.lstCategories.findItems(i18ncat,flag)
			for item in items:
				if item.text().replace(" · ","").lower()==i18ncat.lower():
					self.lstCategories.setCurrentItem(item)
					break
		if self.oldCat!=i18ncat:
			self.oldCat=i18ncat
		cat=self.i18nCat.get(i18ncat,i18ncat)
		if cat==i18n.get("ALL"):
			cat=""
		return(cat)
	#def _getRawCategory

	def _loadTag(self,*args):
		self.appsLoaded=0
		if len(args)>0:
			tag=args[0]
			self._beginLoad()
			self._searchApps(tag)
	#def _loadTag

	def _loadCategory(self,*args):
		self.appsLoaded=0
		cat=None
		flag=""
		if len(args)==0:
			cat=""
		elif isinstance(args[0],str):
			cat=args[0]
		elif isinstance(args[0],QListWidgetItem):
			cat=args[0].text()
		if cat==None:
			return
		if time.time()-self.oldTime<MINTIME:
			return
		self.searchBox.setText("")
		self._beginLoad()
		cat=self._getRawCategory(cat)
		self.searchBox.setText("")
		if cat in self.categoriesTree.keys():
			self.barCategories.populateCategories(self.categoriesTree[cat],cat)
		else:
			for idx in range(0,self.barCategories.count()):
				wdg=self.barCategories.itemAt(idx).widget()
				self.style().unpolish(wdg)
				wdg.setObjectName("categoryTag")
				self.style().polish(wdg)
			self.style().unpolish(self.barCategories.currentItem())
			self.barCategories.currentItem().setObjectName("categoryTagCurrent")
			self.style().polish(self.barCategories.currentItem())
		self.requestGetApps.emit(cat)
	#def _loadCategory

	def _endLoadCategory(self,*args):
		self._debug("LOAD CATEGORY END")
		self._showPane(self._globalView)
		self._endUpdate()
		self.appsRaw=[]
		appsRaw=json.loads(args[0])
		for key,item in appsRaw.items():
			self.appsRaw.extend(item)
		self.apps=self.appsRaw.copy()
		self._globalView.loadApps(self.apps)
		#REM This show launches also after locking store. Investigate but disable ATM
		#self.barCategories.show()
		self.oldTime=time.time()
	#def _endLoadCategory

	def _showPane(self,showPane):
		for pane in [self._detailView,self._homeView,self._errorView,self._globalView]:
			if showPane==self._detailView and pane==self._globalView: #flowlayout goes crazy
				continue
			if showPane!=pane:
				pane.hide()
		#If categories are not populated load them
		if self.lstCategories.count()<=0:
			self._rebost.setAction("getCategories")
			self._rebost.start()
			#self._rebost.wait()
		showPane.show()
		showPane.setCursor(self.oldCursor)
		showPane.setFocus()
		self.lstCategories.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		self.lstCategories.setEnabled(True)
		if self._detailView.isVisible()==True:
			self.barCategories.populateCategories(self._detailView.app.get("categories",[]))
			self.barCategories.show()
		elif self._globalView.isVisible()==True:
			item=self.lstCategories.currentItem()
			if item!=None:
				cat=item.text()
				cat=self._getRawCategory(cat)
				#if cat in self.categoriesTree.keys():
				#	self.barCategories.populateCategories(self.categoriesTree[cat],cat)
				self.barCategories.show()
			else:
				if self.searchBox.text!="":
					self.barCategories.hide()
		else:
			self.barCategories.hide()
			self.searchBox.setText("")
			self.lstCategories.setCurrentRow(-1)
		self.setCursor(self.oldCursor)
	#def _showPane

	def _endLoadDetail(self,*args,**kwargs):
		self.loadStop.emit()
		#self._progressHide()
		self._showPane(self._detailView)
	#def _endLoadDetail

	def _loadDetails(self,*args,**kwargs):
		self._beginLoad(resetScreen=False)
		icn=""
		app=""
		for arg in args:
			if isinstance(arg,tuple):
				for targ in arg:
					if isinstance(targ,QPushButtonRebostApp):
						icn=targ.iconUri.pixmap()
						self.referrerBtn=targ
					if isinstance(targ,dict):
						app=targ
				break
			elif isinstance(arg,QPushButtonRebostApp):
				icn=arg.iconUri.pixmap()
				self.referrerBtn=arg
			elif isinstance(arg,dict):
				app=arg.copy()
				break
		self._stopThreads(ignoreProgress=True)
		if app!="":
			self.parent.setWindowTitle("{} - {}".format(APPNAME,args[-1].get("name","").capitalize()))
			self._detailView.setParms({"name":app.get("name",""),"id":app.get("id",""),"icon":icn})
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
		if self._globalView.isVisible()==True:
			self._globalView.updateBtn(self.referrerBtn,args[1])
		elif self._homeView.isVisible()==True and self.referrerBtn!=None:
			self._homeView.updateBtn(self.referrerBtn,args[1])
		self.referrerBtn=None
		self._return(args,kwargs)
	#def _returnFromDetail

	def _return(self,*args,**kwargs):
		self.setCursor(self.oldCursor)
		self.parent.setWindowTitle("{}".format(APPNAME))
		self.loading=False
		self.loadStop.emit()
		#self._progressHide()
	#def _return

	def softresetScreen(self):
		self._stopThreads(ignoreProgress=True)
	#def resetScreen

	def resetScreen(self):
		self._stopThreads(ignoreProgress=True)
		self.appsLoaded=0
		self.pendingApps={}
		self.refererApp=None
		self.appsSeen=[]
		self._globalView.loadAppsStop()
		self._globalView.table.clean()
	#def resetScreen

	def updateScreen(self,addEnable=None):
		#self._rebost.wait()
		if self.lstCategories.count()<=0:
			self._rebost.setAction("getCategories")
			self._rebost.start()
		else:
			isConnected=self._chkNetwork()
			if isConnected==False:
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
