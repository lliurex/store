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

LAYOUT="appsedu"
class QLabelLink(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		hbox=QHBoxLayout()
		icn=QtGui.QPixmap(os.path.join(RSRC,"link24x24.png"))
		lblIcn=QLabel()
		lblIcn.setPixmap(icn.scaled(16,16,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
		hbox.addWidget(lblIcn)
		self.lbl=QLabel(args[0])
		hbox.addWidget(self.lbl)
		self.setLayout(hbox)
	
	def setOpenExternalLinks(self,*args):
		self.lbl.setOpenExternalLinks(*args)

	def setText(self,*args):
		self.lbl.setText(*args)
#class QLabelLink

