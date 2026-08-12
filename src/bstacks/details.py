#!/usr/bin/python3
import json
from functools import partial
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QHBoxLayout,QApplication
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QIcon
from QtExtraWidgets import QSearchBox,QScrollLabel,QScreenShotContainer,QPushInfoButton,QFlowTouchWidget
from extras.i18n import *
from extras.constants import *
from wdg import btnApp,search
from wdg.flowBar import QFlowBar

class QDetailsPane(QWidget):
	ready=Signal()
	appLoaded=Signal()
	def __init__(self,*args,parent=None,**kwargs):
		self.__EXIT__=False
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.__initScreen__()
		self.appLoaded.connect(self._updateScreen)
		self.destroyed.connect(partial(QDetailsPane._onDestroy,self.__dict__))
		self.app={}
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["__EXIT__"]=True
	#def _onDestroy

	def _defSearch(self):
		wdg=search.QSearch()
		return(wdg)
	#def _defSearch

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

	def _defAppActions(self):
		def _setInstalled(*args):
			installBtn.hide()
			launchBtn.show()
			removeBtn.show()
		def _setZomando(*args):
			installBtn.hide()
			removeBtn.hide()
			launchBtn.show()
		def _setAvailable(*args):
			installBtn.show()
			removeBtn.hide()
			launchBtn.hide()
		wdg=QWidget()
		lay=QGridLayout(wdg)
		installBtn=QPushButton(i18n["INSTALL"])
		lay.addWidget(installBtn,0,0,1,1)
		removeBtn=QPushButton(i18n["REMOVE"])
		lay.addWidget(removeBtn,0,0,1,1)
		launchBtn=QPushButton(i18n["LAUNCH"])
		lay.addWidget(launchBtn)
		wdg._setInstalled=_setInstalled
		wdg._setZomando=_setZomando
		wdg._setAvailable=_setAvailable
		return(wdg)
	#def _defAppActions

	def _defAppDescription(self):
		def _setDescription(*args):
			desc.setText(args[0])
		wdg=QWidget()
		wdg.setDescription=_setDescription
		lay=QGridLayout(wdg)
		desc=QScrollLabel()
		desc.setGradient((224,214,255,50),(220,150,120,110))
		desc.label.x1=1.9
		desc.label.x2=1
		desc.label.setTextFormat(Qt.RichText)
		lay.addWidget(desc)
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

	def _defAppUrls(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		home=QPushButton()
		home.setStyleSheet("""text-align:left;padding:3px""")
		icn=QIcon.fromTheme("go-home")
		home.setIcon(icn)
		lay.addWidget(home)
		info=QPushButton()
		icn=QIcon.fromTheme("showinfo")
		info.setIcon(icn)
		info.setStyleSheet("""text-align:left;padding:3px""")
		lay.addWidget(info)
		wdg.home=home
		wdg.info=info
		return(wdg)
	#def _defAppUrls

	def __initScreen__(self):
		lay=QGridLayout(self)
		searchBox=self._defSearch()
		lay.addWidget(searchBox,0,0,1,3,Qt.AlignTop|Qt.AlignCenter)
		self.header=self._defAppHeader()
		lay.addWidget(self.header,1,0,1,1,Qt.AlignLeft)
		self.actions=self._defAppActions()
		lay.addWidget(self.actions,1,1,1,1,Qt.AlignRight)
		self.urls=self._defAppUrls()
		lay.addWidget(self.urls,1,2,1,1,Qt.Alignment(-2))
		self.screenshots=self._defScreenshots()
		lay.addWidget(self.screenshots,2,0,1,lay.columnCount(),Qt.AlignTop)
		self.description=self._defAppDescription()
		lay.addWidget(self.description,3,0,1,lay.columnCount())
		self.suggestions=self._defAppSuggestions()
		#lay.addWidget(self.suggestions,4,0,1,lay.columnCount())
		lay.setColumnStretch(0,1)
	#def __initScreen__

	def load(self,*args,category=False):
		#self.clean()
		self.btn=args[0]
		if hasattr(self.btn,"instBundle"):
			if self.btn.instBundle=="zomando":
				self.actions._setZomando()
			elif self.btn.instBundle!="":
				self.actions._setInstalled()
			else:
				self.actions._setAvailable()
		else:
			self.actions.hide()
		self.app=json.loads(self.rebost.refreshApp(self.btn.app["id"]))[0]
		self.appLoaded.emit()
	#def load

	def _getTags(self):
		tags=self.app["categories"]+self.app["keywords"]
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
		tags=["<a href=#{0}>#{0}</a>".format(t) for t in tags if len(t)>0 and t.lower() not in common]
		tags=list(set(tags))
		return(tags)
	#def _getTags(self):

	def _loadHeaderData(self):
		self.header.setIcon(self.btn.icon.pixmap())
		self.header.setName(self.app["name"])
		self.header.setSummary(self.app["summary"])
	#def _loadHeaderData

	def _loadDescription(self):
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

	def _loadSuggests(self):
		self.suggestions.clear()
		suggestions={}
		for suggestApp in self.app["suggests"]:
			app=json.loads(self.rebost.showApp(suggestApp))
			if len(app)>0:
				btn=QPushInfoButton(overlay=False)
				btn.defaultSize=36
				btn.setMaximumWidth(256)
				btn.setText(app[0]["name"])
				btn.loadImg(app[0]["icon"])
				btn.setFixedHeight(52)
				self.suggestions.addWidget(btn)
				self.suggestions.setFixedHeight(64)
	#def _loadSuggests

	def _loadUrls(self):
		self.urls.home.hide()
		self.urls.info.hide()
		if len(self.app["infopage"])>0:
			ttt=self.app["homepage"]
			if "appsedu" in self.app["homepage"]:
				lbl="Appsedu"
				icn=QIcon.fromTheme("applications-education")
				self.urls.home.setIcon(icn)
			else:
				lbl="Homepage"
				icn=QIcon.fromTheme("go-home")
				self.urls.home.setIcon(icn)
			self.urls.home.setText(lbl)
			self.urls.home.setToolTip(ttt)
			self.urls.home.show()
		if len(self.app["infopage"])>0:
			ttt=self.app["infopage"]
			lbl="Info"
			self.urls.info.setText(lbl)
			self.urls.info.setToolTip(ttt)
			self.urls.info.show()
	#def _loadUrls

	def _updateScreen(self,*args):
		self._loadHeaderData()
		self._loadDescription()
		self._loadScreenshots()
		self._loadSuggests()
		self._loadUrls()
	 #def _updateScreen(self,*args):

