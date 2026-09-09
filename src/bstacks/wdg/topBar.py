#!/usr/bin/python3
from PySide2.QtWidgets import QPushButton,QWidget,QHBoxLayout
from PySide2.QtCore import Signal
from extras.i18n import *

class QTopBar(QWidget):
	loadHome=Signal(str)
	loadNews=Signal(str)
	loadRecs=Signal(str)
	loadZmds=Signal(str)
	loadCats=Signal(str)
	loadSettings=Signal()
	def __init__(self,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		lay=QHBoxLayout(self)
		self.checked=None
		self._renderGui()
	#def __init__(self,parent=None,**kwargs):

	def _emit(self,*args):
		if self.checked!=None:
			self.checked.setEnabled(True)
			self.checked.setChecked(False)
		for chld in self.children():
			if isinstance(chld,QPushButton):
				if chld.isChecked()==True:
					chld.blockSignals(True)
					self.checked=chld
				else:
					chld.blockSignals(False)
					chld.setChecked(False)
		if self.checked.property("name")==i18n["NEWS"]:
			self.loadNews.emit("news")
		elif self.checked.property("name")==i18n["RECEIPTS"]:
			self.loadRecs.emit("recs")
		elif self.checked.property("name")==i18n["ZOMANDOS"]:
			self.loadZmds.emit("zmds")
		elif self.checked.property("name")==i18n["CATEGORIES"]:
			self.loadCats.emit("cats")
		elif self.checked.property("name")==i18n["CONFIG"]:
			self.loadSettings.emit()
	#def _emit

	def _renderGui(self,*args):
		actions=[i18n["ZOMANDOS"],i18n["CATEGORIES"],i18n["RECEIPTS"],i18n["NEWS"],i18n["CONFIG"]]
		for action in actions:
			btn=QPushButton()	
			btn.setCheckable(True)
			btn.setProperty("name",action)
			btn.clicked.connect(self._emit)
			self.layout().addWidget(btn)
			if self.layout().count()==1:
				self.checked=btn
				btn.setChecked(True)
	#def _renderGui


