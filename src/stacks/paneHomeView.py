#!/usr/bin/python3
import sys,signal
import os,json,time
import subprocess
from functools import partial
from PySide6.QtWidgets import QLabel, QWidget,QHBoxLayout,QVBoxLayout,QSizePolicy,QPushButton,QGridLayout,QApplication
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QScreenShotContainer
import gettext
import css
import rss
from constants import *
from btnRebost import QPushButtonRebostApp
import gettext
_ = gettext.gettext

i18n={"LBL_BLOG":"Blog entries",
	"LBL_APPSEDU":"Latest apps in appsedu",
	"LBL_CATEGORIES":"Relevant categories"}

class main(QWidget):
	clickedCategory=Signal("PyObject")
	clickedBlog=Signal("PyObject")
	clickedApp=Signal("PyObject","PyObject","PyObject")
	requestInstallApp=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.destroyed.connect(partial(main._onDestroy,self.__dict__))
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._debug("home load")
		self.setStyleSheet(css.tablePanel())
		self.setObjectName("mp")
		self.th=[]
		self._rebost=args[0]
		self._rebost.urlEnded.connect(self._setAppseduData)
		self._rebost.gacEnded.connect(self._setAppsByCat)
		self.btns={}
		layout=QGridLayout()
		layout.setVerticalSpacing(0)
		self.setLayout(layout)
		self._stop=False
		self.oldCursor=self.cursor()
		self.__initScreen__()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Home: {}".format(msg))
	#def _debug

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		if selfDict.get("th",[])!=[]:
			for th in selfDict["th"]:
				th.blockSignals(True)
				th.requestInterruption()
				th.deleteLater()
				th.quit()
				th.wait()
	#def _onDestroy

	def _processRss(self,*args,**kwargs):
		url=args[0]
		apps=args[1]
		if len(apps)>0:
			if apps[0]["type"]=="appsedu":
				urls=[]
				for idx in range(0,min(len(apps),10)):
					if self._stop==True:
						break
					url=apps[idx]["link"]
					urls.append(url)
				self._rebost.setAction("urlSearch",urls)
				self._rebost.start()
					#self._rebost.wait()
			else:
				if self._stop==False:
					self._setBlogData(apps)
	#def _processRss(self,*args,**kwargs):

	def _setBlogData(self,*args):
		blogRss=args[0]
		cont=0
		for btn in self.blog.children():
			if not isinstance(btn,QPushButtonRebostApp):
				continue
			img=blogRss[cont].get("img","")
			if img=="":
				continue
			app={"name":"",
				"summary":"<a href=\"{0}\">{1}</a><br>".format(blogRss[cont]["link"],blogRss[cont]["title"]),
				"homepage":"{0}".format(blogRss[cont]["link"]),
				"icon":img,
				"pkgname":"",
				"description":""}
			btn.setApp(app)
			btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
			cont+=1
		self.blog.setCursor(self.oldCursor)
		#Blog chargees without rebost needs so it's a good point to check if rebost data has been loaded
		if self.appsByCat.cursor()==Qt.WaitCursor and self_rebost.isRunning()==False:
			self._getAppsByCat()
		if self.appsEdu.cursor()==Qt.WaitCursor and self_rebost.isRunning()==False:
			self._getAppsedu()
	#def _setBlogData

	def _openBlog(self,*args):
		blogTag=args[1]
		blogUrl=blogTag.get("homepage")
		cmd=["xdg-open",blogUrl]
		subprocess.run(cmd)
	#def _openBlog

	def _getBlog(self):
		rssparser=rss.rssParser()
		rssparser.rssEnded.connect(self._processRss)
		rssparser.feed="blog"
		rssparser.start()
		self.th.append(rssparser)
	#def _getBlog(self):

	def _defBlog(self):
		wdg=QWidget()
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout=QHBoxLayout()
		layout.setSpacing(0)
		for i in range(0,5):
			btn=QPushButtonRebostApp("{}",iconSize=256)
			btn.showBtn=False
			btn.setCursor(QtGui.QCursor(Qt.WaitCursor))
			btn.setObjectName("mp")
			btn.iconSize=IMAGE_PREVIEW/1.2
			btn.iconUri.setMaximumHeight(IMAGE_PREVIEW/1.2)
			btn.label.setMinimumWidth(IMAGE_PREVIEW)
			btn.autoUpdate=True
			btn.clicked.connect(self._openBlog)
			layout.addWidget(btn)
		wdg.setLayout(layout)
		return(wdg)
	#def _defBlog

	def _emitInstallApp(self,*args):
		self.requestInstallApp.emit(args[0],args[1])
	#def _emitInstallApp

	def _setAppseduData(self,*args):
		app=json.loads(args[0])
		for btn in self.appsEdu.children():
			if not isinstance(btn,QPushButtonRebostApp):
				continue
			if isinstance(app,list) and len(app)>0 and btn.app.get("summary","")=="":
				btn.setApp(app[0])
				btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
				btn.install.connect(self._emitInstallApp)
				btn.setVisible(True)
				break
		self.appsEdu.setCursor(self.oldCursor)
		#Ensure that there're categories after all
		if self.appsByCat.cursor()==Qt.WaitCursor and self_rebost.isRunning()==False:
			self._getAppsByCat()
	#def _setAppseduData

	def _loadApp(self,*args):
		app=args[1]
		btn=args[0]
		self.clickedApp.emit(self,btn,app)
	#def _loadApp
	
	def _getAppsedu(self):
		rssparser=rss.rssParser()
		rssparser.rssEnded.connect(self._processRss)
		rssparser.feed="appsedu"
		rssparser.start()
		self.th.append(rssparser)
	#def _getAppsedu

	def _defAppsedu(self):
		wdg=QWidget()
		layout=QHBoxLayout()
		wdg.setLayout(layout)
		layout.setSpacing(32)
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		for i in range(0,10):
			btn=QPushButtonRebostApp("{}",iconSize=int(ICON_SIZE/2))
			btn.setCursor(QtGui.QCursor(Qt.WaitCursor))
			btn.setMaximumWidth(IMAGE_PREVIEW/3)
			btn.autoUpdate=True
			btn.setVisible(False)
			btn.clicked.connect(self._loadApp)
			layout.addWidget(btn,Qt.AlignCenter)
		return(wdg)
	#def _defAppsedu

	def _loadCategory(self,*args):
		app=args[1]
		self.clickedCategory.emit(app["name"])
	#def _loadCategory

	def _setAppsByCat(self,*args):
		categoryApps=json.loads(args[0])
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
			app={"name":apps[idx],"icon":"applications-{}".format(icn),"pkgname":apps[idx],}
			btn=QPushButtonRebostApp(app)
			btn.autoUpdate=True
			btn.clicked.connect(self._loadCategory)
			btn.setFixedSize(QSize(ICON_SIZE*2,ICON_SIZE*1.5))
			btn.showBtn=False
			lay.addWidget(btn,Qt.AlignTop)
		self.appsByCat.setCursor(QtGui.QCursor(self.oldCursor))
	#def _setAppsByCat

	def _getAppsByCat(self):
		self._debug("Get apps per category")
		self._rebost.setAction("getAppsPerCategory")
		self._rebost.start()
	#def _getAppsByCat

	def _defAppsByCat(self):
		wdg=QWidget()
		lay=QHBoxLayout()
		wdg.setLayout(lay)
		return(wdg)
	#def _defAppsByCategory:

	def __initScreen__(self):
		lblBlog=QLabel("{}<hr>".format(i18n["LBL_BLOG"]))
		self.layout().addWidget(lblBlog,0,0)
		self.blog=self._defBlog()
		self.layout().addWidget(self.blog,1,0)
		lblAppsedu=QLabel("{}<hr>".format(i18n["LBL_APPSEDU"]))
		self.layout().addWidget(lblAppsedu,2,0)
		self.appsEdu=self._defAppsedu()
		self.layout().addWidget(self.appsEdu,3,0)
		lblCats=QLabel("{}<hr>".format(i18n["LBL_CATEGORIES"]))
		self.layout().addWidget(lblCats,4,0)
		self.appsByCat=self._defAppsByCat()
		self.layout().addWidget(self.appsByCat,5,0)
	#def __initScreen__

	def updateScreen(self):
		self.blog.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self.appsEdu.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self.appsByCat.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self._getAppsByCat()
		self._getBlog()
		self._getAppsedu()
	#def updateScreen

	def updateBtn(self,btn,app):
		if btn!=None:
			if btn in self.appsEdu.children():
				btn.setApp(app)
	#def updateBtn

	def _stopThreads(self):
		self._stop=True
		for th in self.th:
			th.quit()
		self._rebost.blockSignals(False)
	#def _stopThreads
