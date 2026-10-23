#!/usr/bin/python3
import os,time
from functools import partial
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QVBoxLayout,QLabel
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QEvent
from QtExtraWidgets import QFlowTouchWidget
from wdg.btnRebost import QPushButtonRebostApp
import extras.css as css
from extras.constants import *
from extras.i18n import *

class paneGlobalView(QWidget):
	requestLoadApps=Signal("PyObject")
	requestLoadDetails=Signal("PyObject","PyObject","PyObject")
	requestInstallApp=Signal("PyObject",dict,"PyObject")
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
		self.appsLoaded={}
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
							elements=int(self.width()/(args[0].width()+int(self.table.flowLayout.spacing())*2))
						newPos=idx-elements
					elif args[1].key()==Qt.Key_Right or args[1].key()==Qt.Key_Down:
						idx=self.table.currentIndex()
						elements=1
						if args[1].key()==Qt.Key_Down:
							elements=int(self.width()/(args[0].width()+int(self.table.flowLayout.spacing())*2))
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
		self.empty=self._defEmptyContainer()
		lay.addWidget(self.empty,0,0,1,1)
		self.empty.hide()
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

	def _defEmptyContainer(self):
		wdg=QWidget()
		glay=QGridLayout(wdg)
		lblIcn=QLabel()
		icn=QtGui.QIcon.fromTheme("align-none")
		pxm=icn.pixmap(self.width(),self.height(),QtGui.QIcon.Mode.Disabled)
		lblIcn.setPixmap(pxm)
		glay.addWidget(lblIcn,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		lblTxt=QLabel("<p><strong>{}</strong></p>".format(i18n["ERREMPTY"]))
		lblTxt.setStyleSheet("""padding:5px;""")
		fLbl=lblTxt.font()
		lblTxt.setAutoFillBackground(True)
		fLbl.setPointSize(fLbl.pointSize()+4)
		lblTxt.setFont(fLbl)
		glay.addWidget(lblTxt,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		return(wdg)
	#def _defEmptyContainer


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
			self._rebost.quit()
			#self._rebost.wait()
		self._rebost.start()
	#def getApps

	def loadAppsStop(self):
		self.stopAdding=True
	#def loadAppsStop

	def _emitLoadDetails(self,*args):
		app=args[1]
		btn=args[0]
		self.requestLoadDetails.emit(self,btn,app)
	#def _emitLoadDetails

	def _emitInstallApp(self,*args):
		btn=args[0]
		icon=btn.iconUri.pixmap()
		app=args[1]
		self.requestInstallApp.emit(btn,app,icon)
	#def _emitInstallApp

	def _loadApps(self,apps):
		self.appsLoaded={}
		self.stopAdding=False
		self.table.setSpacing(MARGIN*5)
		self.empty.hide()
		self.table.show()
		if len(apps)==0:
			self.empty.show()
			self.table.hide()
		while apps:
			if hasattr(self,"stopAdding")==False:
				return
			if self.stopAdding==True:
				break
			jsonapp=apps.pop(0)
			if jsonapp.get("hidden",False)==True:
				continue
			btn=QPushButtonRebostApp(jsonapp)
			btn.autoUpdate=True
			btn.clicked.connect(self._emitLoadDetails)
			btn.installEventFilter(self)
			btn.install.connect(self._emitInstallApp)
			self.appsLoaded[jsonapp["id"]]=btn
			self.table.addWidget(btn)
	#def _loadApps

	def loadApps(self,apps):
		self.requestLoadApps.emit(apps)
	#def loadApps

	def refreshBtnForApp(self,rapp):
		#Search for app in loaded buttons and update it
		btn=self.appsLoaded.get(rapp["id" ])
		if btn!=None:
			if rapp.get("icon","").strip()!="":
				btn.setApp(rapp,updateIcon=True)
			else:
				btn.setApp(rapp,updateIcon=False)
	#def updateBtn


