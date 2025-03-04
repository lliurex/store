#!/usr/bin/python3
import sys,signal
import os
import subprocess
import json
import html
from app2menu import App2Menu as app2menu
from rebost import store
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy,QWidget,QComboBox,QHBoxLayout,QListWidget,\
							QVBoxLayout,QListWidgetItem,QGraphicsBlurEffect,QGraphicsOpacityEffect,\
							QAbstractScrollArea, QFrame
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation
#from appconfig.appConfigStack import appConfigStack as confStack
from QtExtraWidgets import QScreenShotContainer,QScrollLabel,QStackedWindowItem
import gettext
import libhelper
import exehelper
from cmbBtn import QComboButton
_ = gettext.gettext
QString=type("")
ICON_SIZE=128
BKG_COLOR_INSTALLED=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Inactive,QtGui.QPalette.Highlight))
ICON_SIZE=128
MINTIME=0.2
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")

i18n={
	"APPUNKNOWN":_("The app could not be loaded. Until included in LliureX catalogue it can't be installed"),
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
				print("Error")
				app=self.app.copy()
			finally:
				if isinstance(app,str):
					app=json.loads(app)
				self.showEnded.emit(app)
		return True
	#def run
#class thShowApp

class QLabelRebostApp(QLabel):
	clicked=Signal("PyObject")
	def __init__(self,parent=None):
		QLabel.__init__(self, parent)
		self.setAlignment(Qt.AlignCenter)
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
	#def __init__

	def loadImg(self,app):
		img=app.get('icon','')
		self.setMinimumWidth(1)
		icn=''
		if os.path.isfile(img):
			icn=QtGui.QPixmap.fromImage(QtGui.QImage(img))
		elif img=='':
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
			icn=icn2.pixmap(ICON_SIZE,ICON_SIZE)
		if icn:
			wsize=ICON_SIZE
			if "/usr/share/banners/lliurex-neu" in img:
				wsize=int(ICON_SIZE*1.8)
			self.setPixmap(icn.scaled(wsize,ICON_SIZE,Qt.KeepAspectRatio,Qt.SmoothTransformation))
			self.setMinimumWidth(wsize+10)
		elif img.startswith('http'):
			aux=QScreenShotContainer()
			self.scr=aux.loadScreenShot(img,self.cacheDir)
			self.scr.start()
			self.scr.imageLoaded.connect(self.load)
			self.scr.wait()
	#def loadImg
	
	def load(self,*args):
		img=args[0]
		self.setPixmap(img.scaled(ICON_SIZE,ICON_SIZE))
		self.setMinimumWidth(ICON_SIZE+10)
	#def load
#class QLabelRebostApp

class QLabelLink(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		hbox=QHBoxLayout()
		icn=QtGui.QPixmap(os.path.join(RSRC,"link24x24.png"))
		lblIcn=QLabel()
		lblIcn.setPixmap(icn.scaled(16,16))
		hbox.addWidget(lblIcn)
		self.lbl=QLabel(args[0])
		hbox.addWidget(self.lbl)
		self.setLayout(hbox)
	
	def setOpenExternalLinks(self,*args):
		self.lbl.setOpenExternalLinks(*args)

	def setText(self,*args):
		self.lbl.setText(*args)

class detailPanel(QWidget):
	clicked=Signal("PyObject")
	loaded=Signal("PyObject")
	tagpressed=Signal(str)
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=False
		self._debug("details load")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setStyleSheet("padding:0px;border:0px;margin:0px;background:#FFFFFF;color:unset;")
		self.refresh=False
		self.mapFile="/usr/share/rebost/lists.d/eduapps.map"
		self._connectThreads()
		self.oldcursor=self.cursor()
		self.stream=""
		self.launcher=""
		self.config={}
		self.app={}
		self.appmenu=app2menu.app2menu()
		self.rc=store.client()
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

	def _showSplash(self,icon):
		pxm=None
		if isinstance(icon,QtGui.QPixmap):
			pxm=icon
		elif len(icon)>0:
			if os.path.isfile(icon):
				pxm=QtGui.QPixmap(icon)
		if not pxm:
			icn=QtGui.QIcon.fromTheme("appedu-generic")
			pxm=icn.pixmap(ICON_SIZE,ICON_SIZE)
		if isinstance(pxm,QtGui.QPixmap):
			color=QtGui.QPalette().color(QtGui.QPalette.Dark)
			self.wdgSplash.setPixmap(pxm.scaled(int(self.width()),int(self.height()/1.1),Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.SmoothTransformation))
		self.wdgSplash.setMaximumWidth(self.width()-ICON_SIZE*1.1)
		self.wdgSplash.setMaximumHeight(self.height()-ICON_SIZE*1.1)
		self.wdgSplash.setVisible(True)
	#def _showSplash

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
		self._showSplash(icon)
	#def setParms

	def _endSetParms(self,*args):
		if len(args)>0:
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
				#	name=self.app.get('name','')
				#	if name!='':
				#		status=self.rc.getAppStatus(name,bundle)
				#		self.app['state'][bundle]=str(status)
		self.setCursor(self.oldcursor)
		for anim in self.anims:
			anim.start()
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
		bundle=self.lstInfo.currentText().lower().split(" ")[0]
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
		signal.raise_signal(signal.SIGUSR1)
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

	def _clicked(self):
		self.clicked.emit(self.app)

	def _loaded(self):
		self.loaded.emit(self.app)

	def __initScreen__(self):
		self.box=QGridLayout()
		self.btnBack=QPushButton()
		self.btnBack.clicked.connect(self._clicked)
		icn=QtGui.QIcon(os.path.join(RSRC,"go-previous32x32.png"))
		self.btnBack.setIcon(icn)
		#self.btnBack.setMinimumSize(QSize(int(ICON_SIZE/1.7),int(ICON_SIZE/1.7)))
		self.btnBack.setIconSize(self.btnBack.sizeHint())
		self.box.addWidget(self.btnBack,0,0,1,1,Qt.AlignTop|Qt.AlignLeft)
		self.header=self._defHeader()
		self.header.setStyleSheet("QWidget#frame{margin:0px;padding:0px;border:1px solid #DDDDDD;bottom:0px}""")
		self.box.addWidget(self.header,1,1,1,4)
		self.screenShot=self._defScreenshot()
		self.box.addWidget(self.screenShot,2,1,1,4)
		resources=self._defResources()
		resources.setObjectName("resources")
		resources.setAttribute(Qt.WA_StyledBackground, True)
		self.lblDesc=QScrollLabel()
		self.lblDesc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.lblDesc.setWordWrap(True)	  
		self.box.addWidget(resources,3,1,1,1)
		resources.setStyleSheet("""QWidget#resources{margin-top:12px;border-right:3px solid;border-radius:1px;border-right-color:#EEEEEE;}""")
		self.box.addWidget(self.lblDesc,3,2,2,2)

		self.setLayout(self.box)
		self.box.setColumnStretch(0,0)
		self.box.setColumnStretch(1,0)
		self.box.setColumnStretch(2,0)
		self.box.setColumnStretch(3,1)
		self.box.setRowStretch(0,0)
		self.box.setRowStretch(4,1)
		self.box.setRowStretch(5,0)
		
		self.wdgSplash=QLabel()
		errorLay=QGridLayout()
		self.wdgSplash.setLayout(errorLay)
		color=QtGui.QPalette().color(QtGui.QPalette.Dark)
		self.wdgSplash.setStyleSheet("background-color:rgba(%s,%s,%s,0.5);"%(color.red(),color.green(),color.blue()))
		self.lblBkg=QLabel()
		errorLay.addWidget(self.lblBkg,0,0,1,1)
		self.box.addWidget(self.wdgSplash,1,0,self.box.rowCount()-1,self.box.columnCount(),Qt.AlignCenter)
		self.anims = [QPropertyAnimation(self.wdgSplash, b"maximumWidth",parent=self),
						QPropertyAnimation(self.wdgSplash, b"maximumHeight",parent=self)]
		self.anims[0].setStartValue(self.wdgSplash.width())
		for anim in self.anims:
			anim.setEndValue(0)
			anim.setDuration(100)
	#def _load_screen

	def _defHeader(self):
		wdg=QWidget()
		wdg.setObjectName("frame")
		lay=QGridLayout()
		self.lblIcon=QLabelRebostApp()
		lay.addWidget(self.lblIcon,1,1,2,1,Qt.AlignTop|Qt.AlignLeft)
  
		self.lblName=QLabel()
		lay.addWidget(self.lblName,1,2,1,1,Qt.AlignTop)
		self.lblSummary=QLabel()
		self.lblSummary.setWordWrap(True)
		lay.addWidget(self.lblSummary,2,2,1,1,Qt.AlignTop)

		launchers=QWidget()
		hlay=QVBoxLayout()
		self.btnInstall=QLabel(i18n.get("INSTALL"))
		#self.btnInstall.setStyleSheet("""color:#002c4f;background:#FFFFFF;border:1px solid;border-color:#AAAAAA;border-radius:5px;padding-bottom:5px;padding-top:5px""")
		#self.btnInstall.clicked.connect(self._genericEpiInstall)
		self.btnInstall.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
		#self.btnInstall.setMinimumHeight(int(ICON_SIZE/3))
		#self.btnInstall.setMaximumHeight(int(ICON_SIZE/3))
		self.btnRemove=QPushButton(i18n.get("REMOVE"))
		self.btnRemove.clicked.connect(self._genericEpiInstall)
		self.btnRemove.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
	#	hlay.addWidget(self.btnRemove,Qt.AlignLeft)

		self.btnZomando=QPushButton(" {} zomando ".format(i18n.get("RUN")))
		self.btnZomando.clicked.connect(self._runZomando)
		self.btnZomando.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
		self.btnZomando.setVisible(False)
	#	hlay.addWidget(self.btnZomando,Qt.AlignLeft)

		self.btnLaunch=QPushButton(i18n.get("RUN"))
		self.btnLaunch.clicked.connect(self._runApp)
		self.btnLaunch.resize(self.btnInstall.sizeHint().width(),int(ICON_SIZE/3))
	#	hlay.addWidget(self.btnLaunch,Qt.AlignLeft)
		launchers.setLayout(hlay)
		lay.addWidget(launchers,1,3,1,1,Qt.AlignTop|Qt.AlignRight)
		for i in [self.btnInstall,self.btnRemove,self.btnLaunch,self.btnZomando]:
			i.setMinimumWidth(self.btnZomando.sizeHint().width()+(4*i.font().pointSize()))

		#self.lstInfo=QListWidget()
		self.lstInfo=QComboButton()
		#self.lstInfo.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lstInfo.setStyleSheet(self._lstInfoStyle())
		self.lstInfo.setMaximumWidth(50)
		self.lstInfo.currentTextChanged.connect(self._setLauncherOptions)	
		self.lstInfo.installClicked.connect(self._genericEpiInstall)
		lay.addWidget(self.btnInstall,2,3,2,1,Qt.AlignRight|Qt.AlignTop)
		lay.addWidget(self.lstInfo,2,3,2,1,Qt.AlignRight|Qt.AlignBottom)
		wdg.setLayout(lay)
		return(wdg)

	def _lstInfoStyle(self):
		fgColor="unset"
		if self.lstInfo.isEnabled()==False:
			fgColor="#AAAAAA"
		css="""QWidget{padding:6px;margin:1px;border:1px solid;border-color:#AAAAAA;border-radius:5px;}
				QComboBox::drop-down{ subcontrol-origin: padding;
				subcontrol-position: top right;
				border-top-right-radius: 3px; /* same radius as the QComboBox */
				border-bottom-right-radius: 3px;
				}
				QComboBox::down-arrow {
					image: url("%s/drop-down16x16.png");
					right:10px;
					border-left:1px solid #AAAAAA;
					padding:6px;
					margin-left:18px;
				}
				QComboBox::down-arrow:on { /* shift the arrow when popup is open */
					top: 1px;
					right: 8px;
				}
				"""%(RSRC)
		return(css)

	def _defScreenshot(self):
		wdg=QScreenShotContainer()
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		wdg.setStyleSheet("margin:0px;padding:0px;")
		return(wdg)
		

	def _defResources(self):
		wdg=QWidget()
		lay=QVBoxLayout()
		self.lblTags=QScrollLabel()
		self.lblTags.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lblTags.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lblTags.setStyleSheet("margin:0px;padding:0px;border:0px;bottom:0px")
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

	def keyPressEvent(self,*args):
		if args[0].key() in [Qt.Key_Escape]:
			self._return()
	#def keyPressEvent

	def _setUnknownAppInfo(self):
		if self.app.get("name","")!="":
			self.lblName.setText("<h1>{}</h1>".format(self.app.get('name')))
			icn=self.app.get("icon","")
			pxm=None
			if isinstance(icn,QtGui.QPixmap):
				pxm=icn
			elif len(icn)>0:
				if os.path.isfile(icn):
					pxm=QtGui.QPixmap(icn)
			if not pxm:
				icn=QtGui.QIcon.fromTheme(self.app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
				pxm=icn.pixmap(ICON_SIZE,ICON_SIZE)
			if pxm:
				self.lblIcon.setPixmap(pxm.scaled(ICON_SIZE,ICON_SIZE))
			self.lblSummary.setText(self.app.get("summary",""))
			self.lblDesc.setText("<hr><p>{}</p><hr>".format(i18n.get("APPUNKNOWN")))
			self.lblDesc.label.setOpenExternalLinks(True)
			homepage="https://portal.edu.gva.es/appsedu/"
			text='<a href="{0}">Appsedu</a>'.format(homepage)
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

	def updateScreen(self):
		if self.stream!="":
			return
		self._initScreen()
		if self.app.get("bundle",None)==None:
			self._setUnknownAppInfo()
			return
		self.lblName.setText("<h1>{}</h1>".format(self.app.get('name')))
		icn=self._getIconFromApp(self.app)
		self.lblIcon.setPixmap(icn.scaled(ICON_SIZE,ICON_SIZE))
		self.lblIcon.loadImg(self.app)
		self.lblSummary.setText("<h2>{}</h2>".format(self.app.get('summary','')))
		bundles=list(self.app.get('bundle',{}).keys())
	#	if "eduapp" in bundles:
	#		self.app["description"]=i18n.get("APPUNKNOWN")
		homepage=self.app.get('homepage','https://portal.edu.gva.es/appsedu/aplicacions-lliurex')
		if not isinstance(homepage,str):
			homepage='https://portal.edu.gva.es/appsedu/aplicacions-lliurex'
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
		self.lblDesc.label.setOpenExternalLinks(False)
		description=html.unescape(self.app.get('description','').replace("***","\n"))
		if "Forbidden" in self.app.get("categories",[]):
			forbReason=""
			if self.app.get("summary","").endswith(")"):
				forbReason=": {}".format(self.app["summary"].split("(")[-1].replace(")",""))
				if forbReason.lower().startswith(": no ")==True:
					forbReason=""
			description='<h2>{0}{4}</h2>{1} <a href="{2}">{2}</a><hr>\n{3}'.format(i18n.get("FORBIDDEN"),i18n.get("INFO"),homepage,description,forbReason)
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
				tags+="<a href=\"#{0}\"><strong>{0}</strong></a> / ".format(icat)
		return("{}".format(tags.strip(" / ")))
	#def _generateCategoryTags

	def _resetScreen(self,name,icon):
		#self.parent.setWindowTitle("AppsEdu")
		self.app={}
		self.app["name"]=name
		self.app["icon"]=icon
		self.app["summary"]=""
		self.app["pkgname"]=""
		self.app["description"]=""
	#def _resetScreen(self):

	def _onError(self):
		self._debug("Error detected")
		qpal=QtGui.QPalette()
		color=qpal.color(qpal.Dark)
		self.parent.setWindowTitle("AppsEdu - {}".format("ERROR"))
		#self.wdgSplash.setVisible(True)
		if "Forbidden" not in self.app.get("categories",[]):
			self.app["categories"]=["Forbidden"]
		self.lstInfo.setEnabled(False)
		self.btnInstall.setEnabled(False)
		self.btnRemove.setEnabled(False)
		self.btnLaunch.setEnabled(False)
		self.blur=QGraphicsBlurEffect() 
		self.blur.setBlurRadius(55) 
		self.opacity=QGraphicsOpacityEffect()
		self.lblBkg.setGraphicsEffect(self.blur)
		self.lblBkg.setStyleSheet("QLabel{background-color:rgba(%s,%s,%s,0.7);}"%(color.red(),color.green(),color.blue()))
		self.app["name"]=i18n.get("APPUNKNOWN").split(".")[0]
		self.app["summary"]=i18n.get("APPUNKNOWN").split(".")[1]
		self.app["pkgname"]="rebost"
		self.app["description"]=i18n.get("APPUNKNOWN")
	#def _onError

	def _setLauncherOptions(self):
		bundle=self.lstInfo.currentText()
		if bundle==i18n["INSTALL"].upper():
			return
		bundle=bundle.split(" ")[0]
		self.btnInstall.setText("{0} / {1}".format(bundle,self.app.get("versions",{}).get(bundle,"lliurex")))
		self.lstInfo.setVisible(True)
		self.lstInfo.setEnabled(True)
		if "Forbidden" in self.app.get("categories",[]) or "eduapp" in bundle:
			self.lstInfo.setVisible(False)
		self.lstInfo.setText(i18n["INSTALL"].upper())

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
		self._setListState(item)
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

	def _setListState(self,item):
		#REM 
		# DISABLED ATM
		self.btnInstall.setVisible(True)
		self.btnRemove.setVisible(False)
		self.btnLaunch.setVisible(False)
		self.btnZomando.setVisible(False)
		return
		#REM 
		bcurrent=item.background().color()
		bcolor=BKG_COLOR_INSTALLED.toRgb()
		if bcurrent==bcolor:
			rgb=bcurrent.getRgb()
			self.btnInstall.setVisible(False)
			if self.app.get("bundle",{}).get("zomando","")!="":
				self.btnLaunch.setVisible(False)
				if "zomando" in item.text():
					self.btnRemove.setVisible(False)
				else:
					self.btnLaunch.setVisible(True)
					self.btnRemove.setVisible(True)
			else:
				self.btnRemove.setVisible(True)
				self.btnLaunch.setVisible(True)
			self.lstInfo.setStyleSheet("selection-color:grey;selection-background-color:rgba({0},{1},{2},0.5);".format(rgb[0],rgb[1],rgb[2]))
		else:
			pkgState=self.app.get('state',{}).get("package",'1')
			if pkgState.isdigit()==True:
				pkgState=int(pkgState)
			else:
				self._onError()
				return()
			self.lstInfo.setStyleSheet("")
			self.btnInstall.setVisible(True)
			self.btnRemove.setVisible(False)
			self.btnLaunch.setVisible(False)
	#def _setLstState

	def _getIconFromApp(self,app):
		icn=QtGui.QIcon()
		if os.path.exists(app.get("icon")):
			icn=QtGui.QPixmap.fromImage(QtGui.QImage(app.get('icon','')))
		if icn.isNull():
		#something went wrong. Perhaps img it's gzipped
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'))
			icn=icn2.pixmap(ICON_SIZE,ICON_SIZE)
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
			#	self.btnZomando.setVisible(True)
				continue
		#	elif bundle=="zomando":
		#		continue
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
		if "eduapp" in bundles.keys():
			bundles.pop("eduapp")
		if len(bundles)<=0:
			self.btnInstall.setEnabled(False)
		#self.lstInfo.setMaximumWidth(self.lstInfo.sizeHintForColumn(0)+16)
		#self.lstInfo.setMinimumHeight(self.lstInfo.sizeHintForRow(0)*4.1)
		#self.lstInfo.setMaximumHeight(self.lstInfo.sizeHintForRow(0)*self.lstInfo.count()-1)
		#self.lstInfo.setCurrentRow(0)
		#self.lblTags.setMaximumWidth(self.lstInfo.sizeHintForColumn(0)+16)
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
			self.lblTags.linkActivated.connect(self._tagNav)
			self.app['name']=self.app.get('name','').replace(" ","")
		else:
			self._onError()
	#def _initScreen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

