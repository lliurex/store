#!/usr/bin/python3
from PySide2.QtWidgets import QWidget,QPushButton,QHBoxLayout
from PySide2.QtGui import QIcon
from PySide2.QtCore import Signal
from QtExtraWidgets import QSearchBox
from extras.i18n import *

class QSearch(QWidget):
	requestSearch=Signal(str)
	goPrevious=Signal()
	def __init__(self,*args,parent=None):
		QWidget.__init__(self, parent)
		self.setMinimumWidth(512)
		lay=QHBoxLayout(self)
		lay.setSpacing(1)
		bck=QPushButton()
		icn=QIcon.fromTheme("go-previous")
		bck.setIcon(icn)
		bck.clicked.connect(self._goPrev)
		lay.addWidget(bck)
		self.src=QSearchBox()
		self.src.clicked.connect(self._reqSearch)
		self.src.returnPressed.connect(self._reqSearch)
		self.src.txtSearch.setPlaceholderText(i18n["SEARCH"])
		self.src.layout().setStretch(1,-1)
		self.src.layout().setStretch(0,1)
		lay.addWidget(self.src)
	#def __init__

	def _goPrev(self,*args):
		self.goPrevious.emit()
	#def _goPrev

	def _reqSearch(self,*args):
		self.requestSearch.emit(args[0])
	#def _reqSearch
