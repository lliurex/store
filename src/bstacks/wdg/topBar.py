#!/usr/bin/python3
from PySide6.QtWidgets import QPushButton,QWidget,QHBoxLayout
from PySide6.QtCore import Signal

class QTopBar(QWidget):
	loadHome=Signal()
	loadNews=Signal()
	loadRecs=Signal()
	loadZmds=Signal()
	loadCats=Signal()
	def __init__(self,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		lay=QHBoxLayout(self)
		self._renderGui()
		self.checked=None
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
		if self.checked.property("name")=="HOME":
			self.loadHome.emit()
		elif self.checked.property("name")=="NEWS":
			self.loadNews.emit()
		elif self.checked.property("name")=="RECEIPTS":
			self.loadRecs.emit()
		elif self.checked.property("name")=="ZOMANDOS":
			self.loadZmds.emit()
		elif self.checked.property("name")=="CATEGORIES":
			self.loadCats.emit()
	#def _emit

	def _renderGui(self,*args):
		actions=["HOME","NEWS","RECEIPTS","ZOMANDOS","CATEGORIES"]
		for action in actions:
			btn=QPushButton()	
			btn.setCheckable(True)
			btn.setProperty("name",action)
			btn.clicked.connect(self._emit)
			self.layout().addWidget(btn)
	#def _renderGui


