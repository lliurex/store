#!/usr/bin/python3
import sys,time,json
import os
from PySide6.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QEvent,QSignalMapper
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QStackedWindowItem,QScrollLabel
import subprocess
import gettext
from appseduWidgets import QPushButtonAppsedu,QFormAppsedu
from appsedu import appsedu
_ = gettext.gettext
QString=type("")

ICON_SIZE=128

i18n={
	"ALL":_("All"),
	"BLOCKED":_("Application is blocked. Check link below for more info."),
	"CONFIG":_("Portrait"),
	"DESC":_("Navigate through all applications"),
	"MISCATALOGUED":_("Application is included in catalogue but doesn't provide an install option"),
	"MENU":_("Show applications"),
	"NEWDATA":_("Updating info"),
	"NOTFOUND":_("Application not found"),
	"SEARCH":_("Search"),
	"SORTDSC":_("Sort alphabetically"),
	"TOOLTIP":_("Portrait"),
	}

class thAppsedu(QThread):
	getApplications=Signal("PyObject")
	getCategoriesFromApplications=Signal("PyObject")
	getApplicationsFromCategory=Signal("PyObject")
	searchApplications=Signal("PyObject")
	getRelatedZomando=Signal("PyObject")
	def __init__(self,parent=None,**kwargs):
		QThread.__init__(self, None)
		self.appsedu=appsedu.manager()

	def run(self):
		if len(self.kwargs)>0:
			args=self.kwargs.copy
		else:
			args=self.args
		if self.action=="getApplications":
			applications=self.appsedu.getApplications(args)
			self.getApplications.emit(applications)
		elif self.action=="getCategoriesFromApplications":
			applications=self.appsedu.getCategoriesFromApplications(args)
			self.getCategoriesFromApplications.emit(applications)
		elif self.action=="getApplicationsFromCategory":
			applications=self.appsedu.getApplicationsFromCategory(args)
			self.getApplicationsFromCategory.emit(applications)
		elif self.action=="searchApplications":
			applications=self.appsedu.searchApplications(args)
			self.searchApplications.emit(applications)
		elif self.action=="getRelatedZomando":
			zomando=self.appsedu.getRelatedZomando(args)
			self.getRelatedZomando.emit(zomando)
			
	def setAction(self,action,*args,**kwargs):
		self.action=action
		if len(args)>0:
			self.args=args[0]
		self.kwargs=kwargs.copy()
#class thAppsedu

