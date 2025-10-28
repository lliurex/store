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
	"ORIGIN":_("Origin"),
	"ORIGINDEL":_("Click: Show only from"),
	"ORIGINSET":_("Click: Show all applications")
	}

class QPushButtonToggle(QWidget):
	toggleClicked=Signal()
	def __init__(self,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.dbg=True
		self.setObjectName("btnToggle")
		self.setStyleSheet(css.btnToggle())
		layout=QGridLayout()
		self.setLayout(layout)
		wdg=QWidget()
		hlayout=QHBoxLayout()
		hlayout.setSpacing(int(MARGIN)*2)
		wdg.setLayout(hlayout)
		self.btnAppsedu=QPushButton()
		self.btnAppsedu.setObjectName("btnOption")
		self.btnAppsedu.setProperty("origin",True)
		icn=QIcon(os.path.join(RSRC,"appsedu128x128.png"))
		self.btnAppsedu.setIcon(icn)
		self.btnAppsedu.setIconSize(QSize(64,64))
		self.btnAppsedu.setMaximumSize(QSize(64,64))
		#layout.addWidget(self.btnAppsedu,0,0,1,1)
		hlayout.addWidget(self.btnAppsedu)
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
		#layout.addWidget(self.btnLliurex,0,1,1,1,Qt.AlignCenter)
		hlayout.addWidget(self.btnLliurex)
		self.btnLliurex.setDisabled(True)
		layout.addWidget(wdg,0,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		self.lblOrigin=QLabel("{}: appsedu".format(i18n["ORIGIN"]))
		layout.addWidget(self.lblOrigin,1,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		layout.setRowStretch(1,1)
		layout.setRowStretch(0,0)
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("btnInstallers: {}".format(msg))
	#def _debug(self,msg):

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
