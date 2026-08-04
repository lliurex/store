#!/usr/bin/python3
import os
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QIcon,QPixmap
from QtExtraWidgets import QPushInfoButton
import lib.libhelper as libhelper

class QAppButton(QPushInfoButton):
	def __init__(self,*args,parent=None):
		QPushInfoButton.__init__(self, parent,scroll=True)
		self.app=args[0]
		self.lblStatus=QLabel("")
		self.defaultSize=64
		self.loadImg(self.app["icon"])
		self.setText(self.app["name"])
		self.setDescription(self.app["summary"])
		self.helper=libhelper.helper()
		self._getAppStatus()
		lay=self.layout()
		lay.addWidget(self.lblStatus,1,0,1,1)
		#self.lblStatus.hide()
		self.cacheDir=os.path.join(os.environ["HOME"],".cache","store","imgs")
	#def __init__

	def _setGradientAvailable(self):
		self.lblDesc.setGradient((224,214,255,50),(120,150,20,250))
		statusIcon=QIcon().fromTheme("install")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientAvailable

	def _setGradientInstalled(self):
		self.lblDesc.setGradient((120,150,20,150),(120,150,120,0))
		statusIcon=QIcon().fromTheme("uninstall")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientInstalled

	def _setGradientPending(self):
		self.lblDesc.setGradient((136,136,136,100),(140,144,144,250))
		self.lblDesc.setForeground((150,150,150))
		statusIcon=QIcon().fromTheme("clock")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientPending

	def _setGradientForbidden(self):
		self.lblDesc.setGradient((224,4,5,90),(250,0,0,200))
		self.lblDesc.setForeground((250,150,150))
		statusIcon=QIcon().fromTheme("dialog-cancel")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientForbidden

	def _getAppStatus(self):
		status=""
		if self.app.get("forbidden",False)==True:
			self._setGradientForbidden()
		elif len(self.app.get("bundle",[]))==0 or self.app.get("unavailable",False)==True:
			self._setGradientPending()
		else:
			self.instBundle=self.helper.getInstalledBundle(self.app)#self._getInstalledBundle()
			if self.instBundle!="":
				self._setGradientInstalled()
			else:
				self._setGradientAvailable()
		return(status)
	#def _getAppStatus

