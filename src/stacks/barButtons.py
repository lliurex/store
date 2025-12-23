#!/usr/bin/python3
import os,subprocess,time
from PySide2.QtWidgets import QLabel, QPushButton,QWidget,QGridLayout,QHBoxLayout
from PySide2.QtCore import Qt,Signal,QSize,QPoint
from PySide2.QtGui import QIcon,QPixmap,QPalette
from btnRebost import QPushButtonRebostApp
import libhelper
import css
from constants import *
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={
	"ALL":_("All"),
	"HOME":_("Go to portrait"),
	"INSTALLED":_("Show installed apps"),
	"ORIGIN":_("Origin"),
	"ORIGINDEL":_("Click: Show only from"),
	"ORIGINSET":_("Click: Show all applications"),
	"REFRESH":_("Reload applications")
	}

class QPushButtonBar(QWidget):
	toggleClicked=Signal()
	homeClicked=Signal()
	installedClicked=Signal()
	reloadClicked=Signal()
	def __init__(self,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.dbg=True
		self.setObjectName("btnToggle")
		self.setStyleSheet(css.btnToggle())
		layout=QGridLayout()
		layout.setSpacing(int(MARGIN)*2)
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		topRow=self._defTopRow()
		layout.addWidget(topRow,0,0,1,2,Qt.AlignCenter)
		self.btnAppsedu=QPushButton()
		self.btnAppsedu.setObjectName("btnOption")
		self.btnAppsedu.setProperty("origin",True)
		icn=QIcon(os.path.join(RSRC,"appsedu128x128.png"))
		self.btnAppsedu.setIcon(icn)
		self.btnAppsedu.setIconSize(QSize(64,64))
		self.btnAppsedu.setMaximumSize(QSize(64,64))
		layout.addWidget(self.btnAppsedu,1,0,1,1,Qt.AlignRight)
		self.btnLliurex=QPushButton()
		self.btnLliurex.enterEvent=lambda x:self._switchPalette("enter",self.btnLliurex)
		self.btnLliurex.leaveEvent=lambda x:self._switchPalette("leave",self.btnLliurex)
		self.btnLliurex.clicked.connect(self.enableLliurexMode)
		self.btnLliurex.setObjectName("btnOption")
		self.btnLliurex.setProperty("origin",False)
		icn=QIcon.fromTheme("llxstore")
		self.btnLliurex.setIcon(icn)
		self.btnLliurex.setIconSize(QSize(64,64))
		self.btnLliurex.setMaximumSize(QSize(64,64))
		self.btnLliurex.setCursor(Qt.PointingHandCursor)
		layout.addWidget(self.btnLliurex,1,1,1,1,Qt.AlignLeft)
		self.btnLliurex.setDisabled(True)
		self.lblOrigin=QLabel("{}: appsedu".format(i18n["ORIGIN"]))
		layout.addWidget(self.lblOrigin,2,0,1,2,Qt.AlignCenter|Qt.AlignTop)
		layout.setRowStretch(1,1)
		layout.setRowStretch(0,0)
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("btnInstallers: {}".format(msg))
	#def _debug(self,msg):

	def _defTopRow(self):
		wdg=QWidget()
		hlay=QHBoxLayout()
		hlay.setSpacing(int(MARGIN))
		wdg.setLayout(hlay)
		#HOME
		self.btnHome=QPushButton()
		self.btnHome.setObjectName("btnOption")
		self.btnHome.setProperty("origin",True)
		icn=QIcon(os.path.join(RSRC,"appsedu_home128x128.png"))
		self.btnHome.setIcon(icn)
		self.btnHome.setIconSize(QSize(48,48))
		self.btnHome.setMaximumSize(QSize(48,48))
		self.btnHome.setToolTip(i18n["HOME"])
		self.btnHome.setCursor(Qt.PointingHandCursor)
		self.btnHome.clicked.connect(self.homeClicked.emit)
		hlay.addWidget(self.btnHome)
		#INSTALLED
		self.btnInstalled=QPushButton()
		self.btnInstalled.setObjectName("btnOption")
		self.btnInstalled.setProperty("origin",True)
		icn=QIcon(os.path.join(RSRC,"appsedu_installed128x128.png"))
		self.btnInstalled.setIcon(icn)
		self.btnInstalled.setIconSize(QSize(48,48))
		self.btnInstalled.setMaximumSize(QSize(48,48))
		self.btnInstalled.setToolTip(i18n["INSTALLED"])
		self.btnInstalled.setCursor(Qt.PointingHandCursor)
		self.btnInstalled.clicked.connect(self.installedClicked.emit)
		hlay.addWidget(self.btnInstalled)
		#REFRESH
		self.btnRefresh=QPushButton()
		self.btnRefresh.setObjectName("btnOption")
		self.btnRefresh.setProperty("origin",True)
		self.btnRefresh.setCursor(Qt.PointingHandCursor)
		icn=QIcon(os.path.join(RSRC,"appsedu_refresh128x128.png"))
		self.btnRefresh.setIcon(icn)
		self.btnRefresh.setIconSize(QSize(48,48))
		self.btnRefresh.setMaximumSize(QSize(48,48))
		self.btnRefresh.setToolTip(i18n["REFRESH"])
		self.btnRefresh.clicked.connect(self.reloadClicked.emit)
		hlay.addWidget(self.btnRefresh)
		return(wdg)
	#def _topRow

	def _switchPalette(self,*args):
		ev=args[0]
		source=args[1]
		if ev=="enter":
			if source==self.btnLliurex:
				if source.property("origin")==False:
					self.lblOrigin.setText("{}".format(i18n["ORIGINSET"]))
				else:
					self.lblOrigin.setText("{} Appsedu".format(i18n["ORIGINDEL"]))
			source.setEnabled(True)
		else:
			if source==self.btnLliurex:
				self.btnLliurex.setEnabled(self.btnLliurex.property("origin"))
			if self.btnLliurex.isEnabled()==True:
				self.lblOrigin.setText("{}: {}".format(i18n["ORIGIN"],i18n["ALL"]))
			else:
				self.lblOrigin.setText("{}: Appsedu".format(i18n["ORIGIN"]))
	#def _switchPalette

	def enableLliurexMode(self):
		self.btnLliurex.style().unpolish(self.btnLliurex)
		if self.btnLliurex.property("origin")==False:
			self.btnLliurex.setProperty("origin",True)
			self.lblOrigin.setText("{}: {}".format(i18n["ORIGIN"],i18n["ALL"]))
		else:
			self.btnLliurex.setProperty("origin",False)
		self.btnLliurex.style().polish(self.btnLliurex)
		self.btnLliurex.setEnabled(self.btnLliurex.property("origin"))
		self.btnLliurex.update()
		self.toggleClicked.emit()
	#def enableLliurexMode

	def setLocked(self,locked=True,lockedUser=True):
		self.btnLliurex.style().unpolish(self.btnLliurex)
		self.btnLliurex.setProperty("origin",not(locked))
		self.btnLliurex.style().polish(self.btnLliurex)
		self.btnLliurex.setEnabled(not(locked))
		if locked==True:
			self.lblOrigin.setText("{}: Appsedu".format(i18n["ORIGIN"]))
		else:
			self.lblOrigin.setText("{}: {}".format(i18n["ORIGIN"],i18n["ALL"]))
		self.btnLliurex.update()
		if lockedUser==True:
			self.btnLliurex.hide()
		else:
			self.btnLliurex.show()
	#def setLocked
