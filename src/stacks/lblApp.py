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

	def loadImg(self,app):
		wsize=ICON_SIZE
		img=app.get('icon','')
		self.setMinimumWidth(1)
		icn=''
		if isinstance(img,QtGui.QPixmap):
			icn=img
		elif os.path.isfile(img):
			if "/usr/share/banners/lliurex-neu" in img:
				wsize=int(ICON_SIZE*1.8)
			icn=QtGui.QPixmap.fromImage(QtGui.QImage(img))
		elif img=='':
			icn2=QtGui.QIcon.fromTheme(app.get('pkgname'),QtGui.QIcon.fromTheme("appedu-generic"))
			icn=icn2.pixmap(ICON_SIZE,ICON_SIZE)
		if icn:
			self.setPixmap(icn.scaled(wsize,ICON_SIZE,Qt.KeepAspectRatio,Qt.SmoothTransformation))
			self.setMinimumWidth(wsize+10)
		elif img.startswith('http'):
			self.scrCnt.addImage(img,self.cacheDir)
		#	self.scr=self.scrCnt.loadScreenShot(img,self.cacheDir)
		#	self.scr.imageReady.connect(self.load)
		#	self.scr.start()
	#def loadImg
	
	def load(self,*args):
		img=args[0]
		self.setPixmap(img.scaled(ICON_SIZE,ICON_SIZE))
		self.setMinimumWidth(ICON_SIZE+10)
	#def load
#class QLabelRebostApp

