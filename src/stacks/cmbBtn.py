#!/usr/bin/python3
import os
import json
from PySide2.QtWidgets import QLabel, QPushButton,QHBoxLayout,QGraphicsDropShadowEffect,QSizePolicy,QComboBox,QWidget
from PySide2.QtCore import Qt,Signal
from PySide2.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor
from QtExtraWidgets import QScreenShotContainer
import gettext
gettext.textdomain('appsedu')
_ = gettext.gettext

i18n={"INSTALL":_("Install")}

LAYOUT="appsedu"
class QComboButton(QComboBox):
	clicked=Signal("PyObject","PyObject")
	def __init__(self,parent=None,**kwargs):
		QComboBox.__init__(self, parent)
		self.showPop=False
		self.overrideHide=QComboBox.hidePopup
		self.setEditable(True)
		self.lineEdit().setDisabled(True)
		self.lineEdit().setReadOnly(True)
		self.lineEdit().setAlignment(Qt.AlignCenter)
	#def __init__

	def setText(self,*args,**kwargs):
		pass
	#def setText

	def mousePressEvent(self,e):
		if (self.width()-e.x())>32:
			e.accept()
			self.clicked.emit(self.currentText().strip(),"")
			return(True)
		else:
			self.showPop=True
			e.ignore()
		self.showPopup()
		return(False)
	#def mousePressEvent

	def hidePopup(self,*args):
		if self.showPop==True:
			self.showPop=False
		else:
			self.overrideHide(self)
		return(True)
	#def hidePopup

#class QComboButton
