#!/usr/bin/python3
import os
from functools import partial
import json
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt,Signal
from PySide6 import QtGui
from QtExtraWidgets import QScreenShotContainer
import gettext
from constants import *
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install")}

class QLabelRebostApp(QLabel):
	clicked=Signal("PyObject")
	def __init__(self,parent=None):
		QLabel.__init__(self, parent)
		self.setAlignment(Qt.AlignCenter)
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		self.scrCnt=QScreenShotContainer()
		self.iconSize=-1
		self.pixmapPath=""
		self.app={}
		self.th=[]
		self.destroyed.connect(partial(QLabelRebostApp._stop,self.__dict__))
	#def __init__

	@staticmethod
	def _stop(*args):
		self=args[0]
		if "scr" in self.keys():
			self["scr"].blockSignals(True)
			self["scr"].requestInterruption()
			self["scr"].deleteLater()
			self["scr"].wait()
	#def _stop(*args):

	def setIconSize(self,size):
		self.iconSize=size
	#def setIconSize

	def loadImg(self,app):
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		self.app=app
		img=app.get('icon','')
		self.setMinimumWidth(1)
		icn=''
		self.pixmapPath=""
		if isinstance(img,QtGui.QPixmap):
			icn=img
		elif os.path.isfile(img):
			if "/usr/share/banners/lliurex-neu" in img:
				wsize=int(baseSize*1.8)
			icn=QtGui.QPixmap.fromImage(QtGui.QImage(img))
			self.pixmapPath=img
		elif img=='':
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
			icn=icn2.pixmap(baseSize,baseSize)
			self.pixmapPath=app.get("pkgname")
		if icn:
			self.setPixmap(icn.scaled(wsize,baseSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
			self.setMinimumWidth(wsize+10)
			if self.pixmapPath=="":
				self._savePixmap()
		elif img.startswith('http'):
			scr=self.scrCnt.loadScreenShot(img,self.cacheDir)
			scr.imageReady.connect(self.load)
			scr.start()
			self.th.append(scr)
	#def loadImg
	
	def load(self,*args):
		img=args[0]
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		self.setPixmap(img.scaled(wsize,baseSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		self.setMinimumWidth(baseSize+10)
		self._savePixmap()
	#def load

	def _savePixmap(self):
		pxm=self.pixmap()
		stripName=''.join(ch for ch in os.path.basename(self.app.get("icon")) if ch.isalnum())
		if stripName.endswith("png"):
			stripName=stripName.replace("png",".png")
		fPath=os.path.join(self.cacheDir,stripName)
		if not os.path.exists(fPath):
			pxm=pxm.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
			pxm.save(fPath,"PNG")#,quality=5)
		self.pixmapPath=fPath
	#def _savePixmap
#class QLabelRebostApp

