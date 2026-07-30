#!/usr/bin/python3
from PySide6.QtWidgets import QPushButton,QWidget,QHBoxLayout

class QTopBar(QWidget):
	def __init__(self,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		lay=QHBoxLayout(self)
		self._renderGui()
	#def __init__(self,parent=None,**kwargs):

	def _renderGui(self,*args):
		actions=["HOME","NEWS","RECEIPTS","ZOMANDOS","CATEGORIES"]
		for action in actions:
			btn=QPushButton()	
			btn.setProperty("name",action)
			self.layout().addWidget(btn)
	#def _renderGui


