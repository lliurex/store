#!/usr/bin/python3
import os,subprocess,time
from PySide2.QtWidgets import QLabel, QPushButton,QMenu,QWidget,QWidgetAction,QSizePolicy,QApplication,QGridLayout
from PySide2.QtCore import Qt,Signal,QSize,QPoint
from PySide2.QtGui import QIcon,QPixmap
from btnRebost import QPushButtonRebostApp
import libhelper
import css
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={
	"ASSISTED":_("Assisted"),
	"HELP":_("What's this?"),
	"INSTALL":_("Install"),
	"OPEN":_("Z-Install"),
	"REMOVE":_("Remove"),
	"UNAUTHORIZED":_("Blocked"),
	"UNAVAILABLE":_("Unavailable"),
	"WEBAPP":_("Web app")
	}

class QPushButtonInstaller(QPushButton):
	installerClicked=Signal(str)
	def __init__(self,parent=None,**kwargs):
		QPushButton.__init__(self, parent)
		self.dbg=True
		self.setCursor(Qt.PointingHandCursor)
		self.setStyleSheet(css.btnRebost())
		self.setObjectName("btnInstaller")
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
		if args[0]!=None:
			args[0].setCursor(Qt.WaitCursor)
		else:
			self.setCursor(Qt.WaitCursor)
		bundle=args[1]["name"].split("<br>")[-1]
		if self.instBundle!="":
			bundle=self.instBundle
		self.installerClicked.emit(bundle)
		time.sleep(2)
		if args[0]!=None:
			args[0].setCursor(Qt.PointingHandCursor)
		else:
			self.setCursor(Qt.PointingHandCursor)
	#def _emitInstall(self,*args):

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
		what.setStyleSheet("""padding:0px;margin:0px;border:0px;color:black""")
		what.clicked.connect(self._openWiki)
		what.setToolTip(i18n["HELP"])
		what.setCursor(Qt.WhatsThisCursor)
		self.menuLayout.addWidget(what,0,self.menuLayout.columnCount(),1,1,Qt.AlignLeft)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount()-1,1)
		self.menuLayout.setColumnStretch(self.menuLayout.columnCount(),0)
	#def _resizeMenu(self,*args):

	def _setActionForMenu(self,*args):
		self._resizeMenu()
		for chld in self.dlgInstallers.children():
			if isinstance(chld,QPushButtonRebostApp) or isinstance(chld,QPushButton):
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
		if args[0].x()>(self.rect().width()-48):
			self._loadLaunchers(bundlesSorted)
			self.showMenu()
		else:
			bundle=bundlesSorted[list(bundlesSorted.keys())[0]].split(" ")[0]
			if bundle=="unknown":
				bundle="epi"
			self._emitInstall(None,{"name":"{}<br>{}".format(self.app["id"],bundle)})
	#def mousePressEvent

	def _populateInstallers(self,bundlesSorted):
		cont=0
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
			#if self.app.get("status",{}).get(bundle,1)!=1:
			#	continue
			#release=self.app.get("versions",{}).get(bundle,"lliurex").split(":")[-1].split("+")[0]
			release=release[0:min(10,len(release))]
			wdg=QPushButtonRebostApp({"name":"{}<br>{}".format(release,bundle.capitalize()),"icon":os.path.join(RSRC,"application-vnd.{}.png".format(bundle))},iconSize=64)
			wdg.lockTooltip=True
			wdg.label.setWordWrap(True)
			wdg.clicked.connect(self._emitInstall)
			wdg.setCompactMode(True)
			wdg.setMaximumWidth(ICON_SIZE/3)
			if cont==0:
				wdg.flyIcon=QPixmap(os.path.join(RSRC,"emblem-favorite32x32.png"))
				wdg.lblFlyIcon.setPixmap(wdg.flyIcon.scaled(16,16,Qt.KeepAspectRatioByExpanding,Qt.FastTransformation))
				wdg.lblFlyIcon.show()
			self.menuLayout.addWidget(wdg,0,self.menuLayout.columnCount(),2,1)
			cont+=1
	#def _populateInstallers

	def _setActionForButton(self):
		self.setText(i18n["INSTALL"])
		self.setMenu(self.menuInstaller)
		if len(self.app.get("bundle",{}))==0 and self.app.get("forbidden",False)==True:
			self.setText(i18n["UNAUTHORIZED"])
			self.setMenu(None)
			self.setEnabled(False)
		else:
			if self.app.get("assisted",False)==True:
				self.setEnabled(False)
				self.setText(i18n["ASSISTED"])
			elif self.app.get("webapp",False)==True:
				self.setEnabled(True)
				self.setText(i18n["WEBAPP"])
			elif len(self.app.get("bundle",{}))==0 or self.app.get("unavailable",False)==True:
				self.setText(i18n["UNAVAILABLE"])
				self.setMenu(None)
				self.setEnabled(False)
			elif self.app.get("forbidden",False)==True:
				self.setText(i18n["UNAUTHORIZED"])
				self.setMenu(None)
				self.setEnabled(False)
			else: #app seems authorized and available
				self.setEnabled(True)
				bundles=self.app["bundle"]
				status=self.app["status"]
				zmd=bundles.get("unknown","")
				action="install"
				if zmd==self.app["name"]==self.app["pkgname"]:
					action="open"
				else:
					for bundle,appstatus in status.items():
						if int(appstatus)==0:# and zmdInstalled!="0":
							self.instBundle=bundle
							action="remove"
							break
				if action=="install":
					self.setVisible(True)
					self.setEnabled(True)
					self.setText(i18n["INSTALL"])
					self.instBundle=""
				elif action=="open":
					self.setVisible(True)
					self.setEnabled(True)
					self.setText(i18n["OPEN"])
					self.instBundle="unknown"
				else:
					self.setMenu(None)
					self.setText(i18n["REMOVE"])
	#def _setActionForButton

	def _loadLaunchers(self,bundlesSorted):
		self._debug("Loading launchers")
		for chld in self.dlgInstallers.children():
			if isinstance(chld,QPushButtonRebostApp) or isinstance(chld,QPushButton):
				chld.setParent(None)
		self._setActionForButton()
		if self.isEnabled()==True:
			self._populateInstallers(bundlesSorted)
	#def _loadLaunchers

