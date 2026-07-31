#!/usr/bin/python3
import os
from QtExtraWidgets import QSearchBox,QFlowTouchWidget,QPushInfoButton
import lib.libhelper as libhelper

class QAppButton(QPushInfoButton):
	def __init__(self,*args,parent=None):
		QPushInfoButton.__init__(self, parent,scroll=True)
		self.app=args[0]
		self.defaultSize=64
		self.loadImg(self.app["icon"])
		self.setText(self.app["name"])
		self.setDescription(self.app["summary"])
		self.helper=libhelper.helper()
		self._getAppStatus()
		self.cacheDir=os.path.join(os.environ["HOME"],".cache","store","imgs")
	#def __init__

	def _setGradientAvailable(self):
		self.lblDesc.setGradient((224,214,255,50),(120,150,20,250))
	#def _setGradientAvailable

	def _setGradientInstalled(self):
		self.lblDesc.setGradient((120,150,20,150),(120,150,120,0))
	#def _setGradientInstalled

	def _setGradientPending(self):
		self.lblDesc.setGradient((136,136,136,100),(140,144,144,250))
		self.lblDesc.setForeground((150,150,150))
		self.setEnabled(False)
	#def _setGradientPending

	def _setGradientForbidden(self):
		self.lblDesc.setGradient((224,4,5,90),(250,0,0,200))
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

