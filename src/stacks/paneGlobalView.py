#!/usr/bin/python3
import os,time
from functools import partial
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QVBoxLayout,QLabel
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QEvent
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
		self.loading=False
		self.referersShowed={}
		self.appsToLoad=0
		self.refresh=True
		self.__initScreen__()
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
							elements=int(self.width()/(args[0].width()+int(self.table.flowLayout.spacing())*2))+1
						newPos=idx-elements
					elif args[1].key()==Qt.Key_Right or args[1].key()==Qt.Key_Down:
						idx=self.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Down:
							elements=int(self.width()/(args[0].width()+int(self.table.flowLayout.spacing())*2))+1
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

	def __initScreen__(self):
		self.setStyleSheet(css.tablePanel())
		lay=QGridLayout()
		self.table=self._defTable()
		lay.addWidget(self.table,0,0,1,1)
		self.setLayout(lay)
	#def __initScreen

	def _defTable(self):
		table=QFlowTouchWidget(self,fastMode=True)
		table.setFocusPolicy(Qt.NoFocus)
		table.setObjectName("qFlow")
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
		self.table.setSpacing(int(MARGIN)*5)
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
			print("-- ERROR UPDATING SCREEN -->")
			print(e)
			print("-- END ERROR REPORT --<")
	#def updateScreen

	def updateBtn(self,btn,app):
		if btn!=None:
			self.table.indexOf(btn)
			idx=self.table.indexOf(btn)
			if idx>=0:
				btn.setApp(app)
	#def updateBtn

