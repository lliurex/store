#!/usr/bin/python3
import sys,time
import os
from lliurex import lliurexup
from PySide2.QtWidgets import QApplication, QLabel, QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QScreenShotContainer,QStackedWindowItem,QInfoLabel
from rebost import store 
from appconfig import appConfig
import subprocess
import json
import random
import gettext
_ = gettext.gettext
QString=type("")

MINTIME=0.2

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
			llxup=lliurexup.LliurexUpCore()
			if len(llxup.getPackagesToUpdate())>0:
				self.upgrades=True
		self.chkEnded.emit(self.upgrades)
#class chkUpgrades

class QPushButtonRebostApp(QPushButton):
	clicked=Signal("PyObject","PyObject")
	def __init__(self,strapp,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.completed=False
		self.app=json.loads(strapp)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setToolTip("<p>{0}</p>".format(self.app.get('summary',self.app.get('name'))))
		text="<strong>{0}</strong> - {1}".format(self.app.get('name',''),self.app.get('summary'),'')
		self.label=QLabel(text)
		self.label.setWordWrap(True)
		img=self.app.get('icon','')
		self.iconUri=QLabel()
		self.iconSize=kwargs.get("iconSize",128)
		self.loadImg(self.app)
		self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		lay=QHBoxLayout()
		lay.addStretch()
		lay.addWidget(self.iconUri,0)
		lay.addWidget(self.label,1)
		self.referrer=None
		self.setDefault(True)
		self.setLayout(lay)
	#def __init__

	def enterEvent(self,*args):
		self.setFocus()

	def loadImg(self,app):
		img=app.get('icon','')
		self.aux=QScreenShotContainer()
		self.scr=self.aux.loadScreenShot(img,self.cacheDir)
		icn=''
		if os.path.isfile(img):
			icn=QtGui.QPixmap.fromImage(img)
		elif img=='':
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'))
			icn=icn2.pixmap(self.iconSize,self.iconSize)
		elif "flathub" in img:
			tmp=img.split("/")
			if "icons" in tmp:
				idx=tmp.index("icons")
				prefix=tmp[:idx-1]
				iconPath=os.path.join("/".join(prefix),"active","/".join(tmp[idx:]))
				if os.path.isfile(iconPath):
					icn=QtGui.QPixmap.fromImage(iconPath)
					self.completed=True
		if icn:
			wsize=self.iconSize
			if "/usr/share/banners/lliurex-neu" in img:
				wsize*=2
			self.iconUri.setPixmap(icn.scaled(wsize,self.iconSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
			self.completed=True
		elif img.startswith('http'):
			self.scr.start()
			self.scr.imageLoaded.connect(self.load)
		installed=False
		forbidden=False
		if "0"  in str(app.get('state',1)):
			#self.setStyleSheet("""QPushButton{background-color: rgba(140, 255, 0, 70);}""")
			installed=True
		if "Forbidden" in app.get("categories",[]):
			forbidden=True
		self._applyDecoration(forbidden,installed)
	#def loadImg

	def _applyDecoration(self,forbidden=False,installed=False):
		self.setObjectName("rebostapp")
		self.setAttribute(Qt.WA_StyledBackground, True)
		color=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Active,QtGui.QPalette.Base))
		bcolor=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Active,QtGui.QPalette.Dark))
		if forbidden==True:
			bcolor=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Inactive,QtGui.QPalette.Base))
			color=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Inactive,QtGui.QPalette.Dark))
		elif installed==True:
			color=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Disabled,QtGui.QPalette.Highlight))
		self.setAutoFillBackground(True)
		pal=self.palette()
		#pal.setColor(QPalette.Window,bcolor)
		rgbColor="{0},{1},{2}".format(color.red(),color.green(),color.blue())
		rgbBcolor="{0},{1},{2}".format(bcolor.red(),bcolor.green(),bcolor.blue())
		self.setStyleSheet("""#rebostapp {
			background-color: rgb(%s); 
			border-style: solid; 
			border-color: rgb(%s); 
			border-width: 1px; 
			border-radius: 2px;}
			#rebostapp:focus:!pressed {
				border-width:3px;
				}
			"""%(rgbColor,rgbBcolor))

	#def _applyDecoration

	def _removeDecoration(self):
		self.setObjectName("")
		self.setStyleSheet("")
	#def _removeDecoration
	
	def load(self,*args):
		img=args[0]
		self.iconUri.setPixmap(img.scaled(self.iconSize,self.iconSize))
		self.completed=True
	#def load
	
	def activate(self):
		self.clicked.emit(self.app)
	#def activate

	def keyPressEvent(self,ev):
		if ev.key() in [Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space]:
			self.clicked.emit(self,self.app)
		ev.ignore()
	#def keyPressEvent(self,ev):

	def mousePressEvent(self,*args):
		self.clicked.emit(self,self.app)
	#def mousePressEvent
