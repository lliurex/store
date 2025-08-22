#!/usr/bin/python3
import sys,signal
import os
from functools import partial
import subprocess
import json
import html
from rebost import store
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QSizePolicy,QWidget,QComboBox,QHBoxLayout,QListWidget,\
							QVBoxLayout,QListWidgetItem,QGraphicsBlurEffect,QGraphicsOpacityEffect,\
							QAbstractScrollArea, QFrame
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation
from QtExtraWidgets import QScreenShotContainer,QScrollLabel
import gettext
import libhelper
import exehelper
import css
from cmbBtn import QComboButton
from lblApp import QLabelRebostApp
from lblLnk import QLabelLink
from libth import thShowApp
from constants import *
_ = gettext.gettext
QString=type("")
BKG_COLOR_INSTALLED=QtGui.QColor(QtGui.QPalette().color(QtGui.QPalette.Inactive,QtGui.QPalette.Highlight))

i18n={
	"CHK_NETWORK":_("Store was unable to get information from internet"),
	"OPN_NETWORK":_("Open network settings")
	}


class paneErrorView(QWidget):
	clicked=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.__initScreen__()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("Details: {}".format(msg))
	#def _debug

	def _launchNetworkSettings(self,*args):
		cmd=["systemsettings","kcm_networkmanagement"]
		subprocess.run(cmd)
	#def _launchNetworkSettings

	def __initScreen__(self):
		self.setAttribute(Qt.WA_StyledBackground, True)
		box=QVBoxLayout()
		self.setLayout(box)
		icn=QtGui.QIcon.fromTheme("network-wireless")
		pxm=QtGui.QPixmap()
		pxm=icn.pixmap(QSize(256,256))
		lblIcn=QLabel()
		lblIcn.setPixmap(pxm)
		box.addWidget(lblIcn,Qt.AlignBottom,Qt.AlignCenter)
		lblTxt=QLabel(i18n["CHK_NETWORK"])
		box.addWidget(lblTxt,Qt.AlignCenter,Qt.AlignCenter)
		btnCnf=QPushButton(i18n["OPN_NETWORK"])
		btnCnf.clicked.connect(self._launchNetworkSettings)
		box.addWidget(btnCnf,Qt.AlignTop,Qt.AlignCenter)
	#def __initScreen__

	def _return(self):
		return
	#def _return
#class paneErrorView
