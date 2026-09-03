#!/usr/bin/python3
import os,json
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
		self.loadImgSync(self.app["icon"])
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

	def _setGradientWebApp(self):
		self.lblDesc.setGradient((224,214,255,50),(170,10,220,250))
		statusIcon=QIcon().fromTheme("internet-web-browser")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientPending

	def _setGradientPending(self):
		self.lblDesc.setGradient((136,136,36,100),(120,150,20,250))
		self.lblDesc.setForeground((100,100,50))
		statusIcon=QIcon().fromTheme("clock")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientPending

	def _setGradientForbidden(self):
		self.lblDesc.setGradient((224,4,5,90),(250,0,0,200))
		self.lblDesc.setForeground((250,50,50))
		statusIcon=QIcon().fromTheme("dialog-cancel")
		pxm=statusIcon.pixmap(32,32)
		self.lblStatus.setPixmap(pxm)
	#def _setGradientForbidden

	def _getAppStatus(self):
		status=""
		if self.app.get("forbidden",False)==True:
			self._setGradientForbidden()
		elif self.app.get("webapp",False)==True:
			self._setGradientWebApp()
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

	def refreshApp(self,app):
		if isinstance(app,str):
			self.app=json.loads(app)
			if isinstance(self.app,list):
				self.app=self.app[0]
		else:
			self.app=app
		self._getAppStatus()
	#def refreshApp
