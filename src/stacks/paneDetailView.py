#!/usr/bin/python3
import sys,signal
import os,random
from functools import partial
import json
import html
from rebost import store
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy,QWidget,QHBoxLayout,QVBoxLayout,QGraphicsBlurEffect,QScrollArea,QListWidget,QListWidgetItem
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,Slot
from QtExtraWidgets import QScreenShotContainer,QScrollLabel,QFlowTouchWidget
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
	"LBL_RELATED":_("More apps"),
	"OPEN":_("Z·Install"),
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
	requestInstallApp=Signal("PyObject","PyObject",str)
	requestLoadCategories=Signal(str)
	requestLoadTag=Signal(str)
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
		self.oldApp={} #Returning point if browsing through related apps
		self.instBundle=""
		self._connectThreads()
		self._renderGui()
	#def __init__

	def _connectThreads(self):
		self.thParmShow=thShowApp(rc=self.rc)
		self.thParmShow.showEnded.connect(self._endSetParms)
		self._rebost.lsgEnded.connect(self._endSuggestsLoad)
	#def _connectThreads

	def _debug(self,msg):
		if self.dbg==True:
			print("Details: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["thParmShow"].blockSignals(True)
		selfDict["thParmShow"].quit()
		selfDict["thParmShow"].wait()
	#def _onDestroy

	def hide(self,*args):
		self.oldApp={}
		self.setVisible(False)
		return True
	#def hide

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
				app=self.rc.refreshApp(name)
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
							app=self.rc.refreshApp(vname)
							if len(app)>2:
								self.app=json.loads(app)[0]
								self.app=json.loads(self.app)
	#def _processStreams

	def setParms(self,*args,**kwargs):
		#self.hideMsg()
		self.thParmShow.blockSignals(True)
		self.thParmShow.quit()
		self.thParmShow.wait()
		pxm=""
		self.referrerBtn=kwargs.get("btn",None)
		if len(args)>0:
			self.thParmShow.blockSignals(False)
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
		bundle=self.cmbBundles.currentSelected().lower().split(" ")[0]
		self.requestInstallApp.emit(self.btnRemove,self.app,bundle)
	#def _genericEpiInstall

	def _tagLinkClicked(self,*args):
		tag=args[0][0].replace("#","")
		self.requestLoadTag.emit(tag)
	#def _categoryTagClicked(self,*args)

	def _categoryLinkClicked(self,*args):
		cat=args[0][0].replace("#","")
		self.requestLoadCategory.emit(cat)
	#def _categoryLinkClicked(self,*args)

	def _clickedBack(self):
		self.screenShot.clear()
		if len(self.oldApp)>0:
			app=self.oldApp
			self.oldApp={}
			self.setParms(app)
		else:
			self.clickedBack.emit(self.referrerBtn,self.app)
	#def _clickedBack

	def keyPressEvent(self,*args):
		if args[0].key()==Qt.Key_Escape:
			self._clickedBack()
		else:
			args[0].ignore()
	#def keyPressEvent

	def _renderGui(self):
		self.box=QGridLayout()
		self.setObjectName("detailPanel")
		self.btnBack=self._defBtnBack()
		self.box.addWidget(self.btnBack,0,0,1,1,Qt.AlignTop|Qt.AlignLeft)
		self.header=self._defHeader()
		self.box.addWidget(self.header,0,1,1,4)
		wdg=QWidget()
		vlay=QVBoxLayout()
		wdg.setLayout(vlay)
		self.lblTags=self._defLblTags()
		self.lblTags.setObjectName("lblTags")
		vlay.addWidget(self.lblTags)
		self.box.addWidget(wdg,1,1,2,1,Qt.AlignTop)
		self.lblDesc=self._defLblDesc()
		self.box.addWidget(self.lblDesc,1,2,3,1)
		self.screenShot=self._defScreenshot()
		self.screenShot.widget.setMinimumHeight(self.lblDesc.height())
		self.screenShot.scroll.setMinimumHeight(self.lblDesc.height())
		self.box.addWidget(self.screenShot,1,3,4,1,Qt.AlignTop)
		self.lstLinks=self._defLstLinks()
		self.lstLinks.setObjectName("lstLinks")
		vlay.addWidget(self.lstLinks)
		self.tblSuggests=self._defSuggests()
		self.box.addWidget(self.tblSuggests,3,2,2,1,Qt.AlignBottom)
		self.setLayout(self.box)
		#COLS
		self.box.setColumnStretch(0,0)
		self.box.setColumnStretch(1,0)
		self.box.setColumnStretch(2,3)
		self.box.setColumnStretch(3,1)
		#ROWS
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(1,3)
		self.box.setRowStretch(2,1)
		self.box.setRowStretch(3,0)
		errorLay=QGridLayout()
		self.lblBkg=QLabel()
		errorLay.addWidget(self.lblBkg,0,0,1,1)
	#def _load_screen

	def _defBtnBack(self):
		wdg=QPushButton()
		wdg.setObjectName("btnBack")
		icn=QtGui.QIcon(os.path.join(RSRC,"go-previous32x32.png"))
		wdg.setIcon(icn)
		wdg.setIconSize(QSize(int(MARGIN)*8,int(MARGIN)*7))
		wdg.clicked.connect(self._clickedBack)
		return(wdg)
	#def _defBtnBack

	def _defLblDesc(self):
		wdg=QScrollLabel()
		wdg.setObjectName("lblDesc")
		wdg.label.setOpenExternalLinks(True)
		return(wdg)
	#def _lblDesc

	def _defHeader(self):
		wdg=QWidget()
		wdg.setObjectName("frame")
		lay=QGridLayout()
		lay.setSpacing(int(MARGIN)*2)
		self.lblIcon=QLabelRebostApp()
		self.lblIcon.setObjectName("lblIcon")
		self.lblIcon.setMaximumWidth(ICON_SIZE+int(MARGIN)*2)
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

		self.boxBundles=self._defBoxBundles()
		lay.addWidget(self.boxBundles,0,3,1,1,Qt.AlignTop|Qt.AlignRight)
		self.lblRelease=QLabel(i18n.get("INSTALL"))
		self.lblRelease.resize(self.lblRelease.sizeHint().width(),int(ICON_SIZE/3))

		self.btnRemove=QPushButton(i18n.get("REMOVE"))
		self.btnRemove.setObjectName("btnInstall")
		self.btnRemove.clicked.connect(self._genericEpiInstall,Qt.UniqueConnection)

		self.btnUnavailable=QPushButton(i18n.get("UNAVAILABLE"))
		self.btnUnavailable.setObjectName("cmbBundles")

		launchers.setLayout(hlay)
		lay.addWidget(launchers,1,3,1,1,Qt.AlignTop|Qt.AlignRight)

		self.cmbBundles=QComboButton()
		self.cmbBundles.setAttribute(Qt.WA_StyledBackground, False)
		self.cmbBundles.setObjectName("cmbBundles")
		self.cmbBundles.setFixedWidth(50)
		self.cmbBundles.currentTextChanged.connect(self._setLauncherOptions)	
		self.cmbBundles.installClicked.connect(self._genericEpiInstall,Qt.UniqueConnection)
		lay.addWidget(self.lblRelease,1,3,1,1,Qt.AlignLeft|Qt.AlignTop)
		lay.addWidget(self.cmbBundles,2,3,1,1,Qt.AlignRight|Qt.AlignTop)
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
		wdg=QScreenShotContainer(direction="vertical")
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
		wdg.setObjectName("screenshot")
		return(wdg)
	#def _defScreenshot

	def _endSuggestsLoad(self,*args):
		suggests=args[0]
		self.suggests.setSpacing(int(MARGIN)*3)
		for app in suggests:
			btn=QPushButtonRebostApp("{}")
			btn.setCompactMode(True)
			btn.clicked.connect(self._loadSuggested)
			btn.setIconSize(QSize(32,32))
			btn.setApp(app)
			self.suggests.addWidget(btn)
		if self.suggests.count()>0:
			self.suggests.setMinimumHeight(btn.sizeHint().height()+int(MARGIN)*8)
			self.suggests.show()
		else:
			self.suggests.hide()
	#def _endSuggestLoad(self,args):

	def _populateSuggestsList(self):
		self.suggests.clean()
		self._rebost.setAction("getAppSuggests",self.app,6) #Load 6 apps
		self._rebost.start()
	#def _defSuggestsLoad

	def _defSuggests(self):
		wdg=QWidget()
		lay=QVBoxLayout()
		wdg.setLayout(lay)
		lay.setSpacing(int(MARGIN))
		lay.addWidget(QLabel(i18n["LBL_RELATED"]))
		self.suggests=QFlowTouchWidget(self)
		self.suggests.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.suggests.setObjectName("lblTags")
		lay.addWidget(self.suggests)
		return(wdg)
	#def _defSuggests

	def _defLblTags(self):
		wdg=QScrollLabel()
		wdg.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.setMinimumWidth(ICON_SIZE*3+(int(MARGIN)*3))
		return(wdg)
	#def _defLblTags

	def _populateLinks(self):
		homepage=self.app.get('homepage','')
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
			text='<a href="{0}" style="text-decoration:none;"><strong>{1}</strong></a> '.format(homepage,desc)
		item=QListWidgetItem()
		self.lstLinks.addItem(item)
		lbl=QLabelLink(text)
		lbl.setToolTip(homepage)
		lbl.setOpenExternalLinks(True)
		item.setSizeHint(QSize(lbl.sizeHint()))
		self.lstLinks.setItemWidget(item,lbl)
	#def _populateLinks

	def _defLstLinks(self):
		wdg=QListWidget()
		return(wdg)
	#def _defLstLinks

	def _populateBoxBundles(self):
		for children in self.boxBundles.children():
			if isinstance(children,QLabel):
				children.hide()
				bundle=children.toolTip().lower()
				if bundle=="epi":
					bundle="unknown"
				if bundle in self.app["bundle"].keys():
					children.show()
	#def _populateBundleIcons

	def _defBoxBundles(self):
		wdg=QWidget()
		wdg.setObjectName("boxBundles")
		lay=QHBoxLayout()
		lay.setSpacing(0)
		lay.setContentsMargins(0,0,0,0)
		wdg.setLayout(lay)
		lbl=None
		for bundle in self.rc.getSupportedFormats():
			pxm=QtGui.QPixmap()
			if bundle=="unknown":
				bundle="epi"
			pxmPath=os.path.join(RSRC,"application-vnd.{}.png".format(bundle))
			pxm.load(pxmPath)
			lbl=QLabel()
			lbl.setObjectName("boxBundles")
			lbl.setPixmap(pxm)
			lbl.setToolTip(bundle.capitalize())
			lbl.hide()
			lay.addWidget(lbl,Qt.AlignRight)
		if lbl!=None:
			wdg.setMaximumHeight(lbl.height())
		return(wdg)
	#def _defBundleIcons

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
			#self.lblHomepage.setText(text)
			#self.lblHomepage.setToolTip(homepage)
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

	def _loadSuggested(self,*args):
		self.parent()._beginLoad(resetScreen=False)
		self.screenShot.clear()
		if len(self.oldApp)==0:
			self.oldApp=self.app
		app=args[1]
		self.setParms(app)
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
		self.cmbBundles.setEnabled(True)
		description=html.unescape(self.app.get('description','').replace("***","\n"))
		print(self.app)
		if "Forbidden" in self.app.get("categories",[]):
			forbReason=""
			if self.app.get("summary","").endswith(")"):
				forbReason=": {}".format(self.app["summary"].split("(")[-1].replace(")",""))
				if forbReason.lower().startswith(": no ")==True:
					forbReason=""

			if self.app.get("ERR",False)!=False:
				description=i18n.get("APPUNKNOWN_SAI")
				description="<h2>{0}{4}</h2>{1} <a href='{2}'>{2}</a><hr>\n{3}".format(i18n.get("APPUNKNOWN").split(".")[0],i18n.get("INFO"),i18n["APPUNKNOWN_SAI"],description,forbReason)
			else:
				description="<h2>{0}{4}</h2>{1} <a href='{2}'>{2}</a><hr>\n{3}".format(i18n.get("FORBIDDEN"),i18n.get("INFO"),i18n["APPUNKNOWN_SAI"],description,forbReason)
			self.lblDesc.label.setOpenExternalLinks(True)
		self.lblDesc.setText(description)
		self._setReleasesInfo()
		#preliminary license support, not supported
		applicense=self.app.get('license','')
		if applicense:
			text="<strong>{}</strong>".format(applicense)
		self._loadScreenshots()	
		self.lblTags.setText(self._generateAppTags())
		if len(self.lblTags.text())==0:
			self.lblTags.hide()
		else:
			self.lblTags.show()
		self._populateSuggestsList()
		self._populateLinks()
		self._populateBoxBundles()
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

	def _generateAppTags(self):
		tags=""
		style="padding:1px;border-radius:3px;text-decoration:none;"
		for keyword in self.app.get("keywords",[]):
			if len(keyword)==0 or keyword=="zomandos" or keyword==self.app["name"]:
				continue
			if keyword in self.app.get("suggests",[]):
				continue
			if keyword not in tags and len(keyword)>1:
				#Disabled as requisite  (250214-11:52)
				tags+="<a href=\"#{0}\" style=\"{1}\">#{0}</a> ".format(keyword,style)
		return("{}".format(tags.strip(" / ")))
	#def _generateAppTags

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
		self.cmbBundles.setEnabled(False)
		self.lblRelease.setEnabled(False)
		self.btnRemove.setEnabled(False)
		self.btnUnavailable.setEnabled(False)
		self.blur=QGraphicsBlurEffect() 
		self.blur.setBlurRadius(55) 
		self.lblBkg.setGraphicsEffect(self.blur)
		self.lblBkg.setStyleSheet("QLabel{background-color:rgba(%s,%s,%s,0.7);}"%(color.red(),color.green(),color.blue()))
		#self.app["name"]=i18n.get("APPUNKNOWN").split(".")[0]
		self.app["summary"]=i18n.get("APPUNKNOWN").split(".")[1]
		self.app["pkgname"]="rebost"
		self.app["description"]="{0}\n{1}".format(i18n.get("APPUNKNOWN"),i18n.get("APPUNKNOWN_SAI"))
		self.app["bundle"]={}
		#self.lblHomepage.setVisible(False)
		self.loaded.emit(self.app)
	#def _onError

	def _setLauncherStatus(self):
		if int(self.app.get("state","0"))>=7:
			try:
				self.btnRemove.blockSignals(True)
				self.cmbBundles.blockSignals(True)
			except Exception as e: #Don't worry
				print(e)
			self.btnRemove.setCursor(QtGui.QCursor(Qt.WaitCursor))
			self.cmbBundles.setCursor(QtGui.QCursor(Qt.WaitCursor))
		else:
			try:	
				self.btnRemove.blockSignals(False)
				self.cmbBundles.blockSignals(False)
			except: #Be happy
				pass
			self.btnRemove.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
			self.cmbBundles.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
	#def _setLauncherStatus

	def _setLauncherOptions(self):
		visible=True
		bundle=self.cmbBundles.currentText()
		if "Forbidden" in self.app.get("categories",[]):
			visible=False
		self.lblRelease.setVisible(visible)
		self.cmbBundles.setVisible(visible)
		if bundle==i18n["INSTALL"].upper():
			return
		bundle=bundle.split(" ")[0]
		self.lblRelease.setText("{0} {1}".format(i18n.get("RELEASE"),self.app.get("versions",{}).get(bundle,"lliurex")))
		self.cmbBundles.blockSignals(True)
		self.cmbBundles.setText(i18n["INSTALL"].upper())
		self.btnRemove.setVisible(False)
		self.btnRemove.setEnabled(False)
		bundles=self.app.get("bundle",{})
		zmd=bundles.get("unknown","")
		status=self.app["status"]
		self.btnRemove.setText("")
		if len(status)>0:
			if zmd!="" and len(bundles)==2: #2->pkg that belongs to a zmd
				self.btnRemove.setText(i18n["OPEN"])
			else:
				for bundle,appstatus in status.items():
					if int(appstatus)==0:# and zmdInstalled!="0":
						if bundle=="package" and zmd!="" and len(bundles)==2: #2->zmd and its own pkg
							self.btnRemove.setText(i18n["OPEN"])
							break
						elif self.btnRemove.text()!=i18n["REMOVE"]:
							self.btnRemove.setText(i18n["REMOVE"])
							self.instBundle=bundle
							break
		elif zmd!="" and len(bundles)==1: #1->No other bundles, so it's a zomando pkg
				self.btnRemove.setVisible(True)
				self.btnRemove.setEnabled(True)
				self.btnRemove.setText(i18n["OPEN"])
		if self.btnRemove.text()!="":
			self.btnRemove.setVisible(True)
			self.btnRemove.setEnabled(True)
			self.btnRemove.setMinimumSize(self.cmbBundles.size())
			self.btnUnavailable.setMinimumSize(self.cmbBundles.size())
			self.cmbBundles.hide()
		self._setLauncherStatus()
		self.cmbBundles.blockSignals(False)
	#def _setLauncherOptions

	def _setReleasesInfo(self):
		for i in range(self.cmbBundles.count()):
			self.cmbBundles.removeItem(i)
		self.cmbBundles.clear()
		priority=self.helper.getBundlesByPriority(self.app)
		if len(priority)<=0:
			self.cmbBundles.setEnabled(False)
		else:
			priorityFinal=list(priority.keys())
			priorityFinal.sort()
			for idx in priorityFinal:
				self.cmbBundles.addItem(priority[idx])
			self.cmbBundles.setText(i18n["INSTALL"].upper())
			for idx in range(0,len(priority)):
				try:
					self.cmbBundles.setState(idx,False)
				except:
					break
	#def _setReleasesInfo

	def _initScreen(self):
		#Reload config if app has been epified
		self.showMsg=self.parent().showMsg
		if len(self.app)>0:
			self.cmbBundles.setVisible(True)
			self.lblRelease.setVisible(True)
			self.lblRelease.setEnabled(True)
			self.lblRelease.setText(i18n.get("INSTALL"))
			self.setCursor(self.oldCursor)
			self.screenShot.clear()
			self.lstLinks.clear()
			#self.lblCategories.setText("")
			#Disabled as requisite (250214-11:52)
			#self.lblCategories.linkActivated.connect(self._categoryLinkClicked)
			self.lblTags.setText("")
			self.lblTags.hide()
			self.lblTags.linkActivated.connect(self._tagLinkClicked)
		else:
			self._onError()
	#def _initScreen
