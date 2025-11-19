#!/usr/bin/python3
from functools import partial
import os,time
import json
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout
from PySide6.QtCore import Qt,Signal,QEvent,QSize
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
from lblApp import QLabelRebostApp
import css
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install"),
	"OPEN":_("Z-Install"),
	"REMOVE":_("Remove"),
	"UNAUTHORIZED":_("Blocked"),
	"UNAVAILABLE":_("Unavailable"),
	}

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
		self._wAttributes()
		self.setStyleSheet(css.btnRebost())
		self._initRegisters()
		self.appIconSize=kwargs.get("iconSize",ICON_SIZE/2)
		self.btn=self._defBtnInstall()
		self.lblFlyIcon=self._defFlyIcon()
		self.lblFlyIcon.setAttribute(Qt.WA_TranslucentBackground)
		self.label=self._defLabel()
		self.iconUri=QLabelRebostApp()
		self.iconUri.setIconSize(self.appIconSize)
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
		self.installEventFilter(self)
		self.th=[]
		#Progress indicator
		self.progress=self._defProgress()
		self.layout().addWidget(self.progress,0,0,Qt.AlignRight|Qt.AlignTop)
		self.lockTooltip=False
		self._renderGui()
	#def __init__

	@staticmethod
	def _stop(*args):
		selfDict=args[0]
		#if "scr" in selfDict.keys():
		#	self["scr"].blockSignals(True)
		#	self["scr"].requestInterruption()
		#	self["scr"].deleteLater()
		#	self["scr"].wait()
		#for th in selfDict.get("th",[]):
		#	th.blockSignals(True)
		#	th.requestInterruption()
		#	th.deleteLater()
		#	th.wait()
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

	def setData(self,data):
		self.data.setData(data)
		self.data.start()
	#def setData

	def _initRegisters(self):
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.instBundle=""
		self.refererApp=None
		self._showBtn=True
		self._compactMode=False
		self.init=None
		self.startLoadImage=False
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

	def setCompactMode(self,*args):
		if args[0]==True:
			self._showBtn=False
			self._compactMode=True
			self.setMinimumSize(QSize(self.appIconSize*1.5,self.appIconSize*1.3))
			self.appIconSize=(self.appIconSize*0.4)
	#def setCompactMode

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
		wdg.setFixedSize(QSize(self.sizeHint().width(),int(MARGIN)/2))
		wdg.setStyleSheet("background: %s"%(COLOR_BACKGROUND_DARK))
		return(wdg)
	#def _defFrame

	def _defBtnInstall(self):
		btn=QPushButton()
		btn.setText(i18n.get("INSTALL"))
		btn.setObjectName("btnInstall")
		btn.clicked.connect(self._emitInstall)
		btn.hide()
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

	def _renderGui(self,*args):
		states=self.app.get("status",{})
		zmd=states.get("zomando","0")
		if len(states)>0:
			for bundle,state in states.items():
				if int(state)==0:
					self.btn.setText(i18n.get("REMOVE"))
					self.instBundle=bundle
					break
		if self.app.get("forbidden",False)==True:
			self.btn.setText(i18n.get("UNAUTHORIZED"))
			self.btn.blockSignals(True)
			#self.btn.setStyleSheet("""color:#AAAAAA""")
		elif len(self.app.get("bundle",[]))==0 or self.app.get("unavailable",False)==True:
			self.btn.setText(i18n.get("UNAVAILABLE"))
			self.btn.blockSignals(True)
			#self.btn.setStyleSheet("""color:#AAAAAA""")
		text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper().replace("L*","L·"),self.app.get('summary','').strip().replace("l*","·"))
		self.label.setText(text)
		if len(text)>0:
			self.setToolTip(text)
		img=self.app.get('icon','')
	#def __init__

	def _emitInstall(self,*args):
		self.progress.show()
		self.lblFlyIcon.hide()
		self.install.emit(self,self.app)
	#def _emitInstall

	def eventFilter(self,*args):
		ev=args[1]
		if isinstance(ev,QEvent):
			if ev.type()==QEvent.Type.Paint:
				#if self.init==False:
				#	self.init=True
				if self.init==None:
					self.init=False
					self._applyDecoration()
				elif self.init==False and self.app.get("summary","")+self.app.get("name","")!="":
					if self.startLoadImage==True:
						self.init=True
						self.iconUri.setIconSize(self.appIconSize)
						self.iconUri.loadImg(self.app)
					else:
						self.startLoadImage=True
						self.updateScreen()
			if ev.type()==QEvent.Type.FocusIn:
				self.focusFrame.setVisible(True)
			if ev.type()==QEvent.Type.FocusOut:
				self.focusFrame.setVisible(False)
		return(False)
	#def eventFilter

	def _setActionForButton(self):
		self.btn.setText(i18n["INSTALL"])
		self.btn.setEnabled(True)
		if len(self.app.get("bundle",{}))==0 and self.app.get("forbidden",False)==True:
			self.btn.setText(i18n["UNAUTHORIZED"])
			self.btn.setEnabled(False)
		else:
			if len(self.app.get("bundle",[]))==0 or self.app.get("unavailable",False)==True:
				self.btn.setText(i18n.get("UNAVAILABLE"))
				self.btn.setText(i18n["UNAVAILABLE"])
				self.btn.setEnabled(False)
			elif self.app.get("forbidden",False)==True:
				self.btn.setEnabled(False)
				self.btn.setText(i18n["UNAUTHORIZED"])
			else: #app seems authorized and available
				bundles=self.app["bundle"]
				status=self.app["status"]
				zmd=bundles.get("unknown","")
				action="install"
				if zmd==self.app["name"]==self.app["pkgname"]:
					action="open"
				else:
					for bundle,appstatus in status.items():
						if int(appstatus)==0:# and zmdInstalled!="0":
							action="remove"
							break
				if action=="install":
					self.btn.setVisible(True)
					self.btn.setEnabled(True)
					self.iconUri.setEnabled(True)
					self.btn.setText(i18n["INSTALL"])
				elif action=="open":
					self.btn.setVisible(True)
					self.btn.setEnabled(True)
					self.btn.setText(i18n["OPEN"])
					self.iconUri.setEnabled(True)
					self.instBundle="unknown"
				else:
					self.btn.setText(i18n["REMOVE"])
	#def _setActionForButton

	def updateScreen(self):
		if hasattr(self,"app")==False:
			return
		_showBtn=self._showBtn
		if self.progress.isVisible()==True:
			self.progress.hide()
			self.lblFlyIcon.show()
		if self.app.get("name","").strip()!="":
			if self.app.get("summary","")!="" and self._compactMode==False:
				text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper(),self.app.get('summary','').strip(),'')
			elif self._compactMode==False:
				text="<p>{0}</p>".format(self.app.get('name','').strip()).upper()
			else:
				text="<p>{0}</p>".format(self.app.get('name','').strip().capitalize())
				self.iconUri.setEnabled(True)
				self.label.setStyleSheet("padding-top:{0}px;".format(int(MARGIN)))
		else:
			text="<p>{0}</p>".format(self.app.get('summary','').strip())
			_showBtn=False
		if self.label.text()!=text and len(text)>0:
			self.label.setText(text)
			if self._compactMode==False:
				self.setToolTip(text)
			elif self.lockTooltip==False:
				text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper(),self.app.get('summary','').strip(),'')
				self.setToolTip(text)
		if self._compactMode==False:
			self._setActionForButton()
		self.iconUri.setVisible(True)
		self.flyIcon=""
		if self.app.get("unavailable",False)==True:
			self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu_unavailable128x128.png"))
		elif self.app.get("forbidden",False)==True:
			self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu_forbidden128x128.png"))
		elif self.app.get("name","").startswith("zero-"):
			self.flyIcon=QPixmap(os.path.join(RSRC,"zero-center128x128.png"))
		elif self.app.get("homepage")!=None:
			if "appsedu" in self.app["homepage"].lower():
				self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu128x128.png"))
		scaleFactor=(self.appIconSize/2)
		if isinstance(self.flyIcon,QPixmap):
			self.lblFlyIcon.setPixmap(self.flyIcon.scaled(scaleFactor,scaleFactor,Qt.KeepAspectRatioByExpanding,Qt.FastTransformation))
		if self.btn.isVisible()!=_showBtn:
			self.btn.setVisible(_showBtn)
		if int(self.app.get("state","0"))>=7:
			self.btn.setCursor(QCursor(Qt.WaitCursor))
			self.btn.setEnabled(False)
			self.progress.show()
			self.lblFlyIcon.hide()
	#def updateScreen

	def enterEvent(self,*args):
	   self.setFocus()
	#def enterEvent

	def loadImg(self,app):
		self.iconUri.loadImg(self.app)
	#def loadImg

	def _applyDecoration(self,app={},forbidden=False,installed=False):
		if app=={}:
			app=self.app
		if (self.app.get("forbidden",False)==True) or len(self.app.get("bundle",[]))==0:
			if len(self.app.get("bundle",[]))==0 and self._showBtn==True:
				self.iconUri.setEnabled(False)
			else:
				self.iconUri.setEnabled(True)
			self.btn.blockSignals(True)
			self.btn.setEnabled(False)
		else:
			self.btn.blockSignals(False)
			self.btn.setEnabled(True)
	#def _applyDecoration

	def load(self,*args):
		currentPxm=self.iconUri.pixmap()
		img=args[0]
		if currentPxm!=None:
			if currentPxm.isNull()==True:
				self.iconUri.setPixmap(img.scaled(self.appIconSize,self.appIconSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		else:
			self.iconUri.setPixmap(img.scaled(self.appIconSize,self.appIconSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
	#def load

	def loadFullScreen(self,img):
		self.iconUri.setPixmap(img.scaled(self.width()-(self.layout().spacing()*2),self.height()-(self.layout().spacing()*2),Qt.KeepAspectRatio,Qt.SmoothTransformation))
	#def loadFullScreen
	
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

	def setApp(self,app,updateIcon=False):
		self.app=app
		if self.autoUpdate==True:
			self.updateScreen()
		if updateIcon==True:
			self.iconUri.loadImg(self.app)
	#def setApp
#class QPushButtonRebostApp
