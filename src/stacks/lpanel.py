#!/usr/bin/python3
import sys,signal
import os
from functools import partial
import subprocess
import json
import html
from rebost import store
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy,QWidget,QComboBox,QHBoxLayout,QListWidget,\
							QVBoxLayout,QListWidgetItem,QGraphicsBlurEffect,QGraphicsOpacityEffect,\
							QAbstractScrollArea, QFrame
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation
from QtExtraWidgets import QScreenShotContainer,QScrollLabel
import gettext
import libhelper
import exehelper
import css
from cmbBtn import QComboButton
from lblApp import QLabelRebostApp
from lblLnk import QLabelLink
from constants import *
_ = gettext.gettext
QString=type("")
BKG_COLOR_INSTALLED=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Inactive,QtGui.QPalette.Highlight))

i18n={
	"APPUNKNOWN":_("The app could not be loaded. Until included in LliureX catalogue it can't be installed"),
	"APPUNKNOWN_SAI":_("For any question the SAI can be contacted at <a href='https://portal.edu.gva.es/sai/es/inicio/'>https://portal.edu.gva.es/sai/es/inicio/</a>"),
	"CHOOSE":_("Choose"),
	"CONFIG":_("Details"),
	"DESC":_("Navigate through all applications"),
	"ERRNOTFOUND":_("Could not open"),
	"ERRLAUNCH":_("Error opening"),
	"ERRSYSTEMAPP":_("System apps can't be removed"),
	"ERRUNKNOWN":_("Unknown error"),
	"FORBIDDEN":_("App unauthorized"),
	"FORMAT":_("Format"),
	"HOMEPAGE":_("Info"),
	"INFO":_("For more info go to"),
	"INSTALL":_("Install"),
	"MENU":_("Show application detail"),
	"OPENING":_("Opening"),
	"RELEASE":_("Release"),
	"REMOVE":_("Remove"),
	"RUN":_("Open"),
	"SEEIT":_("See at Appsedu"),
	"SITE":_("Website"),
	"TOOLTIP":_("Details"),
	"UNAVAILABLE":_("Unavailable"),
	"UPGRADE":_("Upgrade"),
	"ZMDNOTFOUND":_("Zommand not found. Open Zero-Center?"),
	}

class thShowApp(QThread):
	showEnded=Signal("PyObject")
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.rc=store.client()
		self.app={}
	#def __init__

	def setArgs(self,*args):
		if isinstance(args[0],str):
			self.app={}
			self.app["name"]=args[0]
		else:
			self.app=args[0]
	#def setArgs(self:

	def run(self):
		if len(self.app.keys())>0:
			try:
				app=json.loads(self.rc.showApp(self.app.get('name','')))[0]
			except:
				print("Error finding {}".format(self.app.get("name","")))
				app=self.app.copy()
				app["ERR"]=True
			finally:
				if isinstance(app,str):
					app=json.loads(app)
				self.showEnded.emit(app)
	#def run
#class thShowApp

