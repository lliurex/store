#!/usr/bin/python3
import sys,signal
import os,json,time
import subprocess
from functools import partial
from random import shuffle
from PySide6.QtWidgets import QLabel, QWidget,QHBoxLayout,QVBoxLayout,QSizePolicy,QPushButton,QGridLayout,QApplication
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QScreenShotContainer
import gettext
import extras.css as css
from extras.constants import *
from extras.i18n import *
import lib.rss as rss
from wdg.btnRebost import QPushButtonRebostApp
from wdg.blog import blogBar
from wdg.choice import choiBar

class main(QWidget):
	clickedCategory=Signal("PyObject")
	clickedApp=Signal("PyObject","PyObject","PyObject")
	requestInstallApp=Signal("PyObject",dict,"PyObject")
	loaded=Signal()
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.destroyed.connect(partial(main._onDestroy,self.__dict__))
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._debug("home load")
		self.setStyleSheet(css.homePanel())
		self.setObjectName("mp")
		self.th=[]
		self._rebost=args[0]
		self._rebost.urlEnded.connect(self._setAppseduData)
		self._rebost.gacEnded.connect(self._setAppsByCat)
		self.appsEduApps=[]
		self.btns={}
		layout=QGridLayout()
		layout.setVerticalSpacing(0)
		self.setLayout(layout)
		self._stop=False
		self.oldCursor=self.cursor()
		self.itemsPerCat=4
		self.cachedUrls=[]
		if QApplication.primaryScreen().size().width()>1300:
			self.itemsPerCat=5
		self.__initScreen__()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Home: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		for th in selfDict.get("th",[]):
			th.blockSignals(True)
			th.requestInterruption()
			th.deleteLater()
			th.stop()
			th.quit()
			th.wait()
	#def _onDestroy

	def showEvent(self,*args,**kwargs):
		#Ensure that there's info after all
		if self.choiceApps.count()==1:
			self.choiceApps.loadChoice()
		if len(self.appsByCat.children())<=1:
			self._getAppsByCat()
		if self.blog.count()==0:
			self.blog.loadBlog()
		if len(self.appsEduApps)<=6: #6 because, well, why not?
			self._getAppsedu()
	#def showEvent

	def _processRss(self,*args,**kwargs):
		url=args[0]
		apps=args[1]
		if len(apps)>0:
			if apps["0"]["type"]=="appsedu":
				urls=[]
				for idx in range(0,min(len(apps),10)):
					if self._stop==True:
						break
					url=apps[str(idx)]["link"]
					if url not in self.cachedUrls:
						urls.append(url)
				#qt often gets breathless
				time.sleep(0.1)
				self._rebost.setAction("urlSearch",urls)
				self._rebost.start()
				#self._rebost.wait()
	#def _processRss(self,*args,**kwargs):

	def _openBlog(self,*args):
		blogTag=args[1]
		blogUrl=blogTag.get("homepage")
		cmd=["xdg-open",blogUrl]
		subprocess.run(cmd)
	#def _openBlog

	def _emitInstallApp(self,*args):
		btn=args[0]
		icon=btn.iconUri.pixmap()
		app=args[1]
		self.requestInstallApp.emit(btn,app,icon)
	#def _emitInstallApp

	def _setAppseduData(self,*args):
		app=json.loads(args[0])
		if len(app)==0:
			return
		hp=app[0]["homepage"]
		if hp not in self.cachedUrls:
			self.cachedUrls.append(hp)
		cont=0
		for btn in self.appsEdu.children():
			if not isinstance(btn,QPushButtonRebostApp):
				continue
			if len(btn.app.get("name",""))>0:
				continue
			if isinstance(app,list) and len(app)>0:
				if app[0].get("name") in self.appsEduApps:
					continue
				self.appsEduApps.append(app[0].get("name"))
				btn.setApp(app[0],updateIcon=True)
				btn._applyDecoration()
				btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
				btn.install.connect(self._emitInstallApp)
				btn.clicked.connect(self._loadApp)
				btn.lblFlyIcon.setVisible(True)
				btn.setVisible(True)
				break
			if cont>=len(self.appsEdu.children()):
				break
			cont+=1
		self.appsEdu.setCursor(self.oldCursor)
		self.loaded.emit()
	#def _setAppseduData

	def _loadApp(self,*args):
		app=args[1]
		btn=args[0]
		self.clickedApp.emit(self,btn,app)
	#def _loadApp
	
	def _getAppsedu(self):
		rssparser=rss.rssParser()
		rssparser.appsEnded.connect(self._processRss)
		rssparser.feed="appsedu"
		rssparser.start()
		self.th.append(rssparser)
	#def _getAppsedu

	def reloadAppsedu(self):
		i=0
		pxm=QtGui.QPixmap()
		for chld in self.appsEdu.children():
			if isinstance(chld,QPushButtonRebostApp):
				chld.setCursor(QtGui.QCursor(Qt.WaitCursor))
				chld.setApp({})
				chld.iconUri.setEnabled(False)
				#chld.lblFlyIcon.hide()
				if i<3:
					#btn.setObjectName("mp")
					pxm.load(os.path.join(RSRC,"appsedu128x128.png"))
					chld.loadFullScreen(pxm)
				else:
					chld.hide()
				i+=1
		self.appsEduApps=[]
		self._getAppsedu()
	#def reloadAppsedu

	def _loadCategory(self,*args):
		app=args[1]
		self.clickedCategory.emit(app["name"])
	#def _loadCategory

	def _setAppsByCat(self,*args):
		categoryApps=args[0]
		apps={}
		for cat in categoryApps.keys():
			apps[len(categoryApps[cat])]=cat
		lenApps=list(apps.keys())
		lenApps.sort()
		lenApps.reverse()
		lay=self.appsByCat.layout()
		for idx in lenApps[:5]:
			icn=apps[idx].lower()
			if icn=="utility":
				icn="utilities"
			elif icn=="game":
				icn="games"
			elif ("audio" in icn) or ("video" in icn):
				icn="multimedia"
			iconPath="/usr/share/icons/breeze/categories/" # Bad idea. Nested for, hardcoded paths, filename assumptions, non-agnostic... 
			for size in ["24","32"]:
				wrkPath=os.path.join(iconPath,size)
				if os.path.exists(wrkPath):
					for f in os.scandir(wrkPath):
						if icn in f.name:
							icn=f.path
							break
				if "applications" in icn:
					break
			if "applications" not in icn:
				icn="applications-other"
			app={"name":apps[idx],"icon":icn,"pkgname":apps[idx]}
			btn=QPushButtonRebostApp(app,iconSize=64)
			btn.autoUpdate=True
			btn.clicked.connect(self._loadCategory)
			#btn.setFixedSize(QSize(ICON_SIZE*2,ICON_SIZE*1.5))
			btn.setCompactMode(True)
			lay.addWidget(btn,Qt.AlignTop)
		lay.addSpacing(MARGIN*8)
		self.appsByCat.setCursor(QtGui.QCursor(self.oldCursor))
		self.loaded.emit()
	#def _setAppsByCat

	def _getAppsByCat(self):
		self._debug("Get apps per category")
		self._rebost.setAction("getAppsInstalledPerCategory")
		self._rebost.start()
		#self._rebost.wait()
	#def _getAppsByCat

	def _defAppsByCat(self):
		wdg=QWidget()
		lay=QHBoxLayout()
		lay.setSpacing(MARGIN*8)
		lay.addSpacing(MARGIN*8)
		wdg.setLayout(lay)
		return(wdg)
	#def _defAppsByCategory:

	def _defBlogBar(self):
		wdg=blogBar()
		#wdg.selected.connect(self._emitLoadUrl)
		return(wdg)
	#def _defBlogBar

	def _defBlog(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lblBlog=QLabel("{}<hr>".format(i18n["HOME_LBL_BLOG"]))
		lblBlog.setObjectName("lbl")
		lay.addWidget(lblBlog,0,0)
		btnBlog=QPushButton()
		btnBlog.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		btnBlog.setToolTip("Blog LliureX")
		icn=QtGui.QIcon.fromTheme("list-add")
		btnBlog.setIcon(icn)
		dataBlog={"homepage":"https://portal.edu.gva.es/blogs/s1/lliurex/"}
		btnBlog.clicked.connect(lambda x: self._openBlog("",dataBlog))
		lay.addWidget(btnBlog,0,0,Qt.AlignRight)
		#self.blog=self._defBlog()
		self.blog=self._defBlogBar()
		self.blog.loadBlog()
		lay.addWidget(self.blog,1,0)
		return(wdg)
	#def _defBlog

	def _defChoiceApps(self):
		wdg=choiBar(rebost=self._rebost.rc)
		#wdg.selected.connect(self._emitLoadUrl)
		return(wdg)
	#def _defChoiceApps

	def _defChoice(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lay.setSpacing(0)
		lblChoi=QLabel("{}<hr>".format(i18n["HOME_LBL_CHOICE"]))
		lay.addWidget(lblChoi,0,0)
		lblChoi.setObjectName("lbl")
		self.choiceApps=self._defChoiceApps()
		self.choiceApps.loadChoice()
		lay.addWidget(self.choiceApps,1,0)
		return(wdg)
	#def _defChoice

	def _defAppseduApps(self):
		wdg=QWidget()
		layout=QHBoxLayout()
		wdg.setLayout(layout)
		layout.setSpacing(MARGIN*4)
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		pxm=QtGui.QPixmap()
		for i in range(0,self.itemsPerCat):
			btn=QPushButtonRebostApp("{}",iconSize=int(ICON_SIZE)/2)
			btn.clicked.connect(self._loadApp)
			sh=self.screen().size().height()
				#btn._showBtn=False
			btn.setMinimumHeight(min(220,int(sh/5)))
			btn.lblFlyIcon.hide()
			#btn.setCompactMode(True)
			btn.setCursor(QtGui.QCursor(Qt.WaitCursor))
			btn.setMaximumWidth(IMAGE_PREVIEW/3)
			btn.autoUpdate=True
			if i<self.itemsPerCat-1:
				#btn.setObjectName("mp")
				pxm.load(os.path.join(RSRC,"appsedu128x128.png"))
				btn.loadFullScreen(pxm)
			else:
				btn.setVisible(False)
			layout.addWidget(btn,Qt.AlignCenter)
		return(wdg)
	#def _defAppseduApps

	def _defAppsedu(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lblAppsedu=QLabel("{}<hr>".format(i18n["HOME_LBL_APPSEDU"]))
		lblAppsedu.setObjectName("lbl")
		lay.addWidget(lblAppsedu,0,0,Qt.AlignBottom)
		btnApps=QPushButton()
		#btnApps.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		btnApps.setToolTip("Appsedu")
		icn=QtGui.QIcon.fromTheme("list-add")
		btnApps.setIcon(icn)
		dataApps={"homepage":"https://portal.edu.gva.es/appsedu/aplicacions-lliurex/"}
		btnApps.clicked.connect(lambda x: self._openBlog("",dataApps))
		lay.addWidget(btnApps,0,0,Qt.AlignRight)
		self.appsEdu=self._defAppseduApps()
		lay.addWidget(self.appsEdu,1,0)
		return(wdg)
	#def _defAppsedu

	def __initScreen__(self):
		#Blog
		blog=self._defBlog()
		self.layout().addWidget(blog,0,0)
		#Editor's choice
		choi=self._defChoice()
		self.layout().addWidget(choi,1,0)
		#Appsedu
		appsedu=self._defAppsedu()
		self.layout().addWidget(appsedu,2,0)
		#Categories
		lblCats=QLabel("<br>{}<hr>".format(i18n["HOME_LBL_CATEGORIES"]))
		lblCats.setObjectName("lbl")
		#self.layout().addWidget(lblCats,6,0)
		self.appsByCat=self._defAppsByCat()
		self.layout().setRowStretch(0,4)
		self.layout().setRowStretch(1,3)
		self.layout().setRowStretch(2,0)
		self.layout().setContentsMargins(0,0,0,0)
		#self.layout().addWidget(self.appsByCat,7,0)
	#def __initScreen__

	def updateScreen(self):
		self.blog.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self.appsEdu.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self.appsByCat.setCursor(QtGui.QCursor(Qt.WaitCursor))
		rssparser=rss.rssParser()
		rssparser.appsEnded.connect(self._processRss)
		rssparser.loadCache()
	#	self._getAppsByCat()
	#	self._getBlog()
	#	self._getAppsedu()
	#def updateScreen

	def updateBtn(self,btn,app):
		if btn!=None:
			for chld in self.appsEdu.children():
				if isinstance(chld,QPushButtonRebostApp):
					if chld==btn:
						btn.setApp(app)
						break
	#def updateBtn
