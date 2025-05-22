#!/usr/bin/python3
import os,time
from functools import partial
import json
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QGraphicsDropShadowEffect,QSizePolicy,QWidget,QVBoxLayout
from PySide6.QtCore import Qt,Signal,QThread,QCoreApplication,QTimer
from PySide6.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor,QMovie
import css
from constants import *
import random
import gettext
_ = gettext.gettext

i18nLoad={
	"GETTINGINFO":_("Downloading information, wait a moment..."),
	"UPDATINGINFO":_("Upgrading application database")
	}

i18nUnlock={
	"UNLOCKINGDB":_("Loading available applications"),
	}

class progress(QThread):
	updated=Signal()
	def __init__(self,*args,**kwargs):
		QThread.__init__(self)
		self.running=True
	#def __init__

	def run(self):
		self.running=True
		while self.running==True:
			self.updated.emit()
			time.sleep(0.03)
	#def run

	def stop(self):
		self.running=False
	#def stop

class QProgressImage(QWidget):
	def __init__(self,*args,**kwargs):
		QWidget.__init__(self)
		lay=QVBoxLayout()
		self.setLayout(lay)
		self.unlocking=False
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("prgBar")
		self.setStyleSheet(css.prgBar())
		#lblProgress=QLabel(i18n["NEWDATA"])
		#vbox.addWidget(lblProgress)#,Qt.AlignCenter|Qt.AlignBottom)
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","progressBar267x267.png")
		#self.color=QColor(255,255,255)
		self.color=QColor(COLOR_BACKGROUND_DARKEST)
		self.colorEnd=QColor(COLOR_BACKGROUND_LIGHT)
		self.colorCur=self.colorEnd
		self.pxm=QPixmap(img)#.scaled(267,267,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		self.pxm2=QPixmap(self.pxm.size())
		self.lblPxm=QLabel()
		self.lblInfo=QLabel(i18nLoad["GETTINGINFO"])
		lay.setSpacing(0)
		lay.addWidget(self.lblPxm,Qt.AlignBottom)
		lay.addWidget(self.lblInfo,Qt.AlignTop)
		self.lblInfo.setObjectName("lblInfo")
		self.oldTime=0
		#self.updateTimer=QTimer()
		#self.updateTimer.timeout.connect(self._doProgress)
		#self.updateTimer.start(1)
		self.updateTimer=progress(self)
		self.updateTimer.updated.connect(self._doProgress)
		#self.setPixmap(self.pxm)
		self.lblPxm.setAlignment(Qt.AlignCenter)
		self.lblInfo.setAlignment(Qt.AlignCenter)
		self.inc=-5
		self.running=False
		self.destroyed.connect(partial(QProgressImage._onDestroy,self.__dict__))

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		if "updateTimer" in selfDict:
			selfDict["updateTimer"].blockSignals(True)
			selfDict["updateTimer"].requestInterruption()
			selfDict["updateTimer"].deleteLater()
			selfDict["updateTimer"].wait()

	def start(self):
		self.updateTimer.start()
		self.setVisible(True)
	#def start

	def stop(self):
		if self.updateTimer.isRunning():
			self.updateTimer.stop()
		#self.updateTimer.quit()
		#self.updateTimer.wait()
		self.setVisible(False)
	#def stop(self):
		
	def _beginDoProgress(self,*args):
		if self.running==False:
			self._doProgress()
	#def _beginDoProgress

	def _doProgress(self,*args):
		self.running=True
		if self.lblInfo.text()!="":
			if self.unlocking==False:
				i18n=i18nUnlock
			else:
				i18n=i18nLoad
			if (self.oldTime!=0) and (int(time.time())-self.oldTime>3):
				rnd=random.randint(0,len(i18n))-1
				key=list(i18n.keys())[rnd]
				self.lblInfo.setText(i18n[key])
				self.oldTime=time.time()
			elif self.oldTime==0:
				self.oldTime=time.time()
		red=self.colorCur.red()+self.inc
		blue=self.colorCur.blue()+self.inc
		green=self.colorCur.green()+self.inc
		finish=0
		if self.inc>0:
			if red>=self.colorEnd.red():
				red=self.colorEnd.red()
				finish+=1
			if green>=self.colorEnd.green():
				green=self.colorEnd.green()
				finish+=1
			if blue>=self.colorEnd.blue():
				blue=self.colorEnd.blue()
				finish+=1
		else:
			if red<=self.color.red()+3:
				red=self.color.red()+3
				finish+=1
			if green<=self.color.green()+3:
				green=self.color.green()+3
				finish+=1
			if blue<=self.color.blue()+3:
				blue=self.color.blue()+3
				finish+=1
		color=QColor(red,green,blue)
		self.colorCur=color
		if finish==3:
			self.inc*=-1
		self.pxm2.fill(color)
		self.pxm2.setMask(self.pxm.createMaskFromColor(Qt.transparent))
		self.lblPxm.setPixmap(self.pxm2)
		self.update()
		self.running=False
	#def _doProgress

