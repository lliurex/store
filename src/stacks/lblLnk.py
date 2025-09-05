#!/usr/bin/python3
import os
import json
from PySide6.QtWidgets import QLabel,QWidget,QHBoxLayout
from PySide6.QtCore import Qt,Signal
from PySide6 import QtGui
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

class QLabelLink(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		hbox=QHBoxLayout()
		hbox.setSpacing(0)
		icn=QtGui.QPixmap(os.path.join(RSRC,"link24x24.png"))
		lblIcn=QLabel()
		lblIcn.setPixmap(icn.scaled(12,12,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
		lblIcn.setMinimumWidth(16)
		hbox.addWidget(lblIcn)
		self.lbl=QLabel(args[0])
		hbox.addWidget(self.lbl,Qt.AlignLeft)
		self.setLayout(hbox)
	#def __init__
	
	def setOpenExternalLinks(self,*args):
		self.lbl.setOpenExternalLinks(*args)
	#def setOpenExternalLinks

	def setText(self,*args):
		self.lbl.setText(*args)
	#def setText
#class QLabelLink

