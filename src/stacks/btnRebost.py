#!/usr/bin/python3
from functools import partial
import os,time
import json
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy
from PySide6.QtCore import Qt,Signal,QEvent,QSize
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
from QtExtraWidgets import QScreenShotContainer
from lblApp import QLabelRebostApp
import css
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install"),
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
		self._initRegisters()
		self.appIconSize=kwargs.get("iconSize",ICON_SIZE/2)
		self.btn=self._defBtnInstall()
		self.lblFlyIcon=self._defFlyIcon()
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
		self._renderGui()
	#def __init__

	@staticmethod
	def _stop(*args):
		selfDict=args[0]
		if "scr" in selfDict.keys():
			self["scr"].blockSignals(True)
			self["scr"].requestInterruption()
			self["scr"].deleteLater()
			self["scr"].wait()
		for th in selfDict.get("th",[]):
			th.blockSignals(True)
			th.requestInterruption()
			th.deleteLater()
			th.wait()
		if selfDict.get("data","")!="":
			self["data"].blockSignals(True)
			self["data"].requestInterruption()
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
		self.showBtn=True
		self.init=None
		self.startLoadImage=False
		self.autoUpdate=False
	#def _initRegisters

	def _wAttributes(self):
		self.setObjectName("rebostapp")
		#self.appIconSize=self.aaiconSize/2
		self.margin=12
		self.setMinimumHeight(220)
		self.setMinimumWidth(140)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAutoFillBackground(True)
		self.setCursor(QCursor(Qt.PointingHandCursor))
		self.setDefault(True)
	#def _wAttributes

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
		btn.setVisible(False)
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
		if "Forbidden" in self.app.get("categories",[]):
			self.btn.setText(i18n.get("UNAUTHORIZED"))
		elif "eduapp" in self.app.get("bundle",[]) and len(self.app.get("bundle",[]))==1:
			self.btn.setText(i18n.get("UNAVAILABLE"))
		text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper().replace("L*","L·"),self.app.get('summary','').strip().replace("l*","·"))
		self.setToolTip(text)
		self.label.setText(text)
		img=self.app.get('icon','')
	#def __init__

	def _emitInstall(self,*args):
	#	self.btn.setEnabled(False)
	#	self.progress.setVisible(True)
	#	if self.btn.text()==i18n["REMOVE"]:
	#		#Remove, get installed bundle
	#		priority=["zomando","flatpak","snap","package","appimage","eduapp"]
	#		for bundle in priority:
	#			if self.app["status"].get(bundle,"1")=="0" and self.app["bundle"].get("bundle","")!="":
	#				self.app["bundle"]={bundle:self.app["bundle"][bundle]}
	#				break
		self.install.emit(self,self.app)
	#def _emitInstall

	def eventFilter(self,*args):
		ev=args[1]
		#if isinstance(ev,QMouseEvent):
		#	self.activate()
		if isinstance(ev,QEvent):
			if ev.type()==QEvent.Type.Paint:
				#if self.init==False:
				#	self.init=True
				if self.init==None:
					self.init=False
					self._applyDecoration()
				elif self.init==False and self.app.get("summary","")+self.app.get("name","")!="":
					if self.startLoadImage==True:
						print(".")
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

	def updateScreen(self):
		if hasattr(self,"app")==False:
			return
		showBtn=self.showBtn
		if self.progress.isVisible()==True:
			self.progress.setVisible(False)
		if self.app.get("name","").strip()!="":
			if self.app.get("summary","")!="":
				text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper(),self.app.get('summary','').strip(),'')
			else:
				text="<p>{0}</p>".format(self.app.get('name','').strip())
		else:
			text="<p>{0}</p>".format(self.app.get('summary','').strip())
			showBtn=False
		if self.label.text()!=text:
			self.label.setText(text)
			self.setToolTip(text)
		if "Forbidden" in self.app.get("categories",[]) and self.btn.text()!=i18n["UNAUTHORIZED"]:
			self.btn.setText(i18n["UNAUTHORIZED"])
		elif "bundle" not in self.app.keys():
			self.btn.setText(i18n["UNAVAILABLE"])
		elif len(self.app["bundle"])==0 and self.btn.text()!=i18n["UNAVAILABLE"]:
			self.btn.setText(i18n["UNAVAILABLE"])
		else:
			if self.btn.text()!=i18n["INSTALL"]:
				self.btn.setText(i18n["INSTALL"])
			bundles=self.app["bundle"]
			states=self.app["status"]
			zmd=states.get("zomando","0")
			if len(states)>0:
				for bundle,state in states.items():
					if bundle=="package" and zmd=="1":
						if self.app["bundle"]["package"].startswith("zero"):
							continue
					if int(state)==0:# and zmdInstalled!="0":
						if self.btn.text()!=i18n["REMOVE"]:
							self.btn.setText(i18n["REMOVE"])
						self.instBundle=bundle
						break
		if int(self.app.get("state","0"))>=7:
			self.btn.setCursor(QCursor(Qt.WaitCursor))
			self.btn.setEnabled(False)
			self.progress.setVisible(True)
		self.iconUri.setVisible(True)
		self.flyIcon=""
		if self.app.get("name","").startswith("zero-"):
			self.flyIcon=QPixmap(os.path.join(RSRC,"zero-center128x128.png"))
		elif self.app.get("homepage")!=None:
			if "appsedu" in self.app["homepage"].lower():
				self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu128x128.png"))
		scaleFactor=(self.appIconSize/2)
		if isinstance(self.flyIcon,QPixmap):
			self.lblFlyIcon.setPixmap(self.flyIcon.scaled(scaleFactor,scaleFactor,Qt.KeepAspectRatioByExpanding,Qt.FastTransformation))
		if self.btn.isVisible()!=showBtn:
			self.btn.setVisible(showBtn)
	#def updateScreen

	def enterEvent(self,*args):
	   self.setFocus()
	#def enterEvent

	def loadImg(self,app):
		if app.get("icon","")=="":
			return
		img=app.get('icon','')
		icn=''
		if isinstance(img,QPixmap):
			self.load(img)
			return
		elif os.path.isfile(img):
			icn=QPixmap.fromImage(QImage(img))
			icn=icn.scaled(self.appIconSize,self.appIconSize,Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
		elif img=='':
			icn=QIcon.fromTheme(app.get('pkgname'),QIcon.fromTheme("appedu-generic"))
			img=icn.pixmap(self.appIconSize,self.appIconSize)
		if isinstance(img,str):
			if "flathub" in img:
				tmp=img.split("/")
				if "icons" in tmp:
					idx=tmp.index("icons")
					prefix=tmp[:idx-1]
					iconPath=os.path.join("/".join(prefix),"active","/".join(tmp[idx:]))
					if os.path.isfile(iconPath):
						img=iconPath
			elif os.path.exists(os.path.join(self.cacheDir,os.path.basename(img))):
				img=os.path.join(self.cacheDir,os.path.basename(img))

		scrCnt=QScreenShotContainer()
		scr=scrCnt.loadScreenShot(img,self.cacheDir)
		scr.imageReady.connect(self.load)
		scr.start()
		self.th.append(scr)
		self.scr.wait()
		#self._applyDecoration(app)
	#def loadImg

	def _getStats(self,app):
		stats={}
		for bundle,state in app.get("status",{}).items():
			if bundle=="zomando" and state==0:
				stats["zomando"]=True
			elif state==0:
				stats["installed"]=True
			
		if "Forbidden" in app.get("categories",[]):
			stats["forbidden"]=True
		#if app["name"]==app["pkgname"] and "zomando" in app.get("status",{}):
		#	if len(app.get("status",{}))==1:
		#		stats["installed"]=False
		return(stats)
	#def _getStats

	def _getStyle(self,app):
		stats=self._getStats(app)
		style={"bkgColor":"",
			"brdColor":"",
			"frgColor":""}
		lightnessMod=1
		bkgcolor=QColor(QPalette().color(QPalette.Active,QPalette.Base))
		if hasattr(QPalette,"Accent"):
			bkgAlternateColor=QColor(QPalette().color(QPalette.Active,QPalette.Accent))
		else:
			bkgAlternateColor=QColor(QPalette().color(QPalette.Active,QPalette.Highlight))
		fcolor=QColor(QPalette().color(QPalette.Active,QPalette.Text))
		if (stats.get("forbidden",False)==True) or (self.btn.text()==i18n.get("UNAVAILABLE","")):
			bkgcolor=QColor(QPalette().color(QPalette.Disabled,QPalette.Mid))
			fcolor=QColor(QPalette().color(QPalette.Disabled,QPalette.BrightText))
		elif stats.get("installed",False)==True:
			bkgcolor=bkgAlternateColor
		elif stats.get("zomando",False)==True:
			bkgcolor=bkgAlternateColor
			lightnessMod=50
		bkgcolorHls=bkgcolor.toHsl()
		bkglightness=bkgcolorHls.lightness()*(1+lightnessMod/100)
		if 255<bkglightness:
			bkglightness=bkgcolorHls.lightness()/lightnessMod
		style["bkgColor"]="{0},{1},{2}".format(bkgcolorHls.hue(),
												bkgcolorHls.saturation(),
												bkglightness)
		style["bkgBtnColor"]="{0},{1},{2}".format(bkgcolorHls.hue(),
												bkgcolorHls.saturation(),
												bkglightness-10)
		style["brdBtnColor"]="{0},{1},{2}".format(bkgcolorHls.hue(),
												bkgcolorHls.saturation(),
												bkglightness-5)
		style["brdColor"]="{0},{1},{2}".format(bkgcolor.hue(),
												bkgcolor.saturation(),
												bkgcolor.lightness()/2)
		style["frgColor"]="{0},{1},{2}".format(fcolor.red(),
												fcolor.green(),
												fcolor.blue())
		style.update(stats)
		return(style)
	#def _getStyle

	def _applyDecoration(self,app={},forbidden=False,installed=False):
		if app=={}:
			app=self.app
		style=self._getStyle(app)
		brdWidth=6
		if LAYOUT=="appsedu":
			brdWidth=1
			focusedBrdWidth=2
		self.setStyleSheet("""#rebostapp_deprecated {
			background: hsl(%s); 
			border-color: hsl(%s); 
			border-style: solid; 
			border-width: %spx; 
			border-radius: 5px;
			}
			#rebostapp_deprecated:focus:!pressed {
				border-width:%spx;
				}
			#rebostapp {
				border-color: silver;
				border-style: solid; 
				border-width: 1px; 
				border-radius: 5px;
			}
			QLabel{
				color: rgb(%s);
				color: unset;
				/*background:hsl(%s);*/
			}
			#btnInstall{
				color: rgb(%s);
				color: unset;
				background:hsl(%s);
				background:#EEEEEE;
				border:1px solid;
				border-color: hsl(%s); 
				border-color: #EEEEEE; 
				border-radius:5px;
				padding:3px;
				padding-left:12px;
				padding-right:12px;
				margin:12px;
			}
			"""%(style["bkgColor"],style["brdColor"],brdWidth,focusedBrdWidth,style["frgColor"],style["bkgColor"],style["frgColor"],style["bkgBtnColor"],style["brdBtnColor"]))
		if (style.get("forbidden",False)==True) or (self.btn.text()==i18n.get("UNAVAILABLE","")) or self.btn.cursor()==Qt.WaitCursor:
			if self.btn.text()!=i18n.get("UNAVAILABLE",""):
				self.iconUri.setEnabled(False)
			self.btn.blockSignals(True)
			self.btn.setStyleSheet("""color:#AAAAAA""")
		else:
			self.btn.setEnabled(True)
	#def _applyDecoration

	def load(self,*args):
		oldPxm=self.iconUri.pixmap()
		img=args[0]
		if oldPxm!=None:
			if oldPxm.isNull()==True:
				self.iconUri.setPixmap(img.scaled(self.appIconSize,self.appIconSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		else:
			self.iconUri.setPixmap(img.scaled(self.appIconSize,self.appIconSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
	#def load
	
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

	def setApp(self,app):
		self.app=app
		if self.autoUpdate==True:
			print(self.app["icon"])
			self.updateScreen()
	#def setApp
#class QPushButtonRebostApp
