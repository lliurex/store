#!/usr/bin/python3
import json
from functools import partial
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QHBoxLayout,QApplication,QSizePolicy
from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QIcon
from QtExtraWidgets import QSearchBox,QScrollLabel,QScreenShotContainer,QPushInfoButton,QFlowTouchWidget
from extras.i18n import *
from extras.constants import *
from wdg.categories import catsBar
from wdg import btnApp
from lib.threadLib import rebostQuery
from lib.helperLib import appHelper,auxiliary
_ = gettext.gettext

class QDetailsPane(QWidget):
	ready=Signal()
	search=Signal(str)
	loadCategory=Signal(str)
	requestInstall=Signal(dict,str,"PyObject")
	requestRemove=Signal(dict,str,"PyObject")
	requestLaunch=Signal(dict,str,"PyObject")
	def __init__(self,*args,parent=None,**kwargs):
		self.__EXIT__=False
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.app={"id":None}
		self.__initScreen__()
		self.destroyed.connect(partial(QDetailsPane._onDestroy,self.__dict__))
		self.rebostQuery=rebostQuery(rebost=self.rebost)
		self.rebostQuery.queryCompleted.connect(self._updateScreen)
		self.helper=appHelper()
		self.aux=auxiliary()
		self.requested=""
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["__EXIT__"]=True
	#def _onDestroy

	def _search(self,*args):
		token=args[0]
		if isinstance(token,str):
			self.search.emit(token)
		elif isinstance(token,tuple):
			self.search.emit(token[0])
		else:
			cat=token.property("metadata")
			self.loadCategory.emit(cat)
		pass
	#def _search

	def _defAppHeader(self):
		def _setIcon(*args):
			icn.setPixmap(args[0])
		def _setName(*args):
			name.setText("<strong>{0}</strong>".format(args[0]))
		def _setSummary(*args):
			summary.setText(args[0])
		wdg=QWidget()
		wdg.setIcon=_setIcon
		wdg.setName=_setName
		wdg.setSummary=_setSummary
		lay=QGridLayout(wdg)
		icn=QLabel()
		icn.setMaximumHeight(128)
		lay.addWidget(icn,0,0,2,1,Qt.AlignCenter|Qt.AlignRight)
		name=QLabel()
		lay.addWidget(name,0,1,1,1,Qt.AlignLeft)
		summary=QLabel()
		lay.addWidget(summary,1,1,1,1,Qt.AlignLeft)
		return(wdg)
	#def _defAppHeader(self):

	def _installApp(self):
		self.rebostQuery.setQuery("refresh",self.app["id"])
		self.rebostQuery.start()
		self.requested="install"
	#def _installApp
		
	def _removeApp(self):
		self.rebostQuery.setQuery("refresh",self.app["id"])
		self.rebostQuery.start()
		self.requested="remove"
	#def _removeApp

	def _launchApp(self):
		self.requested="launch"
		self._updateScreen()
	#def _launchApp

	def _defAppActions(self):
		def _setInstalled(*args):
			installBtn.hide()
			launchBtn.show()
			removeBtn.show()
		def _setZomando(*args):
			installBtn.show()
			installBtn.setText(i18n["LAUNCH"])
			installBtn.setIcon(launchIcon)
			removeBtn.hide()
			launchBtn.hide()
		def _setAvailable(*args):
			installBtn.show()
			removeBtn.hide()
			launchBtn.hide()
		wdg=QWidget()
		lay=QGridLayout(wdg)
		installBtn=QPushButton(i18n["INSTALL"])
		installIcon=QIcon().fromTheme("install")
		installBtn.setIcon(installIcon)
		installBtn.clicked.connect(self._installApp)
		lay.addWidget(installBtn,0,0,1,1)
		launchBtn=QPushButton(i18n["LAUNCH"])
		launchBtn.clicked.connect(self._launchApp)
		launchIcon=QIcon().fromTheme("system-run")
		launchBtn.setIcon(launchIcon)
		lay.addWidget(launchBtn,0,0,1,1)
		removeBtn=QPushButton(i18n["REMOVE"])
		removeIcon=QIcon().fromTheme("uninstall")
		removeBtn.setIcon(removeIcon)
		removeBtn.clicked.connect(self._removeApp)
		lay.addWidget(removeBtn)
		self.infoBtn=QPushButton("Info")
		icn=QIcon.fromTheme("showinfo")
		self.infoBtn.setIcon(icn)
		self.infoBtn.setStyleSheet("""text-align:left;padding:3px""")
		self.infoBtn.setCheckable(True)
		self.infoBtn.toggled.connect(self._showAppInfo)
		lay.addWidget(self.infoBtn,0,1,1,1)
		wdg._setInstalled=_setInstalled
		wdg._setZomando=_setZomando
		wdg._setAvailable=_setAvailable
		return(wdg)
	#def _defAppActions

	def _defAppDescription(self):
		def _setDescription(*args):
			desc=args[0].replace("\n","<br>").capitalize()
			lblDesc.setText(desc)
		wdg=QWidget()
		wdg.setDescription=_setDescription
		lay=QGridLayout(wdg)
		lblDesc=QScrollLabel()
		lblDesc.setGradient((224,214,255,50),(220,150,120,110))
		lblDesc.label.x1=1.9
		lblDesc.label.x2=1
		lblDesc.label.setTextFormat(Qt.RichText)
		lblDesc.linkActivated.connect(self._search)
		lay.addWidget(lblDesc)
		wdg.setStyleSheet("""margin-bottom:0px""")
		return(wdg)
	#def _defAppDescription

	def _defScreenshots(self):
		wdg=QScreenShotContainer()
		wdg.w=96
		wdg.h=96
		return(wdg)
	#def _defScreenshots

	def _defAppSuggestions(self):
		def addWidget(*args):
			wdg.layout().addWidget(args[0])
		def clear(*args):
			while wdg.layout().count():
				chld=wdg.layout().takeAt(0)
				if chld.widget():
					chld.widget().deleteLater()
		wdg=QWidget()
		wdg.addWidget=addWidget
		wdg.clear=clear
		lay=QHBoxLayout(wdg)
		wdg.setFixedHeight(48)
		return(wdg)
	#def _defAppSuggestions

	def _showAppInfo(self):
		show=self.infoBtn.isChecked()
		self.appInfo.setVisible(show)
		if len(self.app.get("screenshots",[]))>0:
			self.screenshots.setVisible(not show)
	#def _showAppInfo

	def _defAppCategories(self):
		cats=catsBar(rebost=self.rebost)
		cats.selected.connect(self._search)
		cats.setStyleSheet("QScrollArea {border:0px;margin:0px;padding:0px;background-color:rgba(0,0,0,0);}");
		cats.setStyleSheet("padding:0px;margin:0px;border:0px;background-color:rgba(0,0,0,0);");
		cats.showScrollBar(True)
		cats.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		cats.defaultSize=24
		return(cats)
	#def _defAppCategories

	def _defAppInfo(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		cats=self._defAppCategories()
		lay.addWidget(cats,0,0,1,5)
		lblCandidate=QLabel()
		lay.addWidget(lblCandidate,1,0,1,1)
		lblRelease=QLabel()
		lay.addWidget(lblRelease,2,0,1,1)
		lblInstalled=QLabel()
		lay.addWidget(lblInstalled,3,0,1,1)
		btnHomepage=QPushButton()
		btnHomepage.setStyleSheet("""text-align:left;""")
		icn=QIcon.fromTheme("go-home")
		btnHomepage.setIcon(icn)
		btnHomepage.setIconSize(QSize(24,24))
		btnHomepage.setMaximumHeight(btnHomepage.iconSize().height()+2)
		lay.addWidget(btnHomepage,1,1,1,1,Qt.AlignLeft)
		btnInfopage=QPushButton()
		btnInfopage.setStyleSheet("""text-align:left;""")
		icn=QIcon.fromTheme("showinfo")
		btnInfopage.setIconSize(QSize(24,24))
		btnInfopage.setMaximumHeight(btnInfopage.iconSize().height()+2)
		lay.addWidget(btnInfopage,2,1,1,1,Qt.AlignLeft)
		btnInfopage.setIcon(icn)
		tags=QFlowTouchWidget()
		tags.setMaximumHeight(96)
		lay.addWidget(tags,1,4,4,1,Qt.Alignment(-1))
		wdg.cats=cats
		wdg.tags=tags
		wdg.candidate=lblCandidate
		wdg.release=lblRelease
		wdg.installed=lblInstalled
		wdg.homepage=btnHomepage
		wdg.infopage=btnInfopage
		return(wdg)
	#def _defAppInfo

	def _defEmptyContainer(self):
		wdg=QWidget()
		glay=QGridLayout(wdg)
		lblIcn=QLabel()
		icn=QIcon.fromTheme("align-none")
		pxm=icn.pixmap(self.width(),self.height(),QIcon.Mode.Disabled)
		lblIcn.setPixmap(pxm)
		glay.addWidget(lblIcn,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		lblTxt=QLabel()
		lblTxt.setOpenExternalLinks(True)
		lblTxt.setStyleSheet("""padding:5px;""")
		fLbl=lblTxt.font()
		lblTxt.setAutoFillBackground(True)
		fLbl.setPointSize(fLbl.pointSize()+4)
		lblTxt.setFont(fLbl)
		wdg.setText=lblTxt.setText
		glay.addWidget(lblTxt,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		return(wdg)
	#def _defEmptyContainer

	def __initScreen__(self):
		lay=QGridLayout(self)
		self.container=QWidget()
		clay=QGridLayout(self.container)
		self.header=self._defAppHeader()
		clay.addWidget(self.header,0,0,1,1,Qt.AlignLeft)
		self.actions=self._defAppActions()
		clay.addWidget(self.actions,0,1,1,1,Qt.AlignRight)
		self.screenshots=self._defScreenshots()
		clay.addWidget(self.screenshots,1,0,1,clay.columnCount(),Qt.AlignTop)
		self.appInfo=self._defAppInfo()
		clay.addWidget(self.appInfo,1,0,1,clay.columnCount(),Qt.AlignTop)
		self.appInfo.hide()
		self.description=self._defAppDescription()
		clay.addWidget(self.description,2,0,1,clay.columnCount())
		self.suggestions=self._defAppSuggestions()
		#lay.addWidget(self.suggestions,4,0,1,lay.columnCount())
		clay.setColumnStretch(0,1)
		self.emptyContainer=self._defEmptyContainer()
		lay.addWidget(self.container,0,0,lay.rowCount(),lay.columnCount())
		lay.addWidget(self.emptyContainer,0,0,lay.rowCount(),lay.columnCount())
		self.emptyContainer.hide()
	#def __initScreen__
	
	def _clearScreen(self):
		self.app={}
		self.requested=""
	#def _clearScreen

	def loadFromId(self,*args):
		self._clearScreen()
		if isinstance(args[0],str):
			self.app["id"]=args[0]
		else:
			self.btn=args[0]
			self.app["id"]=args[0].property("metadata")
		self.rebostQuery.setQuery("refresh",self.app["id"])
		self.rebostQuery.start()
	#def loadFromId

	def _showActions(self,installed):
		if installed=="zomando" or "unknown" in self.app.get("bundle",{}):
			if self.app["name"]==self.app.get("bundle",{}).get("unknown",""):
				self.actions._setZomando()
			elif installed!="":
				self.actions._setInstalled()
			else:
				self.actions._setAvailable()
		elif installed!="":
			self.actions._setInstalled()
		else:
			self.actions._setAvailable()
	#def _showActions

	def load(self,*args,category=False):
		self._clearScreen()
		self.btn=args[0]
		if hasattr(self.btn,"instBundle"):
			self._showActions(self.btn.instBundle)
		elif self.app.get("unavailable",False)==True:
			self.actions.hide()
		else:
			self.actions._setAvailable()
		self.app=self.btn.app
		if self.app["description"]=="":
			self.rebostQuery.setQuery("refresh",self.app["id"])
			self.rebostQuery.start()
		else:
			self._updateScreen()
	#def load

	def _getTags(self):
		tags=self.app["keywords"]
		common=["gtk",
			"qt",
			"kde",
			"gnome",
			"xfce",
			"system",
			"desktop",
			"x86-64",
			self.app["name"],
			"software",
			"app",
			"release",
			"stable",
			"gplv2-later",
			"appimage",
			"release-stable"]
		tags=["<a href={0}>{0}</a>".format(t.replace(" ","")) for t in tags if len(t.strip())>1 and t.lower() not in common]
		tags=list(set(tags))
		return(tags)
	#def _getTags(self):

	def _loadHeaderData(self):
		self.header.setIcon(self.btn.icon.pixmap())
		self.header.setName(self.app["name"])
		self.header.setSummary(self.app["summary"])
	#def _loadHeaderData

	def _loadDescription(self):
		self.description.setDescription("")
		desc="<p>{}</p>".format(self.app["description"])
		tags=self._getTags()
		if len(tags)>0:
			desc+="<hr>"
			for tag in tags:
				desc+="{} ".format(tag)
		self.description.setDescription(desc)
	#def _loadDescription

	def _loadScreenshots(self):
		self.screenshots.clear()
		self.screenshots.show()
		for scr in self.app["screenshots"]:
			self.screenshots.addImage(scr)
		if len(self.app["screenshots"])==0:
			self.screenshots.hide()
	#def _loadScreenshots

	def _loadUrls(self):
		return
		self.urls.home.hide()
		self.urls.info.hide()
		if len(self.app["homepage"])>0:
			ttt=self.app["homepage"]
			if "appsedu" in self.app["homepage"]:
				lbl="Appsedu"
				icn=QIcon.fromTheme("applications-education")
			else:
				lbl="Homepage"
				icn=QIcon.fromTheme("go-home")
			self.urls.home.setIcon(icn)
			self.urls.home.setText(lbl)
			self.urls.home.setToolTip(ttt)
			self.urls.home.show()
		if len(self.app["infopage"])>0:
			ttt=self.app["infopage"]
			if self.urls.home.text()=="Appsedu":
				lbl="Homepagge"
				icn=QIcon.fromTheme("go-home")
			else:
				lbl="Info"
				icn=QIcon.fromTheme("showinfo")
			self.urls.info.setIcon(icn)
			self.urls.info.setText(lbl)
			self.urls.info.setToolTip(ttt)
			self.urls.info.show()
	#def _loadUrls

	def _loadAppInfo(self):
		data={}
		self.appInfo.cats.clean()
		self.appInfo.cats.loadCategories(self.app["categories"])
		self.appInfo.cats.setFixedHeight(self.appInfo.cats.defaultSize+MARGIN)
		self.appInfo.tags.clean()
		for tag in self._getTags():
			lbl=QLabel(tag)
			lbl.linkActivated.connect(self._search)
			self.appInfo.tags.addWidget(lbl)
		candidates=self.helper.getBundlesByPriority(self.app)
		for candidate in candidates.values():
			bundle,release=candidate.split(" ")
			if bundle=="unknown":
				bundle="zomando"
			self.appInfo.candidate.setText("Bundle: {}".format(bundle))
			self.appInfo.release.setText("Ver: {}".format(release))
			break
		installed=self.helper.getInstalledBundle(self.app)
		self.appInfo.installed.setText("{0}: {1}".format(i18n["INSTALLED"],installed))
		self._showActions(installed)
		ttt=self.app.get("homepage","")
		if isinstance(ttt,str)==False:
			ttt=""
		if "appsedu" in ttt:
			lbl="Appsedu"
			icn=QIcon("/usr/share/store/rsrc/appsedu128x128.png")
		elif "github.com/lliurex" in ttt:
			lbl="Info"
			icn=QIcon.fromTheme("showinfo")
		else:
			lbl="Homepage"
			icn=QIcon.fromTheme("go-home")
		self.appInfo.homepage.setText(lbl)
		self.appInfo.homepage.setIcon(icn)
		self.appInfo.homepage.setToolTip(ttt)
		if len(self.app["infopage"])>0 and "github.com/lliurex" not in ttt:
			ttt=self.app["infopage"]
			self.appInfo.infopage.show()
			if self.appInfo.homepage.text()=="Appsedu":
				lbl="Homepage"
				icn=QIcon.fromTheme("go-home")
			else:
				lbl="Info"
				icn=QIcon.fromTheme("showinfo")
			self.appInfo.infopage.setText(lbl)
			self.appInfo.infopage.setIcon(icn)
			self.appInfo.infopage.setToolTip(ttt)
			self.appInfo.infopage.setFixedWidth(self.appInfo.homepage.sizeHint().width()+MARGIN)
			self.appInfo.homepage.setFixedWidth(self.appInfo.infopage.width())
		else:
			self.appInfo.infopage.hide()
	#def _loadAppInfo

	def _updateScreen(self,*args):
		self.infoBtn.setChecked(False)
		if len(args)>0:
			if len(args[0])>0:
					self.app=args[0]
		if "name" in self.app.keys():
			self.emptyContainer.hide()
			self.container.show()
			if hasattr(self,"btn")==False:
				self.btn=btnApp.QAppButton(self.app)
			if self.requested!="":
				if self.requested=="install":
					self.requestInstall.emit(self.app,"",self.btn.icon.pixmap())
				elif self.requested=="remove":
					self.requestRemove.emit(self.app,"",self.btn.icon.pixmap())
				if self.requested=="launch":
					self.requestLaunch.emit(self.app,self.btn.property("instBundle"),self.btn.icon.pixmap())
			else:
				self.requested=""
				self._loadHeaderData()
				self._loadDescription()
				self._loadScreenshots()
				self._loadAppInfo()
				self.appInfo.setMinimumSize(self.screenshots.width(),self.screenshots.sizeHint().height())
				self._loadUrls()
		else:
			self.emptyContainer.setText("<p><strong>App {0} {1}</strong></p>".format(self.app["id"],i18n["ERRNOTFOUND"]))
			self.emptyContainer.show()
			self.container.hide()
		self.ready.emit()
	 #def _updateScreen(self,*args):

	def refreshApp(self,app):
		if isinstance(app,str):
			self.app=json.loads(app)
			if isinstance(self.app,list):
				self.app=self.app[0]
		else:
			self.app=app
		self.requested=""
		installed=self.helper.getInstalledBundle(self.app)
		self.appInfo.installed.setText("{0}: {1}".format(i18n["INSTALLED"],installed))
		self._showActions(installed)
	#def refreshApp
