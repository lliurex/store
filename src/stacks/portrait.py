#!/usr/bin/python3
import sys,time,signal
import os
try:
	from lliurex import lliurexup
except:
	lliurexup=None
from PySide2.QtWidgets import QApplication, QLabel, QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QScreenShotContainer,QStackedWindowItem,QInfoLabel
from rebost import store 
import subprocess
import json
import dbus
import dbus.service
import dbus.mainloop.glib
import random
import gettext
from btnRebost import QPushButtonRebostApp
_ = gettext.gettext
QString=type("")

ICON_SIZE=128
MINTIME=0.2
LAYOUT="appsedu"

i18n={
	"ALL":_("All"),
	"AVAILABLE":_("Available"),
	"CATEGORIESDSC":_("Filter by category"),
	"CONFIG":_("Portrait"),
	"DESC":_("Navigate through all applications"),
	"FILTERS":_("Filters"),
	"FILTERSDSC":_("Filter by formats and states"),
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


class chkUpgrades(QThread):
	chkEnded=Signal("PyObject")
	def __init__(self,rc):
		QThread.__init__(self, None)
		self.rc=rc
		self.upgrades=False
	
	def run(self):
		apps=json.loads(self.rc.getUpgradableApps())
		if len(apps)>0:
			self.upgrades=True
		else:
			if lliurexup!=None:
				llxup=lliurexup.LliurexUpCore()
				if len(llxup.getPackagesToUpdate())>0:
					self.upgrades=True
		self.chkEnded.emit(self.upgrades)
#class chkUpgrades

class chkRebost(QThread):
	chkRebost=Signal("PyObject")
	def __init__(self):
		QThread.__init__(self, None)
		self.rc=store.client()
	
	def run(self):
		self.rc.execute("list","office")
		self.chkRebost.emit(True)
#class chkRebost

class getData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self):
		QThread.__init__(self, None)

	def setApps(self,apps):
		self.apps=apps
	
	def run(self):
		applist=[]
		for strapp in self.apps:
			jsonapp=json.loads(strapp)
			applist.append(jsonapp)
		self.dataLoaded.emit(applist)
	#def run(self):
#class getData(QThread):

