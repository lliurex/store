#!/usr/bin/python3
import os,subprocess
from PySide2.QtWidgets import QLabel, QPushButton,QMenu,QWidget,QWidgetAction,QSizePolicy,QApplication,QGridLayout
from PySide2.QtCore import Qt,Signal,QSize,QPoint
from PySide2.QtGui import QIcon
from btnRebost import QPushButtonRebostApp
import libhelper
import css
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install"),
		"HELP":_("What's this?")}

class QPushButtonInstaller(QPushButton):
	installerClicked=Signal(str)
	def __init__(self,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.dbg=True
		self.setStyleSheet(css.btnRebost())
		self.setObjectName("btnInstall")
		self.helper=libhelper.helper()
		self.app=kwargs.get("app",{})
		self.dlgInstallers=QWidget()
		self.menuLayout=QGridLayout()
		self.menuLayout.setSpacing(int(MARGIN)/2)
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
		bundle=args[1]["name"].split("<br>")[-1]
		self.installerClicked.emit(bundle)
	#def _emitInstall

	def _openWiki(self):
		proc=["kde-open5","https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Gesti%C3%B3n+de+software+en+LliureX&highlight=snap#Diferents_formats_una_breu_explicaci_"]
		subprocess.run(proc)
	#def _openWiki

	def _resizeMenu(self,*args):
		self.menuInstaller.setFixedWidth((len(self.dlgInstallers.children()))*(ICON_SIZE+int(MARGIN)*2))
		what=QPushButton()
		what.setIcon(QIcon.fromTheme("system-help"))
		what.setIconSize(QSize(16,16))
		what.setFixedSize(QSize(24,24))
		what.setStyleSheet("""padding:0px;margin:0px;border:0px,color:black""")
		what.clicked.connect(self._openWiki)
		what.setToolTip(i18n["HELP"])
		self.menuLayout.addWidget(what,0,self.menuLayout.columnCount(),1,1,Qt.AlignLeft)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount()-1,1)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount(),0)
	#def _resizeMenu(self,*args):

	def _setActionForMenu(self,*args):
		self._resizeMenu()
	#def _setActionForMenu

	def mousePressEvent(self,*args,**kwargs):
		bundlesSorted=self.helper.getBundlesByPriority(self.app)
		self._loadLaunchers(bundlesSorted)
		if len(self.app.get("bundle",[]))>1:
			if self.app.get("bundle",{}).get("package","")==self.app.get("bundle",{}).get("unknown","unknown"):
				bundle=bundlesSorted[list(bundlesSorted.keys())[0]].split(" ")[0]
				self._emitInstall(None,{"name":"{}<br>{}".format(self.app["id"],bundle)})
			else:
				self.showMenu()
		else:
			bundle=bundlesSorted[list(bundlesSorted.keys())[0]].split(" ")[0]
			if bundle=="unknown":
				bundle="epi"
			self._emitInstall(None,{"name":"{}<br>{}".format(self.app["id"],bundle)})
	#def mousePressEvent

	def _loadLaunchers(self,bundlesSorted):
		self._debug("Loading launchers")
		for chld in self.dlgInstallers.children():
			if isinstance(chld,QPushButtonRebostApp) or isinstance(chld,QPushButton):
				chld.setParent(None)
		cont=0
		for idx,bundleData in bundlesSorted.items():
			bundle,release=bundleData.split()
			if bundle=="unknown":
				bundle="epi"
			if self.app.get("status",{}).get(bundle,1)!=1:
				continue
			cont+=1
			#release=self.app.get("versions",{}).get(bundle,"lliurex").split(":")[-1].split("+")[0]
			release=release[0:min(10,len(release))]
			wdg=QPushButtonRebostApp({"name":"{}<br>{}".format(release,bundle.capitalize()),"icon":os.path.join(RSRC,"application-vnd.{}.png".format(bundle))},iconSize=64)
			wdg.label.setWordWrap(True)
			wdg.clicked.connect(self._emitInstall)
			wdg.setCompactMode(True)
			wdg.setMaximumWidth(ICON_SIZE/3)
			self.menuLayout.addWidget(wdg,0,self.menuLayout.columnCount(),2,1)
	#def _loadLaunchers

