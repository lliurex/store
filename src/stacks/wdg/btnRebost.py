#!/usr/bin/python3
from functools import partial
import os,time
import json
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout
from PySide6.QtCore import Qt,Signal,QEvent,QSize
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
import lib.helperLib as helper
from wdg.lblApp import QLabelRebostApp
import extras.css as css
from extras.constants import *
from extras.i18n import *

class QPushButtonRebostApp(QPushButton):
	clicked=Signal("PyObject","PyObject")
	install=Signal("PyObject","PyObject")
	ready=Signal("PyObject")
	keypress=Signal()

	def __init__(self,strapp,appname="",parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.destroyed.connect(partial(QPushButtonRebostApp._stop,self.__dict__))
		if isinstance(strapp,str):
			self.app=json.loads(strapp)
		else:
			self.app=strapp
		self.appIconSize=kwargs.get("iconSize",ICON_SIZE/2)
		self.helper=helper.appHelper()
		self._wAttributes()
		self.setStyleSheet(css.btnRebost())
		self.installEventFilter(self)
		self.th=[]
		self._initRegisters()
		self.lockTooltip=False
		self._renderGui()
	#def __init__

	@staticmethod
	def _stop(*args):
		selfDict=args[0]
		if selfDict.get("data","")!="":
			self["data"].blockSignals(True)
			self["data"].requestInterruption()
			self["data"].quit()
			self["data"].deleteLater()
			self["data"].wait()
	#def _onDestroy

	def _stopThreads(self):
		for th in self.th:
			if th.isRunning():
				th.blockSignals(True)
				th.requestInterruption()
				th.deleteLater()
				th.wait()
	#def _stopThreads

	def _initRegisters(self):
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.instBundle=""
		self.refererApp=None
		self.init=False
		self.autoUpdate=False
	#def _initRegisters

	def _wAttributes(self):
		self.setObjectName("rebostapp")
		#self.appIconSize=self.aaiconSize/2
		self.setMinimumHeight(220)
		self.setMinimumWidth(140)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAutoFillBackground(True)
		self.setCursor(QCursor(Qt.PointingHandCursor))
		self.setDefault(True)
	#def _wAttributes

	def _emitInstall(self,*args):
		self.progress.show()
		self.lblFlyIcon.hide()
		self.install.emit(self,self.app)
	#def _emitInstall

	def enterEvent(self,*args):
	   self.setFocus()
	#def enterEvent

	def activate(self):
		self.clicked.emit(self,self.app)
	#def activate

	def keyPressEvent(self,ev):
		if ev.key() in [Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space]:
			self.clicked.emit(self,self.app)
		else:
			self.keypress.emit()
			ev.ignore()
		return True
	#def keyPressEvent(self,ev):

	def mousePressEvent(self,*args):
		self.clicked.emit(self,self.app)
	#def mousePressEvent

	def eventFilter(self,*args):
		ev=args[1]
		if isinstance(ev,QEvent):
			if ev.type()==QEvent.Type.Paint:
				if self.init==False:
					self.init=True
					self.iconUri.setIconSize(self.appIconSize)
					self.iconUri.loadImg(self.app)
					self.updateScreen()
			if ev.type()==QEvent.Type.FocusIn:
				self.focusFrame.setVisible(True)
			if ev.type()==QEvent.Type.FocusOut:
				self.focusFrame.setVisible(False)
		return(False)
	#def eventFilter

	def _renderGui(self,*args):
		self.btn=self._defBtnInstall()
		self.lblFlyIcon=self._defFlyIcon()
		self.lblFlyIcon.setAttribute(Qt.WA_TranslucentBackground)
		self.label=self._defLabel()
		self.iconUri=QLabelRebostApp()
		self.iconUri.setIconSize(self.appIconSize)
		self.iconUri.setClickable(True)
		self.iconUri.clicked.connect(self.activate)
		self.iconUri.setObjectName("iconUri")
		self.focusFrame=self._defFrame()
		#Btn Layout
		lay=QGridLayout()
		self.setLayout(lay)
		self.layout().addWidget(self.iconUri,0,0,Qt.AlignCenter|Qt.AlignTop)
		self.layout().addWidget(self.lblFlyIcon,0,0,Qt.AlignRight|Qt.AlignTop)
		self.layout().addWidget(self.label,1,0,Qt.AlignCenter|Qt.AlignTop)
		self.layout().addWidget(self.btn,2,0,Qt.AlignCenter|Qt.AlignBottom)
		self.layout().addWidget(self.focusFrame,0,0,3,1,Qt.AlignCenter|Qt.AlignBottom)
		#Progress indicator
		self.progress=self._defProgress()
		self.layout().addWidget(self.progress,0,0,Qt.AlignRight|Qt.AlignTop)
		self.flyIcon=QPixmap(os.path.join(RSRC,"zero-center128x128.png"))
		if self.app.get("homepage")!=None:
			if "appsedu" in self.app["homepage"].lower():
				self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu128x128.png"))
	#def __renderGui

	def _defFlyIcon(self):
		wdg=QLabel()
		wdg.setObjectName("flyIcon")
		return(wdg)
	#def _defFlyIcon

	def _defLabel(self):
		wdg=QLabel()
		wdg.setWordWrap(True)
		wdg.setAlignment(Qt.AlignCenter)
		return(wdg)
	#def _defLabel

	def _defFrame(self):
		wdg=QLabel("")
		wdg.setVisible(False)
		wdg.setFixedSize(QSize(self.sizeHint().width(),MARGIN/2))
		wdg.setStyleSheet("background: %s"%(COLOR_BACKGROUND_DARK))
		return(wdg)
	#def _defFrame

	def _defBtnInstall(self):
		btn=QPushButton()
		btn.setText(i18n.get("BTN_INSTALL"))
		btn.setObjectName("btnInstall")
		btn.clicked.connect(self._emitInstall)
		return(btn)
	#def _defBtnInstall

	def _defProgress(self):
		wdg=QLabel()
		wdg.setObjectName("flyIcon")
		scaleFactor=(self.appIconSize/2)
		wdg.setPixmap(QPixmap(os.path.join(RSRC,"run-build-install.png")).scaled(scaleFactor,scaleFactor,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation))
		wdg.setVisible(False)
		return(wdg)
	#def _defProgress

	def _setFlyIcon(self):
		scaleFactor=(max(self.appIconSize,32)/2)
		self.lblFlyIcon.setPixmap(self.flyIcon.scaled(scaleFactor,scaleFactor,Qt.KeepAspectRatioByExpanding,Qt.FastTransformation))
	#def _setFlyIcon

	def _setBtnText(self):
		text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper().replace("L*","L·"),self.app.get('summary','').strip().replace("l*","·"))
		self.label.setText(text)
		if len(self.app.get("description","").strip())>0:
			descArray=self.app.get("description","").strip().split(" ")
			tt=" ".join(descArray[0:min(len(descArray),20)])
			self.setToolTip(tt)
		elif len(text)>0:
			self.setToolTip(text)
	#def _setBtnText

	def _setAppForbidden(self):
		self.btn.setEnabled(False)
		self.btn.setText(i18n.get("BTN_UNAUTHORIZED"))
		self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu_forbidden128x128.png"))
		self.btn.blockSignals(True)
	#def _setAppForbidden

	def _setAppPending(self):
		self.btn.setEnabled(False)
		self.btn.setText(i18n.get("BTN_UNAVAILABLE"))
		self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu_unavailable128x128.png"))
		self.btn.blockSignals(True)
	#def _setAppPending(self):

	def _setAppInstalled(self):
		self.btn.setVisible(True)
		self.btn.setEnabled(True)
		self.iconUri.setEnabled(True)
		self.btn.setText(i18n["BTN_REMOVE"])
	#def _setAppInstalled

	def _setAppAvailable(self):
		self.btn.setVisible(True)
		self.btn.setEnabled(True)
		self.iconUri.setEnabled(True)
		self.btn.setText(i18n.get("BTN_INSTALL"))
	#def _setAppAvailable

	def _setAppAssisted(self):
		self.btn.setVisible(True)
		self.btn.setEnabled(True)
		self.iconUri.setEnabled(True)
		self.btn.setEnabled(False)
		self.btn.setText(i18n["BTN_ASSISTED"])
	#def _setAppAvailable

	def _setAppWebApp(self):
		self.btn.setEnabled(True)
		self.btn.blockSignals(False)
		self.btn.setText(i18n["BTN_WEBAPP"])
		if "webapp" not in self.app.get("bundle").keys():
			self.app["bundle"].update({"webapp":self.app["homepage"]})
	#def _setAppWebApp

	def _getAppStatus(self):
		status=""
		if self.app.get("forbidden",False)==True:
			self._setAppForbidden()
		elif self.app.get("assisted",False)==True:
			self._setAppAssisted()
		elif self.app.get("webapp",False)==True:
			self._setAppWebApp()
		elif len(self.app.get("bundle",[]))==0 or self.app.get("unavailable",False)==True:
			self._setAppPending()
		else:
			self.instBundle=self.helper.getInstalledBundle(self.app)#self._getInstalledBundle()
			if self.instBundle!="":
				self._setAppInstalled()
			else:
				self._setAppAvailable()
		return(status)
	#def _getAppStatus

	def updateScreen(self):
		if hasattr(self,"app")==False:
			return
		if self.progress.isVisible()==True:
			self.progress.hide()
			self.lblFlyIcon.show()
		self._getAppStatus()
		self._setFlyIcon()
		self._setBtnText()
		if int(self.app.get("state","0"))>=7:
			self.btn.setCursor(QCursor(Qt.WaitCursor))
			self.btn.setEnabled(False)
			self.progress.show()
			self.lblFlyIcon.hide()
	#def updateScreen

	def setApp(self,app,updateIcon=False):
		self.app=app
		if updateIcon==True:
			self.iconUri.loadImg(self.app)
		#Sanitize values
		valuesToSanitize=["description","summary"]
		for sanitize in valuesToSanitize:
			if self.app.get(sanitize)==None:
				self.app[sanitize]=""
		if self.autoUpdate==True:
			self.updateScreen()
	#def setApp
#class QPushButtonRebostApp
