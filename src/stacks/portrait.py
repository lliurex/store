#!/usr/bin/python3
import sys,time,signal
import os
try:
	from lliurex import lliurexup
except:
	lliurexup=None
from PySide2.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox, \
							QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget, \
							QSizePolicy,QCheckBox,QGraphicsDropShadowEffect,QListWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation,QRect,QPoint,QEasingCurve,QEvent
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QStackedWindowItem,QInfoLabel,QFlowTouchWidget
from rebost import store 
import subprocess
import json
import dbus
import dbus.service
import dbus.mainloop.glib
import random
import gettext
from btnRebost import QPushButtonRebostApp
from prgBar import QProgressImage
import exehelper
from rpanel import mainPanel
from lpanel import detailPanel
import css
from constants import *

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
	"SEARCH":_("Search"),
	"SORTDSC":_("Sort alphabetically"),
	"TOOLTIP":_("Portrait"),
	"UPGRADABLE":_("Upgradables"),
	"UPGRADES":_("There're upgrades available")
	}


class storeHelper(QThread):
	chkEnded=Signal("PyObject")
	test=Signal("PyObject")
	lstEnded=Signal("PyObject")
	srcEnded=Signal("PyObject")
	def __init__(self):
		QThread.__init__(self, None)
		self.rc=store.client()
		self.upgrades=False
		self.args=[]
		self.action="upgrade"
	#def __init__

	def setAction(self,action,*args):
		self.action=action
		if len(args)>0:
			self.args=args
	
	def run(self):
		if self.action=="upgrade":
			self._chkUpgrades()
		elif self.action=="test":
			self._test()
		elif self.action=="list":
			self._list()
		elif self.action=="search":
			self._search()
	#def run

	def _chkUpgrades(self):
		apps=json.loads(self.rc.getUpgradableApps())
		if len(apps)>0:
			self.upgrades=True
		else:
			if lliurexup!=None:
				llxup=lliurexup.LliurexUpCore()
				if len(llxup.getPackagesToUpdate())>0:
					self.upgrades=True
		self.chkEnded.emit(self.upgrades)
	#def _chkUpgrades(self):

	def _test(self):
		if self.rc!=None:
			self.rc.execute("list","lliurex")
			self.test.emit(True)
		else:
			self.test.emit(False)
	#def _test

	def _list(self):
		apps=[]
		if len(self.args)==1:
			apps.extend(json.loads(self.rc.execute('list',"({})".format(self.args[0]))))
		elif len(self.args)==2:
			apps.extend(json.loads(self.rc.execute('list',"{}".format(self.args[0]),self.args[1])))
		self.lstEnded.emit(apps)
	#def _list

	def _search(self):
		apps=json.loads(self.rc.execute("search",self.args[0]))
		self.srcEnded.emit(apps)
#class rebostHelper

class chkRebost(QThread):
	test=Signal("PyObject")
	def __init__(self):
		QThread.__init__(self, None)
		try:
			self.rc=store.client()
		except:
			self.rc=None
	#def __init__
	
	def run(self):
		if self.rc!=None:
			self.rc.execute("list","lliurex")
			self.test.emit(True)
		else:
			self.test.emit(False)
	#def run
#class chkRebost

