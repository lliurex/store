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
							QAbstractScrollArea, QFrame,QHeaderView
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation,Slot
from QtExtraWidgets import QScreenShotContainer,QScrollLabel,QTableTouchWidget
import libhelper
import css
from cmbBtn import QComboButton
from lblApp import QLabelRebostApp
from lblLnk import QLabelLink
from btnRebost import QPushButtonRebostApp
from libth import thShowApp
from constants import *
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"APPUNKNOWN":_("The app could not be loaded. Until included in LliureX catalogue it can't be installed"),
	"APPUNKNOWN_SAI":_("For any question the SAI can be contacted at <a href='https://portal.edu.gva.es/sai/es/inicio/'>https://portal.edu.gva.es/sai/es/inicio/</a>"),
	"ERRNOTFOUND":_("Could not open"),
	"ERRLAUNCH":_("Error opening"),
	"ERRMORETHANONE":_("There's another action in progress"),
	"ERRSYSTEMAPP":_("System apps can't be removed"),
	"ERRUNKNOWN":_("Unknown error"),
	"FORBIDDEN":_("App unauthorized"),
	"INFO":_("For more info go to"),
	"INSTALL":_("Install"),
	"OPEN":_("Open"),
	"OPENING":_("Opening"),
	"RELEASE":_("Release"),
	"REMOVE":_("Remove"),
	"RUN":_("Open"),
	"SEEIT":_("See at Appsedu"),
	"SITE":_("Website"),
	"UNAVAILABLE":_("Unavailable"),
	}


