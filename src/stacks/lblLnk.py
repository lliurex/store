#!/usr/bin/python3
import os
import json
from PySide2.QtWidgets import QLabel,QWidget,QHBoxLayout
from PySide2.QtCore import Qt,Signal
from PySide2 import QtGui
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

class QLabelLink(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		hbox=QHBoxLayout()
		hbox.setSpacing(0)
		icn=QtGui.QPixmap()
		icn.fill(Qt.transparent)
		icn.load(os.path.join(RSRC,"link24x24.png"))
		lblIcn=QLabel()
		lblIcn.setAttribute(Qt.WA_StyledBackground, True)
		lblIcn.setPixmap(icn.scaled(12,12,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
		lblIcn.setStyleSheet("background-color:transparent;")
		lblIcn.setMinimumWidth(16)
		hbox.addWidget(lblIcn)
		self.lbl=QLabel("{}".format(args[0]))
		self.lbl.setAttribute(Qt.WA_StyledBackground, True)
		self.setAttribute(Qt.WA_StyledBackground, True)
		hbox.addWidget(self.lbl,Qt.AlignLeft)
		self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		self.lbl.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		self.lbl.setObjectName("lblLink")
		self.lbl.setStyleSheet("background-color:transparent;")
		self.lbl.enterEvent=self._highlightLink
		self.lbl.leaveEvent=self._unhighlightLink
		self.setLayout(hbox)
	#def __init__

	def _highlightLink(self,*args):
		text=self.lbl.text()
		text="<strong><u>{}</u></strong>".format(text)
		self.lbl.setText(text)
	#def _highlightLink
	
	def _unhighlightLink(self,*args):
		text=self.lbl.text().removeprefix("<strong><u>").removesuffix("</u></strong>")
		self.lbl.setText(text)
	def setOpenExternalLinks(self,*args):
		self.lbl.setOpenExternalLinks(*args)
	#def setOpenExternalLinks

	def setText(self,*args):
		self.lbl.setText("{}".format(*args))
	#def setText
#class QLabelLink

