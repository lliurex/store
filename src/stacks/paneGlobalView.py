#!/usr/bin/python3
import os,time
from functools import partial
from PySide6.QtWidgets import QApplication,QHBoxLayout,QWidget,QVBoxLayout,QLabel
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QEvent
from QtExtraWidgets import QFlowTouchWidget
from btnRebost import QPushButtonRebostApp
import css
from constants import *
import gettext
_ = gettext.gettext

i18n={
	"ALL":_("All"),
	"SEARCH":_("Search"),
	}

class paneGlobalView(QWidget):
	requestLoadApps=Signal("PyObject")
	requestLoadCategory=Signal(str)
	requestLoadDetails=Signal("PyObject","PyObject","PyObject")
	requestInstallApp=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		if len(args)<1:
			return
		self._rebost=args[0]
		self.dbg=True
		self.stopAdding=False
		self.destroyed.connect(partial(paneGlobalView._onDestroy,self.__dict__))
		self.requestLoadApps.connect(self._loadApps)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("mp")
		self.installEventFilter(self)
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

	@staticmethod
	def _onDestroy(*args):
		while args[0].keys():
			args[0].popitem()
	#def _onDestroy

	def eventFilter(self,*args):
		if isinstance(args[0],QPushButtonRebostApp):
			if isinstance(args[1],QtGui.QKeyEvent):
				if args[1].type()==QEvent.Type.KeyPress:
					newPos=-1
					if args[1].key()==Qt.Key_Left or args[1].key()==Qt.Key_Up:
						idx=self.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Up:
							elements=int(self.width()/(args[0].width()+int(MARGIN)*2))-1
						newPos=idx-elements
					elif args[1].key()==Qt.Key_Right or args[1].key()==Qt.Key_Down:
						idx=self.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Down:
							elements=int(self.width()/(args[0].width()+int(MARGIN)*2))-1
						newPos=idx+elements
						#Ugly hack for autoscroll to focused item
					if newPos!=-1:
						if newPos<self.table.count() and newPos>=0:
							btn=self.table.itemAt(newPos)
							btn.widget().setFocus()
							btn.widget().setEnabled(False)
							btn.widget().setEnabled(True)
							btn.widget().setFocus()
		return(False)
	#def eventFilter

	def _defCategoriesBar(self):
		wdg=QFlowTouchWidget(self)
		wdg.currentItemChanged.connect(self._catDecorate)
		return(wdg)
	#def _defCategoriesBar

	def _tagNav(self,*args):
		cat=args[0].replace("#","")
		self.requestLoadCategory.emit(cat)
	#def _tagNav(self,*args)

	def _catDecorate(self,*args):
		self._catUndecorate()
		current=args[1]
		text=current.text()
		text=text.replace("none'>#","none'><strong>#").replace("</a>","</strong></a>")
		current.setText(text)
	#def _catDecorate

	def _catUndecorate(self,*args):
		for idx in range(0,self.topBar.count()):
			w=self.topBar.itemAt(idx).widget()
			t=w.text()
			if "<strong>" in t:
				t=t.replace("<strong>","").replace("</strong>","")
				w.setText(t)
		if len(args):
			current=self.topBar.itemAt(0).widget()
			text=current.text()
			text=text.replace("none'>#","none'><strong>#").replace("</a>","</strong></a>")
			current.setText(text)
	#def _catUndecorate

	def populateCategories(self,subcats,cat=""):
		self.topBar.clean()
		self.topBar.leaveEvent=self._catUndecorate
		if cat not in subcats and cat!="":
			subcats.insert(0,cat)
		for subcat in subcats:
			wdg=QLabel()
			if subcat!=cat:
				text="<a href=\"#{0}\" style='color:#FFFFFF;text-decoration:none'>#{0}</a>".format(_(subcat))
			else:
				text="<a href=\"#{0}\" style='color:#FFFFFF;text-decoration:none'><strong>#{0}</strong></a>".format(_(subcat))
			wdg.setText(text)
			wdg.setAttribute(Qt.WA_Hover,True)
			wdg.hoverLeave=self._catUndecorate
			wdg.hoverEnter=self._catDecorate
			wdg.installEventFilter(self)
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
		table=QFlowTouchWidget(self,fastMode=True)
		table.setFocusPolicy(Qt.NoFocus)
		table.clearFocus()
		table.setObjectName("qFlow")
		table.flowLayout.setSpacing(24)
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		#table.setStyleSheet("""QFlowTouchWidget{border:0px; background:#FFFFFF;margin-left:100%;margin-right:1%;} QFlowTouchWidget::item{padding:2px}""")
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
			self._rebost.blockSignals(True)
			self._reobst.quit()
			#self._rebost.wait()
		self._rebost.start()
	#def getApps

	def loadAppsStop(self):
		self.stopAdding=True
	#def stopLoadApps

	def _emitLoadDetails(self,*args):
		app=args[1]
		btn=args[0]
		self.requestLoadDetails.emit(self,btn,app)
	#def _emitLoadDetails

	def _emitInstallApp(self,*args):
		self.requestInstallApp.emit(args[0],args[1])
	#def _emitInstallApp

	def _loadApps(self,apps):
		pendingApps={}
		self.stopAdding=False
		while apps:
			if self.stopAdding==True:
				break
			jsonapp=apps.pop(0)
			btn=QPushButtonRebostApp(jsonapp)
			btn.autoUpdate=True
			btn.clicked.connect(self._emitLoadDetails)
			btn.installEventFilter(self)
			btn.install.connect(self._emitInstallApp)
			self.table.addWidget(btn)
		self.topBar.show()
	#def _loadApps

	def loadApps(self,apps):
		self.requestLoadApps.emit(apps)
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
				for i in self.referersShowed.keys():
					self.referersShowed[i]=None
				#self._debug("Update from {} to {} of {}".format(self.appsLoaded,self.appsToLoad,len(self.apps)))
				#self._beginLoadData(self.appsLoaded,self.appsToLoad)
			#elif self.appsToLoad==-1: #Init 
		except Exception as e:
			print("-----")
			print(e)
			print("-----")
	#def updateScreen

	def updateBtn(self,btn,app):
		if btn!=None:
			self.table.indexOf(btn)
			idx=self.table.indexOf(btn)
			if idx>=0:
				btn.setApp(app)
	#def updateBtn

