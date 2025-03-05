#!/usr/bin/python3
import os
import json
from PySide2.QtCore import Qt,Signal
from QtExtraWidgets import QCheckableComboBox
import gettext
gettext.textdomain('appsedu')
_ = gettext.gettext

i18n={"INSTALL":_("Install")}

LAYOUT="appsedu"
class QComboButton(QCheckableComboBox):
	cmbClicked=Signal("PyObject","PyObject")
	installClicked=Signal("PyObject","PyObject")
	def __init__(self,parent=None,**kwargs):
		QCheckableComboBox.__init__(self, parent)
		self.setFixedWidth(150)
		self.showPop=False
		self.setCursor(Qt.PointingHandCursor)
		self.overrideHide=QCheckableComboBox.hidePopup
		self.setEditable(True)
		self.lineEdit().setDisabled(True)
		self.lineEdit().setReadOnly(True)
		self.lineEdit().setAlignment(Qt.AlignCenter)
		self.title=False
		self.exclusive=True
		self.clicked.connect(self.hidePopup)
	#def __init__

	def setText(self,*args,**kwargs):
		self.lineEdit().setText(args[0])
	#def setText

	def mousePressEvent(self,e):
		if (self.width()-e.x())>32:
			e.accept()
			sw=False
			items=self.getItems()
			for item in items:
				if item.checkState() == Qt.Checked:
					self.installClicked.emit(item.text().strip(),"")
					sw=True
					break
			if sw==False:
				self.installClicked.emit(items[0].text().strip(),"")
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
			self.setText(i18n["INSTALL"].upper())
		return(True)
	#def hidePopup

	def currentText(self):
		text=self.lineEdit().text()
		return(text)

	def currentSelected(self):
		items=self.getItems()
		if len(items)>0:
			for item in items:
				if item.checkState() == Qt.Checked:
					text=item.text().strip()
					break
			if text=="":
				text=items[0].text().strip()
		return(text)
#class QComboButton