#class QPushButtonRebostApp

class portrait(QStackedWindowItem):
	def __init_stack__(self):
		self.aux=[]
		self.minTime=1
		self.oldTime=int(time.time())
		self.dbg=True
		self.enabled=True
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.appconfig=appConfig.appConfig()
		self.appconfig.setConfig(confDirs={'system':'/usr/share/rebost','user':os.path.join(os.environ['HOME'],'.config/rebost')},confFile="store.json")
		self.i18nCat={}
		self.oldCat=""
		self.catI18n={}
		self.config={}
		self.index=1
		self.appsToLoad=50
		self.appsLoaded=0
		self.appsSeen=[]
		self.appsRaw=[]
		self.oldSearch=""
		self.defaultRepos={}
		self.rc=store.client()
		self.hideControlButtons()
		self.changed=[]
		self.level='user'
		self.oldcursor=self.cursor()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Portrait: {}".format(msg))
	#def _debug

	def __initScreen__(self):
		self.config=self.appconfig.getConfig()
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.sortAsc=False
		wdg=QWidget()
		hbox=QHBoxLayout()
		btnHome=QPushButton()
		icn=QtGui.QIcon.fromTheme("home")
		btnHome.setIcon(icn)
		btnHome.clicked.connect(self._goHome)
		hbox.addWidget(btnHome)
		self.cmbCategories=QComboBox()
		self.cmbCategories.activated.connect(self._loadCategory)
		hbox.addWidget(self.cmbCategories)
		self._populateCategories()
		self.apps=self._getAppList()
		self._shuffleApps()
		self.btnFilters=QCheckableComboBox()
		#self.btnFilters.clicked.connect(self._filterView)
		self.btnFilters.activated.connect(self._selectFilters)
		self._loadFilters()
		icn=QtGui.QIcon.fromTheme("view-filter")
		hbox.addWidget(self.btnFilters)
		wdg.setLayout(hbox)
		self.box.addWidget(wdg,0,0,1,1,Qt.AlignLeft)
		self.btnSort=QPushButton()
		icn=QtGui.QIcon.fromTheme("sort-name")
		self.btnSort.setIcon(icn)
		self.btnSort.clicked.connect(self._sortApps)
		self.btnSort.setToolTip(i18n["SORTDSC"])
		self.box.addWidget(self.btnSort,0,1,1,1,Qt.AlignLeft)
		self.searchBox=QSearchBox()
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.box.addWidget(self.searchBox,0,2,1,1,Qt.AlignRight)
		self.searchBox.returnPressed.connect(self._searchApps)
		self.searchBox.textChanged.connect(self._resetSearchBtnIcon)
		self.searchBox.clicked.connect(self._searchAppsBtn)
		self.table=QTableTouchWidget()
		self.table.setAttribute(Qt.WA_AcceptTouchEvents)
		self.table.setColumnCount(3)
		self.table.setShowGrid(False)
		self.table.verticalHeader().hide()
		self.table.horizontalHeader().hide()
		self.table.verticalScrollBar().valueChanged.connect(self._getMoreData)
		#self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.resetScreen()
		self.box.addWidget(self.table,1,0,1,self.box.columnCount())
		btnSettings=QPushButton()
		icn=QtGui.QIcon.fromTheme("settings-configure")
		btnSettings.setIcon(icn)
		btnSettings.clicked.connect(self._gotoSettings)
		self.box.addWidget(btnSettings,2,self.box.columnCount()-1,1,1,Qt.Alignment(-1))
		self.lblInfo=QInfoLabel()
		self.lblInfo.setActionText(i18n.get("LLXUP"))
		self.lblInfo.setActionIcon("lliurex-up")
		self.lblInfo.setText(i18n.get("UPGRADES"))
		self.lblInfo.clicked.connect(self._launchLlxUp)
		self.box.addWidget(self.lblInfo,2,0,1,1)
		self._getUpgradables()
	#def _load_screen

	def _launchLlxUp(self):
		subprocess.run(["pkexec","lliurex-up"])

	def _loadFilters(self):
		self.btnFilters.clear()
		self.btnFilters.setText(i18n.get("FILTERS"))
		self.btnFilters.addItem(i18n.get("ALL"))
		items=[i18n.get("INSTALLED"),"Lliurex","Snap","Appimage","Flatpak","Zomando"]
		for item in items:
			self.btnFilters.addItem(item,state=False)
	#def _loadFilters

	def _populateCategories(self): 
		self.cmbCategories.clear()
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
	#def _populateCategories

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
		else:
			categories=[]
			for i18ncat,cat in self.i18nCat.items():
				categories.append("\"{}\"".format(cat))
			if not "Lliurex" in categories:
				categories.append("\"Lliurex\"")
			if not "Forbidden" in categories:
				categories.append("\"Forbidden\"")
			categories=",".join(categories)
			apps.extend(json.loads(self.rc.execute('list',"({})".format(categories))))
		self.appsRaw=apps
		self.cleanAux()
		return(apps)
	#def _getAppList

	def _endGetUpgradables(self,*args):
		print(args)
		if args[0]==True:
			self.lblInfo.setVisible(True)
		self.th.wait()
	#def _endGetUpgradables(self,*args):

	def _getUpgradables(self):
		self.lblInfo.setVisible(False)
		self.th=chkUpgrades(self.rc)
		self.th.chkEnded.connect(self._endGetUpgradables)
		self.th.start()
	#def _getUpgradables

	def _shuffleApps(self):
		random.shuffle(self.apps)
	#def _shuffleApps

	def _goHome(self):
		if time.time()-self.oldTime<MINTIME*2:
			return
		self.oldTime=time.time()
		self.sortAsc=False
		self.searchBox.setText("")
		self._loadFilters()
		self.apps=self._getAppList()
		self._shuffleApps()
		self.resetScreen()
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
		self.btnFilters.setText(",".join(desc)[0:20])
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
			init=4
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
			self.cmbCategories.setCurrentText(self.oldCat)
			return
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.searchBox.setText("")
		self.resetScreen()
		i18ncat=self.cmbCategories.currentText()
		if self.oldCat!=i18ncat:
			self.oldCat=i18ncat
		cat=self.i18nCat.get(i18ncat,i18ncat)
		if cat==i18n.get("ALL"):
			cat=""
		self.apps=self._getAppList(cat)
		self._filterView(getApps=False)
		self.releaseKeyboard()
		self.oldTime=time.time()
	#def _loadCategory

	def _getMoreData(self):
		if (self.table.verticalScrollBar().value()==self.table.verticalScrollBar().maximum()) and self.appsLoaded!=len(self.apps):
			self._loadData(self.appsLoaded,self.appsLoaded+self.appsToLoad)
			for wdg in self.wdgs:
				self.table.setCellWidget(wdg[0],wdg[1],wdg[2])
	#def _getMoreData

	def _loadData(self,idx,idx2,applist=None):
		if applist==None:
			apps=self.apps[idx:idx2]
		else:
			apps=applist[idx:idx2]
		col=0
		#self.table.setRowHeight(self.table.rowCount()-1,btn.iconSize+int(btn.iconSize/16))
		colspan=random.randint(1,3)
		span=colspan
		btn=None
		self.wdgs=[]
		for strapp in apps:
			jsonapp=json.loads(strapp)
			if jsonapp.get('name','') in self.appsSeen:
				self.appsLoaded+=1
				continue
			self.appsSeen.append(jsonapp.get('name',''))
			row=self.table.rowCount()-1
			btn=QPushButtonRebostApp(strapp)
			btn.clicked.connect(self._loadDetails)
			self.wdgs.append((row,col,btn))
			col+=1
			span=span-1
			if span==0:
				if colspan==3:
					colspan=1
				elif colspan==1:
					colspan=3
				if colspan!=1:
					self.table.setSpan(row,col-1,1,colspan)
				colspan=random.randint(1,3)
				span=colspan
				self.table.setRowHeight(row,btn.iconSize+int(btn.iconSize/16))
				self.table.setRowCount(self.table.rowCount()+1)
				col=0
			self.appsLoaded+=1

		if btn!=None:
			self.table.setRowHeight(self.table.rowCount()-1,btn.iconSize+int(btn.iconSize/16))
		return(self.wdgs)
	#def _loadData

	def _loadDetails(self,*args,**kwargs):
		icn=""
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		if isinstance(args[0],QPushButtonRebostApp):
			icn=args[0].iconUri.pixmap()
		self._endLoadDetails(icn,*args)
	#def _loadDetails(self,*args,**kwargs):

	def _endLoadDetails(self,icn,*args):
