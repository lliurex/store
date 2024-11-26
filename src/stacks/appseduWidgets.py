#!/usr/bin/python3
import os
import json
from PySide6.QtWidgets import QLabel, QPushButton,QHBoxLayout,QGridLayout,QWidget
from PySide6.QtCore import Qt,Signal,QThread,QSize
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
from QtExtraWidgets import QScrollLabel
from appsedu import appsedu
import urllib

DBG=True
ICON_SIZE=128

class getAppInfo(QThread):
	getInfo=Signal("PyObject")
	def __init__(self,parent=None,**kwargs):
		QThread.__init__(self, None)
		self.app=kwargs["app"]
		self.appsedu=appsedu.manager(cache=True)
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
				os.unlink(iconPath)
		if os.path.isfile(iconPath)==False and appInfo.get("icon","").startswith("http"):
			urllib.request.urlretrieve(appInfo["icon"],iconPath)
	#def downloadIcon
#class getInfo

class QPushButtonAppsedu(QPushButton):
	clicked=Signal("PyObject","PyObject")
	install=Signal("PyObject","PyObject")
	dataChanged=Signal("PyObject")
	keypress=Signal()
	def __init__(self,appedu,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.app=appedu
		self.iconSize=kwargs.get("iconSize",128)
		self.iconSize=self.iconSize/2
		self.margin=12
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","appsedu","imgs")
		self.btnInstall=QPushButton()
		self.btnInstall.setIcon(QIcon.fromTheme("download"))
		self.btnInstall.clicked.connect(self._emitInstall)
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.setObjectName("appedu")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAutoFillBackground(True)
		self.setToolTip("<p>{0}</p>".format(self.app.get('summary',self.app.get('app'))))
		text="<strong>{0}</strong><p>{1}</p>".format(self.app.get('app',''),self.app.get('summary',""))
		self.label=QLabel(text)
		self.label.setWordWrap(True)
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
		if pxm.isNull()==False:
			#Mark as done if img
			self.init=True
			self.iconUri.setPixmap(pxm)
		if "Forbidden" in self.app.get("categories",[]):
			self._applyDecoration(forbidden=True)
		elif "Preinstalled" in self.app.get("categories",[]):
			self._applyDecoration(installed=True)
		else:
			self._applyDecoration()
		self.dataChanged.emit(self)
	#def updateScreen

	def enterEvent(self,*args):
		self.setFocus()
	#def enterEvent

	def loadInfo(self):
		if self.init==False:
			self.info.start()
	#def loadInfo(self):

	def loadImg(self,app):
		self._applyDecoration(app)
	#def loadImg

	def _getStats(self,app):
		stats={}
		if "Forbidden" in app.get("categories",[]):
			stats["forbidden"]=True
		if "Preinstalled" in app.get("categories",[]):
			stats["installed"]=True
		if "Zomando" in app.get("categories",[]):
			stats["zomando"]=True
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
			self.btnInstall.setVisible(False)
		elif stats.get("installed",False)==True:
			bkgcolor=bkgAlternateColor
			self.btnInstall.setVisible(False)
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
		brdWidth=1
		self.setStyleSheet("""#appedu {
			background-color: hsl(%s); 
			border-color: hsl(%s); 
			border-style: solid; 
			border-width: 1px; 
			border-radius: 5px;
			}
			#appedu:focus:!pressed {
				border-width:%spx;
				}
			QLabel{
				color: rgb(%s);
			}
			"""%(style["bkgColor"],style["brdColor"],brdWidth,style["frgColor"]))
		if style.get("forbidden",False)==True:
			self.iconUri.setEnabled(False)
			self.btnInstall.setEnabled(False)
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
	
	def _emitInstall(self,*args):
		self.install.emit(self,self.app)
	#def _emitInstall

	def setApp(self,app):
		self.app=app
	#def setApp
#class QPushButtonAppsEdu

class QFormAppsedu(QWidget):
	linkActivated=Signal("PyObject")
	clicked=Signal()
	install=Signal("PyObject")
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		lay=QGridLayout()
		self.detailIcon=QLabel()
		self.detailTitle=QLabel()
		self.detailTitle.setWordWrap(True)
		self.detailInstall=QPushButton()
		self.detailInstall.setIcon(QIcon.fromTheme("download"))
		self.detailInstall.clicked.connect(self._emitInstall)
		self.detailRemove=QPushButton()
		self.detailRemove.setIcon(QIcon.fromTheme("edit-delete"))
		self.detailRemove.clicked.connect(self._emitInstall)
		self.detailOpen=QPushButton()
		self.detailOpen.setIcon(QIcon.fromTheme("document-open"))
		self.detailExit=QPushButton("")
		self.detailExit.setIcon(QIcon.fromTheme("window-close"))
		self.detailExit.setIconSize(QSize(24,24))
		self.detailExit.clicked.connect(self._emitClicked)
		self.detailTags=QLabel()
		self.detailTags.linkActivated.connect(self._emitLinkActivated)
		self.detailTags.setWordWrap(True)
		self.detailDescription=QScrollLabel()
		self.detailDescription.linkActivated.connect(self._emitLinkActivated)
		self.detailDescription.setWordWrap(True)
		self.title=""
		wdg=QWidget()
		hlay=QHBoxLayout()
		wdg.setLayout(hlay)
		hlay.addWidget(self.detailInstall)
		hlay.addWidget(self.detailRemove)
		hlay.addWidget(self.detailOpen)
		lay.addWidget(self.detailIcon,0,0,2,1,Qt.AlignTop)
		lay.addWidget(self.detailTitle,0,1,1,1,Qt.AlignTop|Qt.AlignLeft)
		lay.addWidget(self.detailExit,0,2,1,1,Qt.AlignTop|Qt.AlignRight)
		lay.addWidget(wdg,4,2,1,1,Qt.AlignRight)
		lay.addWidget(self.detailTags,3,0,1,1)
		#lay.addWidget(self.detailSummary,1,0,1,2,Qt.AlignTop)
		lay.addWidget(self.detailDescription,2,0,1,3)
		self.setLayout(lay)
		self.setVisible(False)
	#def __init__

	def updateData(self,app):
		self.setTitle(app["app"])
		self.setDescription(app["description"],app["url"])
		self.setIcon(app["icon"])

	def title(self):
		return(self.title)
	#def title

	def setTitle(self,title):
		self.detailTitle.setText("<h1>{}</h1>".format(title))
		self.title=title
	#def setTitle

	def description(self):
		return(self.detailDescription.text())
	#def description

	def setDescription(self,description,url=""):
		self.detailDescription.setText("<p>{0}</p><p><a href=\"{1}\">{1}</a></p>".format(description,url))
	#def setDescription

	def icon(self):
		return(self.detailIcon,pixmap())
	#def icon(self)

	def setIcon(self,icon):
		pxm=None
		if isinstance(icon,QPixmap):
			pxm=icon
		elif os.path.isfile(icon):
			pxm=QPixmap(icon)
		if pxm:
			self.detailIcon.setPixmap(pxm.scaled(ICON_SIZE,ICON_SIZE))
	#def setIcon

	def setTags(self,taglist):
		tags=""
		for cat in taglist:
			tags+="<a href=\"#{0}\"><strong>{0}</strong></a> ".format(cat)
		self.detailTags.setText("{}".format(tags.strip()))
	#def setTags

	def lock(self):
		self.setEnabled(False)
		self.detailTags.setEnabled(False)
		self.detailDescription.setEnabled(False)
		self.detailExit.setEnabled(False)
	#def lock

	def unlock(self):
		self.setEnabled(True)
		self.detailTags.setEnabled(True)
		self.detailDescription.setEnabled(True)
		self.detailExit.setEnabled(True)
	#def unlock

	def setEnabled(self,state):
		self.detailIcon.setEnabled(state)
		self.detailTitle.setEnabled(state)
		self.setManageEnabled(state)
	#def setEnabled

	def setManageEnabled(self,state):
		self.detailInstall.setEnabled(state)
		self.detailRemove.setEnabled(state)
		self.detailOpen.setEnabled(state)
	#def setManageEnabled
	
	def _emitClicked(self):
		self.clicked.emit()
	#def _emitClicked

	def _emitLinkActivated(self,*args):
		url=args[0]
		if isinstance(url,tuple):
			url=url[0]
		self.linkActivated.emit(url)
	#def _emitLinkActivated

	def _emitInstall(self,*args):
		self.install.emit(self.title)
	#def _emitLinkActivated