class portrait(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=True
		self.enabled=True
		self._debug("portrait load")
		self.setProps(shortDesc=i18n.get("DESC"),
			longDesc=i18n.get("MENU"),
			icon="application-x-desktop",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.hideControlButtons()
		self.appsedu=thAppsedu()
		self.appsedu.getApplications.connect(self._loadTableData)
		self.appsedu.getCategoriesFromApplications.connect(self._loadCategoriesData)
		self.appsedu.getApplicationsFromCategory.connect(self._loadApplicationsData)
		self.appsedu.searchApplications.connect(self._loadApplicationsData)
		self.appsedu.getRelatedZomando.connect(self._launchZomando)
		self.oldCursor=self.cursor()
		self.mapper=QSignalMapper(self)
		self.mapper.mappedObject.connect(self._gotoDetails)
		self.mapperInstall=QSignalMapper(self)
		self.mapperInstall.mappedObject.connect(self._installApp)
		self.refresh=True
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Portrait: {}".format(msg))
	#def _debug

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.sortAsc=False
		#Banner is hidden
		lbl=self._defBanner()
		lbl.setVisible(False)
		self.box.addWidget(lbl,0,0,1,2,Qt.AlignTop|Qt.AlignCenter)
		navBar=self._defNavBar()
		self.box.addWidget(navBar,1,0,1,1,Qt.AlignLeft)
		self.table=self._defTable()
		self.box.addWidget(self.table,1,1,1,self.box.columnCount())
		self.details=self._defDetails()
		self.box.addWidget(self.details,1,1,1,self.box.columnCount())
		self.progress=self._defProgress()
		self.box.addWidget(self.progress,0,0,self.table.rowCount(),2,Qt.AlignCenter)
		self.box.setColumnStretch(1,1)
		self.table.setMinimumHeight(QPushButtonAppsedu({}).iconSize*9)
		self.progressbarShow()
	#def _load_screen

	def _defBanner(self):
		lbl=QLabel()
		imgDir=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","banner.png")
		img=QtGui.QImage(imgDir)
		lbl.setPixmap(QtGui.QPixmap(img))
		lbl.setStyleSheet("""QLabel{padding:0px}""")
		return(lbl)
	#def _defBanner
	
	def _defDetails(self):
		wdg=QWidget()
		wdg=QFormAppsedu()
		wdg.linkActivated.connect(self._gotoUrl)
		wdg.clicked.connect(self._gotoHome)
		wdg.install.connect(self._installApp)
		wdg.setVisible(False)
		return(wdg)
	#def _defDetails

	def _defNavBar(self):
		wdg=QWidget()
		vbox=QVBoxLayout()
		vbox.setContentsMargins(0,0,10,0)
		self.searchBox=QSearchBox()
		self.searchBox.btnSearch.setMinimumSize(int(ICON_SIZE/3),int(ICON_SIZE/3))
		self.searchBox.txtSearch.setMinimumSize(int(ICON_SIZE/3),int(ICON_SIZE/3))
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.searchBox.returnPressed.connect(self._searchApps)
		self.searchBox.clicked.connect(self._searchApps)
		self.cmbCategories=QListWidget()
		vbox.addWidget(self.searchBox)
		vbox.addWidget(self.cmbCategories)
		self.cmbCategories.setMinimumHeight(int(ICON_SIZE/3))
		self.cmbCategories.currentItemChanged.connect(self._loadCategory)
		wdg.setLayout(vbox)
		return(wdg)
	#def _defNavBar

	def _defTable(self):
		self.maxCol=1
		table=QTableTouchWidget()
		table.setAutoScroll(True)
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setColumnCount(self.maxCol)
		table.setShowGrid(False)
		table.verticalHeader().hide()
		table.horizontalHeader().hide()
		table.verticalScrollBar().valueChanged.connect(self._getMoreData)
		table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		table.setStyleSheet("""QTableWidget::item{padding:12px}""")
		return(table)
	#def _defTable

	def _defProgress(self):
		wdg=QWidget()
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		vbox=QVBoxLayout()
		vbox.setContentsMargins(0,0,0,0)
		lblProgress=QLabel("<h3>{}</h3>".format(i18n["NEWDATA"]))
		progress=QProgressBar()
		progress.setMinimum(0)
		progress.setMaximum(0)
		vbox.addWidget(progress)
		vbox.addWidget(lblProgress,Qt.AlignBottom,Qt.Alignment(-1))
		wdg.setLayout(vbox)
		bkgcolor=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Active,QtGui.QPalette.Button)).toRgb()
		lblProgress.setObjectName("frame")
		lblProgress.setStyleSheet('''#frame{
								border:2px solid;
								background-color:rgba(%s,%s,%s,1);
								border-color:rgba(%s,%s,%s,1)}'''
								%(bkgcolor.red(),bkgcolor.green(),bkgcolor.blue(),bkgcolor.red(),bkgcolor.green(),bkgcolor.blue()))
		return(wdg)
	#def _defProgress

	def progressbarHide(self):
		self.progress.setVisible(False)
		self.table.setEnabled(True)
		self.cmbCategories.setEnabled(True)
		self.searchBox.setEnabled(True)
	#def progressbarHide

	def progressbarShow(self):
		self.progress.setVisible(True)
		self.table.setEnabled(False)
		self.cmbCategories.setEnabled(False)
		self.searchBox.setEnabled(False)
	#def progressbarShow

	def updateScreen(self,applications=[]):
		if len(applications)==0:
			self.appsedu.setAction("getApplications",cache=True)
			self.appsedu.start()
		else:
			self._loadTableData(applications)
	#def updateScreen
	
	def _populateCategoriesFromApps(self,applications):
		self.appsedu.setAction("getCategoriesFromApplications",applications)
		self.appsedu.start()
	#def _populateCategoriesFromApps
	
	def _loadCategoriesData(self,categories):
		self.cmbCategories.clear()
		self.cmbCategories.setSizeAdjustPolicy(self.cmbCategories.SizeAdjustPolicy.AdjustToContents)
		self.cmbCategories.addItem(i18n.get('ALL'))
		for cat in categories:
			icat=_(cat)
			if cat=="Forbidden":
				self.forbiddenCat=icat
			self.cmbCategories.addItem(icat)
		self.progressbarHide()
	#def _loadCategoriesData

	def _loadCategory(self):
		self._gotoHome()
		self.progressbarShow()
		category=self.cmbCategories.currentItem().text()
		if category==self.forbiddenCat:
			category="Forbidden"
		if self.cmbCategories.currentRow()>0:
			self.appsedu.setAction("getApplicationsFromCategory",category)
		else:
			self.appsedu.setAction("getApplications")
		self.appsedu.start()
	#def _loadCategory

	def _loadTableData(self,applications):
		if self.cmbCategories.count()==0:
			self._populateCategoriesFromApps(applications)
		#self.table.viewportEvent=self.viewPortEvent
		self.table.clearContents()
		self.table.setRowCount(0)
		self.table.setRowCount(len(applications))
		idx=0
		for app in applications:
			btn=QPushButtonAppsedu(app)
			btn.clicked.connect(self.mapper.map)
			btn.install.connect(self.mapperInstall.map)
			self.mapper.setMapping(btn,btn)
			self.mapperInstall.setMapping(btn,btn)
			self.table.setCellWidget(idx,0,btn)
			self.table.setRowHeight(idx,btn.iconSize*2)
			idx+=1
			if idx<=8:
				btn.loadInfo()
		if self.cmbCategories.currentRow()>0:
			self.table.setCurrentCell(0,0)
			self.table.verticalScrollBar().setValue(0)
		self.progressbarHide()
	#def _loadTableData

	def _loadApplicationsData(self,applications):
		self._loadTableData(applications)
	#def _loadApplicationsData
	
	def _getMoreData(self,*args):
		limitY=self.table.verticalScrollBar().value()
		row=int(limitY/QPushButtonAppsedu({}).iconSize)
		for i in range(row-8,row+8):
			btn=self.table.cellWidget(i,0)
			if isinstance(btn,QPushButtonAppsedu):
				btn.loadInfo()
	#def _getMoreData

	def _tagCategories(self,categories):
		tags=[]
		for cat in categories:
			if cat.strip().islower() or len(cat)==0:
				continue
			icat=_(cat)
			if icat not in tags:
				tags.append(icat)
		return(tags)
	#def _tagCategories

	def _gotoHome(self,*args):
		self.details.setVisible(False)
		self.table.setVisible(True)
	#def _gotoHome

	def _gotoDetails(self,btn):
		self.details.setTitle(btn.app.get("app"))
		self.details.setDescription(btn.app.get("description"),btn.app.get("url"))
		self.details.setIcon(btn.app.get("icon"))
		#self.detailSummary.setText(btn.app.get("summary"))
		taglist=self._tagCategories(btn.app.get("categories",[]))
		self.details.setTags(taglist)
		self.table.setVisible(False)
		self.details.setEnabled(True)
		if "Forbidden" in btn.app.get("categories",[]):
			text="<h3>{}</h3".format(i18n.get("BLOCKED"))
			text+=self.details.description()
			self.details.setDescription(text)
			self.details.setEnabled(False)
		self.details.setVisible(True)
	#def _gotoDetails

	def _gotoUrl(self,*args):
		if args[0].startswith("#"):
			self._gotoCategory(*args)
		else:
			cmd=["kde-open5",args[0]]
			subprocess.run(cmd)
	#def _gotoUrl

	def _gotoCategory(self,*args):
		item=self.cmbCategories.findItems(args[0].replace("#",""),Qt.MatchExactly)
		if item!=None:
			self.cmbCategories.setCurrentItem(item[0])
		self._loadCategory()
	#def _gotoCategory(self,*args):

	def _installApp(self,*args):
		self.details.lock()
		if isinstance(args[0],str):
			app=args[0]
		else:
			app=args[0].app.get("app")
		self.progressbarShow()
		self.appsedu.setAction("getRelatedZomando",app)
		self.appsedu.start()
	#def _installApp

	def _searchApps(self,*args):
		self._gotoHome()
		app=self.searchBox.text()
		self.progressbarShow()
		self.appsedu.setAction("searchApplications",app)
		self.cmbCategories.currentItemChanged.disconnect()
		self.cmbCategories.setCurrentRow(0)
		self.cmbCategories.currentItemChanged.connect(self._loadCategory)
		self.appsedu.start()
	#def _searchApps

	def _launchZomando(self,*args):
		cmd=""
		if len(args)>0:
			if len(args[0])>0:
				cmd=["pkexec",args[0]]
				subprocess.run(cmd)
		self.progressbarHide()
		if len(cmd)==0:
			self.showMsg(summary=i18n.get("NOTFOUND"),timeout=5,text=i18n.get("MISCATALOGUED"))
		self.details.unlock()

	#def _launchZomando(self,*args):

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