class _performUpdate(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.rc=store.client()
		self.name=args[0]
	#def __init__

	def run(self):
		self.dataLoaded.emit(self.rc.showApp(self.name))
	#def run

class updateAppData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.apps=kwargs.get("apps",{})
		self.updates=[]
		self._stop=False
		self.cont=0
	#def __init__

	def setApps(self,*args):
		self.apps=args[0]
	#def setApps

	def run(self):
		app={}
		self._stop=False
		for name in self.apps.keys():
			if self._stop==True:
				break
			while self.cont>1:
				time.sleep(0.5)
				QApplication.processEvents()
			upd=_performUpdate(name)
			upd.dataLoaded.connect(self._emitDataLoaded)
			self.updates.append(upd)
			upd.start()
			self.cont+=1
		if self._stop==True:
			for th in self.updates:
				if th.isRunning():
					th.quit()
					th.wait()
	#def run

	def stop(self):
		self._stop=True
		for th in self.updates:
			if th.isRunning():
				th.quit()
				th.wait()
		self.cont=0
	#def stop

	def _emitDataLoaded(self,*args):
		app={}
		if len(args)>0 and isinstance(args[0],str):
			try:
				app=json.loads(args[0])
			except Exception as e:
				self._debug("_emitDataLoaded ERR: Json could not be parsed\n{}\n".format(e))
		self.dataLoaded.emit(app)
		self.cont-=1
	#def _emitDataLoaded
#class updateAppData

class getData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self._stop=False
	#def __init__

	def setApps(self,apps):
		self.apps=apps
	#def setApps
	
	def run(self):
		applist=[]
		for strapp in self.apps:
			if self._stop==True:
				break
			jsonapp=json.loads(strapp)
			applist.append(jsonapp)
		if self._stop==False:
			self.dataLoaded.emit(applist)
	#def run

	def stop(self):
		self._stop=True
		self.quit()
		self.wait()
	#def stop
#class getData

class portrait(QStackedWindowItem):
	def __init_stack__(self):
		self.aux=[]
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
		#Catalogue related
		self.i18nCat={}
		self.oldCat=""
		self.catI18n={}
		self.appsToLoad=1000
		self.appsLoaded=0
		self.appsSeen=[]
		self.appsRaw=[]
		self.oldSearch=""
		self.maxCol=5
		#Thread related
		self.loading=False
		self.pendingApps={}
		self.rc=store.client()
		self.appUpdate=updateAppData()
		self.getData=getData()
		self.getData.dataLoaded.connect(self._loadData)
		self._rebost=storeHelper()
		self._rebost.chkEnded.connect(self._endGetUpgradables)
		self._rebost.test.connect(self._goHome)
		self._rebost.lstEnded.connect(self._endLoadCategory)
		self._rebost.srcEnded.connect(self._endSearchApps)
		self.epi=exehelper.appLauncher()
		self.epi.runEnded.connect(self._endLaunchHelper)
		self.zmdLauncher=exehelper.zmdLauncher()
		self.zmdLauncher.zmdEnded.connect(self._endLaunchHelper)
		#self.thUpgrades=chkUpgrades(self.rc)
		#GUI related
		self.hideControlButtons()
		self.referersHistory={}
		self.referersShowed={}
		self.level='user'
		self.oldCursor=self.cursor()
		self.refresh=True
		self.released=True
		self.setStyleSheet(css.portrait())
		#self.epi.runEnded.connect(self._getEpiResults)
		#DBUS
		signal.signal(signal.SIGUSR1,self._signals)
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	#def __init__

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

	def __initScreen__(self):
		bus=dbus.SessionBus()
		objbus=bus.get_object("net.lliurex.rebost","/net/lliurex/rebost")
		#objbus.connect_to_signal("updatedSignal",self._goHome,dbus_interface="net.lliurex.rebost")
		objbus.connect_to_signal("beginUpdateSignal",self._beginUpdate,dbus_interface="net.lliurex.rebost")
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.box.setContentsMargins(0,0,0,0)
		self.sortAsc=False
		wdg=self._navPane()
		wdg.setObjectName("wdg")
		self.box.addWidget(wdg,0,0,Qt.AlignLeft)
		self.rp=self._mainPane()
		self.rp.table.installEventFilter(self)
		self.box.addWidget(self.rp,0,1)
		self.lp=self._detailPane()
		self.lp.clicked.connect(self._return)
		self.lp.loaded.connect(self._updateBtn)
		self.lp.tagpressed.connect(self._loadCategory)
		self.box.addWidget(self.lp,0,1)
		self.lp.hide()
		self.progress=self._defProgress()
		self.box.addWidget(self.progress,0,0,self.box.rowCount(),self.box.columnCount())
		self.btnSettings=QPushButton()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		self.btnSettings.setIcon(icn)
		self.btnSettings.clicked.connect(self._gotoSettings)
		if LAYOUT=="appsedu":
			self.btnSettings.setVisible(False)
		self.box.setColumnStretch(1,1)
		self.setObjectName("portrait")
		self.resetScreen()
	#def _load_screen

	def _closeEvent(self,*args):
		if hasattr(self,"progress"):
			self.progress.stop()
		if hasattr(self,"appUpdate"):
			self.appUpdate.stop()
			self.appUpdate.quit()
			self.appUpdate.wait()
		if hasattr(self,"getData"):
			self.getData.stop()
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
		topBar=self._defTopBar()
		if LAYOUT=="appsedu":
			topBar.setVisible(False)
		lay.addWidget(topBar)
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
		vbox.addWidget(self._appseduCertified(),Qt.AlignRight)
		self.lstCategories=QListWidget()
		self.lstCategories.setObjectName("lstCategories")
		self.lstCategories.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lstCategories.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		vbox.addWidget(self.lstCategories,Qt.AlignTop|Qt.AlignCenter)
		self.lstCategories.setMinimumHeight(int(ICON_SIZE/3))
		self.lstCategories.setCursor(Qt.PointingHandCursor)
		self.lstCategories.currentItemChanged.connect(self._decoreCmbCategories)
		self.lstCategories.itemActivated.connect(self._loadCategory)
		self.lblInfo=self._defInfo()
		vbox.addSpacing(30)
		vbox.addWidget(self.lblInfo,Qt.AlignBottom)
		vbox.setStretch(0,0)
		vbox.setStretch(1,1)
		vbox.setStretch(2,0)
		vbox.setStretch(3,0)
		return(wdg)
	#def _defNavBar

	def _defTopBar(self):
		wdg=QWidget()
		hbox=QHBoxLayout()
		#hbox.addWidget(self.lstCategories)
		self.apps=[]
		self.btnFilters=QCheckableComboBox()
		self.btnFilters.setMaximumHeight(ICON_SIZE/3)
		self.btnFilters.clicked.connect(self._filterView)
		self.btnFilters.activated.connect(self._selectFilters)
		self._loadFilters()
		icn=QtGui.QIcon.fromTheme("view-filter")
		hbox.addWidget(self.btnFilters)
		wdg.setLayout(hbox)
		self.btnSort=QPushButton()
		icn=QtGui.QIcon.fromTheme("sort-name")
		self.btnSort.setIcon(icn)
		self.btnSort.setMaximumSize(QSize(int(ICON_SIZE/3),int(ICON_SIZE/3)))
		self.btnSort.setIconSize(self.btnSort.sizeHint())
		self.btnSort.clicked.connect(self._sortApps)
		self.btnSort.setToolTip(i18n["SORTDSC"])
		hbox.addWidget(self.btnSort)
		return(wdg)
	#def _defTopBar

	def _appseduCertified(self):
		wdg=QWidget()
		lay=QHBoxLayout()
		lay.setSpacing(3)
		lbl=QLabel()
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","appsedu128x128.png")
		lay.addWidget(lbl)
		chk=QCheckBox(i18n.get("CERTIFIED"))
		chk.setObjectName("certified")
		pxm=QtGui.QPixmap(img).scaled(24,24)
		lbl.setPixmap(pxm)
		chk.setChecked(True)
		chk.setEnabled(False)
		chk.setLayoutDirection(Qt.RightToLeft)
		lay.addWidget(chk)
		wdg.setLayout(lay)
		return(wdg)
	#def _appseduCertified

	def _defInst(self):
		btnInst=QPushButton(i18n.get("INSTALLED"))
		btnInst.clicked.connect(self._filterInstalled)
		return(btnInst)
	#def _defHome

	def _defHome(self):
		btnHome=QPushButton(i18n.get("HOME"))
		#btnHome.setIcon(icn)
		btnHome.clicked.connect(self._goHome)
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
	#def _defInfo(self):

	def _defProgress(self):
		wdg=QProgressImage()
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

	def tableKeyPressEvent(self,*args):
		return(False)
	#def tableKeyPressEvent

	def _detailPane(self):
		dp=detailPanel()
		return(dp)
	#def _detailPane

	def _launchLlxUp(self):
		self.parent.setVisible(False)
		QApplication.processEvents()
		subprocess.run(["pkexec","lliurex-up"])
		self.parent.setVisible(True)
	#def _launchLlxUp

	def _loadFilters(self):
		if hasattr(self,"btnFilters"):
			self.btnFilters.clear()
			self.btnFilters.setText(i18n.get("FILTERS"))
			self.btnFilters.addItem(i18n.get("ALL"))
			items=[i18n.get("INSTALLED"),"Snap","Appimage","Flatpak","Zomando"]
			for item in items:
				self.btnFilters.addItem(item,state=False)
	#def _loadFilters

	def _populateCategories(self): 
		self.lstCategories.clear()
		self.lstCategories.setSizeAdjustPolicy(self.lstCategories.SizeAdjustPolicy.AdjustToContents)
		self.i18nCat={}
		self.catI18n={}
		catList=json.loads(self.rc.execute('getCategories'))
		self.lstCategories.addItem(i18n.get('ALL'))
		item=self.lstCategories.itemAt(0,0)
		if item!=None:
			font=item.font()
			font.setBold(True)
			item.setFont(font)
		seenCats={}
		#Sort categories
		translatedCategories=[]
		for cat in catList:
			#if cat.islower() it's a category from system without appstream info 
			if _(cat).capitalize() in self.i18nCat.keys() or cat.islower():
				continue
			translatedCategories.append(_(cat).capitalize())
			self.i18nCat[_(cat).capitalize()]=cat
			self.catI18n[cat]=_(cat)
		translatedCategories.sort()
		lowercats=[]
		for cat in translatedCategories:
			if cat.lower() not in lowercats:
				self.lstCategories.addItem(" · {}".format(cat))
				lowercats.append(cat.lower())
	#def _populateCategories

	def _getAppList(self,cat=[]):
		self.loading=True
		if isinstance(cat,str):
			cat=cat.split()
		if len(cat)>0:
			categories=",".join(cat)
			if len(cat)>1:
				self._rebost.setAction("list","({})".format(categories))
				#apps.extend(json.loads(self.rc.execute('list',"({})".format(categories))))
				self._debug("Loading cat {}".format(",".join(cat)))
			else:
				#If max rows is defined rebost tries to return as many apps as possible
				#getting categories from raw data (deep search)
				self._rebost.setAction("list","{}".format(categories),1000)
				#apps.extend(json.loads(self.rc.execute('list',"{}".format(categories),1000)))
				self._debug("Loading cat {}".format(categories))
			self._rebost.start()
		else:
			self._rebost.setAction("search","")
			self._rebost.start()
	#def _getAppList

	def _endGetUpgradables(self,*args):
		if args[0]==True:
			self.lblInfo.setVisible(True)
		self._rebost.terminate()
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self.lblInfo.setVisible(False)
		self._rebost.setAction("upgrade")
		self._rebost.start()
	#def _getUpgradables

	def _beginUpdate(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btnSettings.setVisible(False)
		if self.init==False:
			self.progress.start()
		self.rp.setVisible(False)
	#def _beginUpdate

	def _endUpdate(self):
		self.setCursor(self.oldCursor)
		self._return()
		#self.progress.setVisible(False)
	#def _endUpdate

	def _goHome(self,*args,**kwargs):
		self._debug("Rebost running: {} - {} - {}".format(self._rebost.isFinished(),self._rebost.isRunning(),self._rebost.action))
		if self._rebost.isFinished()==True and self._rebost.isRunning()==False:
			self._getUpgradables()
		self.oldTime=time.time()
		self.sortAsc=False
		self.rp.searchBox.setText("")
		self._loadFilters()
		#self.apps=self._getAppList()
		self._rebost.setAction("search","")
		self._rebost.start()
		#self.apps=json.loads(self.rc.execute('search',""))
		self._populateCategories()
		self.resetScreen()
		if isinstance(self.lstCategories,QListWidget):
			self.lstCategories.setCurrentRow(0)
		elif isinstance(self.lstCategories,QComboBox):
			self.lstCategories.setCurrentIndex(0)
		self.updateScreen()
	#def _goHome

	def _filterView(self,getApps=True):
		filters={}
		appsFiltered=[]
		self.apps=self.appsRaw
		self._debug("Checking {} apps".format(len(self.apps)))
		self.resetScreen()
		filters=self._readFilters()
		if getApps==True:
			if len(filters)==0:
				filters['package']=True
			if filters.get("lliurex",False)==True:
				self.apps=self._getAppList(["\"Lliurex\"","\"Lliurex-Administration\"","\"Lliurex-Infantil\""])
			if filters.get("zomando",False)==True:
				self.apps=self._getAppList(["Zomando"])
		self.apps=self._applyFilters(filters)
		self.updateScreen()
	#def _filterView

	def _readFilters(self):
		filters={}
		desc=[]
		for item in self.btnFilters.getItems():
		   if item.checkState()==Qt.Checked:
		   	filters[item.text().lower()]=True
		   	desc.append(item.text())
		if len(filters)>1:
			filters[i18n.get("ALL").lower()]=False
		if len(desc)==0:
			item=self.btnFilters.model().item(1)
			item.setCheckState(Qt.Checked)
			desc.append(item.text())
		self.btnFilters.setText(",".join(desc))
		return(filters)
	#def _readFilters

	def _filterInstalled(self):
		self.resetScreen()
		appsFiltered=[]
		for app in self.apps:
			japp=json.loads(app)
			bundles=japp.get("bundle")
			states=japp.get("state",{}).copy()
			zmd="1"
			if "zomando" in states.keys():
				zmd=states.pop("zomando")
			for bun in bundles.keys():
				if states.get(bun,"1")!="0" or zmd!="0":
					continue
				appsFiltered.append(app)
				break
		self.apps=appsFiltered.copy()
		self.appUpdate.start()
		self.appsRaw=self.apps.copy()
		self.refresh=True
		if len(self.apps)==0:
			self.refresh=False
		self.updateScreen()
	#def _filterInstalled

	def _applyFilters(self,filters):
		appsFiltered=[]
		filterList=False
		if filters.get(i18n.get("ALL").lower(),False)!=True:
			for app in self.apps:
				japp=json.loads(app)
				#Filter bundles
				flterList=False
				for bund in ["appimage","flatpak","snap","zomando"]:
					if bund  in filters.keys():
						filterList=True
						break
				for bund in japp.get('bundle',{}).keys():
					if filters.get(i18n.get("UPGRADABLE",False))==True:
						state=japp.get('state',{})
						installed=japp.get('installed',{}).get(bund,"")
						if state.get(bund,"1")=="0":
							available=japp.get('versions',{}).get(bund,"")
							if available=="" or available==installed:
								continue
						else:
							continue
					if filters.get(i18n.get("INSTALLED").lower(),False)==True:
						state=japp.get('state',{})
						if state.get(bund,"1")!="0":
							continue
					if bund not in filters.keys() and filterList==True:
						continue
					if app not in appsFiltered:
						appsFiltered.append(app)
		else:
			appsFiltered=self.appsRaw
		return(appsFiltered)
	#def _applyFilters

	def _selectFilters(self,*args):
		cat=""
		if len(args)>0:
			idx=args[0]
		else:
			idx=self.btnFilters.currentIndex()
		if idx<1:
			return
		item=self.btnFilters.model().item(idx)
		state=item.checkState()
		if state==Qt.Checked:
			state=Qt.Unchecked
			init=2
		else:
			state=Qt.Checked
			init=3
		if idx==1:
			for i in (range(init,self.btnFilters.count())):
				item=self.btnFilters.model().item(i)
				item.setCheckState(state)
		elif state==Qt.Unchecked: # -> Remember: swap
			item=self.btnFilters.model().item(1)
			item.setCheckState(Qt.Unchecked)
		self._filterView(getApps=False)
	#def _selectFilters

	def _resetSearchBtnIcon(self):
		txt=self.rp.searchBox.text()
		if txt==self.oldSearch:
			icn=QtGui.QIcon.fromTheme("dialog-cancel")
		else:
			icn=QtGui.QIcon.fromTheme("search")
	#def _resetSearchBtnIcon

	def _sortApps(self):
		self.apps.sort()
		self.sortAsc=not(self.sortAsc)
		if self.sortAsc==False:
			self.apps.reverse()
		self.appsRaw=self.apps.copy()
		self._filterView(getApps=False)
	#def _sortApps

	def _searchApps(self):
		self.lstCategories.setCurrentRow(-1)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		txt=self.rp.searchBox.text()
		if txt==self.oldSearch:
			self.rp.searchBox.setText("")
			txt=""
		self.oldSearch=txt
		self.appUpdate.stop()
		if len(txt)==0:
			self.apps=self._getAppList()
		else:
			self.apps=json.loads(self.rc.execute('search',txt))
			self.appsRaw=self.apps.copy()
		self.refresh=True
		if len(self.apps)==0:
			self.refresh=False
		self._filterView(getApps=False)
	#def _searchApps

	def _endSearchApps(self,*args):
		self.appsRaw=args[0]
		self.appsRaw.sort()
		self._filterView(getApps=False)
		self.oldTime=time.time()
		self.loading=False
		self._endUpdate()
		self.progress.stop()
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

	def _loadCategory(self,*args):
		cat=None
		flag=""
		if self.loading==True:
			return
		if isinstance(args[0],QListWidgetItem):
			cat=args[0].text()
		elif isinstance(args[0],str):
			cat=args[0]
		if cat==None:
			return
		if time.time()-self.oldTime<MINTIME:
			return
		self._debug("LOAD CATEGORY {}".format(cat))
		self.rp.setVisible(False)
		self.progress.start()
		QApplication.processEvents()
		self.refresh=True
		self.rp.searchBox.setText("")
		self.resetScreen()
		self._beginUpdate()
		if cat=="":
			i18ncat=self.lstCategories.currentItem().text().replace(" · ","")
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
		self._getAppList(cat)
		#self.apps=self._getAppList(cat)
		#self._filterView(getApps=False)
		#self.oldTime=time.time()
		#self._debug("LOAD CATEGORY {} END".format(cat))
		#self.progress.stop()
		#self._endUpdate()
	#def _loadCategory

	def _endLoadCategory(self,*args):
		self.appsRaw=args[0]
		self._filterView(getApps=False)
		self.oldTime=time.time()
		self._debug("LOAD CATEGORY END")
		self.progress.stop()
		self._endUpdate()

	def eventFilter(self,*args):
		ev=args[1]
		if ev.type()==QEvent.Type.Resize:
			if hasattr(self,"first")==False:
				self.first=ev
				ev.accept()
			if self.first!=None:
				self.first=None
				self.progress.stop()
				self.rp.setVisible(True)
			else:
				self.first=ev
		elif isinstance(args[0],QFlowTouchWidget) and ev.type()==QEvent.Type.Paint:
			args[0].setVisible(True)
			self.init=True
			if hasattr(self,"appUpdate"):
				self.appUpdate.start()
			else:
				self._debug("Event filter failed starting appUpdate")
			if hasattr(self,"firstHide")==False:
				self.firstHide=None
			else:
				self.progress.stop()
				self.rp.table.removeEventFilter(self)
				self.box.addWidget(self.progress,0,1,self.box.rowCount(),self.box.columnCount()-1)
		elif isinstance(args[0],QListWidget):
			if args[1].type==QEvent.Type.KeyRelease:
				self.released=True
			elif args[1].type==QEvent.Type.KeyPress:
				self.released=False
		return(False)
	#def eventFilter(self,*args):

	def _fillTable(self,*args):
		#self.progress.start()
		self.rp.table.flowLayout.setEnabled(False)
		self.rp.setVisible(False)
		#self.rp.table.setVisible(False)
		for wdg in args[0]:
			if wdg==None:
				continue
			wdg.setVisible(False)
			self.rp.table.addWidget(wdg)
		self.rp.table.flowLayout.setEnabled(True)
		self.rp.setVisible(True)
		#self.rp.table.setVisible(True)
		#self.progress.stop()
	#def _fillTable

	def _getMoreData(self):
		return
		if (self.rp.table.verticalScrollBar().value()==self.rp.table.verticalScrollBar().maximum()) and self.appsLoaded!=len(self.apps):
			self._beginLoadData(self.appsLoaded,self.appsLoaded+self.appsToLoad)
			for wdg in self.wdgs:
				self.rp.table.addWidget(wdg)
				#self.rp.table.setCellWidget(wdg[0],wdg[1],wdg[2])
	#def _getMoreData

	def _beginLoadData(self,idx,idxEnd,applist=None):
		#appData=getData(apps)
		if self.getData.isRunning()==False:
			self._beginUpdate()
			if applist==None:
				apps=self.apps[idx:idxEnd]
			else:
				apps=applist[idx:idxEnd]
			self.getData.setApps(apps)
			self.getData.start()
	#def _beginLoadData

	def _loadData(self,apps):
		col=0
		#self.table.setRowHeight(self.table.rowCount()-1,btn.iconSize+int(btn.iconSize/16))
		colspan=random.randint(1,self.maxCol)
		colspan=self.maxCol
		span=colspan
		btn=None
		self.rp.table.flowLayout.setEnabled(False)
		#self.rp.table.setVisible(False)
		self.rp.setVisible(False)
		if len(self.pendingApps)>0:
			self.appUpdate.stop()
			self.appUpdate.quit()
			self.appUpdate.wait()
			self.pendingApps={}
			
		for jsonapp in apps:
			appname=jsonapp.get('name','')
			if appname in self.appsSeen:
				self.appsLoaded+=1
				continue
			self.appsSeen.append(appname)
			btn=QPushButtonRebostApp(jsonapp)
			btn.clicked.connect(self._loadDetails)
			btn.keypress.connect(self.tableKeyPressEvent)
			btn.install.connect(self._installBundle)
			if jsonapp.get("summary","")=="":
				self.pendingApps.update({appname:btn})
			self.rp.table.addWidget(btn)
			if appname in self.referersHistory.keys():
				self.referersShowed.update({appname:btn})
			self.appsLoaded+=1
			QApplication.processEvents()
		self.rp.table.flowLayout.setEnabled(True)
		#self.rp.table.setVisible(True)
		self.rp.setVisible(True)
		self._endLoadData()
	#def _loadData

	def _endLoadData(self):
		#if self.appsLoaded==0 and self._readFilters().get(i18n.get("ALL").lower(),False)==True:
		if self.appsLoaded==0 and self.lstCategories.count()==0:
			#self._beginUpdate()
			self._rebost.setAction("test")
			self._rebost.start()
		else:
			self.rp.setVisible(True)
			self.appUpdate.stop() #JustInCase
			self.appUpdate.setApps(self.pendingApps)
			self.appUpdate.start()
			self.appUpdate.dataLoaded.connect(self._endLoadApps)
			self._endUpdate()
		self.refresh=True
	#def _endLoadData(self):

	def _endLoadApps(self,args):
		if isinstance(args[0],str):
			app=json.loads(args[0])
		else:
			app=args[0]
		if app["name"] in self.pendingApps.keys():
			self.pendingApps[app["name"]].setApp(app)
			self.pendingApps[app["name"]].updateScreen()

	def _installBundle(self,*args):
		app=args[0]
		if isinstance(app,dict)==False:
			return
		bundle=""
		priority=["flatpak","snap","package","appimage","eduapp"]
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
			self.updateScreen()
		else:
			if bundle=="zomando" and app.get("state",{}).get("zomando","1")=="0":
				self.zmdLauncher.setApp(app)
				self.zmdLauncher.start()
			else:
				cmd=["pkexec","/usr/share/rebost/helper/rebost-software-manager.sh",res.get('epi')]
				self.epi.setArgs(app,cmd,bundle)
				self.epi.start()
	#def _installBundle

	def _endLaunchHelper(self,*args,**kwargs):
		self.setCursor(self.oldCursor)
	#def _endLaunchHelper

	def _loadDetails(self,*args,**kwargs):
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
		self.parent.setWindowTitle("{} - {}".format(APPNAME,args[-1].get("name","")))
		self.lp.setParms({"name":args[-1].get("name",""),"icon":icn})
		self.rp.hide()
		self.lp.show()
		self.setCursor(self.oldCursor)
	#def _endLoadDetails

	def _updateBtn(self,*args,**kwargs):
		QApplication.processEvents()
		self.progress.stop()
		if not hasattr(self,"refererApp"):
			return()
		if self.refererApp==None:
			return()
		#for arg in args:
		#	if isinstance(arg,dict):
		#		for key,item in arg.items():
		#			kwargs[key]=item
		#self.refresh=kwargs.get("refresh",False)
		#app=kwargs.get("app",{})
		app={}
		if isinstance(args[0],dict):
			app=args[0]
		if app!={}:
			#refered btn can be deleted so ensure there's a btn
			if self.referersShowed.get(app.get("name"))!=None:
				self.refererApp=self.referersShowed[app["name"]]
				self.refererApp.setApp(app)
				self.refererApp.updateScreen()
	#def _updateBtn

	def _return(self,*args,**kwargs):
		self.setCursor(self.oldCursor)
		self.parent.setWindowTitle("{}".format(APPNAME))
		self.lp.hide()
		self.rp.show()
		self.progress.stop()
		self.loading=False
	#def _return

	def _gotoSettings(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.parent.setCurrentStack(idx=2,parms="")
	#def _gotoSettings

	def updateScreen(self):
		self.btnFilters.setMaximumWidth(self.btnFilters.sizeHint().width())
		self._debug("Reload data (self.refresh={})".format(self.refresh))
		if self.refresh==True:
			for i in self.referersShowed.keys():
				self.referersShowed[i]=None
			self._beginLoadData(self.appsLoaded,self.appsToLoad)
		else:
			self._endUpdate()
	#def _updateScreen

	def resetScreen(self):
		self.rp.table.clean()
		self.appsLoaded=0
		if len(self.rp.searchBox.text())==0:
			self.oldSearch=""
		self.appsSeen=[]
	#def resetScreen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

