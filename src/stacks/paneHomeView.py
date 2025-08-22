#!/usr/bin/python3
import sys,signal
import os,json
from functools import partial
from PySide6.QtWidgets import QLabel, QWidget,QHBoxLayout,QVBoxLayout,QSizePolicy,QPushButton,QGridLayout
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal
from QtExtraWidgets import QScreenShotContainer
import concurrent.futures as Futures
import gettext
import css
import rss
from constants import *
from lblArticle import QLabelArticle
from btnRebost import QPushButtonRebostApp
import gettext
_ = gettext.gettext

i18n={"LBL_BLOG":"Blog entries",
	"LBL_APPSEDU":"Latest apps in appsedu",
	"LBL_CATEGORIES":"Relevant categories"}

class main(QWidget):
	clicked=Signal("PyObject")
	loaded=Signal("PyObject")
	tagpressed=Signal(str)
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.thExecutor=Futures.ThreadPoolExecutor(max_workers=4)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self._debug("home load")
		self.setStyleSheet(css.tablePanel())
		self.setObjectName("mp")
		self.th=[]
		self._rebost=args[0]
		self._rebost.urlEnded.connect(self._setAppseduData)
		self._rebost.gacEnded.connect(self._setAppsData)
		self.btns={}
		layout=QGridLayout()
		layout.setVerticalSpacing(0)
		self.setLayout(layout)
		self.__initScreen__()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Home: {}".format(msg))
	#def _debug

	def _processRss(self,*args,**kwargs):
		result=args[0]
		if len(result)>0:
			print(result[0]["type"])
			if result[0]["type"]=="appsedu":
				for idx in range(0,min(len(result),10)):
					url=result[idx]["link"]
					self._rebost.setAction("urlSearch",url)
					self._rebost.start()
					self._rebost.wait()
			else:
				self._setBlogData(result)
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
				"icon":img,
				"pkgname":"",
				"description":""}
			btn.setApp(app)
			cont+=1
	#def _setBlogData

	def _getBlog(self):
		wdg=QWidget()
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout=QHBoxLayout()
		layout.setSpacing(0)
		for i in range(0,5):
			btn=QPushButtonRebostApp("{}")
			btn.showBtn=False
			btn.setObjectName("mp")
			btn.iconSize=IMAGE_PREVIEW/1.2
			btn.iconUri.setMaximumHeight(IMAGE_PREVIEW/1.2)
			btn.label.setMinimumWidth(IMAGE_PREVIEW)
			btn.autoUpdate=True
			layout.addWidget(btn)
		rssparser=rss.rssParser()
		rssparser.rssEnded.connect(self._processRss)
		rssparser.feed="blog"
		rssparser.start()
		self.th.append(rssparser)
		wdg.setLayout(layout)
		return(wdg)
	#def _getBlog(self):

	def _setAppseduData(self,*args):
		self._debug("Setting data --->")
		app=json.loads(args[0])
		for btn in self.appsEdu.children():
			if not isinstance(btn,QPushButtonRebostApp):
				continue
			if isinstance(app,list) and len(app)>0 and btn.app.get("summary","")=="":
				btn.setApp(app[0])
				btn.setVisible(True)
				break
		self._debug("Setting data ---<")
	#def _setAppseduData
	
	def _getAppsedu(self):
		wdg=QWidget()
		layout=QHBoxLayout()
		layout.setSpacing(32)
		wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		for i in range(0,10):
			btn=QPushButtonRebostApp("{}")
			btn.setMaximumWidth(IMAGE_PREVIEW/3)
			btn.autoUpdate=True
			btn.setVisible(False)
			layout.addWidget(btn,Qt.AlignCenter)
		rssparser=rss.rssParser()
		rssparser.rssEnded.connect(self._processRss)
		rssparser.feed="appsedu"
		rssparser.start()
		self.th.append(rssparser)
		wdg.setLayout(layout)
		return(wdg)
	#def _getAppsedu

	def _setAppsData(self,*args):
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
			btn.setFixedSize(QSize(ICON_SIZE*2,ICON_SIZE*1.5))
			btn.showBtn=False
			lay.addWidget(btn,Qt.AlignTop)
	#def _setAppsData

	def _getAppsByCategory(self):
		wdg=QWidget()
		lay=QHBoxLayout()
		wdg.setLayout(lay)
		self._debug("Get apps per category")
		self._rebost.setAction("getAppsPerCategory")
		self._rebost.start()
		return(wdg)
	#def _getAppsByCategory(self):

	def __initScreen__(self):
		lblBlog=QLabel("{}<hr>".format(i18n["LBL_BLOG"]))
		self.layout().addWidget(lblBlog,0,0)
		self.blog=self._getBlog()
		self.layout().addWidget(self.blog,1,0)
		lblAppsedu=QLabel("{}<hr>".format(i18n["LBL_APPSEDU"]))
		self.layout().addWidget(lblAppsedu,2,0)
		self.appsEdu=self._getAppsedu()
		self.layout().addWidget(self.appsEdu,3,0)
		lblCats=QLabel("{}<hr>".format(i18n["LBL_CATEGORIES"]))
		self.layout().addWidget(lblCats,4,0)
		self.appsByCat=self._getAppsByCategory()
		self.layout().addWidget(self.appsByCat,5,0)
	#def __initScreen__


