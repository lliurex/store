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
from lib.threadLib import runner
from wdg.btnRebost import QPushButtonRebostApp
from wdg.blog import blogBar
from wdg.choice import choiBar
from wdg.appsedu import appseduBar

class main(QWidget):
	clickedCategory=Signal("PyObject")
	clickedApp=Signal("PyObject","PyObject",dict)
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
		self.runner=runner()
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

	def _openBlog(self,*args):
		if len(args)==1:
			txt=args[0].lblDesc.text()
		else:
			txt=args[-1]
		href=txt.split("href=\"")[-1].split("\"")[0]
		self.runner.setAction("xdg-open",href)
		self.runner.start()
	#def _openBlog

	def _loadApp(self,*args):
		btn=args[0]
		app=btn.property("metadata")
		self.clickedApp.emit(self,btn,app)
	#def _loadApp
	
	def _defBlogBar(self):
		wdg=blogBar()
		wdg.selected.connect(self._openBlog)
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
		dataBlog="https://portal.edu.gva.es/blogs/s1/lliurex/"
		btnBlog.clicked.connect(lambda x: self._openBlog("",dataBlog))
		lay.addWidget(btnBlog,0,0,Qt.AlignRight)
		self.blog=self._defBlogBar()
		self.blog.loadBlog()
		lay.addWidget(self.blog,1,0)
		return(wdg)
	#def _defBlog

	def _defChoiceApps(self):
		wdg=choiBar(rebost=self._rebost.rc)
		wdg.selected.connect(self._loadApp)
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
		wdg=appseduBar(rebost=self._rebost.rc)
		wdg.selected.connect(self._loadApp)
		return(wdg)
	#def _defAppseduApps

	def _defAppsedu(self):
		#wdg.selected.connect(self._emitLoadUrl)
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
		dataApps="https://portal.edu.gva.es/appsedu/aplicacions-lliurex/"
		btnApps.clicked.connect(lambda x: self._openBlog("",dataApps))
		lay.addWidget(btnApps,0,0,Qt.AlignRight)
		self.appsedu=self._defAppseduApps()
		self.appsedu.loadApps()
		lay.addWidget(self.appsedu,1,0)
		return(wdg)
	#def _defAppsedu

	def __initScreen__(self):
		self.layout().setContentsMargins(0,0,0,0)
		#Blog
		blog=self._defBlog()
		self.layout().addWidget(blog,0,0)
		#Editor's choice
		choi=self._defChoice()
		self.layout().addWidget(choi,1,0)
		#Appsedu
		appsedu=self._defAppsedu()
		self.layout().addWidget(appsedu,2,0)
		self.layout().setRowStretch(0,4)
		self.layout().setRowStretch(1,3)
		self.layout().setRowStretch(2,0)
	#def __initScreen__

	def updateScreen(self):
		#Ensure that there's info after all
		if self.choiceApps.count()==1:
			self.choiceApps.loadChoice()
		if self.blog.count()==0:
			self.blog.loadBlog()
		if self.appsedu.count()==0: 
			self.appsedu.loadApps()
	#def updateScreen

	def updateBtn(self,btn,app):
		if btn!=None:
			for chld in self.appsEdu.children():
				if isinstance(chld,QPushButtonRebostApp):
					if chld==btn:
						btn.setApp(app)
						break
	#def updateBtn
