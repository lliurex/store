#!/usr/bin/python3
import os
from functools import partial
import json
import requests
from PySide2.QtWidgets import QLabel
from PySide2.QtCore import Qt,Signal,QSize,QThread
from PySide2 import QtGui
import gettext
from constants import *
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install")}

class _imageLoader(QThread):
	fetched=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.uri=kwargs.get("uri","")
		self.pxm=kwargs.get("pxm","")
		self.name=os.path.basename(self.uri)
		self.pxm=QtGui.QPixmap()
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
	#def __init__
	
	def _debug(self,msg):
		if self.dbg==True:
			print("_imageLoader: {}".format(msg))
	#def _debug

	def setPxm(self,pxm):
		self.pxm=pxm
	#def setPxm

	def setUri(self,uri):
		self.uri=uri
		self.pxm=QtGui.QPixmap()
	#def setUri

	def run(self):
		pxm=self.pxm
		if pxm.isNull():
			uri=self.uri
			if self.uri!="":
				if not os.path.exists(uri):
					uri=os.path.join(self.cacheDir,os.path.basename(uri))
				if not os.path.exists(uri):
					uri=self.uri
			if not os.path.exists(uri):
				if uri==os.path.basename(uri):
					icn=QtGui.QIcon()
					if uri.strip()=="":
						#Wayland related? Qt seems to lose the ability for loading icons from main theme.
						icn.setThemeName("hicolor")
						icn.fromTheme("appedu-generic")
					else:
						icn.fromTheme(uri)
						if icn.isNull():
							if os.path.exists("/usr/share/rebost-data/icons/cache/{0}.png".format(uri)):
								icn.addFile("/usr/share/rebost-data/icons/cache/{0}.png".format(uri))
							elif os.path.exists("/usr/share/rebost-data/icons/cache/{0}_{0}.png".format(uri)):
								icn.addFile("/usr/share/rebost-data/icons/cache/{0}_{0}.png".format(uri))
							elif os.path.exists("/usr/share/rebost-data/icons/64x64/{0}.png".format(uri)):
								icn.addFile("/usr/share/rebost-data/icons/64x64/{}.png".format(uri))
							elif os.path.exists("/usr/share/rebost-data/icons/64x64/{0}_{0}.png".format(uri)):
								icn.addFile("/usr/share/rebost-data/icons/64x64/{0}_{0}.png".format(uri))
						if icn.isNull():
							icn.setThemeName("hicolor")
							icn.fromTheme("appedu-generic")
					pxm=icn.pixmap(QSize(64,64))
				elif "://":
					try:
						img=requests.get(uri,timeout=5)
						img.close()
						pxm.loadFromData(img.content)
						if not os.path.exists(self.cacheDir):
							os.makedirs(self.cacheDir)
						fPath=os.path.join(self.cacheDir,os.path.basename(uri))
						if not os.path.exists(fPath):
							pxm=pxm.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
							pxm.save(fPath,"PNG")#,quality=5)
					except Exception as e:
						icn=QtGui.QIcon()
						icn.setThemeName("hicolor")
						icn=QtGui.QIcon.fromTheme("appedu-generic")
						pxm=icn.pixmap(QSize(64,64))
			else:
				pxm=QtGui.QPixmap()
				pxm.load(uri)
		#self._debug("Emit {}".format(pxm))
		self.fetched.emit(pxm)
#class _imageLoader(QThread):

class QLabelRebostApp(QLabel):
	clicked=Signal("PyObject")
	def __init__(self,parent=None):
		QLabel.__init__(self, parent)
		self.setAlignment(Qt.AlignCenter)
		self._imageLoader=_imageLoader()
		self._imageLoader.fetched.connect(self._setIcon)
		self.iconSize=-1
		self.pixmapPath=""
		self.app={}
		self.th=[]
		self.destroyed.connect(partial(QLabelRebostApp._stop,self.__dict__))
	#def __init__

	@staticmethod
	def _stop(*args):
		selfDict=args[0]
		if "th" in selfDict.keys():
			for th in selfDict["th"]:
				th.finished.emit()
				th.blockSignals(True)
				th.requestInterruption()
				th.quit()
				th.deleteLater()
			for th in selfDict["th"]:
				if th.isRunning():
					th.requestInterruption()
					th.quit()
					th.wait()
	#def _stop(*args):

	def setIconSize(self,size):
		self.iconSize=size
	#def setIconSize

	def _setIcon(self,*args):
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		pxm=args[0]
		if pxm.isNull()==True:
			icn=QtGui.QIcon()
			icn.setThemeName("hicolor")
			icn=QtGui.QIcon.fromTheme("appedu-generic")
			pxm=icn.pixmap(QSize(64,64))
		self.setPixmap(pxm.scaled(wsize,baseSize,Qt.IgnoreAspectRatio,Qt.FastTransformation))
	#def _setIcon(self,*args):

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
			self._imageLoader.setPxm(img)
		else:
			if not isinstance(img,str):
				img=""
			if img=="":
				img=app["name"]
			self._imageLoader.setUri(img)
		self._imageLoader.start()
		self.th.append(self._imageLoader)
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

