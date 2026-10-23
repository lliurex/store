#!/usr/bin/python3
import os,subprocess,time
from PySide2.QtWidgets import QLabel, QPushButton,QMenu,QWidget,QWidgetAction,QSizePolicy,QApplication,QGridLayout
from PySide2.QtCore import Qt,Signal,QSize,QPoint
from PySide2.QtGui import QIcon,QPixmap
from QtExtraWidgets import QPushInfoButton
from lib.helperLib import appHelper
import extras.css as css
from extras.constants import *
from extras.i18n import *

class QPushButtonInstaller(QPushButton):
	installerClicked=Signal(str)
	def __init__(self,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.dbg=True
		self.setCursor(Qt.PointingHandCursor)
		self.setStyleSheet(css.btnRebost())
		self.setObjectName("btnInstaller")
		self.helper=appHelper()
		self.app=kwargs.get("app",{})
		self.dlgInstallers=QWidget()
		self.menuLayout=QGridLayout()
		self.menuLayout.setSpacing(MARGIN/2)
		self.dlgInstallers.setLayout(self.menuLayout)
		self.dlgInstallers.setWhatsThis("https://lliurex.net")
		self.menuInstaller=QMenu()
		self.setMenu(self.menuInstaller)
		act=QWidgetAction(self.menuInstaller)
		act.createWidget(self.dlgInstallers)
		act.setDefaultWidget(self.dlgInstallers)
		self.menuInstaller.addAction(act)
		self.menuInstaller.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
		self.menuInstaller.aboutToShow.connect(self._setActionForMenu)
		self.setProperty("clicked",False)
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("btnInstallers: {}".format(msg))
	#def _debug(self,msg):

	def setApp(self,app):
		self.app=app
		bundlesSorted=self.helper.getBundlesByPriority(self.app)
		self._loadLaunchers(bundlesSorted)
	#def setApp

	def _emitInstall(self,*args):
		if len(args[0])==0:
			return
		if args[0]!=None:
			args[0].setCursor(Qt.WaitCursor)
		else:
			self.setCursor(Qt.WaitCursor)
		bundle=args[1]["name"].split("<br>")[-1]
		if self.instBundle!="":
			bundle=self.instBundle
		self.installerClicked.emit(bundle)
		if args[0]!=None:
			args[0].setCursor(Qt.PointingHandCursor)
		else:
			self.setCursor(Qt.PointingHandCursor)
	#def _emitInstall(self,*args):

	def _openWiki(self):
		proc=["xdg-open","https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Gesti%C3%B3n+de+software+en+LliureX&highlight=snap#Diferents_formats_una_breu_explicaci_"]
		subprocess.run(proc)
	#def _openWiki

	def _resizeMenu(self,*args):
		self.menuInstaller.setFixedWidth((len(self.dlgInstallers.children()))*(ICON_SIZE+MARGIN*2))
		what=QPushButton()
		what.setIcon(QIcon.fromTheme("system-help"))
		what.setIconSize(QSize(16,16))
		what.setFixedSize(QSize(24,24))
		what.setStyleSheet("""padding:0px;margin:0px;border:0px;color:black""")
		what.clicked.connect(self._openWiki)
		what.setToolTip(i18n["BTN_HELP"])
		what.setCursor(Qt.WhatsThisCursor)
		self.menuLayout.addWidget(what,0,self.menuLayout.columnCount(),1,1,Qt.AlignLeft)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount()-1,1)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount(),0)
	#def _resizeMenu(self,*args):

	def _setActionForMenu(self,*args):
		self._resizeMenu()
		for chld in self.dlgInstallers.children():
			if isinstance(chld,QPushInfoButton) or isinstance(chld,QPushButton):
				if hasattr(chld,"app"):
					release,bundle=chld.app["name"].split("<br>")
					text="<p>Kind: {0}<br>Release: {1}</p>".format(bundle.capitalize(),release)
					chld.setToolTip(text)
	#def _setActionForMenu

	def mousePressEvent(self,*args,**kwargs):
		if self.app.get("webapp",False)==True:
			self.app["bundle"].update({"webapp":self.app["homepage"]})
		bundlesSorted=self.helper.getBundlesByPriority(self.app)
		if len(bundlesSorted)==0:
			return
		self.style().unpolish(self)
		self.setProperty("clicked",True)
		self.style().polish(self)
		QApplication.processEvents()
		if args[0].x()>(self.rect().width()-48) and self.instBundle=="":
			self._loadLaunchers(bundlesSorted)
			self.showMenu()
		else:
			bundle=bundlesSorted[list(bundlesSorted.keys())[0]].split(" ")[0]
			if bundle=="unknown":
				bundle="epi"
			self._emitInstall(None,{"name":"{}<br>{}".format(self.app["id"],bundle)})
	#def mousePressEvent

	def _btnInstaller(self,bundle,release):
		wdg=QPushInfoButton(overlay=False,scroll=False)
		wdg.defaultSize=72
		wdg.loadImgSync(os.path.join(RSRC,"application-vnd.{}.png".format(bundle)))
		wdg.lblDesc.setText("<strong>{}</strong>".format(bundle.capitalize()))
		wdg.lblDesc.setAttribute(Qt.WA_StyledBackground, True)
		clrBkg="#002c4f00"
		clrBkg="0,44,79,0.8"
		wdg.lblDesc.setStyleSheet("""border-radius:5px;padding:1px;background:rgba(%s);color:white;border:1px solid %s;"""%(clrBkg,COLOR_BORDER))
		wdg.lblDesc.setFixedWidth(ICON_SIZE)
		wdg.lblDesc.setAlignment(Qt.AlignCenter)
		release=release[0:min(10,len(release))]
		wdg.setToolTip(release)
		wdg.clicked.connect(self._emitInstall)
		wdg.setMaximumWidth(ICON_SIZE/3)
		wdg.layout().setContentsMargins(6,0,6,3)
		return(wdg)
	#def _btnInstaller(self,bundle):

	def _populateInstallers(self,bundlesSorted):
		cont=0
		epi=False
		align=Qt.AlignCenter|Qt.AlignBottom
		for idx,bundleData in bundlesSorted.items():
			try:
				bundleData=bundleData.strip()
				if " " not in bundleData:
					bundleData+=" contrib"
				bundle,release=bundleData.split()
			except Exception as e:
				self._debug("ERROR!!!!")
				self._debug(e)
				self._debug("DUMP")
				self._debug(bundleData)
				self._debug("--- END ---")
			if bundle=="unknown":
				bundle="epi"
			wdg=self._btnInstaller(bundle,release)
			wdg.layout().addWidget(wdg.lblDesc,0,0,1,2,align)
			self.menuLayout.addWidget(wdg,0,self.menuLayout.columnCount(),2,1)
			if bundle=="epi": #epi at idx[0] so don't process more
				break
			cont+=1
	#def _populateInstallers

	def _setAppForbidden(self):
		self.setText(i18n["BTN_UNAUTHORIZED"])
		self.setMenu(None)
		self.setEnabled(False)
	#def _setAppForbidden

	def _setAppAssisted(self):
		self.setEnabled(False)
		self.setText(i18n["BTN_ASSISTED"])
	#def _setAppAssisted

	def _setAppWebApp(self):
		self.instBundle=""
		self.setEnabled(True)
		self.setText(i18n["BTN_WEBAPP"])
	#def _setAppWebApp

	def _setAppPending(self):
		self.setText(i18n["BTN_UNAVAILABLE"])
		self.setMenu(None)
		self.setEnabled(False)
	#def _setAppPending

	def _setAppAvailable(self):
		self.setVisible(True)
		self.setEnabled(True)
		self.setText(i18n["BTN_INSTALL"])
		self.instBundle=""
	#def _setAppAvailable

	def _setAppInstalled(self):
		self.setText(i18n.get("BTN_REMOVE"))
		action="remove"
	#def _setAppInstalled

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

	def _loadLaunchers(self,bundlesSorted):
		self._debug("Loading launchers")
		for chld in self.dlgInstallers.children():
			if isinstance(chld,QPushInfoButton) or isinstance(chld,QPushButton):
				chld.setParent(None)
		self._getAppStatus()
		if self.isEnabled()==True:
			self._populateInstallers(bundlesSorted)
	#def _loadLaunchers
