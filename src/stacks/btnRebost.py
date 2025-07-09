#!/usr/bin/python3
from functools import partial
import os,time
import json
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QGraphicsOpacityEffect,QSizePolicy,QApplication
from PySide2.QtCore import Qt,Signal,QThread,QEvent,QSize,QPropertyAnimation
from PySide2.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor,QPainter
from QtExtraWidgets import QScreenShotContainer
import css
from constants import *
from prgBar import QProgressImage
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install"),
	"REMOVE":_("Remove"),
	"UNAUTHORIZED":_("Blocked"),
	"UNAVAILABLE":_("Unavailable"),
	}

class processData(QThread):
	processed=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self,None)
		self.data=args[0]
		self.autoUpdate=kwargs.get("autoUpdate",False)
	#def __init__

	def setData(self,data):
		self.data=data

	def run(self):
		if isinstance(self.data,str):
			app=json.loads(self.data)
		else:
			app=self.data
#		if self.autoUpdate==True:
#			self._getAppseduInfo()
		self.processed.emit(app)
		return True
	#def run
#class processData

class QPushButtonRebostApp(QPushButton):
	clicked=Signal("PyObject","PyObject")
	install=Signal("PyObject","PyObject")
	ready=Signal("PyObject")
	keypress=Signal()

	def __init__(self,strapp,appname="",parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.iconSize=kwargs.get("iconSize",96)
		self.destroyed.connect(partial(QPushButtonRebostApp._stop,self.__dict__))
		if LAYOUT=="appsedu":
			self.iconSize=self.iconSize/2
		self.margin=12
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		self.setObjectName("rebostapp")
		self.setMinimumHeight(220)
		self.setMinimumWidth(140)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAutoFillBackground(True)
		self.instBundle=""
		self.btn=QPushButton()
		self.btn.setText(i18n.get("INSTALL"))
		self.btn.setObjectName("btnInstall")
		self.btn.clicked.connect(self._emitInstall)
		self.btn.setVisible(False)
		self.lblFlyIcon=QLabel()
		self.lblFlyIcon.setObjectName("flyIcon")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.label=QLabel()
		self.label.setWordWrap(True)
		self.label.setAlignment(Qt.AlignCenter)
		self.iconUri=QLabel()
		self.iconUri.setObjectName("iconUri")
		self.setCursor(QCursor(Qt.PointingHandCursor))
		lay=QGridLayout()
		self.refererApp=None
		self.setDefault(True)
		self.setLayout(lay)
		self.init=False
		self.focusFrame=QLabel("")
		self.focusFrame.setVisible(False)
		self.focusFrame.setFixedSize(QSize(self.sizeHint().width(),int(MARGIN)/2))
		self.focusFrame.setStyleSheet("background: %s"%(COLOR_BACKGROUND_DARK))
		#Btn Layout
		self.layout().addWidget(self.iconUri,0,0,Qt.AlignCenter|Qt.AlignTop)
		self.layout().addWidget(self.lblFlyIcon,0,0,Qt.AlignRight|Qt.AlignTop)
		self.layout().addWidget(self.label,1,0,Qt.AlignCenter|Qt.AlignTop)
		self.layout().addWidget(self.btn,2,0,Qt.AlignCenter|Qt.AlignBottom)
		self.layout().addWidget(self.focusFrame,0,0,3,1,Qt.AlignCenter|Qt.AlignBottom)
		self.installEventFilter(self)
		self.scrCnt=QScreenShotContainer()
		self.th=[]
		if isinstance(strapp,str):
			self.app=json.loads(strapp)
		else:
			self.app=strapp
		#Progress indicator
		self.progress=QProgressImage(self)
		self.progress.setAttribute(Qt.WA_StyledBackground, False)
		self.progress.lblInfo.setMinimumWidth(self.rect().width()+int(MARGIN)*2)
		self.progress.lblInfo.setText("")
		pxm=QPixmap(QSize(self.focusFrame.width(),self.focusFrame.size().height()))
		pxm.fill(QColor(COLOR_BACKGROUND_DARK))
		self.progress.setPixmap(pxm)
		self.progress.setInc(3)
		self.progress.setColor(COLOR_BACKGROUND_DARK,COLOR_BORDER)
		self.layout().addWidget(self.progress,0,0,3,1,Qt.AlignBottom)
		self._renderGui()
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
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

	def _renderGui(self,*args):
		states=self.app.get("state",{})
		zmd=states.get("zomando","0")
		if len(states)>0:
			for bundle,state in states.items():
				if bundle=="package" and zmd=="1":
					if self.app["bundle"]["package"].startswith("zero"):
						continue
				if state=="0":# and zmdInstalled!="0":
					installed=True
					self.btn.setText(i18n.get("REMOVE"))
					self.instBundle=bundle
					break
		if "Forbidden" in self.app.get("categories",[]):
			self.btn.setText(i18n.get("UNAUTHORIZED"))
		elif "eduapp" in self.app.get("bundle",[]) and len(self.app.get("bundle",[]))==1:
			self.btn.setText(i18n.get("UNAVAILABLE"))
		self.flyIcon=""
		if self.app.get("name","").startswith("zero-"):
			self.flyIcon=QPixmap(os.path.join(RSRC,"zero-center128x128.png"))
		elif self.app.get("infopage")!=None:
			if "appsedu" in self.app["infopage"].lower():
				self.flyIcon=QPixmap(os.path.join(RSRC,"appsedu128x128.png"))
		scaleFactor=(self.iconSize/2)
		if isinstance(self.flyIcon,QPixmap):
			self.lblFlyIcon.setPixmap(self.flyIcon.scaled(scaleFactor,scaleFactor,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation))
		text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper().replace("L*","L·"),self.app.get('summary','').strip().replace("l*","·"))
		self.setToolTip(text)
		self.label.setText(text)
		img=self.app.get('icon','')
	#def __init__

	def _emitInstall(self,*args):
		self.btn.setEnabled(False)
		self.progress.start()
		if self.btn.text()==i18n["REMOVE"]:
			#Remove, get installed bundle
			priority=["zomando","flatpak","snap","package","appimage","eduapp"]
			for bundle in priority:
				if self.app["state"].get(bundle,"1")=="0" and self.app["bundle"].get("bundle","")!="":
					self.app["bundle"]={bundle:self.app["bundle"][bundle]}
					break
		self.install.emit(self,self.app)
	#def _emitInstall

	def eventFilter(self,*args):
		ev=args[1]
		#if isinstance(ev,QMouseEvent):
		#	self.activate()
		if isinstance(ev,QEvent):
			if ev.type()==QEvent.Type.Hide:
				if hasattr(self,"data"):
					self.data.quit()
					self.data.wait()
			if ev.type()==QEvent.Type.Paint:
				if self.init==False:
					self.updateScreen()
					self.init=True
			if ev.type()==QEvent.Type.FocusIn:
				self.focusFrame.setVisible(True)
			if ev.type()==QEvent.Type.FocusOut:
				self.focusFrame.setVisible(False)
	
		return(False)
	#def eventFilter

	def updateScreen(self):
		if hasattr(self,"app")==False:
			return
		if self.progress.isVisible()==True:
			self.progress.stop()
		text="<p>{0}<br>{1}</p>".format(self.app.get('name','').strip().upper(),self.app.get('summary','').strip(),'')
		self.setToolTip(text)
		self.label.setText(text)
		self.loadImg(self.app)
		states=self.app.get("state",{}).copy()
		if "Forbidden" in self.app.get("categories",[]):
			self.btn.setText(i18n.get("UNAUTHORIZED"))
		elif ("eduapp" in self.app.get("bundle",[]) and len(self.app.get("bundle",[]))==1) or len(self.app.get("bundle",[]))==0:
			self.btn.setText(i18n.get("UNAVAILABLE"))
		else:
			self.btn.setText(i18n.get("INSTALL"))
			states=self.app.get("state",{}).copy()
			bundles=self.app.get("bundle",{}).copy()



			zmd=states.get("zomando","0")
			if len(states)>0:
				for bundle,state in states.items():
					if bundle=="package" and zmd=="1":
						if self.app["bundle"]["package"].startswith("zero"):
							continue
					if state=="0":# and zmdInstalled!="0":
						installed=True
						self.btn.setText(i18n.get("REMOVE"))
						self.instBundle=bundle
						break
		self._applyDecoration()
		self.iconUri.setVisible(True)
		if self.app.get("summary","")!="":
			self.btn.setVisible(True)
	#def updateScreen

	def pulse(self):
		self.setStyleSheet("opacity:0")
	#def pulse

	def enterEvent(self,*args):
	   self.setFocus()
	#def enterEvent

	def loadImg(self,app):
		if app.get("name","")=="":
			return
		img=app.get('icon','')
		icn=''
		if isinstance(img,QPixmap):
			self.load(img)
			return
		elif os.path.isfile(img):
			icn=QPixmap.fromImage(QImage(img))
			icn=icn.scaled(self.iconSize,self.iconSize,Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
		elif img=='':
			icn=QIcon.fromTheme(app.get('pkgname'),QIcon.fromTheme("appedu-generic"))
			img=icn.pixmap(self.iconSize,self.iconSize)
		if isinstance(img,str):
			if "flathub" in img:
				tmp=img.split("/")
				if "icons" in tmp:
					idx=tmp.index("icons")
					prefix=tmp[:idx-1]
					iconPath=os.path.join("/".join(prefix),"active","/".join(tmp[idx:]))
					if os.path.isfile(iconPath):
						img=iconPath
			#			icn=QPixmap.fromImage(iconPath)
			#			icn=icn.scaled(self.iconSize,self.iconSize,Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
			elif os.path.exists(os.path.join(self.cacheDir,os.path.basename(img))):
				img=os.path.join(self.cacheDir,os.path.basename(img))
		#if icn:
		#	wsize=self.iconSize
		#	if "/usr/share/banners/lliurex-neu" in img or os.path.basename(img).startswith("zero-lliurex-"):
		#		wsize*=2
		#	#self.iconUri.setPixmap(icn.scaled(wsize,self.iconSize,Qt.IgnoreAspectRatio,Qt.SmoothTransformation))
		#elif img.startswith('http'):
		scr=self.scrCnt.loadScreenShot(img,self.cacheDir)
		scr.imageReady.connect(self.load)
		scr.start()
		self.th.append(scr)
		#self.scr.wait()
		#self._applyDecoration(app)
	#def loadImg

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
	#def _stop

	def _getStats(self,app):
		stats={}
		for bundle,state in app.get("state",{}).items():
			if bundle=="zomando" and state=="0":
				stats["zomando"]=True
			elif state=="0":
				stats["installed"]=True
			
		if "Forbidden" in app.get("categories",[]):
			stats["forbidden"]=True
		if app["name"]==app["pkgname"] and "zomando" in app.get("state",{}):
			if len(app.get("state",{}))==1:
				stats["installed"]=False
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
		self.btn.setEnabled(True)
		if (style.get("forbidden",False)==True) or (self.btn.text()==i18n.get("UNAVAILABLE","")):
			if self.btn.text()!=i18n.get("UNAVAILABLE",""):
				self.iconUri.setEnabled(False)
			self.btn.setEnabled(False)
			self.btn.setStyleSheet("""color:#AAAAAA""")
	#def _applyDecoration

	def _removeDecoration(self):
		self.setObjectName("")
		self.setStyleSheet("")
	#def _removeDecoration
	
	def load(self,*args):
		oldPxm=self.iconUri.pixmap()
		img=args[0]
		if oldPxm!=None:
			if oldPxm.isNull()==True:
				self.iconUri.setPixmap(img.scaled(self.iconSize,self.iconSize))
		else:
			self.iconUri.setPixmap(img.scaled(self.iconSize,self.iconSize))
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
	#def setApp
#class QPushButtonRebostApp
