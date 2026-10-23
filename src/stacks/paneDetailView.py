#!/usr/bin/python3
import sys,signal
import os,random
from functools import partial
import json
import html
from rebost import store
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy,QWidget,QHBoxLayout,QVBoxLayout,QGraphicsBlurEffect,QListWidget,QListWidgetItem
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,Slot,QUrl
from QtExtraWidgets import QScreenShotContainer,QScrollLabel,QFlowTouchWidget
import lib.helperLib as helper
import extras.css as css
from extras.constants import *
from extras.i18n import *
from wdg.btnInstallers import QPushButtonInstaller
from wdg.lblApp import QLabelRebostApp
from wdg.lblLnk import QLabelLink
from wdg.btnRebost import QPushButtonRebostApp
from wdg.suggests import suggestsBar

class main(QWidget):
	clickedBack=Signal("PyObject","PyObject")
	loaded=Signal("PyObject")
	requestInstallApp=Signal("PyObject",dict,"PyObject")
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
		self.rc=store.client()
		self.helper=helper.appHelper()
		self.aux=helper.auxiliary()
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
		self._rebost.lsgEnded.connect(self._endSuggestsLoad)
		self._rebost.rfrEnded.connect(self._endSetParms)
	#def _connectThreads

	def _debug(self,msg):
		if self.dbg==True:
			print("Details: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
	#def _onDestroy

	def hide(self,*args):
		self.oldApp={}
		self.setVisible(False)
		return True
	#def hide

	def setParms(self,*args,**kwargs):
		self.referrerBtn=kwargs.get("btn",None)
		if self.referrerBtn!=None:
			self.app=self.referrerBtn.app
			if self.app["description"].strip()!="":
				self.updateScreen()
				return
			else:
				name=self.app["id"]
				if "appsedu" in self.app.get("homepage",""):
					details=self.helper.getAppseduDetails(self.app["homepage"])
					self.app["description"]=details["description"]
					self.updateScreen()
					return
		if isinstance(args[0],dict):
			name=args[0]["id"]
		else:
			self.app={}
			name=args[-1]
			name=self.aux.getAppFromStream(name)
		self._resetScreen(name,"")
		self._rebost.setAction("refreshApp",name)
		self._rebost.start()
	#def setParms

	def _endSetParms(self,*args):
		if len(args)>0:
			app=args[0]
			if isinstance(app,dict):
				self.app=app
			else:
				self.app=self.aux.getAppFromString(app)
		if len(self.app)>0:
			if isinstance(self.app,dict):
				if "ERR" in self.app.keys():
					self._onError()
			else:
				self._onError()
			homepage=self.app.get('homepage','')
			if isinstance(homepage,str)==False:
				homepage=""
			if homepage.startswith("https://portal.edu.gva.es/appsedu")==True and self.app["description"].count(" ")<3:
				details=self.helper.getAppseduDetails(homepage)
				if len(details.get("description",""))>len(self.app["description"]):
					self.app["description"]=details["description"]
				if len(details.get("icon",""))>0:
					self.app["icon"]=details["icon"]
				if self.app.get("webapp",False)==True:
					self.app["bundle"].update({"webapp":details.get("url","")})
			#for bundle,name in (self.app.get('bundle',{}).items()):
			#	if bundle=='package':
			#		continue
		if self.referrerBtn!=None:
			self.referrerBtn.setApp(self.app)
		self.setEnabled(True)
		self.setCursor(self.oldCursor)
		self.updateScreen()
	#def _endSetParms

	def _setInstallingState(self):
		if self.cmbBundles.text()==i18n["BTN_REMOVE"]:
			self.app["state"]=8
			self._rebost.setAction("setAppState",self.app["id"],8)
		else:
			self.app["state"]=7
			self._rebost.setAction("setAppState",self.app["id"],7)
		self._rebost.start()
		self._rebost.wait()
	#def _setInstallingState

	@Slot("PyObejct,","PyObject")
	def _genericEpiInstall(self,*args):
		self._setInstallingState()
		app=self.app
		if len(args)>0:
			bundle=args[0].lower()
			if bundle=="epi":
				bundle="unknown"
			if bundle not in self.app["bundle"].keys():
				if "unknown" in self.app["bundle"].keys():
					bundle="unknown"
			app["bundle"]={bundle:self.app["bundle"].get(bundle,"")}
		icon=self.lblIcon.pixmap()
		self.requestInstallApp.emit(self.referrerBtn,app,icon)
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
		font=self.font()
		font.setPointSize(font.pointSize()+(12-font.pointSize()))
		self.setFont(font)
		self.setObjectName("detailPanel")
		self.box=QGridLayout()
		self.btnBack=self._defBtnBack()
		self.box.addWidget(self.btnBack,0,0,1,1,Qt.AlignTop|Qt.AlignLeft)
		self.header=self._defHeader()
		self.box.addWidget(self.header,0,1,1,4)
		wdg=QWidget()
		vlay=QVBoxLayout()
		wdg.setLayout(vlay)
		self.lblTags=self._defLblTags()
		vlay.addWidget(self.lblTags)
		self.box.addWidget(wdg,1,1,2,1,Qt.AlignTop)
		self.lblDesc=self._defLblDesc()
		self.box.addWidget(self.lblDesc,1,2,3,1)
		self.screenShot=self._defScreenshot()
		self.screenShot.widget.setMinimumHeight(self.lblDesc.height())
		self.screenShot.scroll.setMinimumHeight(self.lblDesc.height())
		self.box.addWidget(self.screenShot,1,3,3,1,Qt.AlignTop)
		self.lstLinks=self._defLstLinks()
		vlay.addWidget(self.lstLinks)
		self.tblSuggests=self._defSuggests()
		self.box.addWidget(self.tblSuggests,3,1,2,2)
		self.setLayout(self.box)
		#COLS
		self.box.setColumnStretch(0,0)
		self.box.setColumnStretch(1,1)
		self.box.setColumnStretch(2,3)
		self.box.setColumnStretch(3,1)
		#ROWS
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(1,3)
		self.box.setRowStretch(2,0)
		self.box.setRowStretch(3,1)
		errorLay=QGridLayout()
		self.lblBkg=QLabel()
		errorLay.addWidget(self.lblBkg,0,0,1,1)
	#def _load_screen

	def _defBtnBack(self):
		wdg=QPushButton()
		wdg.setObjectName("btnBack")
		icn=QtGui.QIcon(os.path.join(RSRC,"go-previous32x32.png"))
		wdg.setIcon(icn)
		wdg.setIconSize(QSize(max(MARGIN,3)*8,max(MARGIN,3)*7))
		wdg.clicked.connect(self._clickedBack)
		return(wdg)
	#def _defBtnBack

	def _defLblDesc(self):
		wdg=QScrollLabel(styled=False)
		wdg.setObjectName("lblDesc")
		wdg.label.setOpenExternalLinks(True)
		wdg.label.setFont(self.font())
		return(wdg)
	#def _lblDesc

	def _defHeader(self):
		wdg=QWidget()
		wdg.setObjectName("frame")
		lay=QGridLayout()
		lay.setSpacing(MARGIN*2)
		self.lblIcon=QLabelRebostApp()
		self.lblIcon.setObjectName("lblIcon")
		self.lblIcon.setMaximumWidth(ICON_SIZE*2+MARGIN*2)
		lay.addWidget(self.lblIcon,0,1,3,1)
		self.lblName=QLabel()
		self.lblName.setObjectName("lblName")
		self.lblName.setFont(self.font())
		self.lblSummary=QLabel()
		self.lblSummary.setObjectName("lblSummary")
		self.lblSummary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
		self.lblSummary.setWordWrap(True)
		self.lblSummary.setFont(self.font())
		lay.addWidget(self.lblSummary,0,2,3,1)
		launchers=QWidget()
		hlay=QVBoxLayout()
		self.boxBundles=self._defBoxBundles()
		lay.addWidget(self.boxBundles,0,3,1,1,Qt.AlignTop|Qt.AlignRight)
		self.lblRelease=QLabel(i18n.get("BTN_INSTALL"))
		self.lblRelease.resize(self.lblRelease.sizeHint().width(),int(ICON_SIZE/3))
		self.lblRelease.hide()
		lay.addWidget(self.lblRelease,1,3,1,1,Qt.AlignLeft|Qt.AlignTop)

		launchers.setLayout(hlay)
		lay.addWidget(launchers,1,3,1,1,Qt.AlignTop|Qt.AlignRight)

		self.cmbBundles=QPushButtonInstaller()
		self.cmbBundles.installerClicked.connect(self._genericEpiInstall,Qt.UniqueConnection)
		self.cmbBundles.setText(i18n["BTN_INSTALL"])
		self.cmbBundles.setVisible(False)
		self.cmbBundles.setMinimumSize(ICON_SIZE*4,ICON_SIZE/2)
		self.cmbBundles.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
		self.cmbBundles.setFont(self.font())
		lay.addWidget(self.cmbBundles,1,3,1,1)
		self.cmbBundles.hide()

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
		wdg.scroll.setObjectName("screenshot")
		return(wdg)
	#def _defScreenshot

	def _endSuggestsLoad(self,*args):
		self.suggests.loadSuggests(args[0])
	#def _endSuggestLoad(self,args):

	def _populateSuggestsList(self):
		self.suggests.clean()
		self._rebost.setAction("getAppSuggests",self.app,10) #Load 4 apps
		self._rebost.start()
	#def _populateSuggestsList

	def _loadSuggestedApp(self,*args):
		self.setCursor(Qt.WaitCursor)
		app=self.oldApp
		self.oldApp={}
		self.setEnabled(False)
		self.setParms(args[0].property("metadata"))
	#def _loadSuggestedApp

	def _defSuggests(self):
		wdg=QWidget()
		lay=QVBoxLayout()
		wdg.setLayout(lay)
		lay.setSpacing(MARGIN)
		lay.addWidget(QLabel(i18n["DETAIL_LBL_RELATED"]))
		self.suggests=suggestsBar()
		self.suggests.selected.connect(self._loadSuggestedApp)
		self.suggests.setObjectName("lstSuggests")
		lay.addWidget(self.suggests)
		return(wdg)
	#def _defSuggests

	def _defLblTags(self):
		wdg=QScrollLabel(styled=False)
		wdg.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		#wdg.setMinimumWidth(ICON_SIZE*3+(MARGIN))
		wdg.setMaximumWidth(ICON_SIZE*3+(MARGIN*4))
		wdg.setObjectName("lblTags")
		return(wdg)
	#def _defLblTags

	def _populateLinks(self):
		homepage=self.app.get('homepage','')
		if homepage=='':
			homepage=self.app.get('homepage','https://portal.edu.gva.es/appsedu/aplicacions-lliurex')
		if not isinstance(homepage,str):
			homepage=""
			#homepage='https://portal.edu.gva.es/appsedu/aplicacions-lliurex'
		text=""
		if homepage:
			homepage=homepage.rstrip("/")
			desc=homepage
			if desc.startswith("https://portal.edu.gva.es/appsedu")==True:
				desc=i18n.get("DETAIL_SEEIT")
			else:
				desc=i18n.get("DETAIL_SITE")
			text='<a href="{0}"><strong>{1}</strong></a> '.format(homepage,desc)
			text=desc
		if len(text)>0:
			item=QListWidgetItem()
			self.lstLinks.addItem(item)
			lbl=QLabelLink(text)
			lbl.setObjectName("lblLink")
			lbl.setToolTip(homepage)
			#lbl.setOpenExternalLinks(True)
			item.setSizeHint(QSize(lbl.sizeHint()))
			self.lstLinks.setItemWidget(item,lbl)
			self.lstLinks.show()
		else:
			self.lstLinks.hide()
		self.lstLinks.setMinimumWidth(self.lstLinks.sizeHintForColumn(0))
	#def _populateLinks

	def _defLstLinks(self):
		def _enableLink(*args):
			lnk=self.lstLinks.itemWidget(args[0])
			url=QUrl(lnk.toolTip())
			QtGui.QDesktopServices.openUrl(url)
		wdg=QListWidget()
		wdg.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		wdg.setMouseTracking(True)
		wdg.itemPressed.connect(_enableLink)
		wdg.setObjectName("lstLinks")
		return(wdg)
	#def _defLstLinks

	def _populateBoxBundles(self):
		bundlesSorted=self.helper.getBundlesByPriority(self.app)
		bundles=[]
		for idx,bundleData in bundlesSorted.items():
			bundleData=bundleData.strip()
			if " " not in bundleData:
				bundleData+=" contrib"
			bundles.append(bundleData.split()[0])
		defBund=None
		epi=False
		for children in self.boxBundles.children():
			if isinstance(children,QLabel):
				children.hide()
				chldText=children.toolTip().lower().split("\n")[0].replace("<p>","").replace("</p>","")
				bundle=chldText.split(":")[-1].lower().strip()
				if bundle=="epi":
					bundle="unknown"
					defBund=children
					defBund.setEnabled(True)
				if bundle in bundles:
					release=self.app.get("versions",{}).get(bundle,"")
					if bundle=="unknown":
						bundle="epi"
					text="Kind: {0}\nRelease: {1}".format(bundle.capitalize(),release)
					children.setToolTip(text)
					if bundle=="epi":
						epi=True
						children.show()
					elif epi==False:
						children.show()
					added=True
					defBund=None
		if defBund!=None:
			defBund.setEnabled(False)
			defBund.show()
	#def _populateBoxBundles

	def _defBoxBundles(self):
		wdg=QWidget()
		wdg.setObjectName("boxBundles")
		lay=QHBoxLayout()
		lay.setSpacing(0)
		lay.setContentsMargins(0,0,0,0)
		wdg.setLayout(lay)
		lbl=None
		priority=["epi","package","flatpak","snap","appimage","eduapp"]
		for bundle in priority:
			pxm=QtGui.QPixmap()
			if bundle=="unknown":
				bundle="epi"
			pxmPath=os.path.join(RSRC,"application-vnd.{}.png".format(bundle))
			pxm.load(pxmPath)
			lbl=QLabel()
			lbl.setObjectName("boxBundles")
			lbl.setPixmap(pxm)
			lbl.setToolTip("Kind: {}\nRelease: {}".format(bundle.capitalize(),""))
			lbl.hide()
			lay.addWidget(lbl,Qt.AlignRight)
		if lbl!=None:
			wdg.setMaximumHeight(lbl.height())
		return(wdg)
	#def _defBoxBundles

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
			self.lblDesc.setText("<hr><p>{}</p><hr>".format(i18n.get("DETAIL_APPUNKNOWN")))
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
				print("Error adding image")
				self._debug(e)
	#def _loadScreenshots

	def _loadSuggested(self,*args):
		self.parent()._beginLoad(resetScreen=False)
		self.screenShot.clear()
		if len(self.oldApp)==0:
			self.oldApp=self.app
		app=args[1]
		self.setParms(app)
	#def _loadSuggested

	def _loadIcon(self):
		pxm=self.lblIcon.pixmap()
		if pxm==None:
			self.lblIcon.loadImg(self.app)
		elif pxm.isNull()==True:
			self.lblIcon.loadImg(self.app)
		else:
			self.app["icon"]=self.lblIcon.pixmapPath
	#def _loadIcon

	def _setInfo(self):
		summary="{}<br>{}".format(self.app["name"].upper(),self.app.get("summary",""))
		if len(summary)>150:
			summary="{}...".format(summary[0:150])
		self.lblSummary.setText("{}".format(summary))
		description=html.unescape(self.app.get('description','').replace("***","\n"))
		self.lblDesc.setText(description)
		#preliminary license support, not supported
		applicense=self.app.get('license','')
		if applicense:
			text="<strong>{}</strong>".format(applicense)
	#def _setInfo

	def _setTags(self):
		exclude=self.app.get("suggests",[])
		exclude.extend([self.app["name"],self.app["id"]])
		extra=self.app.get("summary")
		if len(extra)==0:
			extra=self.app.get("description")
		self.lblTags.setText(self.aux.tokenizeTags(self.app.get("keywords",[]),exclude=exclude,extra=extra))
		if len(self.lblTags.text())==0:
			self.lblTags.hide()
		else:
			self.lblTags.show()
	#def _setTags

	def updateScreen(self):
		self._initScreen()
		if self.app.get("bundle",None)==None:
			self._setUnknownAppInfo()
			return
		self._loadIcon()
		self._setInfo()
		bundles=list(self.app.get('bundle',{}).keys())
		self.cmbBundles.setEnabled(True)
		self._loadScreenshots()	
		self._setTags()
		self._populateSuggestsList()
		self._populateLinks()
		self._populateBoxBundles()
		self.cmbBundles.setApp(self.app)
		self.setCursor(self.oldCursor)
		self.loaded.emit(self.app)
	#def _updateScreen

	def refreshCmbForApp(self,app):
		if app["id"]==self.app["id"]:
			self.app=app
			self.cmbBundles.setApp(self.app)
	#def refreshCmbForApp

	def _resetScreen(self,name,icon):
		self.app={}
		self.lblIcon.setPixmap(QtGui.QPixmap())
		self.instBundle=""
		self.app["name"]=name
		self.app["icon"]=icon
		self.app["summary"]=""
		self.app["pkgname"]=""
		self.app["description"]=""
	#def _resetScreen

	def _initScreen(self):
		#Reload config if app has been epified
		self.showMsg=self.parent().showMsg
		if len(self.app)>0:
			self.cmbBundles.setVisible(True)
			self.lblRelease.setEnabled(True)
			self.lblRelease.setText(i18n.get("BTN_INSTALL"))
			self.setCursor(self.oldCursor)
			self.screenShot.clear()
			self.lstLinks.clear()
			self.lblTags.setText("")
			self.lblTags.hide()
			self.lblTags.linkActivated.connect(self._tagLinkClicked)
		else:
			self._onError()
	#def _initScreen

	def _onError(self):
		self._debug("Error detected")
		qpal=QtGui.QPalette()
		color=qpal.color(QtGui.QPalette.Dark)
		self.parent().setWindowTitle("LLiureX - {}".format("ERROR"))
		self.cmbBundles.setEnabled(False)
		self.lblRelease.setEnabled(False)
		self.blur=QGraphicsBlurEffect() 
		self.blur.setBlurRadius(55) 
		self.lblBkg.setGraphicsEffect(self.blur)
		self.lblBkg.setStyleSheet("QLabel{background-color:rgba(%s,%s,%s,0.7);}"%(color.red(),color.green(),color.blue()))
		#self.app["name"]=i18n.get("APPUNKNOWN").split(".")[0]
		self.app["summary"]=i18n.get("DETAIL_APPUNKNOWN").split(".")[0]
		self.app["pkgname"]="rebost"
		self.app["description"]="{0}".format(i18n.get("DETAIL_APPUNKNOWN_SAI"))
		self.app["bundle"]={}
		#self.lblHomepage.setVisible(False)
		self.loaded.emit(self.app)
	#def _onError

