#!/usr/bin/python3
from functools import partial
import subprocess
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QWidget,QHBoxLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread,QPropertyAnimation
from QtExtraWidgets import QScreenShotContainer,QScrollLabel
import gettext
import css
_ = gettext.gettext

i18n={
	"CHK_NETWORK":_("Store was unable to get information from internet"),
	"OPN_NETWORK":_("Open network settings"),
	"OPN_CONTINUE":_("Go to store anyway")
	}


class paneErrorView(QWidget):
	requestLoadPortrait=Signal()
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

	def _loadPortrait(self,*args):
		self.requestLoadPortrait.emit()
	#def _loadPortrait

	def __initScreen__(self):
		self.setAttribute(Qt.WA_StyledBackground, True)
		box=QGridLayout()
		self.setLayout(box)
		icn=QtGui.QIcon.fromTheme("network-wireless")
		pxm=QtGui.QPixmap()
		pxm=icn.pixmap(QSize(256,256))
		lblIcn=QLabel()
		lblIcn.setPixmap(pxm)
		box.addWidget(lblIcn,0,0,1,1,Qt.AlignCenter|Qt.AlignBottom)
		lblTxt=QLabel(i18n["CHK_NETWORK"])
		box.addWidget(lblTxt,1,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		btnBox=QWidget()
		layBox=QHBoxLayout()
		btnBox.setLayout(layBox)
		btnCnf=QPushButton(i18n["OPN_NETWORK"])
		btnCnf.clicked.connect(self._launchNetworkSettings)
		layBox.addWidget(btnCnf)
		btnLoad=QPushButton(i18n["OPN_CONTINUE"])
		btnLoad.clicked.connect(self._loadPortrait)
		layBox.addWidget(btnLoad)
		box.addWidget(btnBox,2,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		box.setRowStretch(0,2)
		box.setRowStretch(1,0)
		box.setRowStretch(2,1)
	#def __initScreen__

	def _return(self):
		return
	#def _return
#class paneErrorView
