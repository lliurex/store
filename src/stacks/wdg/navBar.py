#!/usr/bin/python3

'''Add widget
'''

from PySide6.QtWidgets import QWidget,QStackedLayout,QListWidget

class QStackedMenu(QStackedLayout):
	def __init__(self,parent=None):
		super().__init__(self,parent)
		self.items={}
		self.current=0
	#def __init__

	def addStack(self,wdg):
		self.addWidget(wdg)
	#def addStack
