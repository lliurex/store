#!/usr/bin/python3
import os
from PySide6.QtWidgets import QWidget,QPushButton,QHBoxLayout,QSizePolicy,QLineEdit,QPushButton
from PySide6.QtGui import QIcon,Qt
from PySide6.QtCore import Signal,QSize
from QtExtraWidgets import QSearchBox
from extras.i18n import *
from extras.constants import *

class QSearch(QWidget):
	requestSearch=Signal(str)
	goPrevious=Signal()

	def __init__(self,*args,parent=None):
		QWidget.__init__(self, parent)
		wdgParent=QWidget()
		layParent=QHBoxLayout(self)
		wdgParent.setObjectName("wdgsearch")
		wdgParent.setAttribute(Qt.WA_StyledBackground, True)
		wdg=QWidget()
		wdg.setMaximumWidth(450)
		lay=QHBoxLayout(wdg)
		lay.setSpacing(0)
		wdg.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.setObjectName("wsearch")
		self.searchBox=QLineEdit()
		font=self.searchBox.font()
		font.setPointSize(font.pointSize()+2)
		self.text=self.searchBox.text
		self.searchBox.setFont(font)
		self.searchBox.setObjectName("search")
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.searchBox.returnPressed.connect(self._reqSearch)
		self.btnSearch=QPushButton()
		self.btnSearch.setObjectName("bsearch")
		icn=QIcon(os.path.join(RSRC,"search.png"))
		self.btnSearch.setIcon(icn)
		self.btnSearch.setMinimumSize(int(ICON_SIZE/4),int(ICON_SIZE/4))
		self.btnSearch.setIconSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		#self.searchBox.textChanged.connect(self._changeSearchAppsBtnIcon)
		self.btnSearch.clicked.connect(self._reqSearch)
		lay.addWidget(self.searchBox)#,Qt.AlignCenter|Qt.AlignCenter)
		lay.addWidget(self.btnSearch)
		layParent.addWidget(wdg)
	#def __init__

	def _reqSearch(self,*args):
		query=self.searchBox.text()
		self.requestSearch.emit(query)
	#def _reqSearch

	def setText(self,text):
		self.searchBox.setText(text)
	#def setText
