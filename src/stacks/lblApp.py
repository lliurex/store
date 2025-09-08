#!/usr/bin/python3
import os
from functools import partial
import json
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt,Signal,QSize
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
		self.app=app
		load=True
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		self.pixmapPath=""
		img=app.get('icon','')
		if isinstance(img,QtGui.QPixmap):
			self.load(img)
			return
		elif os.path.isfile(img):
			self.pixmapPath=img
		elif img=='':
			icn=QtGui.QIcon.fromTheme(app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
			if not icn.isNull():
				self.setPixmap(icn.pixmap(QSize(wsize,baseSize)))
				load=False
		elif os.path.exists(os.path.join(self.cacheDir,os.path.basename(img))):
			img=os.path.join(self.cacheDir,os.path.basename(img))
			self.pixmapPath=img
		if load:
			scrCnt=QScreenShotContainer()
			scr=scrCnt.loadScreenShot(img,self.cacheDir)
			scr.imageReady.connect(self.load)
			scr.start()
			self.th.append(scr)
	#	self.scr.wait()
	#def loadImg

	def load(self,*args,**kwargs):
		img=args[0]
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		if "/usr/share/banners/lliurex-neu" in self.pixmapPath:
			wsize=int(baseSize*2.3)
		self.setPixmap(img.scaled(wsize,baseSize,Qt.IgnoreAspectRatio,Qt.FastTransformation))
		self.setMinimumWidth(wsize+10)
		self._savePixmap()
	#def load

	def _savePixmap(self):
		pxm=self.pixmap()
		if isinstance(self.app.get("icon"),QtGui.QPixmap)==True:
			stripName=''.join(ch for ch in os.path.basename(self.app.get("pkgname")) if ch.isalnum())
		else:
			stripName=''.join(ch for ch in os.path.basename(self.app.get("icon")) if ch.isalnum())
		if stripName.endswith("png"):
			stripName=stripName.replace("png",".png")
		fPath=os.path.join(self.cacheDir,stripName)
		if not os.path.exists(fPath):
			pxm=pxm.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.FastTransformation)
			pxm.save(fPath,"PNG")#,quality=5)
		self.pixmapPath=fPath
	#def _savePixmap
#class QLabelRebostApp