class main(QWidget):
	clickedBack=Signal("PyObject","PyObject")
	loaded=Signal("PyObject")
	requestLoadCategory=Signal(str)
	requestInstallApp=Signal("PyObject","PyObject",str)
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self._debug("details load")
		self.destroyed.connect(partial(main._onDestroy,self.__dict__))
		self._rebost=args[0]
		self.setObjectName("detailPanel")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setStyleSheet(css.detailPanel())
		self.refresh=False
		self.mapFile="/usr/share/rebost/lists.d/eduapps.map"
		self.rc=store.client()
		self.helper=libhelper.helper()
		self.oldCursor=self.cursor()
		self.launcher=""
		self.config={}
		self.app={}
		self.instBundle=""
		self._connectThreads()
		self.__initScreen__()
	#def __init__

	def _connectThreads(self):
		self.thParmShow=thShowApp(rc=self.rc)
		self.hParmShow.showEnded.connect(self._endSetParms)
		self._rebost.shwEnded.connect(self._endLoadSuggested)
	#def _connectThreads

	def _debug(self,msg):
		if self.dbg==True:
			print("Details: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["thParmShow"].quit()
	#def _onDestroy


	def _return(self):
		return
	#def _return

	def _tagNav(self,*args):
		cat=args[0][0].replace("#","")
		self.requestLoadCategory.emit(cat)
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

	def setParms(self,*args,**kwargs):
		#self.hideMsg()
		self.parent()._stopThreads()
		pxm=""
		self.referrerBtn=kwargs.get("btn",None)
		if len(args)>0:
			name=args[-1]
			self._resetScreen(name,"")
			if isinstance(args[0],dict):
				name=args[0].get("name","")
				pxm=args[0].get("icon","")
				appid=args[0].get("id",name)
				self.thParmShow.setArgs(args[0])
				self.thParmShow.start()
			elif isinstance(name,str):
				self._processStreams(name)
				self.thParmShow.setArgs(self.app)
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
					pass
		swErr=False
		if len(self.app)>0:
			for bundle,name in (self.app.get('bundle',{}).items()):
				if bundle=='package':
					continue
		self.setCursor(self.oldCursor)
		if "ERR" in app.keys():
			self._onError()
		self.updateScreen()
	#def _endSetParms

	def _getRunappResults(self,app,proc):
		self.setCursor(self.oldCursor)
		if proc==None:
			return
		if proc.returncode!=0:
			#pkexec ret values
			#127 -> Not authorized
			if proc.returncode==127:
				self.showMsg(title="AppsEdu Store",summary=self.app["name"],text=i18n.get("ERRUNAUTHORIZED"),icon=self.app["icon"],timeout=5000)
		self._rebost.setAction("setAppState",self.app["id"],0)
		self._rebost.start()
		self._rebost.wait()
		self.app["state"]=0
		self._setLauncherStatus()
		return
	#def _getRunappResults

	def _setInstallingState(self):
		if self.btnRemove.isVisible()==True:
			self.app["state"]=8
			if self.btnRemove.text()==i18n["REMOVE"]:
				self._rebost.setAction("setAppState",self.app["id"],8)
		else:
			self._rebost.setAction("setAppState",self.app["id"],7)
			self.app["state"]=7
		self._rebost.start()
		self._rebost.wait()
	#def _setInstallingState

	@Slot("PyObejct,","PyObject")
	def _genericEpiInstall(self,*args):
		bundle=self.lstInfo.currentSelected().lower().split(" ")[0]
		self.requestInstallApp.emit(self.btnRemove,self.app,bundle)
	#def _genericEpiInstall

	def _clickedBack(self):
		if self.thParmShow.isRunning():
			self.thParmShow.quit()
		pxm=self.lblIcon.pixmap()
		if pxm.isNull()==False:
			self.app["icon"]=self.lblIcon.pixmapPath
		self.screenShot.clear()
		self.clickedBack.emit(self.referrerBtn,self.app)
	#def _clickedBack

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
		#self.screenShot.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.box.addWidget(self.screenShot,2,2,1,3)
		resources=self._defResources()
		resources.setObjectName("resources")
		resources.setAttribute(Qt.WA_StyledBackground, True)
		self.lblDesc=QScrollLabel()
		self.lblDesc.label.setOpenExternalLinks(True)
		self.lblDesc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.suggests=self._defSuggests()
		spacing=QLabel("")
		spacing.setFixedHeight(6)
		self.box.addWidget(spacing,3,1,1,1)
		self.box.addWidget(resources,4,2,1,1)
		self.box.addWidget(self.lblDesc,4,3,2,1)
		self.box.addWidget(self.suggests,6,3,1,1,Qt.AlignBottom)
		self.setLayout(self.box)
		self.box.setColumnStretch(0,0)
		self.box.setColumnStretch(1,0)
		self.box.setColumnStretch(2,0)
		self.box.setColumnStretch(3,1)
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(5,1)
		self.box.setRowStretch(7,0)
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

		self.lblRelease=QLabel(i18n.get("INSTALL"))
		#self.lblRelease.setObjectName("lblRelease")
		self.lblRelease.resize(self.lblRelease.sizeHint().width(),int(ICON_SIZE/3))

		self.btnRemove=QPushButton(i18n.get("REMOVE"))
		self.btnRemove.setObjectName("lstInfo")
		self.btnRemove.clicked.connect(self._genericEpiInstall,Qt.UniqueConnection)

		self.btnUnavailable=QPushButton(i18n.get("UNAVAILABLE"))
		self.btnUnavailable.setObjectName("lstInfo")

		launchers.setLayout(hlay)
		lay.addWidget(launchers,1,3,1,1,Qt.AlignTop|Qt.AlignRight)

		self.lstInfo=QComboButton()
		self.lstInfo.setObjectName("lstInfo")
		self.lstInfo.setMaximumWidth(50)
		self.lstInfo.currentTextChanged.connect(self._setLauncherOptions)	
		self.lstInfo.installClicked.connect(self._genericEpiInstall,Qt.UniqueConnection)
		lay.addWidget(self.lblRelease,1,3,3,1,Qt.AlignLeft|Qt.AlignTop)
		lay.addWidget(self.lstInfo,2,3,1,1,Qt.AlignRight|Qt.AlignTop)
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

	def _defSuggests(self):
		wdg=QTableTouchWidget()
		wdg.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.horizontalHeader().hide()
		wdg.verticalHeader().hide()
		wdg.setShowGrid(False)
		wdg.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
		wdg.setRowCount(2)
		wdg.setColumnCount(1)
		wdg.setCellWidget(0,0,QLabel("Related apps<br>"))
		return(wdg)
	#def _defSuggests

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
		if args[0].key()==Qt.Key_Escape:
			self._clickedBack()
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
				pprint("Error adding image")
				print(e)
	#def _loadScreenshots

	def _endLoadSuggested(self,*args):
		app=json.loads(args[0])
	#def _endLoadSuggested

	def _loadSuggested(self,*args):
		name=args[1]["name"]
		self._rebost.setAction("show",name,0)
		self._rebost.start()
	#def _loadSuggested

	def updateScreen(self):
		self._initScreen()
		if self.app.get("bundle",None)==None:
			self._setUnknownAppInfo()
			return
		self.lblIcon.loadImg(self.app)
		pxm=self.lblIcon.pixmap()
		if pxm!=None:
			if pxm.isNull()==False:
				self.app["icon"]=self.lblIcon.pixmapPath
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
		self._setReleasesInfo()
		#preliminary license support, not supported
		applicense=self.app.get('license','')
		if applicense:
			text="<strong>{}</strong>".format(applicense)
		self._loadScreenshots()	
		#self._setLauncherOptions()
		self.lblTags.setText(self._generateCategoryTags())
		self.lblTags.adjustSize()
		for suggest in self.app.get("suggests",[]):
			self.suggests.setColumnCount(self.suggests.columnCount()+1)
			app={"name":suggest,"icon":"","pkgname":suggest,"description":""}
			btn=QPushButtonRebostApp(app)
			btn.clicked.connect(self._loadSuggested)
			btn.autoUpdate=True
			btn.setFixedSize(QSize(ICON_SIZE,ICON_SIZE*1.5))
			btn.showBtn=False
			self.suggests.setCellWidget(1,self.suggests.columnCount()-2,btn)
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
				tags+="<a href=\"#{0}\"><strong>{0}</strong></a> / ".format(icat)
			#	tags+="{0} / ".format(icat)
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
		self.lblRelease.setEnabled(False)
		self.btnRemove.setEnabled(False)
		self.btnUnavailable.setEnabled(False)
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

	def _setLauncherStatus(self):
		if int(self.app.get("state","0"))>=7:
			try:
				self.btnRemove.blockSignals(True)
				self.lstInfo.blockSignals(True)
			except Exception as e: #Don't worry
				print(e)
			self.btnRemove.setCursor(QtGui.QCursor(Qt.WaitCursor))
			self.lstInfo.setCursor(QtGui.QCursor(Qt.WaitCursor))
		else:
			try:	
				self.btnRemove.blockSignals(False)
				self.lstInfo.blockSignals(False)
			except: #Be happy
				pass
			self.btnRemove.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
			self.lstInfo.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
	#def _setLauncherStatus

	def _setLauncherOptions(self):
		visible=True
		bundle=self.lstInfo.currentText()
		if "Forbidden" in self.app.get("categories",[]) or "eduapp" in bundle:
			visible=False
		self.lblRelease.setVisible(visible)
		self.lstInfo.setVisible(visible)
		if bundle==i18n["INSTALL"].upper():
			return
		bundle=bundle.split(" ")[0]
		self.lblRelease.setText("{0} {1}".format(i18n.get("RELEASE"),self.app.get("versions",{}).get(bundle,"lliurex")))
		self.lstInfo.blockSignals(True)
		self.lstInfo.setText(i18n["INSTALL"].upper())
		self.btnRemove.setVisible(False)
		self.btnRemove.setEnabled(False)
		bundles=self.app.get("bundle",{})
		zmd=bundles.get("unknown","")
		states=self.app["status"]
		if len(states)>0:
			for bundle,state in states.items():
				if int(state)==0:# and zmdInstalled!="0":
					self.btnRemove.setVisible(True)
					self.btnRemove.setEnabled(True)
					if bundle=="package" and zmd!="" and len(bundles)==2: #2->zmd and its own pkg
						self.btnRemove.setText(i18n["OPEN"])
						break
					elif self.btnRemove.text()!=i18n["REMOVE"]:
						self.btnRemove.setText(i18n["REMOVE"])
						self.instBundle=bundle
						break
		self._setLauncherStatus()
		if len(self.app.get("bundle",[]))==1 and "eduapp" in self.app.get("bundle",{}).keys():
			self.btnRemove.setEnabled(False)
			self.btnUnavailable.setVisible(True)
		else:
			self.btnUnavailable.setVisible(False)
		self.lstInfo.blockSignals(False)
	#def _setLauncherOptions

	def _setReleasesInfo(self):
		for i in range(self.lstInfo.count()):
			self.lstInfo.removeItem(i)
		self.lstInfo.clear()
		priority=self.helper.getBundlesByPriority(self.app)
		if len(priority)<=0:
			self.lstInfo.setEnabled(False)
		else:
			priorityFinal=list(priority.keys())
			priorityFinal.sort()
			for idx in priorityFinal:
				self.lstInfo.addItem(priority[idx])
			self.lstInfo.setText(i18n["INSTALL"].upper())
			for idx in range(0,len(priority)):
				try:
					self.lstInfo.setState(idx,False)
				except:
					break
	#def _setReleasesInfo

	def _initScreen(self):
		#Reload config if app has been epified
		self.showMsg=self.parent().showMsg
		if len(self.app)>0:
			self.lstInfo.setVisible(True)
			self.lblRelease.setVisible(True)
			self.lblRelease.setEnabled(True)
			self.lblRelease.setText(i18n.get("INSTALL"))
			self.setCursor(self.oldCursor)
			self.screenShot.clear()
			self.lblHomepage.setText("")
			self.lblTags.setText("")
			#Disabled as requisite (250214-11:52)
			self.lblTags.linkActivated.connect(self._tagNav)
		else:
			self._onError()
	#def _initScreen