class detailPanel(QWidget):
	clicked=Signal("PyObject")
	loaded=Signal("PyObject")
	tagpressed=Signal(str)
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=False
		self._debug("details load")
		self.setObjectName("detailPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setStyleSheet(css.detailPanel())
		self.refresh=False
		self.mapFile="/usr/share/rebost/lists.d/eduapps.map"
		self._connectThreads()
		self.oldcursor=self.cursor()
		self.stream=""
		self.launcher=""
		self.config={}
		self.app={}
		self.rc=store.client()
		self.instBundle=""
		self.th=[]
		self.__initScreen__()
	#def __init__

	def _connectThreads(self):
		self.helper=libhelper.helper()
		self.epi=exehelper.appLauncher()
		self.epi.runEnded.connect(self._getEpiResults)
		self.runapp=exehelper.appLauncher()
		self.runapp.runEnded.connect(self._getRunappResults)
		self.thEpiShow=thShowApp()
		self.thEpiShow.showEnded.connect(self._endGetEpiResults)
		self.thParmShow=thShowApp()
		self.thParmShow.showEnded.connect(self._endSetParms)
		self.zmdLauncher=exehelper.zmdLauncher()
		self.zmdLauncher.finished.connect(self._endRunZomando)
	#def _connectThreads

	def _debug(self,msg):
		if self.dbg==True:
			print("Details: {}".format(msg))
	#def _debug

	def _return(self):
		return
	#def _return

	def _tagNav(self,*args):
		cat=args[0][0].replace("#","")
		self.tagpressed.emit(cat)
	#def _tagNav(self,*args)

	def _processStreams(self,args):
		self.app={}
		if isinstance(args,str):
			name=""
			args=args.split("://")[-1]
			if args.startswith("install?"):
				ocs=args.split("&")[-1]
				idx=1
				for i in ocs.split("=")[-1]:
					if i.isalnum():
						idx+=1
					else:
						break
				name=ocs.split("=")[-1][:idx-1]
			else:
				name=args.replace(".desktop","").replace(".flatpakref","")
				name=name.split(".")[-1]
			if len(name)>0:
				app=self.rc.showApp(name)
				if len(app)>2:
					self.app=json.loads(app)[0]
					self.app=json.loads(self.app)
				else: #look for an aliases mapped from virtual app
					if os.path.exists(self.mapFile):
						fcontent={}
						with open(self.mapFile,"r") as f:
							fcontent=f.read()
						jcontent=json.loads(fcontent)
						vname=jcontent.get(name,"")
						self._debug("Find virtual pkg {0} for  {1}".format(vname,name))
						if len(vname)>0:
							app=self.rc.showApp(vname)
							if len(app)>2:
								self.app=json.loads(app)[0]
								self.app=json.loads(self.app)
	#def _processStreams

	def setParms(self,*args):
		#self.hideMsg()
		self.stream=""
		pxm=""
		if len(args)>0:
			name=args[-1]
			if isinstance(args[0],dict):
				name=args[0].get("name","")
				pxm=args[0].get("icon","")
			elif "://" in args[-1]:
				self.stream=args[-1]
			icon=""
			if self.stream=="":
				if isinstance(pxm,QtGui.QPixmap):
					icon=pxm
				else:
					icon=self.app.get("icon","")
			if name!="":
				self._resetScreen(name,icon)
				self.thParmShow.setArgs(args[0])
				self.thParmShow.start()
		self.lblHomepage.setVisible(True)
		#self._showSplash(icon)
	#def setParms

	def _endSetParms(self,*args):
		if len(args)>0:
			#Preserve icon 
			icn=self.app.get("icon")
			app=args[0]
			if isinstance(app,dict):
				self.app=app
			else:
				try:
					self.app=json.loads(app)
				except Exception as e:
					print(e)
		swErr=False
		if self.stream!="":
			self._processStreams(self.stream)
			self.stream=""
		else:
			if len(self.app)>0:
				for bundle,name in (self.app.get('bundle',{}).items()):
					if bundle=='package':
						continue
		self.setCursor(self.oldcursor)
		if "ERR" in app.keys():
			self._onError()
		self.updateScreen()
	#def _endSetParms

	def _endRunZomando(self):
		self.thEpiShow.setArgs(self.app["name"])
		self.thEpiShow.start()
	#def _endRunZomando

	def _runZomando(self):
		self.zmdLauncher.setApp(self.app)
		self.zmdLauncher.start()
		self.setEnabled(False)
	#def _runZomando

	def _runApp(self):
		bundle=self.lstInfo.currentItem().text().lower().split(" ")[-1]
		launchCmd=self.helper.getCmdForLauncher(self.app,bundle)
		self._debug("Opening {0} with {1}".format(self.app["name"],launchCmd))
		notifySummary=i18n.get("ERRNOTFOUND","")
		if len(launchCmd)>0:
			self.runapp.setArgs(self.app,launchCmd,bundle)
			self.runapp.start()
			notifySummary=i18n.get("OPENING","")
		notifyIcon=None
		if os.path.exists(self.app["icon"]):
			notifyIcon=self.app["icon"]
		self.showMsg(title="AppsEdu Store",summary=notifySummary,text=self.app["name"],icon=notifyIcon,timeout=2000)
	#def _runApp

	def _getRunappResults(self,app,proc):
		if "attempted" not in app.keys():
			app["attempted"]=[]
		if proc.returncode!=0 or len(proc.stderr.strip())>0:
			pkgname=""
			bundle=self.lstInfo.currentItem().text().lower().split(" ")[-1]
			if bundle not in ["flatpak","snap"]:
				cmd=["gtk-launch"]
			else:
				pkgname=" ".join(self.helper.getCmdForLauncher(self.app,bundle)[2:])
				cmd=[bundle,"run"]
			if pkgname in app["attempted"]:
				if app["pkgname"].split(".")[-1] not in app["attempted"]:
					pkgname=app["pkgname"].split(".")[-1]
				elif app["pkgname"]+"-appimage" not in app["attempted"]:
					pkgname=app["pkgname"]+"-appimage"
				elif "zero-lliurex" not in app["pkgname"]:
					pkgname="net.lliurex.{}".format(app["pkgname"])
					if pkgname in app["attempted"]:
						pkgname=" ".join(self.helper.getCmdForLauncher(self.app,bundle,self.app["pkgname"])[1:],)
					if pkgname in app["attempted"]:
						pkgname="net.lliurex.{}".format(app["pkgname"].split("-")[0])
					if pkgname in app["attempted"]:
						pkgname="net.lliurex.{}".format(app["pkgname"])
					if pkgname in app["attempted"]:
						pkgname=" ".join(self.helper.getCmdForLauncher(self.app,bundle)[1:],)
			pkgname=pkgname.replace("org.packagekit.","")
			if pkgname not in app["attempted"]:
				app["attempted"].append(pkgname)
				if "zero-lliurex" in pkgname:
					self._runZomando()
				else:
					self.runapp.setArgs(app,cmd.extend("{}".format(pkgname)))
					self.runapp.start()
			elif app["attempted"][-1]!="getLastAttempt":
				self._debug("Last attempt")
				app["attempted"].append("getLastAttempt")
				self.runapp.setArgs(app,["{}".format(app["pkgname"])])
				self.runapp.start()
			else:
				try:
					self.showMsg(summary=i18n.get("ERRLAUNCH",""),msg="{}".format(self.app["name"]))
				except Exception as e:
					print("Warning: {}".format(e))
					pass
	#def _getRunappResults

	def _genericEpiInstall(self,*args):
		if self.instBundle=="":
			bundle=self.lstInfo.currentSelected().lower().split(" ")[0]
		else:
			bundle=self.instBundle
		self.rc.enableGui(True)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		pkg=self.app.get('name').replace(' ','')
		user=os.environ.get('USER')
		res=self.rc.testInstall("{}".format(pkg),"{}".format(bundle),user=user)
		try:
			res=json.loads(res)[0]
		except:
			res={}
		epi=res.get('epi')
		self._debug("Invoking EPI for {}".format(epi))
		if epi==None:
			if res.get("done",0)==1 and "system package" in res.get("msg","").lower():
				self.parent().showMsg(summary=i18n.get("ERRSYSTEMAPP",""),msg="{}".format(self.app["name"]),timeout=4)
			else:
				self.parent().showMsg(summary=i18n.get("ERRUNKNOWN",""),msg="{}".format(self.app["name"]),timeout=4)
			self.updateScreen()
		else:
			if bundle=="zomando" and self.app.get("state",{}).get("zomando","1")=="0":
				self.zmdLauncher.setApp(self.app)
				self.zmdLauncher.start()
			else:
				cmd=["pkexec","/usr/share/rebost/helper/rebost-software-manager.sh",res.get('epi')]
				self.epi.setArgs(self.app,cmd,bundle)
				self.epi.start()
	#def _genericEpiInstall
	
	def _getEpiResults(self,app,*args):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.setEnabled(False)
		self.refresh=False
		#signal.raise_signal(signal.SIGUSR1)
		self.thEpiShow.setArgs(app)
		self.thEpiShow.start()
	#def _getEpiResults

	def _endGetEpiResults(self,app):
		self.thEpiShow.wait()
		bundle=list(app.get('bundle').keys())[0]
		state=app.get('state',{}).get(bundle,1)
		if app.get('name','')==self.app.get('name',''):
			if state!=self.app.get("state",{}).get(bundle,1):
				self.rc.commitInstall(app.get('name'),bundle,state)
				self.refresh=True
			self.app=app
		else:
			self.rc.commitInstall(app.get('name'),bundle,state)
			self.refresh=True
		self.setEnabled(True)
		self.updateScreen()
	 #def _endGetEpiResults

	def _clickedBack(self):
		if self.thParmShow.isRunning():
			self.thParmShow.quit()
		pxm=self.lblIcon.pixmap()
		if pxm.isNull()==False:
			self.app["icon"]=pxm
		for th in self.th:
			th.quit()
			th.wait()
		self.clicked.emit(self.app)

	def _loaded(self):
		self.loaded.emit(self.app)

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setObjectName("dp")
		self.btnBack=QPushButton()
		self.btnBack.clicked.connect(self._clickedBack)
		icn=QtGui.QIcon(os.path.join(RSRC,"go-previous32x32.png"))
		self.btnBack.setIcon(icn)
		self.btnBack.setIconSize(self.btnBack.sizeHint())
		self.box.addWidget(self.btnBack,0,0,1,1,Qt.AlignTop|Qt.AlignLeft)
		spacingI=QLabel("")
		spacingE=QLabel("")
		spacingI.setFixedWidth(16)
		spacingE.setFixedWidth(48)
		self.box.addWidget(spacingI,0,1,1,1)
		self.header=self._defHeader()
		self.box.addWidget(self.header,1,2,1,3)
		self.screenShot=self._defScreenshot()
		self.screenShot.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.box.addWidget(self.screenShot,2,2,1,3)
		resources=self._defResources()
		resources.setObjectName("resources")
		resources.setAttribute(Qt.WA_StyledBackground, True)
		self.lblDesc=QScrollLabel()
		self.lblDesc.label.setOpenExternalLinks(True)
		self.lblDesc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		spacing=QLabel("")
		spacing.setFixedHeight(6)
		self.box.addWidget(spacing,3,1,1,1)
		self.box.addWidget(resources,4,2,1,1)
		self.box.addWidget(self.lblDesc,4,3,2,1)
		self.setLayout(self.box)
		self.box.setColumnStretch(0,0)
		self.box.setColumnStretch(1,0)
		self.box.setColumnStretch(2,0)
		self.box.setColumnStretch(3,1)
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(5,1)
		self.box.setRowStretch(6,0)
		self.box.addWidget(spacingE,0,self.box.columnCount(),1,1)
		errorLay=QGridLayout()
		self.lblBkg=QLabel()
		errorLay.addWidget(self.lblBkg,0,0,1,1)
	#def _load_screen

	def _defHeader(self):
		wdg=QWidget()
		wdg.setObjectName("frame")
		lay=QGridLayout()
		lay.setSpacing(int(MARGIN)*2)
		self.lblIcon=QLabelRebostApp()
		self.lblIcon.setObjectName("lblIcon")
		self.lblIcon.setMaximumWidth(ICON_SIZE+6)
		lay.addWidget(self.lblIcon,0,1,3,1)
		self.lblName=QLabel()
		self.lblName.setObjectName("lblName")
		self.lblSummary=QLabel()
		self.lblName.setObjectName("lblSummary")
		self.lblSummary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
		self.lblSummary.setWordWrap(True)
		lay.addWidget(self.lblSummary,0,2,3,1)
		launchers=QWidget()
		hlay=QVBoxLayout()

		self.btnInstall=QLabel(i18n.get("INSTALL"))
		#self.btnInstall.setObjectName("btnInstall")
		self.btnInstall.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))

		self.btnRemove=QPushButton(i18n.get("REMOVE"))
		self.btnRemove.setObjectName("lstInfo")
		self.btnRemove.clicked.connect(self._genericEpiInstall)

		self.btnUnavailable=QPushButton(i18n.get("UNAVAILABLE"))
		self.btnUnavailable.setObjectName("lstInfo")

		self.btnZomando=QPushButton(" {} zomando ".format(i18n.get("RUN")))
		self.btnZomando.clicked.connect(self._runZomando)
		self.btnZomando.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
		self.btnZomando.setVisible(False)

		self.btnLaunch=QPushButton(i18n.get("RUN"))
		self.btnLaunch.clicked.connect(self._runApp)
		self.btnLaunch.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
		launchers.setLayout(hlay)
		lay.addWidget(launchers,1,3,1,1,Qt.AlignTop|Qt.AlignRight)
		for i in [self.btnInstall,self.btnLaunch,self.btnZomando]:
			i.setMinimumWidth(self.btnZomando.sizeHint().width()+(4*i.font().pointSize()))

		self.lstInfo=QComboButton()
		self.lstInfo.setObjectName("lstInfo")
		self.lstInfo.setMaximumWidth(50)
		self.lstInfo.currentTextChanged.connect(self._setLauncherOptions)	
		self.lstInfo.installClicked.connect(self._genericEpiInstall)
		lay.addWidget(self.btnInstall,1,3,3,1,Qt.AlignLeft|Qt.AlignTop)
		lay.addWidget(self.lstInfo,2,3,1,1,Qt.AlignLeft|Qt.AlignTop)
		lay.addWidget(self.btnRemove,2,3,1,1)
		lay.addWidget(self.btnUnavailable,2,3,1,1)
		self.btnRemove.setVisible(False)
		self.btnUnavailable.setVisible(False)
		spacing=QLabel("")
		spacing.setFixedWidth(64)
		lay.addWidget(spacing,0,lay.columnCount())
		wdg.setLayout(lay)
		lay.setColumnStretch(0,0)
		lay.setColumnStretch(1,3)
		lay.setColumnStretch(2,2)
		return(wdg)
	#def _defHeader

	def _defScreenshot(self):
		wdg=QScreenShotContainer()
		wdg.setObjectName("screenshot")
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		return(wdg)
	#def _defScreenshot

	def _defResources(self):
		wdg=QWidget()
		lay=QVBoxLayout()
		self.lblTags=QScrollLabel()
		self.lblTags.setObjectName("lblTags")
		self.lblTags.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lblTags.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		lay.addWidget(self.lblTags)
		self.resources=QWidget()
		layResources=QVBoxLayout()
		self.resources.setLayout(layResources)
		self.lblHomepage=QLabelLink('<a href="http://lliurex.net">lliurex.net</a>')
		self.lblHomepage.setToolTip("http://lliurex.net")
		self.lblHomepage.setOpenExternalLinks(True)
		layResources.addWidget(self.lblHomepage)
		lay.addWidget(self.resources)
		wdg.setLayout(lay)
		return(wdg)
	#def _defResources

	def keyPressEvent(self,*args):
		if args[0].key() in [Qt.Key_Escape]:
			self._return()
	#def keyPressEvent

	def _setUnknownAppInfo(self):
		if self.app.get("name","")!="":
			#Disabled as requisite (250214-11:52)
			#self.lblName.setText("<h1>{}</h1>".format(self.app.get('name')))
			self.lblName.setText("{}".format(self.app.get('name')))
			icn=self.app.get("icon","")
			pxm=None
			if isinstance(icn,QtGui.QPixmap):
				pxm=icn
			elif len(icn)>0:
				if os.path.isfile(icn):
					pxm=QtGui.QPixmap(icn)
			if not pxm :
				icn=QtGui.QIcon.fromTheme(self.app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
				pxm=icn.pixmap(ICON_SIZE,ICON_SIZE)
			if pxm:
				self.lblIcon.setPixmap(pxm.scaled(ICON_SIZE,ICON_SIZE))
			self.lblSummary.setText(self.app.get("summary",""))
			self.lblDesc.setText("<hr><p>{}</p><hr>".format(i18n.get("APPUNKNOWN")))
			self.lblDesc.label.setOpenExternalLinks(True)
			homepage="https://portal.edu.gva.es/appsedu/"
			text="<a href='{0}'>Appsedu</a>".format(homepage)
			self.lblHomepage.setText(text)
			self.lblHomepage.setToolTip(homepage)
			#self.lblIcon.loadImg(self.app)
			#self.lstInfo.setMaximumWidth(self.lblDesc.width()/2)
			if self.lblDesc.width()>self.lblTags.width():
				self.lblTags.setMaximumWidth(self.lblDesc.width()/2)
	#def _setUnknownAppInfo

	def _loadScreenshots(self):
		scrs=self.app.get('screenshots',[])
		if isinstance(scrs,list)==False:
			scrs=[]
		self.screenShot.clear()
		if len(scrs)==0:
			self.screenShot.setVisible(False)
		else:
			self.screenShot.setVisible(True)
		for icn in scrs:
			try:
				self.screenShot.addImage(icn)
			except Exception as e:
				print(e)
	#def _loadScreenshots

	def _updateIcon(self,*args):
		icn=args[0]
		self.lblIcon.setPixmap(icn.scaled(ICON_SIZE,ICON_SIZE))

	def updateScreen(self):
		if self.stream!="":
			return
		self._initScreen()
		if self.app.get("bundle",None)==None:
			self._setUnknownAppInfo()
			return
		#Disabled as requisite (250214-11:52)
		#self.lblName.setText("<h1>{}</h1>".format(self.app.get('name')))
	#	self.lblName.setText("{}".format(self.app.get('name').upper()))
	#	icn=self.app["icon"]
	#	if isinstance(icn,QtGui.QIcon):
	#		icn=icn.pixmap(ICON_SIZE,ICON_SIZE)
	#	elif isinstance(icn,QtGui.QPixmap)==False:
	#		icn=self._getIconFromApp(self.app)
	#		if isinstance(icn,QtGui.QIcon):
	#			icn=icn.pixmap(ICON_SIZE,ICON_SIZE)
		#self.lblIcon.setPixmap(icn.scaled(ICON_SIZE,ICON_SIZE))
		self.lblIcon.loadImg(self.app)
		pxm=self.lblIcon.pixmap()
		if pxm!=None:
			if pxm.isNull()==False:
				self.app["icon"]=pxm
		#Disabled as requisite (250214-11:52)
		#self.lblSummary.setText("<h2>{}</h2>".format(self.app.get('summary','')))
		summary="{}<br>{}".format(self.app["name"].upper(),self.app.get("summary",""))
		if len(summary)>150:
			summary="{}...".format(summary[0:150])
		self.lblSummary.setText("{}".format(summary))
		bundles=list(self.app.get('bundle',{}).keys())
		self.lstInfo.setEnabled(True)
		homepage=self.app.get('infopage','')
		if homepage=='':
			homepage=self.app.get('homepage','https://portal.edu.gva.es/appsedu/aplicacions-lliurex')
		if not isinstance(homepage,str):
			homepage='https://portal.edu.gva.es/appsedu/aplicacions-lliurex'
		text=""
		if homepage:
			homepage=homepage.rstrip("/")
			desc=homepage
			if desc.startswith("https://portal.edu.gva.es/appsedu")==True:
				desc=i18n.get("SEEIT")
			else:
				desc=i18n.get("SITE")
			text='<a href="{0}">{1}</a> '.format(homepage,desc)
		self.lblHomepage.setText(text)
		self.lblHomepage.setToolTip(homepage)
		#self.lblDesc.label.setOpenExternalLinks(False)
		description=html.unescape(self.app.get('description','').replace("***","\n"))
		if "Forbidden" in self.app.get("categories",[]):
			forbReason=""
			if self.app.get("summary","").endswith(")"):
				forbReason=": {}".format(self.app["summary"].split("(")[-1].replace(")",""))
				if forbReason.lower().startswith(": no ")==True:
					forbReason=""

			if self.app.get("ERR",False)!=False:
				description=i18n.get("APPUNKNOWN_SAI")
				description="<h2>{0}{4}</h2>{1} <a href='{2}'>{2}</a><hr>\n{3}".format(i18n.get("APPUNKNOWN").split(".")[0],i18n.get("INFO"),homepage,description,forbReason)
			else:
				description="<h2>{0}{4}</h2>{1} <a href='{2}'>{2}</a><hr>\n{3}".format(i18n.get("FORBIDDEN"),i18n.get("INFO"),homepage,description,forbReason)
			self.lblDesc.label.setOpenExternalLinks(True)
		self.lblDesc.setText(description)
		self._updateScreenControls(bundles)
		#preliminary license support, not supported
		applicense=self.app.get('license','')
		if applicense:
			text="<strong>{}</strong>".format(applicense)
		self._loadScreenshots()	
		#self._setLauncherOptions()
		self.lblTags.setText(self._generateCategoryTags())
		self.lblTags.adjustSize()
		self.loaded.emit(self.app)
	#def _updateScreen

	def _getLauncherForApp(self):
		#Best effort for get launcher
		self.appmenu.set_desktop_system()
		cats=self.appmenu.get_categories()
		launcher=""
		for cat in cats:
			apps=self.appmenu.get_apps_from_category(cat.lower())
			for app in apps:
				appsplit=app.split(".")
				if len(appsplit)>2:
					searchapp=appsplit[-2]
				else:
					searchapp=appsplit[0]
				namesplit=self.app["pkgname"].split("-")
				allitems=namesplit+[searchapp]
				if len(allitems)!=len(set(allitems)):
					launcher=app
					break
			if len(launcher)>0:
				break
		return(launcher)
	#def _getLauncherForApp

	def _generateCategoryTags(self):
		tags=""
		for cat in self.app.get("categories",[]):
			if cat.strip().islower() or len(cat)==0:
				continue
			icat=_(cat)
			if icat not in tags:
				#Disabled as requisite  (250214-11:52)
				#tags+="<a href=\"#{0}\"><strong>{0}</strong></a> / ".format(icat)
				tags+="{0} / ".format(icat)
		return("{}".format(tags.strip(" / ")))
	#def _generateCategoryTags

	def _resetScreen(self,name,icon):
		self.app={}
		self.instBundle=""
		self.app["name"]=name
		self.app["icon"]=icon
		self.app["summary"]=""
		self.app["pkgname"]=""
		self.app["description"]=""
	#def _resetScreen

	def _onError(self):
		self._debug("Error detected")
		qpal=QtGui.QPalette()
		color=qpal.color(QtGui.QPalette.Dark)
		self.parent().setWindowTitle("AppsEdu - {}".format("ERROR"))
		if "Forbidden" not in self.app.get("categories",[]):
			self.app["categories"]=["Forbidden"]
		self.lstInfo.setEnabled(False)
		self.btnInstall.setEnabled(False)
		self.btnRemove.setEnabled(False)
		self.btnUnavailable.setEnabled(False)
		self.btnLaunch.setEnabled(False)
		self.blur=QGraphicsBlurEffect() 
		self.blur.setBlurRadius(55) 
		self.opacity=QGraphicsOpacityEffect()
		self.lblBkg.setGraphicsEffect(self.blur)
		self.lblBkg.setStyleSheet("QLabel{background-color:rgba(%s,%s,%s,0.7);}"%(color.red(),color.green(),color.blue()))
		#self.app["name"]=i18n.get("APPUNKNOWN").split(".")[0]
		self.app["summary"]=i18n.get("APPUNKNOWN").split(".")[1]
		self.app["pkgname"]="rebost"
		self.app["description"]="{0}\n{1}".format(i18n.get("APPUNKNOWN"),i18n.get("APPUNKNOWN_SAI"))
		self.app["bundle"]={}
		self.lblHomepage.setVisible(False)
		self.loaded.emit(self.app)
	#def _onError

	def _setLauncherOptions(self):
		visible=True
		bundle=self.lstInfo.currentText()
		if "Forbidden" in self.app.get("categories",[]) or "eduapp" in bundle:
			visible=False
		self.btnInstall.setVisible(visible)
		self.lstInfo.setVisible(visible)
		if bundle==i18n["INSTALL"].upper():
			return
		bundle=bundle.split(" ")[0]
		self.btnInstall.setText("{0} {1}".format(i18n.get("RELEASE"),self.app.get("versions",{}).get(bundle,"lliurex")))
		self.lstInfo.blockSignals(True)
		self.lstInfo.setText(i18n["INSTALL"].upper())
		states=self.app.get("state",{}).copy()
		installed=False
		zmdInstalled=""
		print(states)
		if len(states)>0:
			for bundle,state in states.items():
				if state=="0":# and zmdInstalled!="0":
					installed=True
					self.instBundle=bundle
					break
		self.btnRemove.setVisible(installed)
		self.btnRemove.setEnabled(installed)
		if len(self.app.get("bundle",[]))==1 and "eduapp" in self.app.get("bundle",{}).keys():
			self.lstInfo.setVisible(False)
			self.btnRemove.setVisible(False)
			self.btnRemove.setEnabled(False)
			self.btnUnavailable.setVisible(True)
		else:
			self.btnUnavailable.setVisible(False)
		self.lstInfo.blockSignals(False)
	#def _setLauncherOptions

	def _old_setLauncherOptions(self):
		self.lstInfo.setEnabled(True)
		self.btnInstall.setEnabled(True)
		self.btnRemove.setEnabled(True)
		self.btnLaunch.setEnabled(True)
		self.btnZomando.setEnabled(True)
		bundle=""
		release=""
		tooltip=""
		item=self.lstInfo.currentText()
		if item==None:
			self._debug("This app has not install option. Waiting data")
			bundles=self.app.get("bundle",{}).copy()
			if len(bundles)>0:
				bundle=bundles.popitem()[1]
			else:
				bundle="package"
			bitem=QListWidgetItem("{}".format(bundle))
			self.lstInfo.insertItem(0,bitem)
			item=self.lstInfo.item(0)
		bundle=item.lower().split(" ")[-1].strip()
		release=item.lower().split(" ")[0]
		tooltip=item
		if bundle=="package":
			bundle="app" # Only for show purposes. "App" is friendly than "package"
		if self.lstInfo.count()>0:
			#self.btnInstall.setText("{0} {1}".format(i18n.get("INSTALL"),bundle))
			self.btnInstall.setText("{0} / {1}".format(bundle,self.app.get("versions",{}).get(bundle,"")))
			self.btnRemove.setText("{0} {1}".format(i18n.get("REMOVE"),bundle))
			self.btnLaunch.setText("{0} {1}".format(i18n.get("RUN"),bundle))
		self.btnInstall.setToolTip("{0}: {1}\n{2}".format(i18n.get("RELEASE"),release,bundle.capitalize()))
		self.btnRemove.setToolTip(tooltip)
		self.btnLaunch.setToolTip(tooltip)
		if "Forbidden" in self.app.get("categories",[]) or "eduapp" in bundle:
			self.btnInstall.setEnabled(False)
			self.btnRemove.setEnabled(False)
			self.btnLaunch.setEnabled(False)
			self.btnZomando.setEnabled(False)
	#def _setLauncherOptions

	def _getIconFromApp(self,app):
		icn=QtGui.QIcon()
		appIcn=app.get("icon")
		if isinstance(appIcn,str):
			if os.path.exists(app.get("icon")):
				icn=QtGui.QPixmap.fromImage(QtGui.QImage(appIcn))
		elif icn.isNull():
		#something went wrong. Perhaps img it's gzipped
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'))
			icn=icn2.pixmap(ICON_SIZE,ICON_SIZE)
		elif isinstance(appIcn,QtGui.QPixmap):
			icn=appIcn
		return(icn)
	#def _getIconFromApp

	def _updateScreenControls(self,bundles):
		pkgState=0
		if "zomando" in bundles:
			if "package" in bundles:
				pkgState=self.app.get('state',{}).get("package",'1')
				if pkgState.isdigit()==True:
					pkgState=int(pkgState)
		states=0
		self.btnZomando.setVisible(False)
		for bundle in bundles:
			state=(self.app.get('state',{}).get(bundle,'1'))
			if state.isdigit()==True:
				state=int(state)
			else:
				state=1
			states+=state
			if bundle=="zomando" and ((pkgState==0 or state==0) or (self.app.get("pkgname","x$%&/-1") not in self.app["bundle"]["zomando"])):
				continue
		self._setReleasesInfo()
	#def _updateScreenControls

	def _setReleasesInfo(self):
		bundles=self.app.get('bundle',{})
		for i in range(self.lstInfo.count()):
			self.lstInfo.removeItem(i)
		self.lstInfo.clear()
		if len(bundles)<=0:
			return()
		(installed,uninstalled)=self._classifyBundles(bundles)
		priority=["zomando","flatpak","snap","package","appimage","eduapp"]
		for i in installed+uninstalled:
			version=self.app.get('versions',{}).get(i,'')
			if version=="":
				version="lliurex23"
			if not("eduapp" in bundles.keys() and len(bundles.keys())==1 or "zero" not in self.app.get("name")):
				if "zomando" in bundles and i!="zomando":
					continue
			if i in priority:
				fversion=version.split("+")[0][0:10]
				release=QListWidgetItem("{} {}".format(fversion,i))
				release.setSizeHint(QSize(self.lstInfo.sizeHint().width()-50,self.lstInfo.font().pointSize()*3))
				idx=priority.index(i)
				if i in uninstalled:
					idx+=len(installed)
				else:
					bcolor=BKG_COLOR_INSTALLED
					release.setBackground(bcolor)
				release.setToolTip(version)
				release="{} {}".format(i,fversion)
				#release="{0}".format(i)
				self.lstInfo.insertItem(idx,release)
		self.lstInfo.setText(i18n["INSTALL"].upper())
		for idx in range(0,len(priority)):
			try:
				self.lstInfo.setState(idx,False)
			except:
				break
		if "eduapp" in bundles.keys():
			bundles.pop("eduapp")
		if len(bundles)<=0:
			self.lstInfo.setEnabled(False)
	#def _setReleasesInfo

	def _classifyBundles(self,bundles):
		installed=[]
		uninstalled=[]
		for bundle in bundles.keys():
			state=self.app.get("state",{}).get(bundle,1)
			if bundle=="zomando":
				#if "package" in bundles.keys():
				#	continue
				if os.path.isfile(bundles[bundle]):
					state="0"
			if isinstance(state,str):
				if state.isdigit()==False:
					state="1"
			if int(state)==0: #installed
				installed.append(bundle)
			else:
				uninstalled.append(bundle)
		return(installed,uninstalled)
	#def _classifyBundles

	def _initScreen(self):
		#Reload config if app has been epified
		if len(self.app)>0:
			self.lstInfo.setVisible(True)
			self.btnInstall.setVisible(True)
			if self.app.get('name','')==self.epi.app.get('name',''):
				try:
					self.app=json.loads(self.rc.showApp(self.app.get('name','')))[0]
				except Exception as e:
					print(e)
			if isinstance(self.app,str):
				try:
					self.app=json.loads(self.app)
				except Exception as e:
					print(e)
					self.app={}
			self.btnInstall.setEnabled(True)
			self.btnInstall.setText(i18n.get("INSTALL"))
			self.setCursor(self.oldcursor)
			self.screenShot.clear()
			self.btnZomando.setVisible(False)
			self.lblHomepage.setText("")
			self.lblTags.setText("")
			#Disabled as requisite (250214-11:52)
			#self.lblTags.linkActivated.connect(self._tagNav)
			self.app['name']=self.app.get('name','').replace(" ","")
		else:
			self._onError()
	#def _initScreen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

