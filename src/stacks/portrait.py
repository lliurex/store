#!/usr/bin/python3
import sys,time,json
import os
from PySide6.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QEvent,QSignalMapper
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QStackedWindowItem,QInfoLabel
import subprocess
import gettext
from appseduWidgets import QPushButtonAppsedu
from appsedu import manager
_ = gettext.gettext
QString=type("")

ICON_SIZE=128
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
	"NEWDATA":_("Updating info"),
	"SEARCH":_("Search"),
	"SORTDSC":_("Sort alphabetically"),
	"TOOLTIP":_("Portrait"),
	"UPGRADABLE":_("Upgradables"),
	"UPGRADES":_("There're upgrades available")
	}

class thAppsedu(QThread):
	getApplications=Signal("PyObject")
	getCategoriesFromApplications=Signal("PyObject")
	getApplicationsFromCategory=Signal("PyObject")
	searchApplications=Signal("PyObject")
	def __init__(self,parent=None,**kwargs):
		QThread.__init__(self, None)
		self.appsedu=manager()

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
			
	def setAction(self,action,*args,**kwargs):
		self.action=action
		if len(args)>0:
			self.args=args[0]
		self.kwargs=kwargs.copy()
#class thAppsedu

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
		self.hideControlButtons()
		self.referersHistory={}
		self.referersShowed={}
		self.appsedu=thAppsedu()
		self.appsedu.getApplications.connect(self._loadTableData)
		self.appsedu.getCategoriesFromApplications.connect(self._loadCategoriesData)
		self.appsedu.getApplicationsFromCategory.connect(self._loadApplicationsData)
		self.appsedu.searchApplications.connect(self._loadApplicationsData)
		self.oldCursor=self.cursor()
		self.mapper=QSignalMapper(self)
		self.mapper.mappedObject.connect(self._gotoDetails)
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
		lbl=self._defBanner()
		lbl.setVisible(False)
		self.box.addWidget(lbl,0,0,1,2,Qt.AlignTop|Qt.AlignCenter)
		navBar=self._defNavBar()
		self.box.addWidget(navBar,1,0,1,1,Qt.AlignLeft)
		self.table=self._defTable()
		tableCol=1
		self.box.addWidget(self.table,2-tableCol,tableCol,1,self.box.columnCount())
		self.progress=self._defProgress()
		self.box.addWidget(self.progress,0,0,self.table.rowCount(),2,Qt.AlignCenter)
		self.box.setColumnStretch(1,1)
		self.table.setMinimumHeight(QPushButtonAppsedu({}).iconSize*9)
		self.progressEnable()
	#def _load_screen

	def _defBanner(self):
		lbl=QLabel()
		imgDir=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","banner.png")
		img=QtGui.QImage(imgDir)
		lbl.setPixmap(QtGui.QPixmap(img))
		lbl.setStyleSheet("""QLabel{padding:0px}""")
		return(lbl)
	#def _defBanner

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
		table.setAutoScroll(False)
		table.leaveEvent=self.tableLeaveEvent
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
		lblProgress=QLabel("<strong>{}</strong>".format(i18n["NEWDATA"]))
		lblProgress.setStyleSheet("background-color:rgba(255,255,255,0.1")
		progress=QProgressBar()
		progress.setMinimum(0)
		progress.setMaximum(0)
		vbox.addWidget(progress)
		vbox.addWidget(lblProgress,Qt.AlignBottom,Qt.Alignment(-1))
		wdg.setLayout(vbox)
		wdg.setObjectName("frame")
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

	def _populateCategoriesFromApps(self,applications):
		self.appsedu.setAction("getCategoriesFromApplications",applications)
		self.appsedu.start()
	#def _populateCategoriesFromApp
	
	def _loadCategoriesData(self,categories):
		self.cmbCategories.clear()
		self.cmbCategories.setSizeAdjustPolicy(self.cmbCategories.SizeAdjustPolicy.AdjustToContents)
		self.cmbCategories.addItem(i18n.get('ALL'))
		for cat in categories:
			self.cmbCategories.addItem(cat)
		self.progressDisable()
	#def _loadCategoriesData

	def progressDisable(self):
		self.progress.setVisible(False)
		self.table.setEnabled(True)
		self.cmbCategories.setEnabled(True)
		self.searchBox.setEnabled(True)
	#def progressDisable

	def progressEnable(self):
		self.progress.setVisible(True)
		self.table.setEnabled(False)
		self.cmbCategories.setEnabled(False)
		self.searchBox.setEnabled(False)
	#def progressEnable

	def _gotoDetails(self,btn):
		self.parent.setCurrentStack(2,parms=btn.app)
	#def _gotoDetails

	def updateScreen(self,applications=[]):
		if len(applications)==0:
			self.appsedu.setAction("getApplications",cache=True)
			self.appsedu.start()
		else:
			self._loadTableData(applications)
	#def updateScreen
	
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
			self.mapper.setMapping(btn,btn)
			self.table.setCellWidget(idx,0,btn)
			self.table.setRowHeight(idx,btn.iconSize*2)
			idx+=1
			if idx<=8:
				btn.loadInfo()
		if self.cmbCategories.currentRow()>0:
			self.table.setCurrentCell(0,0)
			self.table.verticalScrollBar().setValue(0)
		self.progressDisable()
	#def _loadTableData

	def _loadApplicationsData(self,applications):
		self._loadTableData(applications)
	
	def _getMoreData(self,*args):
		limitY=self.table.verticalScrollBar().value()
		row=int(limitY/QPushButtonAppsedu({}).iconSize)
		for i in range(row-8,row+8):
			btn=self.table.cellWidget(i,0)
			if isinstance(btn,QPushButtonAppsedu):
				btn.loadInfo()
	#def _getMoreData

	def _loadCategory(self):
		self.searchBox.setText("")
		self.progressEnable()
		category=self.cmbCategories.currentItem().text()
		if self.cmbCategories.currentRow()>0:
			self.appsedu.setAction("getApplicationsFromCategory",category)
		else:
			self.appsedu.setAction("getApplications")
		self.appsedu.start()
	#def _loadCategory

	def _searchApps(self,*args):
		app=self.searchBox.text()
		self.progressEnable()
		self.appsedu.setAction("searchApplications",app)
		self.appsedu.start()
	#def _searchApps
		

	def _endLoad(self,applications=[]):
		self.updateScreen(applications)

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

