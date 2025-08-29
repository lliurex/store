#!/usr/bin/python3
import sys,time,signal,time
from functools import partial
import os
import subprocess
import json
import dbus
import dbus.service
import dbus.mainloop.glib
import random
from PySide6.QtWidgets import QApplication, QLineEdit,QLabel,QPushButton,QGridLayout,QHBoxLayout, QWidget,QVBoxLayout,QListWidget, \
							QCheckBox,QListWidgetItem,QSizePolicy
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QEvent
from QtExtraWidgets import QStackedWindowItem
from rebost import store 
from libth import storeHelper,llxup
from btnRebost import QPushButtonRebostApp
from prgBar import QProgressImage
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
		self.rc=store.client()
		self._referrerPane=None
		self._rebost=storeHelper(rc=self.rc)
		self._llxup=llxup()
		self.runapp=exehelper.appLauncher()
		self.runapp.runEnded.connect(self._getRunappResults)
		self._initRegisters()
		self._initThreads()
		self._initGUI()
		#DBUS loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		#DBUS connections
		bus=dbus.SessionBus()
		objbus=bus.get_object("net.lliurex.rebost","/net/lliurex/rebost")
		self._getUpgradables()
	#	objbus.connect_to_signal("beginUpdateSignal",self._beginUpdate,dbus_interface="net.lliurex.rebost")
	#	(self.locked,self.userLocked)=self._rebost.isLocked()
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["_rebost"].blockSignals(True)
		selfDict["_llxup"].blockSignals(True)
		selfDict["_rebost"].requestInterruption()
		selfDict["_rebost"].wait()
		selfDict["_rebost"].quit()
		selfDict["_rebost"].blockSignals(False)
		selfDict["_llxup"].wait()
		selfDict["_llxup"].quit()
		selfDict["_llxup"].blockSignals(False)
	#def _onDestroy

	def _initRegisters(self):
		#Catalogue related
		self.i18nCat={}
		self.oldCat=""
		self.catI18n={}
		self.appsToLoad=-1
		self.appsLoaded=0
		self.appsSeen=[]
		self.appsRaw=[]
		self.locked=True
		self.userLocked=True
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
		self._llxup.chkEnded.connect(self._endGetUpgradables)
		self._rebost.lstEnded.connect(self._endLoadCategory)
		self._rebost.linEnded.connect(self._endLoadInstalled)
		self._rebost.srcEnded.connect(self._endSearchApps)
		self._rebost.lckEnded.connect(self._endLock)
		self._rebost.rstEnded.connect(self._endRestart)
		self._rebost.staEnded.connect(self._endGetLockStatus)
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
		self._rebost.setAction("getCategories")
		self._rebost.start()
		self.setStyleSheet(css.portrait())
	#def _initGUI

	def _debug(self,msg):
		if self.dbg==True:
			print("Portrait: {}".format(msg))
	#def _debug

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
			except:
				state=True
			else:
				if status==70:
					state=True
		return(state)
	#def _chkNetwork

	def _endGetLockStatus(self,*args):
		self.certified.blockSignals(True)
		self.locked=args[0]
		self.userLocked=args[1]
		if self.userLocked==False and self.locked==False:
			self.certified.setChecked(False)
		self.certified.blockSignals(False)
		self._debug("<-------- Rebost status acquired")
		time.sleep(0.1)
		self._rebost.setAction("getCategories")
		self._rebost.start()
		#QApplication.processEvents()
		self._rebost.wait()
		if self.locked==False and self.userLocked==True:
			self._loadLockedRebost()
		else:
			self._getApps()
			self._endUpdate()
	#def _endGetLockStatus

	def _endRestart(self,*args):
		self.progress.stop()
		self._goHome()
	#def _endRestart

	def _endLock(self,*args):
		self._endRestart()
	#def _endLock

	def _stopThreads(self):
		if self.appsToLoad==-1: #Init 
			exit
		self._rebost.blockSignals(True)
		self._llxup.blockSignals(True)
		self._rebost.requestInterruption()
		self._rebost.wait()
		self._rebost.quit()
		self._rebost.blockSignals(False)
		self._llxup.wait()
		self._llxup.quit()
		self._llxup.blockSignals(False)
		self.progress.stop()
	#def _stopThreads

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.box.setContentsMargins(0,0,0,0)
		self.box.setSpacing(0)
		self.sortAsc=False
		navwdg=self._navPane()
		navwdg.setObjectName("wdg")
		self.box.addWidget(navwdg,0,0,2,1,Qt.AlignLeft)
		searchwdg=QWidget()
		wlay=QHBoxLayout()
		searchwdg.setLayout(wlay)
		searchwdg.setObjectName("wdgsearch")
		searchwdg.setAttribute(Qt.WA_StyledBackground, True)
		self.search=self._defSearch()
		wlay.addWidget(self.search)
		self.box.addWidget(searchwdg,0,1)
		self._homeView=self._getHomeViewPane()
		self.box.addWidget(self._homeView,1,1)
		self._globalView=self._getGlobalViewPane()
		self._globalView.requestLoadCategory.connect(self._loadCategory)
		self._globalView.hide()
		self.box.addWidget(self._globalView,1,1)
		self._detailView=self._getDetailViewPane()
		self._detailView.setObjectName("detailPanel")
		self._detailView.clickedBack.connect(self._returnFromDetail)
		self._detailView.loaded.connect(self._detailLoaded)
		self._detailView.requestLoadCategory.connect(self._loadCategory)
		self.box.addWidget(self._detailView,1,1)
		self._detailView.hide()
		self.btnSettings=QPushButton()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		self.box.setColumnStretch(1,1)
		self.setObjectName("portrait")
		self._errorView=self._defError()
		self._errorView.setObjectName("errorMsg")
		self._errorView.setVisible(not(self.isConnected))
		self.box.addWidget(self._errorView,0,1,self.box.rowCount(),self.box.columnCount())
		self.progress=self._defProgress()
		self.progress.lblInfo.hide()
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
	#def _load_screen

	def _closeEvent(self,*args):
		self._stopThreads()
		if self._llxup.isRunning():
			self._llxup.quit()
			self._llxup.wait()
	#def _closeEvent
	
	def eventFilter(self,*args):
		if isinstance(args[0],QListWidget):
			if args[1].type==QEvent.Type.KeyRelease:
				self.released=True
			elif args[1].type==QEvent.Type.KeyPress:
				self.released=False
		return(False)
	#def eventFilter(self,*args):

	def _navPane(self):
		wdg=QWidget()
		wdg.setObjectName("wdg")
		lay=QVBoxLayout()
		self.sortAsc=False
		banner=self._defBanner()
		lay.addWidget(banner)
		btnBar=self._btnBar()
		hlay=QHBoxLayout()
		wdg2=QWidget()
		wdg2.setLayout(hlay)
		hlay.addWidget(btnBar,Qt.AlignCenter)
		lay.addWidget(wdg2)
		navBar=self._defNavBar()
		lay.addWidget(navBar)
		wdg.setLayout(lay)
		return(wdg)
	#def _navPane

	def _defBanner(self):
		lbl=QLabel()
		lbl.setObjectName("banner")
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","banner.svg")
		pxm=QtGui.QPixmap(img).scaled(172,64,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		lbl.setPixmap(pxm)
		return lbl
	#def _defBanner

	def _defNavBar(self):
		wdg=QWidget()
		if LAYOUT=="appsedu":
			vbox=QVBoxLayout()
		else:
			vbox=QHBoxLayout()
		wdg.setLayout(vbox)
		vbox.setContentsMargins(10,0,10,0)
		self.certified=self._appseduCertified()
		vbox.addWidget(self.certified,Qt.AlignCenter)
		self.lstCategories=QListWidget()
		self.lstCategories.setObjectName("lstCategories")
		self.lstCategories.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lstCategories.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		vbox.addWidget(self.lstCategories,Qt.AlignTop|Qt.AlignCenter)
		self.lstCategories.setMinimumHeight(int(ICON_SIZE/3))
		self.lstCategories.currentItemChanged.connect(self._decoreLstCategories)
		self.lstCategories.itemActivated.connect(self._loadCategory)
		self.lstCategories.itemClicked.connect(self._loadCategory)
		self.lblInfo=self._defInfo()
		vbox.addSpacing(30)
		vbox.addWidget(self.lblInfo,Qt.AlignBottom)
		vbox.setStretch(0,0)
		vbox.setStretch(1,1)
		vbox.setStretch(2,0)
		vbox.setStretch(3,0)
		return(wdg)
	#def _defNavBar

	def _unlockRebost(self,*args):
		self._stopThreads()
		self.stopAdding=True
		self.refresh=True
		self.searchBox.setText("")
		self.progress.start()
		self._beginUpdate()
		if self.certified.isChecked()==False and self.userLocked==False and self.locked==True:
			self._rebost.setAction("unlock","")
		elif self.locked==False:
			self._rebost.setAction("lock","")
		if self._rebost.isRunning():
			self._rebost.requestInterruption()
			self._rebost.wait()
		self._rebost.start()
	#def _unlockRebost

	def _appseduCertified(self):
		wdg=QWidget()
		lay=QHBoxLayout()
		lay.setSpacing(0)
		lbl=QLabel()
		chk=QCheckBox()
		chk.setObjectName("certifiedChk")
		wdg.setChecked=chk.setChecked
		wdg.isChecked=chk.isChecked
		wdg.blockSignals=chk.blockSignals
		if self.userLocked==True:
			chk.setChecked(True)
			chk.setEnabled(True)
		chk.stateChanged.connect(self._unlockRebost)
		wdg.setObjectName("certified")
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","appsedu128x64.png")
		pxm=QtGui.QPixmap(img).scaled(132,40,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
		lbl.setPixmap(pxm)
		lbl.setAlignment(Qt.AlignCenter|Qt.AlignCenter)
		lay.addWidget(lbl,Qt.AlignRight)
		lay.addWidget(chk,Qt.AlignLeft)
		wdg.setLayout(lay)
		wdg.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		return(wdg)
	#def _appseduCertified

	def _defInst(self):
		btnInst=QPushButton(i18n.get("INSTALLED"))
		btnInst.clicked.connect(self._loadInstalled)
		return(btnInst)
	#def _defHome

	def _defHome(self):
		btnHome=QPushButton(i18n.get("HOME"))
		#btnHome.setIcon(icn)
		btnHome.clicked.connect(self._goHome)
		btnHome.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		return(btnHome)
	#def _defHome

	def _btnBar(self):
		wdg=QWidget()
		wdg.setObjectName("btnBar")
		lay=QHBoxLayout()
		wdg.setLayout(lay)
		btnHome=self._defHome()
		btnHome.setObjectName("btnHome")
		lay.addWidget(btnHome,Qt.AlignRight)
		btnInst=self._defInst()
		btnInst.setObjectName("btnHome")
		lay.addWidget(btnInst,Qt.AlignLeft)
		btnHome.setMaximumWidth(btnInst.sizeHint().width())
		wdg.setMaximumWidth(btnInst.sizeHint().width()*2+10)
		return(wdg)
	#def _btnBar

	def _launchLlxUp(self):
		self.parent.hide()
		#QApplication.processEvents()
		subprocess.run(["pkexec","lliurex-up"])
		self.parent.show()
	#def _launchLlxUp

	def _defInfo(self):
		wdg=QPushButton(i18n.get("UPGRADES"))
		wdg.setObjectName("upgrades")
		wdg.clicked.connect(self._launchLlxUp)
		wdg.hide()
		wdg.setCursor(Qt.PointingHandCursor)
		return(wdg)
	#def _defInfo

	def _defError(self):
		pev=paneErrorView.paneErrorView()
		pev.requestLoadPortrait.connect(self._loadPortraitFromError)
		return(pev)
	#def _defError
	
	def _defSearch(self):
		wdg=QWidget()
		wdg.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.setObjectName("wsearch")
		self.searchBox=QLineEdit()
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
		return(wdg)
	#def _defSearch

	def _defProgress(self):
		wdg=QProgressImage(self)
		return(wdg)
	#def _defProgress

	def _resetSearch(self):
		self.searchBox.setText("")
		self.searchBox.setFocus()
	#def _resetSearch

	def tableLeaveEvent(self,*args):
		self._globalView.table.setAutoScroll(False)
		return(False)
	#def tableLeaveEvent

	def _getGlobalViewPane(self):
		gvp=paneGlobalView.paneGlobalView(self._rebost)
		gvp.requestLoadDetails.connect(self._loadGlobalDetails)
		gvp.requestInstallApp.connect(self._installApp)
		return(gvp)
	#def _getGlobalViewPane

	def _getDetailViewPane(self):
		dvp=paneDetailView.main(self._rebost)
		dvp.requestInstallApp.connect(self._installApp)
		return(dvp)
	#def _getDetailViewPane

	def _getHomeViewPane(self):
		hvp=paneHomeView.main(self._rebost)
		hvp.clickedApp.connect(self._loadHomeDetails)
		hvp.clickedCategory.connect(self._loadCategory)
		hvp.requestInstallApp.connect(self._installApp)
		return(hvp)
	#def _getHomeViewPane

	def _populateCategories(self,cats):
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
		for cat in masterCategories:
			if cat.lower() not in lowercats:
				self.lstCategories.addItem(" · {}".format(cat))
				item=self.lstCategories.item(self.lstCategories.count()-1)
				if item!=None:
					item.setToolTip(cat)
				lowercats.append(cat.lower())
	#def _populateCategories

	def _getApps(self,category="",installed=False):
		if category!="":
			category=self.i18nCat.get(category,category)
			self._globalView.getApps(category,installed)
		else:
			self._globalView.hide()
	#def _getApps

	def _endGetUpgradables(self,*args):
		if args[0]==True:
			self.lblInfo.show()
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self._debug("Get available upgrades")
		self._llxup.start()
	#def _getUpgradables

	def _beginUpdate(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btnSettings.hide()
		if self.init==False:
			self.progress.start()
		self.stopAdding=True
		self._homeView.hide()
	#def _beginUpdate

	def _endUpdate(self):
		self._return()
	#def _endUpdate

	def _goHome(self,*args,**kwargs):
		self.lstCategories.setCurrentRow(-1)
		self._stopThreads()
		self._homeView.show()
		self._globalView.hide()
		self._detailView.hide()
	#def _goHome

	def _beginLoad(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.lstCategories.setEnabled(False)
		self.progress.start()
		QApplication.processEvents()
		self.resetScreen()
		self.oldTime=time.time()
	#def _beginLoad

	def _loadInstalled(self):
		self._beginLoad()
		self._rebost.setAction("installed")
		self._rebost.blockSignals(False)
		self._rebost.start()
		return
		#Disable app url if any (JustInCase)
	#def _loadInstalled

	def _endLoadInstalled(self,*args):
		self.appsRaw=json.loads(args[0])
		self.apps=self.appsRaw.copy()
		self.loading=False
		self._debug("LOAD INSTALLED END")
		self._globalView.show()
		self._homeView.hide()
		self._endUpdate()
		self._globalView.loadApps(self.apps)
		self.updateScreen(True)
		self.oldTime=time.time()
	#def _endSearchApps

	def _searchApps(self):
		txt=self.searchBox.text()
		self._beginLoad()
		self.lstCategories.setCurrentRow(-1)
		if len(txt)==0:
			return
		else:
			self._rebost.setAction("search",txt)
			self._rebost.blockSignals(False)
			self._rebost.start()
	#def _searchApps

	def _endSearchApps(self,*args):
		self.appsRaw=json.loads(args[0])
		self.apps=self.appsRaw.copy()
		self.loading=False
		self._debug("LOAD SEARCH END")
		self._globalView.show()
		self._homeView.hide()
		self._endUpdate()
		self._globalView.loadApps(self.apps)
		self.updateScreen(True)
		self.oldTime=time.time()
	#def _endSearchApps

	def setBtnIcon(self,icn=""):
		if icn!="":
			icn=QtGui.QIcon(os.path.join(RSRC,"{}.png".format(icn)))
		if len(self.searchBox.text())>0:
			icn=QtGui.QIcon(os.path.join(RSRC,"cancel.png"))
		else:
			icn=QtGui.QIcon(os.path.join(RSRC,"search.png"))
		#self.btnSearch.setIconSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		self.btnSearch.setIcon(icn)
	#def setBtnIcon

	def _changeSearchAppsBtnIcon(self):
		if len(self.searchBox.text())>0:
			self.setBtnIcon("cancel")
		else:
			self.setBtnIcon("search")
	#def _changeSearchAppsBtnIcon(self):

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

	def _loadCategory(self,*args):
		#Disable app url if any (JustInCase)
		print("START LOAD")
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
		self._beginLoad()
		cat=self._getRawCategory(cat)
		self.searchBox.setText("")
		if cat in self.categoriesTree.keys():
			self._globalView.populateCategories(self.categoriesTree[cat],cat)
		elif cat!="":
			wdg=self._globalView.topBar.currentItem()
			if wdg!=None:
				font=wdg.font()
				font.setBold(False)
				for idx in range(0,self._globalView.topBar.count()):
					self._globalView.topBar.itemAt(idx).widget().setFont(font)
				font.setBold(True)
				wdg.setFont(font)
			self._globalView.topBar.show()
		self._getApps(cat)
	#def _loadCategory

	def _endLoadCategory(self,*args):
		self._debug("LOAD CATEGORY END")
		self._globalView.show()
		self._homeView.hide()
		self._detailView.hide()
		self._endUpdate()
		self.appsRaw=[]
		appsRaw=json.loads(args[0])
		for key,item in appsRaw.items():
			self.appsRaw.extend(item)
		self.apps=self.appsRaw.copy()
		self._globalView.loadApps(self.apps)
		#self.updateScreen(True)
		self.oldTime=time.time()
	#def _endLoadCategory

	def _setInstallingState(self,app,state):
		app["state"]=state
		self._rebost.setAction("setAppState",app["id"],state)
		self._rebost.start()
		self._rebost.wait()
		return(app)
	#def _setInstallingState

	def _getRunappResults(self,app,proc):
		self.setCursor(self.oldCursor)
		app["state"]=0
		if proc==None:
			return
		if proc.returncode!=0:
			#pkexec ret values
			#127 -> Not authorized
			if proc.returncode==127:
				self.showMsg(title="AppsEdu Store",summary=app["name"],text=i18n.get("ERRUNAUTHORIZED"),icon=app["icon"],timeout=5000)
			else:
				self.showMsg(title="AppsEdu Store",summary=app["name"],text=i18n.get("ERRUNKNOWN"),icon=app["icon"],timeout=5000)
		if self.installingBtn!=None:
			oldReferrer=self.referrerBtn
			self.referrerBtn=self.installingBtn
			self._returnFromDetail(None,app)
			self.referrerBtn=oldReferrer
			self.installingBtn=None
		self._rebost.setAction("setAppState",app["id"],0)
		self._rebost.start()
		self._rebost.wait()
		return
	#def _getRunappResults

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
			priority=self.helper.getBundlesByPriority(app)
			idx=list(priority.keys())
			idx.sort()
			bundle=priority[idx[0]].split(" ")[0]
		pkg=app.get('bundle',{}).get(bundle,'')
		if pkg!="":
			installer=str(self.rc.getExternalInstaller())
			if installer!="":
				state=7
				if isinstance(wdg,QPushButtonRebostApp):
					self.installingBtn=wdg
					if wdg.text()==i18n["REMOVE"]:
						state=8
				elif isinstance(wdg,QPushButton):
					state=8
				self._setInstallingState(app,state)
				self.runapp.setArgs(app,[installer,pkg,bundle])
				self.runapp.start()
		return
	#def _installApp

	def _loadLockedRebost(self):
		self.progress.start()
		self._rebost.setAction("restart")
		self._rebost.start()
	#def _loadLockedRebost

	def _detailLoaded(self,*args,**kwargs):
		self._stopThreads()
		self._detailView.show()
		self._homeView.hide()
		self.progress.stop()
	#def _detailLoaded

	def _endLoadDetails(self,icn,*args):
		self.setChanged(False)
		self.parent.setWindowTitle("{} - {}".format(APPNAME,args[-1].get("name","").capitalize()))
		self._detailView.setParms({"name":args[-1].get("name",""),"id":args[-1].get("id",""),"icon":icn})
		self._detailView.show()
		self.setCursor(self.oldCursor)
		self._detailView.setFocus()
	#def _endLoadDetails

	def _loadDetails(self,*args,**kwargs):
		self._stopThreads()
		self.progress.start()
		icn=""
		app=""
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
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
		self._stopThreads()
		if app!="":
			self._endLoadDetails(icn,app)
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
		self._errorView.hide()
		self._goHome()
	#def _loadPortraitFromError

	def _loadFromArgs(self,*args,**kwargs):
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self._referrerPane=self._homeView
		self._loadDetails(json.loads(args[0])[0],kwargs)
	#def _loadFromArgs

	def setParms(self,*args):
		appsedu=args[0]
		self._debug("** Detected parm on init **")
		if "://" in appsedu:
			self._stopThreads()
			pkgname=appsedu.split("://")[-1]
			self._referrerPane=self._detailView
			self._debug("Seeking for {}".format(pkgname))
			self._detailView.setParms(pkgname)
	#def setParms
	
	def _returnFromDetail(self,*args,**kwargs):
		if self._detailView.isVisible():
			self._detailView.hide()
			if self._referrerPane==self._detailView:
				self._referrerPane=None
				self._homeView.show()
				if len(self._homeView.layout().children())==0:
					self._homeView.updateScreen()
			else:
				self._referrerPane.show()
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
		#QApplication.processEvents()
		#	self.referrerBtn.setApp(args[1])
		#	self.referrerBtn.updateScreen()
		self.progress.stop()
		self.lstCategories.setCursor(self.oldCursor)
		self.lstCategories.setEnabled(True)
	#def _return

	def updateScreen(self,addEnable=None):
		isConnected=self._chkNetwork()
		self._errorView.setVisible(not(isConnected))
		if isConnected==False:
			self._endUpdate()
			self._globalView.hide()
			self._homeView.hide()
			self._detailView.hide()
			self._stopThreads()
			return
		if self._referrerPane!=None:
			self._globalView.hide()
			self._homeView.hide()
			self._detailView.hide()
			self._referrerPane.show()
		if self._globalView.isVisible():
			self._globalView.updateScreen()
		elif self._detailView.isVisible():
			self._stopThreads()
		elif self._homeView.isVisible():
			self._stopThreads()
			if len(self._homeView.layout().children())==0:
				self._homeView.updateScreen()
			self._endUpdate()
	#def _updateScreen
	
	def resetScreen(self):
		self._stopThreads()
		self.appsLoaded=0
		self.pendingApps={}
		self.refererApp=None
		self.appsSeen=[]
		self._globalView.loadAppsStop()
		self._globalView.table.clean()
		self._globalView.topBar.hide()
	#def resetScreen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

