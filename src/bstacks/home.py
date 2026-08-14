#!/usr/bin/python3
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel
from PySide6.QtCore import Qt,Signal
from wdg.topBar import QTopBar
from wdg.blog import blogBar
from wdg.receipts import recsBar
from wdg.choice import choiBar
from wdg.categories import catsBar
from wdg.zomandos import zmdsBar
from QtExtraWidgets import QStackedWindowItem,QSearchBox
from extras.i18n import *
from extras.constants import *
from lib.threadLib import runner

class QHomePane(QWidget):
	search=Signal(str)
	loadCategory=Signal(str)
	requestInstall=Signal("PyObject")
	requestInstallFromId=Signal("PyObject")
	def __init__(self,*args,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.__initScreen__()
		self.runner=runner()
	#def __init__

	def _emitSearch(self,*args):
		self.search.emit(args[0])
	#def _emitSearch

	def _defSearch(self):
		wdg=QSearchBox()
		wdg.clicked.connect(self._emitSearch)
		wdg.returnPressed.connect(self._emitSearch)
		wdg.txtSearch.setPlaceholderText(i18n["SEARCH"])
		return(wdg)
	#def _defSearch

	def _topBar(self):
		wdg=QTopBar()
		for chld in wdg.children():
			if isinstance(chld,QPushButton):
				chld.setText(i18n.get(chld.property("name"),chld.property("name")).upper())
		#wdg.loadHome.connect(self._goHome)
		wdg.loadNews.connect(self._loadContent)
		wdg.loadRecs.connect(self._loadContent)
		wdg.loadZmds.connect(self._loadContent)
		wdg.loadCats.connect(self._loadContent)
		return (wdg)
	#def _topBar

	def _loadContent(self,content):
		self.flowBlog.hide()
		self.flowRecs.hide()
		self.flowCats.hide()
		self.flowZmds.hide()
		if content=="news":
			self.flowBlog.show()
		elif content=="cats":
			self.flowCats.show()
		elif content=="recs":
			self.flowRecs.show()
		elif content=="zmds":
			self.flowZmds.show()

	def _emitLoadRec(self,*args):
		txt=args[0].property("metadata")
		href=txt.split("href=\"")[-1].split("\"")[0]
		self.runner.setAction("xdg-open",href)
		self.runner.start()
	#def _emitLoadRec

	def _defRecsBar(self):
		wdg=recsBar()
		wdg.selected.connect(self._emitLoadRec)
		return(wdg)
	#def _defRecsBar

	def _emitLoadUrl(self,*args):
		txt=args[0].lblDesc.text()
		href=txt.split("href=\"")[-1].split("\"")[0]
		self.runner.setAction("xdg-open",href)
		self.runner.start()
	#def _emitLoadUrl

	def _defBlogBar(self):
		wdg=blogBar()
		wdg.selected.connect(self._emitLoadUrl)
		return(wdg)
	#def _defBlogBar

	def _emitLoadApp(self,*args):
		meta=args[0].property("metadata")
		if meta==None:
			meta=""
		if meta=="":
			self.requestInstall.emit(args[0])
		else:
			self.requestInstallFromId.emit(args[0])
	#def _emitLoadApp

	def _defChoiBar(self):
		wdg=choiBar(rebost=self.rebost)
		wdg.selected.connect(self._emitLoadApp)
		return(wdg)
	#def _defChoiBar

	def _defZmdsBar(self):
		wdg=zmdsBar(rebost=self.rebost)
		wdg.selected.connect(self._emitLoadApp)
		return(wdg)
	#def _defZmdsBar

	def _emitLoadCategory(self,*args):
		self.loadCategory.emit(args[0].text())
	#def _emitLoadCategory

	def _defCatsBar(self):
		wdg=catsBar(rebost=self.rebost)
		wdg.selected.connect(self._emitLoadCategory)
		return(wdg)
	#def _defCatsBar

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		topBar=self._topBar()
		lay.addWidget(topBar,0,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.flowZmds=self._defZmdsBar()
		self.flowZmds.loadZomandos()
		lay.addWidget(self.flowZmds,1,0,1,self.layout().columnCount(),Qt.AlignTop)
		self.flowCats=self._defCatsBar()
		self.flowCats.loadCategories()
		self.flowCats.hide()
		lay.addWidget(self.flowCats,1,0,1,self.layout().columnCount(),Qt.AlignTop)
		self.flowRecs=self._defRecsBar()
		self.flowRecs.loadRecs()
		self.flowRecs.hide()
		lay.addWidget(self.flowRecs,1,0,1,self.layout().columnCount(),Qt.AlignTop)
		self.flowBlog=self._defBlogBar()
		self.flowBlog.loadBlog()
		self.flowBlog.hide()
		lay.addWidget(self.flowBlog,1,0,1,self.layout().columnCount(),Qt.AlignTop)
		searchBox=self._defSearch()
		searchBox.setMinimumWidth(512)
		#self.layout().addWidget(QLabel("<hr>"),2,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.layout().addWidget(searchBox,2,0,1,self.layout().columnCount(),Qt.AlignCenter|Qt.AlignCenter)
		self.layout().addWidget(QLabel("{}".format(i18n["CHOICE"])),3,0,1,self.layout().columnCount(),Qt.AlignBottom|Qt.AlignCenter)
		self.flowChoi=self._defChoiBar()
		self.flowChoi.loadChoice()
		lay.addWidget(self.flowChoi,4,0,1,self.layout().columnCount(),Qt.AlignTop)
		self.layout().addWidget(QLabel("<hr>".format(i18n["CHOICE"])),5,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		lay.setRowStretch(0,0)
		lay.setRowStretch(1,1)
		lay.setRowStretch(2,1)
		lay.setRowStretch(3,0)
		lay.setRowStretch(4,1)
	#def __initScreen__

