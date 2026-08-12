#!/usr/bin/python3
from PySide6.QtWidgets import QWidget,QPushButton,QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from QtExtraWidgets import QSearchBox
from extras.i18n import *

class QSearch(QWidget):
	requestSearch=Signal("PyObject")
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
		src=QSearchBox()
		src.clicked.connect(self._reqSearch)
		src.returnPressed.connect(self._reqSearch)
		src.txtSearch.setPlaceholderText(i18n["SEARCH"])
		lay.addWidget(src)
	#def __init__

	def _goPrev(self,*args):
		self.goPrevious.emit()
	#def _goPrev

	def _reqSearch(self,*args):
		self.requestSearch.emit(args)
	#def _reqSearch