class portrait(QStackedWindowItem):
	def __init_stack__(self):
		self.aux=[]
		self.init=True
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
		self.i18nCat={}
		self.oldCat=""
		self.catI18n={}
		self.appsToLoad=1000
		self.appsLoaded=0
		self.appsSeen=[]
		self.appsRaw=[]
		self.oldSearch=""
		self.maxCol=3
		if LAYOUT=="appsedu":
			self.maxCol=1
		self.rc=store.client()
		self.chkRebost=chkRebost()
		self.getData=getData()
		self.thUpgrades=chkUpgrades(self.rc)
		self.hideControlButtons()
		self.referersHistory={}
		self.referersShowed={}
		self.level='user'
		self.oldCursor=self.cursor()
		self.refresh=True
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
		objbus.connect_to_signal("updatedSignal",self._goHome,dbus_interface="net.lliurex.rebost")
		objbus.connect_to_signal("beginUpdateSignal",self._beginUpdate,dbus_interface="net.lliurex.rebost")
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.sortAsc=False
		btnHome=self._defHome()
		self.box.addWidget(btnHome,0,0,1,1,Qt.AlignTop|Qt.AlignLeft)
		lbl=self._defBanner()
		lbl.setVisible(False)
		self.box.addWidget(lbl,0,0,1,2,Qt.AlignTop|Qt.AlignCenter)
		if LAYOUT=="appsedu":
			btnHome.setVisible(False)
			lbl.setVisible(True)
		topBar=self._defTopBar()
		if LAYOUT=="appsedu":
			topBar.setVisible(False)
		self.box.addWidget(topBar,1,0,1,1,Qt.AlignLeft)
		navBar=self._defNavBar()
		if LAYOUT=="appsedu":
			self.box.addWidget(navBar,1,0,1,1,Qt.AlignLeft)
		else:
			self.box.addWidget(navBar,1,1,1,1)
		self.table=self._defTable()
		if LAYOUT=="appsedu":
			tableCol=1
		else:
			tableCol=0
		self.box.addWidget(self.table,2-tableCol,tableCol,1,self.box.columnCount())
		self.lblInfo=self._defInfo()
		self.box.addWidget(self.lblInfo,self.box.rowCount()-1,0,2,2)
		self.progress=self._defProgress()
		self.box.addWidget(self.progress,self.box.rowCount()-1,0,1,2,Qt.AlignBottom)
		self.btnSettings=QPushButton()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		self.btnSettings.setIcon(icn)
		self.btnSettings.clicked.connect(self._gotoSettings)
		if LAYOUT=="appsedu":
			self.btnSettings.setVisible(False)
		self.box.addWidget(self.btnSettings,self.box.rowCount()-1,self.box.columnCount()-1,1,1,Qt.Alignment(-1))
		self.box.setColumnStretch(1,1)
		self.resetScreen()
	#def _load_screen

	def _defHome(self):
		btnHome=QPushButton()
		icn=QtGui.QIcon.fromTheme("view-refresh")
		btnHome.setIcon(icn)
		btnHome.clicked.connect(self._goHome)
		btnHome.setMinimumSize(QSize(int(ICON_SIZE/1.7),int(ICON_SIZE/1.7)))
		btnHome.setIconSize(btnHome.sizeHint())
		return(btnHome)
	#def _defHome

	def _defBanner(self):
		lbl=QLabel()
		imgDir=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","banner.png")
		img=QtGui.QImage(imgDir)
		lbl.setPixmap(QtGui.QPixmap(img))
		lbl.setStyleSheet("""QLabel{padding:0px}""")
		return(lbl)
	#def _defBanner

	def _defTopBar(self):
		wdg=QWidget()
		hbox=QHBoxLayout()
		#hbox.addWidget(self.cmbCategories)
		self.apps=[]
		self.btnFilters=QCheckableComboBox()
		self.btnFilters.setMaximumHeight(ICON_SIZE/3)
		#self.btnFilters.clicked.connect(self._filterView)
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

	def _defNavBar(self):
		wdg=QWidget()
		if LAYOUT=="appsedu":
			vbox=QVBoxLayout()
		else:
			vbox=QHBoxLayout()
		vbox.setContentsMargins(0,0,10,0)
		self.searchBox=QSearchBox()
		self.searchBox.btnSearch.setMinimumSize(int(ICON_SIZE/3),int(ICON_SIZE/3))
		self.searchBox.txtSearch.setMinimumSize(int(ICON_SIZE/3),int(ICON_SIZE/3))
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.searchBox.returnPressed.connect(self._searchApps)
		self.searchBox.textChanged.connect(self._resetSearchBtnIcon)
		self.searchBox.clicked.connect(self._searchAppsBtn)
		if LAYOUT=="appsedu":
			self.cmbCategories=QListWidget()
			vbox.addWidget(self.searchBox)
			vbox.addWidget(self.cmbCategories)
		else:
			self.cmbCategories=QComboBox()
			vbox.addWidget(self.cmbCategories,Qt.AlignLeft)
			vbox.addWidget(self.searchBox,Qt.AlignRight)
		self.cmbCategories.setMinimumHeight(int(ICON_SIZE/3))
		if isinstance(self.cmbCategories,QListWidget):
			self.cmbCategories.currentItemChanged.connect(self._loadCategory)
		elif isinstance(self.cmbCategories,QComboBox):
			self.cmbCategories.activated.connect(self._loadCategory)
		wdg.setLayout(vbox)
		return(wdg)
	#def _defNavBar

	def _defTable(self):
		table=QTableTouchWidget()
		table.setAutoScroll(False)
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setColumnCount(self.maxCol)
		table.setShowGrid(False)
		table.verticalHeader().hide()
		table.horizontalHeader().hide()
		table.verticalScrollBar().valueChanged.connect(self._getMoreData)
		#table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		if LAYOUT=="appsedu":
			table.setStyleSheet("""QTableWidget::item{padding:12px}""")
		return(table)
	#def _defTable

	def _defInfo(self):
		lblInfo=QInfoLabel()
		lblInfo.setActionText(i18n.get("LLXUP"))
		lblInfo.setActionIcon("lliurex-up")
		lblInfo.setText(i18n.get("UPGRADES"))
		lblInfo.clicked.connect(self._launchLlxUp)
		lblInfo.setVisible(False)
		return(lblInfo)
	#def _defInfo(self):

	def _defProgress(self):
		wdg=QWidget()
		vbox=QVBoxLayout()
		lblProgress=QLabel(i18n["NEWDATA"])
		vbox.addWidget(lblProgress,Qt.AlignCenter|Qt.AlignBottom)
		progress=QProgressBar()
		progress.setMinimum(0)
		progress.setMaximum(0)
		vbox.addWidget(progress,Qt.AlignCenter)
		wdg.setLayout(vbox)
		return(wdg)
	#def _defProgress

	def tableLeaveEvent(self,*args):
		self.table.setAutoScroll(False)
		return(False)
	#def enterEvent

	def tableKeyPressEvent(self,*args):
		if self.table.doAutoScroll()==None:
			self.table.setAutoScroll(True)
		return(False)
	#def tableKeyPressEvent


	def _launchLlxUp(self):
		subprocess.run(["pkexec","lliurex-up"])
	#def _launchLlxUp

	def _loadFilters(self):
		self.btnFilters.clear()
		self.btnFilters.setText(i18n.get("FILTERS"))
		self.btnFilters.addItem(i18n.get("ALL"))
		items=[i18n.get("INSTALLED"),"Snap","Appimage","Flatpak","Zomando"]
		for item in items:
			self.btnFilters.addItem(item,state=False)
	#def _loadFilters

	def _populateCategories(self): 
		self.cmbCategories.clear()
		self.cmbCategories.setSizeAdjustPolicy(self.cmbCategories.SizeAdjustPolicy.AdjustToContents)
		self.i18nCat={}
		self.catI18n={}
		catList=json.loads(self.rc.execute('getCategories'))
		self.cmbCategories.addItem(i18n.get('ALL'))
		seenCats={}
		#Sort categories
		translatedCategories=[]
		for cat in catList:
			#if cat.islower() it's a category from system without appstream info 
			if _(cat) in self.i18nCat.keys() or cat.islower():
				continue
			translatedCategories.append(_(cat))
			self.i18nCat[_(cat)]=cat
			self.catI18n[cat]=_(cat)
		translatedCategories.sort()
		for cat in translatedCategories:
			self.cmbCategories.addItem(cat)
		#self.cmbCategories.view().setMinimumWidth(self.cmbCategories.minimumSizeHint().width())
	#def _populateCategories

	def _populateCategoriesFromApps(self):
		self.cmbCategories.clear()
		self.cmbCategories.setSizeAdjustPolicy(self.cmbCategories.SizeAdjustPolicy.AdjustToContents)
		seen=[]
		self.cmbCategories.addItem(i18n.get('ALL'))
		for app in self.apps:
			japp=json.loads(app)
			categories=japp.get("categories",[])
			for cat in categories:
				if cat=="Forbidden":
					cat="No Disponible"
				if cat not in seen:
					self.cmbCategories.addItem(cat)
					seen.append(cat)
	#def _populateCategoriesFromApp


	def _getAppList(self,cat=[]):
		apps=[]
		if isinstance(cat,str):
			cat=cat.split()
		if len(cat)>0:
			categories=",".join(cat)
			if len(cat)>1:
				apps.extend(json.loads(self.rc.execute('list',"({})".format(categories))))
			else:
				#If max rows is defined rebost tries to return as many apps as possible
				#getting categories from raw data (deep search)
				apps.extend(json.loads(self.rc.execute('list',"{}".format(categories),1000)))
			self._debug("Loading cat {}".format(",".join(cat)))
		elif LAYOUT!="appsedu":
			categories=[]
			for i18ncat,cat in self.i18nCat.items():
				categories.append("\"{}\"".format(cat))
			if not "Lliurex" in categories:
				categories.append("\"Lliurex\"")
			if not "Forbidden" in categories:
				categories.append("\"Forbidden\"")
			categories=",".join(categories)
			apps.extend(json.loads(self.rc.execute('list',"({})".format(categories))))
		else:
			apps=json.loads(self.rc.execute("search",""))
		self.appsRaw=apps
		apps.sort()
		self.cleanAux()
		return(apps)
	#def _getAppList

	def _endGetUpgradables(self,*args):
		if args[0]==True:
			self.lblInfo.setVisible(True)
		self.thUpgrades.terminate()
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self.lblInfo.setVisible(False)
		self.thUpgrades.chkEnded.connect(self._endGetUpgradables)
		self.thUpgrades.start()
	#def _getUpgradables

	def _beginUpdate(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btnSettings.setVisible(False)
		self.progress.setVisible(True)
	#def _beginUpdate

	def _endUpdate(self):
		self.setCursor(self.oldCursor)
		if LAYOUT!="appsedu":
			self.btnSettings.setVisible(True)
		self.progress.setVisible(False)
	#def _endUpdate

	def _shuffleApps(self):
		if LAYOUT!="appsedu":
			random.shuffle(self.apps)
	#def _shuffleApps

	def _goHome(self,*args,**kwargs):
		if time.time()-self.oldTime<MINTIME*2:
			return
		if self.thUpgrades.isFinished()==False and self.thUpgrades.isRunning()==False:
			self._getUpgradables()
		self.oldTime=time.time()
		self.sortAsc=False
		self.searchBox.setText("")
		self._loadFilters()
		self.apps=self._getAppList()
		self._populateCategoriesFromApps()
		self._shuffleApps()
		self.resetScreen()
		if isinstance(self.cmbCategories,QListWidget):
			self.cmbCategories.setCurrentRow(0)
		elif isinstance(self.cmbCategories,QComboBox):
			self.cmbCategories.setCurrentIndex(0)
		self.updateScreen()
	#def _goHome

	def _filterView(self,getApps=True):
		filters={}
		appsFiltered=[]
		self.apps=self.appsRaw
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
		txt=self.searchBox.text()
		if txt==self.oldSearch:
			icn=QtGui.QIcon.fromTheme("dialog-cancel")
		else:
			icn=QtGui.QIcon.fromTheme("search")
		self.searchBox.btnSearch.setIcon(icn)
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
		if LAYOUT=="appsedu":
			self.cmbCategories.setCurrentRow(0)
		else:
			self.cmbCategories.setCurrentText(i18n.get("ALL"))
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		txt=self.searchBox.text()
		if txt==self.oldSearch:
			self.searchBox.setText("")
			txt=""
		self.oldSearch=txt
		self.resetScreen()
		if len(txt)==0:
			icn=QtGui.QIcon.fromTheme("search")
			self.apps=self._getAppList()
		else:
			icn=QtGui.QIcon.fromTheme("dialog-cancel")
			self.apps=json.loads(self.rc.execute('search',txt))
			self.appsRaw=self.apps.copy()
		self.searchBox.btnSearch.setIcon(icn)
		self.refresh=True
		if len(self.apps)==0:
			self.refresh=False
		self._filterView(getApps=False)
	#def _searchApps

	def _searchAppsBtn(self):
		txt=self.searchBox.text()
		if txt==self.oldSearch:
			self.searchBox.setText("")
			txt=""
		self.oldSearch=txt
		self._searchApps()
	#def _searchAppsBtn

	def _loadCategory(self):
		if time.time()-self.oldTime<MINTIME:
			#self.cmbCategories.setCurrentText(self.oldCat)
			return
		self.searchBox.setText("")
		self.resetScreen()
		self._beginUpdate()
		i18ncat=self.cmbCategories.currentItem().text()
		if self.oldCat!=i18ncat:
			self.oldCat=i18ncat
		cat=self.i18nCat.get(i18ncat,i18ncat)
		if cat==i18n.get("ALL"):
			cat=""
		self.apps=self._getAppList(cat)
		self._filterView(getApps=False)
		self.releaseKeyboard()
		self.oldTime=time.time()
		#self._endUpdate()
	#def _loadCategory

	def _getMoreData(self):
		return
		if (self.table.verticalScrollBar().value()==self.table.verticalScrollBar().maximum()) and self.appsLoaded!=len(self.apps):
			self._beginLoadData(self.appsLoaded,self.appsLoaded+self.appsToLoad)
			for wdg in self.wdgs:
				self.table.setCellWidget(wdg[0],wdg[1],wdg[2])
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
			self.getData.dataLoaded.connect(self._loadData)
	#def _beginLoadData

	def _loadData(self,apps):
		col=0
		#self.table.setRowHeight(self.table.rowCount()-1,btn.iconSize+int(btn.iconSize/16))
		colspan=random.randint(1,self.maxCol)
		span=colspan
		btn=None
		self.wdgs=[]
		rowH=QPushButtonRebostApp("{}").iconSize
		if LAYOUT=="appsedu":
			rowH=rowH*2
		for jsonapp in apps:
			appname=jsonapp.get('name','')
			if appname in self.appsSeen:
				self.appsLoaded+=1
				continue
			self.appsSeen.append(appname)
			row=self.table.rowCount()-1
			btn=QPushButtonRebostApp(jsonapp)
			btn.clicked.connect(self._loadDetails)
			btn.keypress.connect(self.tableKeyPressEvent)
			self.wdgs.append((row,col,btn))
			if appname in self.referersHistory.keys():
				self.referersShowed.update({appname:btn})
			col+=1
			span=span-1
			if span==0:
				if colspan==self.maxCol:
					colspan=1
				elif colspan==1:
					colspan=self.maxCol
				if colspan!=1:
					self.table.setSpan(row,col-1,1,colspan)
				colspan=random.randint(1,self.maxCol)
				span=colspan
				self.table.setRowHeight(row,rowH+int(rowH/16))
				self.table.setRowCount(self.table.rowCount()+1)
				col=0
			self.appsLoaded+=1
		if btn!=None:
			self.table.setRowHeight(self.table.rowCount()-1,rowH+int(rowH/16))
		self._endLoadData()
	#def _loadData

	def _endLoadData(self):
		if self.appsLoaded==0 and self._readFilters().get(i18n.get("ALL").lower(),False)==True:
			#self._beginUpdate()
			self.chkRebost.start()
			self.chkRebost.finished.connect(self._goHome)
		else:
			for wdg in self.wdgs:
				self.table.setCellWidget(wdg[0],wdg[1],wdg[2])
			self._endUpdate()
		self.cleanAux()
		self.refresh=True
	#def _endLoadData(self):

	def _endLoadApps(self,args):
		pass

	def _loadDetails(self,*args,**kwargs):
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
		self.parent.setCurrentStack(idx=3,parms={"name":args[-1].get("name",""),"icon":icn})
	#def _loadDetails

	def _gotoSettings(self):
		self.cleanAux()
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.parent.setCurrentStack(idx=2,parms="")
	#def _gotoSettings

	def _thTERM(self,*args):
		self._debug("Pending thread end")
	#def _thTERM

	def cleanAux(self,*args):
		self._debug("Cleaning")
		i=0
		if isinstance(self.aux,list):
			for w in self.aux:
				if hasattr(w,"finished"):
					self._debug("Finish {}".format(w))
					if w.isRunning()==False:
						w.wait()
						i+=1
						self._debug("Removing {}".format(w))
		self._debug("Caching: {}".format(len(self.aux)))
		self._debug("Cleaned: {}".format(i))
	#def cleanAux

	def updateScreen(self):
		self.btnFilters.setMaximumWidth(self.btnFilters.sizeHint().width())
		self._debug("Reload data (self.refresh={})".format(self.refresh))
		if self.refresh==True:
			for i in self.referersShowed.keys():
				self.referersShowed[i]=None
			self.cleanAux()
			self._beginLoadData(self.appsLoaded,self.appsToLoad)
		else:
			self._endUpdate()
	#def _updateScreen

	def resetScreen(self):
		for x in range(self.table.rowCount()):
			for y in range(self.table.columnCount()):
				w=self.table.cellWidget(x,y)
				if isinstance(w,QPushButton):
					if w.scr.isRunning():
						self.aux.append(w.scr)
					elif w.scr in self.aux:
						self.aux.remove(w)
				self.table.removeCellWidget(x,y)
		self.table.setRowCount(0)
		self.table.setRowCount(1)
		self.appsLoaded=0
		self.oldSearch=""
		self.appsSeen=[]
	#def resetScreen

	def setParms(self,*args,**kwargs):
		#referer will be only fulfilled when details stack
		#fires events, if there's a repeated call to setParms
		#referer will be none so function can exit. This must not happen.
		if not hasattr(self,"refererApp"):
			return()
		if self.refererApp==None:
			return()
		for arg in args:
			if isinstance(arg,dict):
				for key,item in arg.items():
					kwargs[key]=item
		self.refresh=kwargs.get("refresh",False)
		app=kwargs.get("app",{})
		if app!={}:
			#refered btn can be deleted so ensure there's a btn
			if self.referersShowed.get(app.get("name"))!=None:
				self.refererApp=self.referersShowed[app["name"]]
				self.refererApp.setApp(app)
				self.refererApp.updateScreen()
		if self.refresh==False:
			cursor=QtGui.QCursor(Qt.WaitCursor)
			self.setCursor(cursor)
			if len(self.searchBox.text())>1:
		#			self._populateCategories()
					self.oldSearch=""
		#			self._searchApps()
		else:
			cat=kwargs.get("cat",{})
			if len(cat)>0:
				if isinstance(self.cmbCategories,QListWidget):
					it=self.cmbCategories.findItems(cat.strip(),Qt.MatchFlags.MatchFixedString)
					if it==None or len(it)==0:
						it=self.cmbCategories.findItems("No Disponible",Qt.MatchFlags.MatchFixedString)
					self.cmbCategories.setCurrentItem(it[0])
				else:
					self.cmbCategories.setCurrentText(self.catI18n.get(cat,cat))
				self._loadCategory()
			else:
				self.oldSearch=""
				#self._populateCategories()
				self.refresh=False
				self.updateScreen()
		self.refererApp=None
	#def setParms

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

