#!/usr/bin/python3
import os
from functools import partial
from PySide6.QtWidgets import QLabel,QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt,Signal
from PySide6 import QtGui
from QtExtraWidgets import QScreenShotContainer,QScrollLabel
import gettext
from constants import *
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"INSTALL":_("Install")}

class QLabelArticle(QLabel):
	clicked=Signal("PyObject")
	def __init__(self,parent=None):
		QLabel.__init__(self, parent)
		self.setAlignment(Qt.AlignCenter)
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		layout=QVBoxLayout()
		self.scrCnt=QScreenShotContainer()
		self.lbl=QScrollLabel()
		self.lbl.setMaximumHeight(64)
		layout.addWidget(self.lbl,Qt.AlignBottom)
		layout.addWidget(self.scrCnt,Qt.AlignTop)
		layout.setStretch
		self.iconSize=256
		self.th=[]
		self.setLayout(layout)
		self.destroyed.connect(partial(QLabelArticle._stop,self.__dict__))
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

	def loadImg(self,img):
		if self.iconSize>0:
			baseSize=self.iconSize
		else:
			baseSize=ICON_SIZE
		wsize=baseSize
		self.setMinimumWidth(1)
		if os.path.isfile(img):
			icn=QtGui.QPixmap.fromImage(QtGui.QImage(img))
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
		print(baseSize)
	#def load

	def setText(self,text):
		self.lbl.setText("<a href=\"{0}\">{0}</a>".format(text))
#class QLabelRebostApp

