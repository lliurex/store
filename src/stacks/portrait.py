#!/usr/bin/python3
import sys,time,signal
import os
import subprocess
import json
import dbus
import dbus.service
import dbus.mainloop.glib
import random
from PySide2.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHBoxLayout, QWidget,QVBoxLayout,QListWidget, \
							QCheckBox,QListWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread,QEvent
from QtExtraWidgets import QSearchBox,QStackedWindowItem,QFlowTouchWidget
from rebost import store 
from libth import storeHelper,updateAppData,getData,llxup
from btnRebost import QPushButtonRebostApp
from prgBar import QProgressImage
import exehelper
from rpanel import mainPanel
from lpanel import detailPanel
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
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.pendingApps={}
		self.rc=store.client()
		self.getData=getData()
		self._rebost=storeHelper(rc=self.rc)
		self._llxup=llxup()
		self.epi=exehelper.appLauncher()
		self._initRegisters()
		self._initThreads()
		self._initGUI()
		#DBUS loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		#DBUS connections
		bus=dbus.SessionBus()
		objbus=bus.get_object("net.lliurex.rebost","/net/lliurex/rebost")
		self._getUpgradables()
	#	objbus.connect_to_signal("reloadSignal",self._reload,dbus_interface="net.lliurex.rebost")
	#	objbus.connect_to_signal("beginUpdateSignal",self._beginUpdate,dbus_interface="net.lliurex.rebost")
	#	(self.locked,self.userLocked)=self._rebost.isLocked()
	#def __init__

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
		self.isConnected=self._chkNetwork()
	#def _initCatalogue

	def _initThreads(self):
		self.appUpdate=updateAppData(rc=self.rc)
		self.appUpdate.dataLoaded.connect(self._endLoadApps)
		self.getData.dataLoaded.connect(self._loadData)
		self._llxup.chkEnded.connect(self._endGetUpgradables)
		self._rebost.test.connect(self._loadHome)
		self._rebost.lstEnded.connect(self._endLoadCategory)
		self._rebost.srcEnded.connect(self._endSearchApps)
		self._rebost.lckEnded.connect(self._endLock)
		self._rebost.rstEnded.connect(self._endRestart)
		self._rebost.staEnded.connect(self._endGetLockStatus)
		self._rebost.catEnded.connect(self._populateCategories)
		self.epi.runEnded.connect(self._endLaunchHelper)
		self.zmdLauncher=exehelper.zmdLauncher()
		self.zmdLauncher.zmdEnded.connect(self._endLaunchHelper)
	#def _initThreads(self):

	def _initGUI(self):
		self.appUrl=""
		self.hideControlButtons()
		self.referersHistory={}
		self.referersShowed={}
		self.installingApp=None
		self.level='user'
		self.oldCursor=self.cursor()
		self.refresh=True
		self.released=True
		self.oldSearch=""
		self.maxCol=5
		self.setStyleSheet(css.portrait())
	#def _initGUI

	def _signals(self,*args):
		applied=[]
		for name,ref in self.referersShowed.items():
			if ref==None:
				applied.append(name)
				continue
			app=json.loads(self.rc.showApp(name))[0]
			if isinstance(app,str):
				app=json.loads(app)
			ref.setApp(app)
			ref.updateScreen()
		for app in applied:
			if app in self.referersHistory.keys():
				self.referersHistory.pop(app)
	#def _signals

	def _debug(self,msg):
		if self.dbg==True:
			print("Portrait: {}".format(msg))
	#def _debug

	def _chkNetwork(self):
		state=False
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
		self._rebost.wait()
		QApplication.processEvents()
		if self.locked==False and self.userLocked==True:
			self._loadLockedRebost()
		else:
			self.progress.lblInfo.setVisible(False)
			self.progress.setAttribute(Qt.WA_StyledBackground, False)
			self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
			self._getAppList()
			self._endUpdate()
	#def _endGetLockStatus

	def _endRestart(self,*args):
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self.progress.stop()
		self._goHome()
	#def _endRestart

	def _endLock(self,*args):
		self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self.progress.stop()
		self._goHome()
	#def _endLock

	def _stopThreads(self):
		if self.appsToLoad==-1: #Init 
			exit
		self.appUpdate.blockSignals(True)
		self.getData.blockSignals(True)
		self._rebost.blockSignals(True)
		self._llxup.blockSignals(True)
		self.appUpdate.stop()
		self.appUpdate.requestInterruption()
		self.appUpdate.wait()
		self.getData.stop()
		self.getData.requestInterruption()
		self.getData.wait()
		self._rebost.requestInterruption()
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
		self.sortAsc=False
		wdg=self._navPane()
		wdg.setObjectName("wdg")
		self.box.addWidget(wdg,0,0,Qt.AlignLeft)
		self.rp=self._mainPane()
		self.rp.tagpressed.connect(self._loadCategory)
		self.box.addWidget(self.rp,0,1)
		self.lp=self._detailPane()
		self.lp.setObjectName("detailPanel")
		self.lp.clicked.connect(self._returnDetail)
		self.lp.loaded.connect(self._detailLoaded)
		self.box.addWidget(self.lp,0,1)
		self.lp.hide()
		self.progress=self._defProgress()
		self.box.addWidget(self.progress,0,0,self.box.rowCount(),self.box.columnCount())
		self.btnSettings=QPushButton()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		self.box.setColumnStretch(1,1)
		self.setObjectName("portrait")
		self.rp.setVisible(False)
		self.errTab=self._defError()
		self.errTab.setObjectName("errorMsg")
		self.errTab.setVisible(not(self.isConnected))
		self.box.addWidget(self.errTab,0,1,self.box.rowCount(),self.box.columnCount(),Qt.AlignCenter)
	#	self.resetScreen()
	#def _load_screen

	def _reload(self,*args,**kwargs):
		self._stopThreads()
		self.progress.start()
		self.refresh=True
		self.rp.searchBox.setText("")
		self._beginUpdate()

	def _closeEvent(self,*args):
		self._stopThreads()
	#def _closeEvent
	
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
		self.lstCategories.setCursor(Qt.PointingHandCursor)
		self.lstCategories.currentItemChanged.connect(self._decoreCmbCategories)
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

	def _defInfo(self):
		wdg=QPushButton(i18n.get("UPGRADES"))
		wdg.setObjectName("upgrades")
		wdg.clicked.connect(self._launchLlxUp)
		wdg.setVisible(False)
		return(wdg)
	#def _defInfo
	
	def _defError(self):
		wdg=QWidget()
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		box=QVBoxLayout()
		wdg.setLayout(box)
		icn=QtGui.QIcon.fromTheme("network-wireless")
		pxm=QtGui.QPixmap()
		pxm=icn.pixmap(QSize(256,256))
		lblIcn=QLabel()
		lblIcn.setPixmap(pxm)
		box.addWidget(lblIcn,Qt.AlignBottom,Qt.AlignCenter)
		lblTxt=QLabel(i18n["CHK_NETWORK"])
		box.addWidget(lblTxt,Qt.AlignCenter,Qt.AlignCenter)
		btnCnf=QPushButton(i18n["OPN_NETWORK"])
		btnCnf.clicked.connect(self._launchNetworkSettings)
		box.addWidget(btnCnf,Qt.AlignTop,Qt.AlignCenter)
		return(wdg)
	#def _defError

	def _defProgress(self):
		wdg=QProgressImage(self)
		return(wdg)
	#def _defProgress

	def _mainPane(self):
		mp=mainPanel()
		mp.searchBox.returnPressed.connect(self._searchApps)
		mp.searchBox.textChanged.connect(self._changeSearchAppsBtnIcon)
		mp.btnSearch.clicked.connect(self._resetSearch)
		return(mp)
	#def _mainPane

	def _resetSearch(self):
		self.rp.searchBox.setText("")
		self.rp.searchBox.setFocus()

	def tableLeaveEvent(self,*args):
		self.rp.table.setAutoScroll(False)
		return(False)
	#def enterEvent

	def _detailPane(self):
		dp=detailPanel()
		return(dp)
	#def _detailPane

	def _launchNetworkSettings(self,*args):
		self.parent.setVisible(False)
		QApplication.processEvents()
		cmd=["systemsettings","kcm_networkmanagement"]
		subprocess.run(cmd)
		self.parent.setVisible(True)
	#def _launchNetworkSettings

	def _launchLlxUp(self):
		self.parent.setVisible(False)
		QApplication.processEvents()
		subprocess.run(["pkexec","lliurex-up"])
		self.parent.setVisible(True)
	#def _launchLlxUp

	def _unlockRebost(self,*args):
		self._stopThreads()
		self.box.addWidget(self.progress,0,0,self.box.rowCount(),self.box.columnCount())
		self.progress.setAttribute(Qt.WA_StyledBackground, True)
		self.progress.lblInfo.setVisible(True)
		self.progress.lblInfo.unlocking=True
		self.stopAdding=True
		self.refresh=True
		self.rp.searchBox.setText("")
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

	def _populateCategories(self,cats):
		self.lstCategories.clear()
		self.lstCategories.setSizeAdjustPolicy(self.lstCategories.SizeAdjustPolicy.AdjustToContents)
		self.i18nCat={}
		self.catI18n={}
		self.categoriesTree=cats
		self.lstCategories.addItem(i18n.get('ALL'))
		item=self.lstCategories.itemAt(0,0)
		if item!=None:
			font=item.font()
			font.setBold(True)
			item.setFont(font)
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

	def _getAppList(self,cat="",limitBy=0):
		if len(cat)>0:
			cat=self.i18nCat.get(cat,cat)
			if limitBy==0:
				self._rebost.setAction("list","({})".format(cat))
				self._debug("Loading cat {}".format(cat))
			else:
				#If max rows is defined rebost tries to return as many apps as possible
				#getting categories from raw data (deep search)
				self._rebost.setAction("list","{}".format(categories),limitBy)
				self._debug("Loading limited cat {}".format(cat))
		else:
			self._rebost.setAction("search","")
		if self._rebost.isRunning():
			self._rebost.requestInterruption()
			#self._rebost.wait()
		self._rebost.start()
	#def _getAppList

	def _endGetUpgradables(self,*args):
		if args[0]==True:
			QApplication.processEvents()
			self.lblInfo.setVisible(True)
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self._debug("Get available upgrades")
		self._llxup.start()
		#self._rebost.wait()
	#def _getUpgradables

	def _beginUpdate(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btnSettings.setVisible(False)
		if self.init==False:
			self.progress.start()
		self.stopAdding=True
		#self.rp.setVisible(False)
	#def _beginUpdate

	def _endUpdate(self):
		self.appUpdate.blockSignals(False)
		self._return()
	#def _endUpdate

	def _goHome(self,*args,**kwargs):
		self.lstCategories.setCurrentRow(0)
		self._loadCategory("")
	#def _goHome

	def _loadHome(self,*args,**kwargs):
		self._debug("Rebost running: {} - {} - {}".format(self._rebost.isFinished(),self._rebost.isRunning(),self._rebost.action))
		if isinstance(args[0],bool):
			if args[0]==False:
				return
		self.oldTime=time.time()
		self.sortAsc=False
		self.rp.searchBox.setText("")
		if self.appUrl=="":
			self._rebost.blockSignals(False)
			self._rebost.setAction("search","")
			self._rebost.start()
		self.resetScreen()
		self.lstCategories.setCurrentRow(0)
		self.updateScreen(True)
	#def _loadHome

	def _loadInstalled(self):
		#Disable app url if any (JustInCase)
		self.filters["installed"]=True
		#self._goHome()
		#return
		self.appUrl=""
		self.appsLoaded=0
		flag=""
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.lstCategories.setEnabled(False)
		self._stopThreads()
		self.stopAdding=True
		self.resetScreen()
		self.progress.start()
		appsFiltered=[]
		for app in self.apps:
			japp=json.loads(app)
			states=japp.get("state",{}).copy()
			bundles=japp.get("bundle",{}).copy()
			if "package" in states.keys():
				states["package"]=states.get("zomando",states["package"])
			for bundle in bundles:
				if states.get(bundle,"1")=="0":
					appsFiltered.append(app)
		self.apps=appsFiltered.copy()
		self.appUpdate.blockSignals(False)
		self.appUpdate.start()
		self.appsRaw=self.apps.copy()
		self.refresh=True
		if len(self.apps)==0:
			self.refresh=False
		self.loading=False
		self.updateScreen(True)
		self._endUpdate()
	#def _loadInstalled

	def _resetSearchBtnIcon(self):
		txt=self.rp.searchBox.text()
		if txt==self.oldSearch:
			icn=QtGui.QIcon.fromTheme("dialog-cancel")
		else:
			icn=QtGui.QIcon.fromTheme("search")
	#def _resetSearchBtnIcon

	def _searchApps(self):
		txt=self.rp.searchBox.text()
		if txt==self.oldSearch:
			return
		self.lstCategories.setCurrentRow(-1)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self._stopThreads()
		self.stopAdding=True
		self.resetScreen()
		self.progress.start()
		self.oldSearch=txt
		self.lstCategories.setCurrentRow(0)
		if len(txt)==0:
			self._getAppList()
		else:
			self._rebost.setAction("search",txt)
			self._rebost.blockSignals(False)
			self._rebost.start()
	#def _searchApps

	def _endSearchApps(self,*args):
		self.appsRaw=args[0]
		self.appsRaw.sort()
		self.apps=self.appsRaw
		self.updateScreen(True)
		self.oldTime=time.time()
		self.loading=False
		self._endUpdate()
	#def _endSearchApps

	def _changeSearchAppsBtnIcon(self):
		if len(self.rp.searchBox.text())>0:
			self.rp.setBtnIcon("cancel")
		else:
			self.rp.setBtnIcon("search")
	def _searchAppsBtn(self):
		txt=self.rp.searchBox.text()
		if txt==self.oldSearch:
			self.rp.searchBox.setText("")
			txt=""
		self.oldSearch=txt
		self._searchApps(resetOld=False)
	#def _searchAppsBtn

	def _decoreCmbCategories(self,*args):
		if isinstance(args[0],QListWidgetItem):
			font=args[0].font()
			font.setBold(True)
			args[0].setFont(font)
		if len(args)>1:
			if isinstance(args[1],QListWidgetItem):
				font=args[1].font()
				font.setBold(False)
				args[1].setFont(font)
	#def _decoreCmbCategories

	def _loadCategory(self,*args):
		#Disable app url if any (JustInCase)
		self.appUrl=""
		self.appsLoaded=0
		cat=None
		flag=""
		if len(args)==0:
			cat=""
		elif isinstance(args[0],QListWidgetItem):
			cat=args[0].text()
		elif isinstance(args[0],str):
			cat=args[0]
		if cat==None:
			return
		if time.time()-self.oldTime<MINTIME:
			return
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.lstCategories.setEnabled(False)
		self._stopThreads()
		self.stopAdding=True
		self.resetScreen()
		self.progress.start()
		self.oldTime=time.time()
		cat=self._getRawCategory(cat)
		self.rp.searchBox.setText("")
		self._getAppList(cat)
		if cat in self.categoriesTree.keys():
			self.rp.populateCategories(self.categoriesTree[cat],cat)
		elif cat!="":
			self.rp.topBar.setVisible(True)
	#def _loadCategory

	def _endLoadCategory(self,*args):
		self.appsRaw=args[0]
		self.apps=self.appsRaw.copy()
		self.updateScreen(True)
		self.oldTime=time.time()
		self._debug("LOAD CATEGORY END")
		self._endUpdate()
	#def _endLoadCategory

	def eventFilter(self,*args):
		if isinstance(args[0],QPushButtonRebostApp):
			if isinstance(args[1],QtGui.QKeyEvent):
				if args[1].type()==QEvent.Type.KeyPress:
					newPos=-1
					if args[1].key()==Qt.Key_Left or args[1].key()==Qt.Key_Up:
						idx=self.rp.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Up:
							elements=int(self.rp.width()/(args[0].width()+int(MARGIN)*2))-1
						newPos=idx-elements
					elif args[1].key()==Qt.Key_Right or args[1].key()==Qt.Key_Down:
						idx=self.rp.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Down:
							elements=int(self.rp.width()/(args[0].width()+int(MARGIN)*2))-1
						newPos=idx+elements
						#Ugly hack for autoscroll to focused item
					if newPos!=-1:
						if newPos<self.rp.table.count() and newPos>=0:
							btn=self.rp.table.itemAt(newPos)
							btn.widget().setFocus()
							btn.widget().setEnabled(False)
							btn.widget().setEnabled(True)
							btn.widget().setFocus()
		if isinstance(args[0],QListWidget):
			if args[1].type==QEvent.Type.KeyRelease:
				self.released=True
			elif args[1].type==QEvent.Type.KeyPress:
				self.released=False
		return(False)
	#def eventFilter(self,*args):

	def _getMoreData(self):
		#if (self.rp.table.verticalScrollBar().value()>=self.rp.table.verticalScrollBar().maximum()-30) and self.appsLoaded!=len(self.apps):
		if (self.rp.table.verticalScrollBar().value()>=self.rp.table.verticalScrollBar().maximum()/2) and self.appsLoaded!=len(self.apps):
			if hasattr(self,"loading")==False:
				self.loading=True
			if self.loading==True:
				return
			self.loading=True
			self.appsToLoad=int(self.appsToLoad*2.90)
			if self.appsToLoad+self.appsLoaded>len(self.apps):
				self.appsToLoad=len(self.apps)-self.appsLoaded
			self.getData.stop()
			self.getData.wait()
			moreApps=[]
			apps=self.apps[self.appsLoaded:self.appsLoaded+self.appsToLoad]
			for app in apps:
				moreApps.append(json.loads(app))
			#self._loadData(moreApps)
			self.loading=False
			#for wdg in self.wdgs:
			#	self.rp.table.addWidget(wdg)
			#	#self.rp.table.setCellWidget(wdg[0],wdg[1],wdg[2])
	#def _getMoreData

	def _beginLoadData(self,idx,idxEnd,applist=None):
		if self.getData.isRunning()==False:
			self.loading=False
			self._beginUpdate()
			self.getData.setApps(self.apps)
			self.getData.blockSignals(False)
			self.getData.start()
	#def _beginLoadData

	def _loadData(self,apps):
		col=0
		#self.table.setRowHeight(self.table.rowCount()-1,btn.iconSize+int(btn.iconSize/16))
		colspan=random.randint(1,self.maxCol)
		colspan=self.maxCol
		span=colspan
		btn=None
		if self.loading==True:
			return
		self.loading=True
		self.appsToLoad=len(self.apps)
		if len(self.pendingApps)>0:
			self._stopThreads()
		self._debug("************************")
		self._debug("************************")
		self._debug("From {} To {} of {}".format(self.appsLoaded,self.appsLoaded+self.appsToLoad,len(apps)))
		a=time.time()
		self._debug("Start: {}".format(a))
		if len(apps)>0:
			if self.stopAdding==True:
				self.appsLoaded=0
				apps=[json.loads(item) for item in self.apps]
				self.stopAdding=False
				self.pendingApps={}
			self._addAppsToGrid(apps)
		self._debug("End: {}".format(time.time()-a))
		self._debug("************************")
		self._debug("************************")
		self._endLoadData()
		self.loading=False
	#def _loadData

	def _addAppsToGrid(self,apps):
		if self.filters.get("installed",False)==True:
			self.rp.table.setEnabled(False)
			print("WARNING!!!!: INSTALLED FILTER APPLIED")
		pendingApps={}
		while apps:
			jsonapp=apps.pop(0)
			if self.stopAdding==True:
				break
			b=time.time()
			appname=jsonapp['name']
			if appname in self.appsSeen:
				self.appsLoaded+=1
				continue
			if len(appname.strip())==0:
				continue
			if self.filters["installed"]==True:
				state="1"
				for bun,state in jsonapp["state"].items():
					if bun=="zomando":
						continue
					if state=="0":
						state="3"
						break
				if state!="3":
					continue
				self._debug("State for {}: {}".format(jsonapp["name"],jsonapp["state"]))
			self.appsSeen.append(appname)
			btn=QPushButtonRebostApp(jsonapp)
			btn.clicked.connect(self._loadDetails)
			btn.installEventFilter(self)
			btn.install.connect(self._installBundle)
			if jsonapp["summary"]=="":
				pendingApps.update({appname:btn})
			self.rp.table.addWidget(btn)
			if appname in self.referersHistory.keys():
				self.referersShowed.update({appname:btn})
			self.appsLoaded+=1
			#self._debug("Add: {}".format(time.time()-b))
			#Force btn show
			QApplication.processEvents()
			if len(pendingApps)>9:
				self.appUpdate.addApps(pendingApps)
				self.pendingApps.update(pendingApps)
				if self.appUpdate.isRunning()==False:
					self.appUpdate.start()
				pendingApps={}

		if len(pendingApps)>0:
			self.appUpdate.addApps(pendingApps)
			self.pendingApps.update(pendingApps)
			if self.appUpdate.isRunning()==False:
				self.appUpdate.start()
			pendingApps={}
		if self.filters.get("installed",False)==True:
			self.rp.table.setEnabled(True)
		self.filters["installed"]=False
	#def _addAppsToGrid

	def _endLoadData(self):
		if (self.appsLoaded==0 and self.lstCategories.count()==0):
			self._rebost.setAction("test")
			self._rebost.blockSignals(False)
			self._rebost.start()
		elif self.init==False:
			self.rp.setVisible(True)
			self.init=True
		else:
			#if len(self.pendingApps)>0:
			#	self.appUpdate.blockSignals(False)
			#	self.appUpdate.start()
			self._endUpdate()
		self.refresh=True
	#def _endLoadData(self):

	def _endLoadApps(self,args):
		if len(args)==0:
			self._loadHome()
		if isinstance(args[0],str):
			app=json.loads(args[0])
		else:
			app=args[0]
		if app["name"] in self.pendingApps.keys():
			self.pendingApps[app["name"]].setApp(app)
			self.pendingApps[app["name"]].updateScreen()
		self._rebost.setAction("updatePkgData",app)
		self._rebost.blockSignals(False)
		self._rebost.start()
	#def _endLoadApps

	def _installBundle(self,*args):
		app=args[1]
		refererApp=args[0]
		if self.zmdLauncher.isRunning() or self.epi.isRunning():
			self.showMsg(summary=i18n.get("ERRMORETHANONE",""),msg="{}".format(app["name"]),timeout=4)
			refererApp.progress.stop()
			self.installingApp.setFocus()
			return
		self.installingApp=refererApp
		self.refererApp=refererApp
		if isinstance(app,dict)==False:
			return
		bundle=""
		priority=["zomando","flatpak","snap","package","appimage","eduapp"]
		for bund in priority:
			if app.get("bundle",{}).get(bund,"")!="":
				bundle=bund
				break
		if len(bundle)==0 or bundle=="package":
			if app.get("bundle",{}).get("zomando","")!="":
				bundle="zomando"
			elif len(bundle)==0:
				return
		self.rc.enableGui(True)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		pkg=app.get('name').replace(' ','')
		user=os.environ.get('USER')
		res=self.rc.testInstall("{}".format(pkg),"{}".format(bundle),user=user)
		try:
			res=json.loads(res)[0]
		except Exception as e:
			self._debug(e)
			res={}
		epi=res.get('epi')
		self._debug("Invoking EPI for {}".format(epi))
		if epi==None:
			if res.get("done",0)==1 and "system package" in res.get("msg","").lower():
				self.showMsg(summary=i18n.get("ERRSYSTEMAPP",""),msg="{}".format(app["name"]),timeout=4)
			else:
				self.showMsg(summary=i18n.get("ERRUNKNOWN",""),msg="{}".format(app["name"]),timeout=4)
			self.updateScreen(True)
			self.progress.stop()
		else:
			if bundle=="zomando":# and app.get("state",{}).get("zomando","0")=="1":
				self.zmdLauncher.setApp(app)
				self.zmdLauncher.start()
			else:
				cmd=["pkexec","/usr/share/rebost/helper/rebost-software-manager.sh",res.get('epi')]
				self.epi.setArgs(app,cmd,bundle)
				self.epi.start()
	#def _installBundle

	def _endLaunchHelper(self,*args,**kwargs):
		for app in [self.refererApp,self.installingApp]:
			if app==None:
				continue
			btn=app
			app=json.loads(self.rc.showApp(args[0]["name"]))[0]
			btn.setApp(json.loads(app))
			btn.updateScreen()
		self.referererApp=None
		self.installingApp=None
		self.setCursor(self.oldCursor)
	#def _endLaunchHelper

	def _loadLockedRebost(self):
		self.box.addWidget(self.progress,0,0,self.box.rowCount(),self.box.columnCount())
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self.progress.start()
		self._rebost.setAction("restart")
		self._rebost.start()
	#def _loadLockedRebost


	def _loadDetails(self,*args,**kwargs):
		#self._stopThreads()
		self.progress.start()
		icn=""
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		if isinstance(args[0],QPushButtonRebostApp):
			icn=args[0].iconUri.pixmap()
		self._endLoadDetails(icn,*args)
	#def _loadDetails(self,*args,**kwargs):

	def _endLoadDetails(self,icn,*args):
		self.refererApp=args[0]
		self.referersHistory.update({self.refererApp.app["name"]:self.refererApp})
		self.referersShowed.update({self.refererApp.app["name"]:self.refererApp})
		self.setChanged(False)
		#self.parent.setCurrentStack(idx=3,parms={"name":args[-1].get("name",""),"icon":icn})
		self.parent.setWindowTitle("{} - {}".format(APPNAME,args[-1].get("name","").capitalize()))
		self.lp.setParms({"name":args[-1].get("name",""),"icon":icn})
		#self.rp.hide()
		self.setCursor(self.oldCursor)
	#def _endLoadDetails

	def setParms(self,*args):
		appsedu=args[0]
		self._debug("** Detected parm on init **")
		if "://" in appsedu:
			pkgname=appsedu.split("://")[-1]
			self.appUrl=pkgname
			self._debug("Seeking for {}".format(self.appUrl))
	#def setParms
	
	def _detailLoaded(self,*args,**kwargs):
		self.lp.show()
		self.progress.stop()
		if not hasattr(self,"refererApp"):
			return()
		if self.refererApp==None:
			return()

	def _updateBtn(self,*args,**kwargs):
		app=kwargs.get("app",{})
		app={}
		if isinstance(args[0],dict):
			app=args[0]
		if app!={}:
			#refered btn can be deleted so ensure there's a btn
			if self.referersShowed.get(app.get("name"))!=None:
				self.refererApp=self.referersShowed[app["name"]]
				self.refererApp.setApp(app)
				self.refererApp._stopThreads()
				self.refererApp.updateScreen()
	#def _updateBtn

	def _returnDetail(self,*args,**kwargs):
		self._updateBtn(args[0])
		if self.appUrl!="":
			self.appUrl=""
			self.progress.setAttribute(Qt.WA_StyledBackground, False)
			self.progress.lblInfo.setVisible(False)
			self.firstHide=True
			self._stopThreads()
			self._rebost.terminate()
		else:
			self._return()
	#def _returnDetail

	def _return(self,*args,**kwargs):
		self.setCursor(self.oldCursor)
		self.parent.setWindowTitle("{}".format(APPNAME))
		self.loading=False
		QApplication.processEvents()
		if self.appUrl!="":
			self.parent.setWindowTitle("{} - {}".format(APPNAME,self.appUrl.capitalize()))
			self.lp.setParms({"name":self.appUrl,"icon":""})
			self.rp.hide()
			self.lp.show()
			self.setCursor(self.oldCursor)
		else:
			self.lp.hide()
			self.rp.show()
			self.progress.stop()
		self.lstCategories.setCursor(self.oldCursor)
		self.lstCategories.setEnabled(True)
	#def _return

	def updateScreen(self,addEnable=None):
		self.isConnected=self._chkNetwork()
		self.rp.setVisible(self.isConnected)
		self.errTab.setVisible(not(self.isConnected))
		if self.isConnected==False:
			self._endUpdate()
			self._stopThreads()
			return
		if self.lstCategories.count()==0:
			self._rebost.setAction("getCategories")
			self._rebost.start()
			self._rebost.wait()

		if isinstance(addEnable,bool):
			adding=addEnable
		else:
			adding=False
		if self.loading==True:
			adding=False
		self._debug("Reload data (self.refresh={} adding={})".format(self.refresh,adding))
		if self.refresh==True and adding==True:
			for i in self.referersShowed.keys():
				self.referersShowed[i]=None
			if self.appUrl!="":
				self.init=True
				self._endUpdate()
			else:
				self._debug("Update from {} to {} of {}".format(self.appsLoaded,self.appsToLoad,len(self.apps)))
				self._beginLoadData(self.appsLoaded,self.appsToLoad)
		elif self.appsToLoad==-1: #Init 
				self.progress.start()
				self._rebost.setAction("status")
				self._rebost.start()
				QApplication.processEvents()
				self.rp.table.removeEventFilter(self)
				self.appsToLoad=0
	#def _updateScreen
	
	def resetScreen(self):
		self._stopThreads()
		self.appsLoaded=0
		self.pendingApps={}
		if len(self.rp.searchBox.text())==0:
			self.oldSearch=""
		self.appsSeen=[]
		self.rp.table.clean()
		self.rp.topBar.setVisible(False)
		QApplication.processEvents()
	#def resetScreen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