#		self.stack.gotoStack(idx=3,parms=(args))
		#Refresh all pkg info
		self.referrer=args[0]
		self.setChanged(False)
		self.parent.setCurrentStack(idx=3,parms={"name":args[-1].get("name",""),"icon":icn})
	#def _loadDetails

	def _gotoSettings(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.parent.setCurrentStack(idx=2,parms="")
	#def _gotoSettings

	def _thTERM(self,*args):
		self._debug("Pending thread end")
	#def _thTERM

	def cleanAux(self,*args):
		print("Cleaning")
		if isinstance(self.aux,list):
			for w in self.aux:
				if hasattr(w,"finished"):
					print("Finish {}".format(w))
					w.terminate()
					w.wait()
					self.aux.remove(w)
					print("Removed {}".format(w))
		self._debug("Caching: {}".format(len(self.aux)))
		print("Cleaned")
	#def cleanAux

	def updateScreen(self):
		self.cleanAux()
		self._loadData(self.appsLoaded,self.appsToLoad)
		for wdg in self.wdgs:
			self.table.setCellWidget(wdg[0],wdg[1],wdg[2])
		#self.table.show()
		self.cleanAux()
		self.setCursor(self.oldcursor)
	#def _udpate_screen

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
		#For some reason setParms is launching N times
		#referrer will be only fulfilled when details stack
		#fires events, when is a repeated call to setParms
		#referrer will be none so function can exit. This must be investigated
		if not hasattr(self,"referrer"):
			return()
		if self.referrer==None:
			return()
		for arg in args:
			if isinstance(arg,dict):
				for key,item in arg.items():
					kwargs[key]=item
		if kwargs.get("refresh",False)==False:
			cursor=QtGui.QCursor(Qt.WaitCursor)
			self.setCursor(cursor)
			if len(args)>=1:
				self._populateCategories()
				self.oldSearch=""
				self._searchApps()
		else:
			if hasattr(self,"referrer")==False:
				return()
			app=kwargs.get("app",{})
			cat=kwargs.get("cat",{})
			if len(cat)>0:
				self.cmbCategories.setCurrentText(self.catI18n.get(cat,cat))
				self._loadCategory()
			elif len(app)>0:
				self._searchApps()
			else:
				self.updateScreen()
		self.referrer=None
	#def setParms

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

