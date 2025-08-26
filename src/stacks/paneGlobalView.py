#!/usr/bin/python3
import os
from PySide6.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget,QSizePolicy,QCheckBox,QGraphicsDropShadowEffect
from btnRebost import QPushButtonRebostApp
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QCheckableComboBox,QTableTouchWidget,QInfoLabel,QFlowTouchWidget
from lblLnk import QLabelLink
import css
import gettext
_ = gettext.gettext

ICON_SIZE=128
MINTIME=0.2
LAYOUT="appsedu"
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")
i18n={
	"ALL":_("All"),
	"SEARCH":_("Search"),
	}

class paneGlobalView(QWidget):
	tagpressed=Signal(str)
	requestLoadDetails=Signal("PyObject","PyObject")
	requestInstallApp=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		if len(args)<1:
			return
		self._rebost=args[0]
		self.dbg=False
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("mp")
		self.setStyleSheet(css.tablePanel())
		lay=QVBoxLayout()
		lay.addSpacing(32)
		lay.setSpacing(24)
		hlay=QHBoxLayout()
		wdg=QWidget()
		wdg.setLayout(hlay)
		lay.addWidget(wdg)
		self.topBar=self._defCategoriesBar()
		self.topBar.setObjectName("categoriesBar")
		self.topBar.setVisible(False)
		self.topBar.setAttribute(Qt.WA_StyledBackground, True)
		lay.addWidget(self.topBar,Qt.AlignTop|Qt.AlignCenter)
		self.table=self._defTable()
		lay.addWidget(self.table)
		self.setLayout(lay)
		self.loading=False
		self.referersShowed={}
		self.appsToLoad=0
		self.refresh=True
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("GlobalView: {}".format(msg))

	def _defCategoriesBar(self):
		wdg=QFlowTouchWidget(self)
		return(wdg)
	#def _defCategoriesBar

	def _tagNav(self,*args):
		cat=args[0].replace("#","")
		self.tagpressed.emit(cat)
	#def _tagNav(self,*args)

	def _catDecorate(self,*args):
		text=self.topBar.currentItem().text()
		w=self.topBar.currentItem()
		text=text.replace("none'>#","none'><strong>#").replace("</a>","</strong></a>")
		self.topBar.currentItem().setText(text)
	#def _catDecorate

	def _catUndecorate(self,*args):
		for idx in range(0,self.topBar.count()):
			w=self.topBar.itemAt(idx).widget()
			t=w.text()
			if "<strong>" in t:
				t=t.replace("<strong>","").replace("</strong>","")
				w.setText(t)
	#def _catUndecorate

	def populateCategories(self,subcats,cat=""):
		self.topBar.clean()
		if cat not in subcats and cat!="":
			subcats.insert(0,cat)
		for subcat in subcats:
			wdg=QLabel("<a href=\"#{0}\" style='color:#FFFFFF;text-decoration:none'>#{0}</a>".format(_(subcat)))
			wdg.leaveEvent=self._catUndecorate
			wdg.enterEvent=self._catDecorate
			wdg.setAttribute(Qt.WA_StyledBackground, True)
			wdg.setOpenExternalLinks(False)
			wdg.setObjectName("categoryTag")
			wdg.linkActivated.connect(self._tagNav)
			self.topBar.addWidget(wdg)
		if len(subcats)>1:
			self.topBar.setVisible(True)
			self.topBar.setMaximumHeight(wdg.sizeHint().height()*2.3)
		else:
			self.topBar.setVisible(False)
	#def populateCategories

	def _defTable(self):
		table=QFlowTouchWidget(self)
		table.setFocusPolicy(Qt.NoFocus)
		table.clearFocus()
		table.setObjectName("qFlow")
		table.flowLayout.setSpacing(24)
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		table.setStyleSheet("""QFlowTouchWidget{border:0px; background:#FFFFFF;margin-left:100%;margin-right:1%;} QFlowTouchWidget::item{padding:2px}""")
		return(table)
	#def _defTable

	def tableLeaveEvent(self,*args):
		return(False)
	#def enterEvent

	def tableKeyPressEvent(self,*args):
		return(False)
	#def tableKeyPressEvent

	def getApps(self,category="",search=""):
		self._debug("Loading apps {}".format(category))
		if category!="":
			self._rebost.setAction("list","{}".format(category))
		else:
			self._rebost.setAction("search",search)
		if self._rebost.isRunning():
			self._rebost.requestInterruption()
			#self._rebost.wait()
		print("Launch rebost")
		self._rebost.start()
	#def getApps

	def loadAppsStop(self):
		self.stopAdding=True
	#def stopLoadApps

	def _emitLoadDetails(self,*args):
		self.requestLoadDetails.emit(args[0],args[1])
	#def _emitLoadDetails

	def _emitInstallApp(self,*args):
		self.requestInstallApp.emit(args[0],args[1])
	#def _emitInstallApp

	def loadApps(self,apps):
		pendingApps={}
		self.stopAdding=False
		while apps:
			if self.stopAdding==True:
				break
			jsonapp=apps.pop(0)
			btn=QPushButtonRebostApp(jsonapp)
			btn.clicked.connect(self._emitLoadDetails)
			btn.installEventFilter(self)
			btn.install.connect(self._emitInstallApp)
			self.table.addWidget(btn)
			#Force btn show
			QApplication.processEvents()
	#def _addAppsToGrid

	def updateScreen(self,addEnable=None):
		try:
			if isinstance(addEnable,bool):
				adding=addEnable
			else:
				adding=False
			if self.loading==True:
				adding=False
			if self.refresh==True and adding==True:
				print("REFRESH TRUE")
				for i in self.referersShowed.keys():
					self.referersShowed[i]=None
				#self._debug("Update from {} to {} of {}".format(self.appsLoaded,self.appsToLoad,len(self.apps)))
				#self._beginLoadData(self.appsLoaded,self.appsToLoad)
			#elif self.appsToLoad==-1: #Init 
		except Exception as e:
			print("-----")
			print(e)
			print("-----")
		print("UPDATE END")
