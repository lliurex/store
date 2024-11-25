#!/usr/bin/python3
import os
import json
from PySide6.QtWidgets import QLabel, QPushButton,QHBoxLayout
from PySide6.QtCore import Qt,Signal,QThread,QSize
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
from appsedu import manager
import urllib

DBG=True

class getAppInfo(QThread):
	getInfo=Signal("PyObject")
	def __init__(self,parent=None,**kwargs):
		QThread.__init__(self, None)
		self.app=kwargs["app"]
		self.appsedu=manager(cache=True)
		self.cache=os.path.join(os.environ.get("HOME"),".cache","appsedu","imgs")
		if os.path.exists(self.cache)==False:
			os.makedirs(self.cache)
	#def __init__
		
	def _debug(self,msg):
		if DBG==True:
			print("getInfo: {}".format(msg))
	#def _debug

	def run(self):
		#self._debug("Getting info for {}".format(self.app))
		appInfo=self.appsedu.getApplication(self.app["url"])
		iconPath="_".join(appInfo.get("icon","/ / / /").split("/")[-3:])
		self.downloadIcon(appInfo)
		appInfo["icon"]=os.path.join(self.cache,iconPath)
		self.getInfo.emit(appInfo)
	#def run
	
	def downloadIcon(self,appInfo):
		iconPath="_".join(appInfo.get("icon","/ / / /").split("/")[-3:])
		iconPath=os.path.join(self.cache,iconPath)
		if os.path.isfile(iconPath)==True:
			pxm=QPixmap(iconPath)
			if pxm.isNull()==True:
				print("REMOVE: {}".format(iconPath))
				os.unlink(iconPath)
		if os.path.isfile(iconPath)==False and appInfo.get("icon","").startswith("http"):
			urllib.request.urlretrieve(appInfo["icon"],iconPath)
			

#class getInfo

class QPushButtonAppsedu(QPushButton):
	clicked=Signal("PyObject","PyObject")
	def __init__(self,appedu,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.app=appedu
		self.iconSize=kwargs.get("iconSize",128)
		self.iconSize=self.iconSize/2
		self.margin=12
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","appsedu","imgs")
		self.btnInstall=QPushButton()
		self.btnInstall.setIcon(QIcon.fromTheme("download"))
		if os.path.exists(self.cacheDir)==False:
			print("GENERATING CACHE {}".format(self.cacheDir))
			os.makedirs(self.cacheDir)
		self.setObjectName("rebostapp")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAutoFillBackground(True)
		self.setToolTip("<p>{0}</p>".format(self.app.get('summary',self.app.get('app'))))
		text="<strong>{0}</strong><p>{1}</p>".format(self.app.get('app',''),self.app.get('summary',""))
		self.label=QLabel(text)
		self.label.setWordWrap(True)
		img=self.app.get('icon','')
		self.iconUri=QLabel()
		self.iconUri.setStyleSheet("""QLabel{margin-left: %spx;margin-right:%spx}"""%(self.margin,self.margin))
		self.setCursor(QCursor(Qt.PointingHandCursor))
		lay=QHBoxLayout()
		lay.addWidget(self.iconUri,0)
		lay.addWidget(self.label,1)
		lay.addWidget(self.btnInstall)
		self.refererApp=None
		self.setDefault(True)
		self.setMinimumHeight(self.iconSize)
		self.setLayout(lay)
		self.init=False
		self.info=getAppInfo(app=self.app)
		self.info.getInfo.connect(self.updateScreen)
		self.destroyed.connect(lambda x:QPushButtonAppsedu._on_destroyed(self.info))

		#self.installEventFilter(self)
	#def __init__

	@staticmethod
	def _on_destroyed(th):
		try:
			if isinstance(th,QThread):
				th.terminate()
				th.wait()
		except:
			pass
	#def _on_destroyed

	def updateScreen(self,*args):
		if len(args)>0 and isinstance(args[0],dict):
			self.app.update(args[0])
		self.setToolTip("<p>{0}</p>".format(self.app.get('summary',self.app.get('app'))))
		text="<strong>{0}</strong><p>{1}</p>".format(self.app.get('app',''),self.app.get('summary'),'')
		self.label.setText(text)
		pxm=QPixmap(self.app.get("icon")).scaled(QSize(self.iconSize,self.iconSize),Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.SmoothTransformation)
		if pxm.isNull()==True:
			print("NULL IMAGE: {}\n----".format(self.app))
		else:
			self.init=True
			self.iconUri.setPixmap(pxm)
	#def updateScreen

	def enterEvent(self,*args):
		self.setFocus()
	#def enterEvent

	def loadInfo(self):
		if self.init==False:
			self.info.start()

	def loadImg(self,app):
		self._applyDecoration(app)
	#def loadImg

	def _getStats(self,app):
		stats={}
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
		if stats.get("forbidden",False)==True:
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
		self.setStyleSheet("""#rebostapp {
			background-color: hsl(%s); 
			border-color: hsl(%s); 
			border-style: solid; 
			border-width: 1px; 
			border-radius: 5px;
			}
			#rebostapp:focus:!pressed {
				border-width:%spx;
				}
			QLabel{
				color: rgb(%s);
			}
			"""%(style["bkgColor"],style["brdColor"],brdWidth,style["frgColor"]))
		if style.get("forbidden",False)==True:
			self.iconUri.setEnabled(False)
			self.btn.setEnabled(False)
	#def _applyDecoration

	def _removeDecoration(self):
		self.setObjectName("")
		self.setStyleSheet("")
	#def _removeDecoration
	
	def load(self,*args):
		img=args[0]
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
#class QPushButtonRebostApp
