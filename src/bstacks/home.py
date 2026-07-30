#!/usr/bin/python3
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel
from PySide6.QtCore import Qt,Signal
from blog import blogBar
from choice import choiBar
from categories import catsBar
from QtExtraWidgets import QStackedWindowItem,QSearchBox
from extras.i18n import *

class QHomePane(QWidget):
	search=Signal(str)
	def __init__(self,*args,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.__initScreen__()
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

	def _defBlogBar(self):
		wdg=blogBar()
		return(wdg)
	#def _defBlogBar

	def _defChoiBar(self):
		wdg=choiBar(rebost=self.rebost)
		return(wdg)
	#def _defChoiBar

	def _defCatsBar(self):
		wdg=catsBar(rebost=self.rebost)
		return(wdg)
	#def _defCatsBar

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.flowBlog=self._defBlogBar()
		self.flowBlog.loadBlog()
		lay.addWidget(self.flowBlog,0,0,1,self.layout().columnCount(),Qt.AlignTop)
		searchBox=self._defSearch()
		searchBox.setMinimumWidth(512)
		self.layout().addWidget(QLabel("<hr>"),1,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.layout().addWidget(searchBox,2,0,1,self.layout().columnCount(),Qt.AlignCenter)
		self.layout().addWidget(QLabel("<hr>".format(i18n["CHOICE"])),3,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.flowChoi=self._defChoiBar()
		self.flowChoi.loadChoice()
		lay.addWidget(self.flowChoi,4,0,1,self.layout().columnCount())
		self.layout().addWidget(QLabel("<hr>".format(i18n["CHOICE"])),5,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.flowCats=self._defCatsBar()
		self.flowCats.loadCategories()
		lay.addWidget(self.flowCats,6,0,1,self.layout().columnCount(),Qt.AlignTop)
		lay.setRowStretch(0,1)
		lay.setRowStretch(1,0)
		lay.setRowStretch(2,0)
		lay.setRowStretch(3,0)
		lay.setRowStretch(4,1)
	#def __initScreen__

