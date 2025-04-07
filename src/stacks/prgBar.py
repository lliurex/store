#!/usr/bin/python3
import os,time
import json
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QGraphicsDropShadowEffect,QSizePolicy,QWidget,QVBoxLayout
from PySide2.QtCore import Qt,Signal,QThread,QCoreApplication,QTimer
from PySide2.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor,QMovie
import css
from constants import *
import random
import gettext
_ = gettext.gettext

i18n={
	"GETTINGAPPS":_("Getting applications"),
	"WAITMOMENT":_("Wait a moment"),
	"SETTINGUP":_("Setting up information"),
	"FILLINGINFO":_("Filling caches"),
	"WARMUP":_("Warming up engine"),
	"ACCESINGNETWORK":_("Network checking")
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
			time.sleep(0.05)
	#def run

	def stop(self):
		self.running=False
	#def stop

class QProgressImage(QWidget):
	def __init__(self,*args,**kwargs):
		QWidget.__init__(self)
		lay=QVBoxLayout()
		self.setLayout(lay)
		self.setObjectName("prgBar")
		self.setStyleSheet(css.prgBar())
		#lblProgress=QLabel(i18n["NEWDATA"])
		#vbox.addWidget(lblProgress)#,Qt.AlignCenter|Qt.AlignBottom)
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","progressBar267x267.png")
		self.color=QColor(255,255,255)
		self.pxm=QPixmap(img)#.scaled(267,267,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		self.pxm2=QPixmap(self.pxm.size())
		self.lblPxm=QLabel()
		self.lblInfo=QLabel(i18n["SETTINGUP"])
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
		self.inc=5
		self.oldColor=QColor(255-self.inc,255-self.inc,255-self.inc)
		self.running=False

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
			if int(time.time())-self.oldTime>3:
				rnd=random.randint(0,len(i18n))-1
				key=list(i18n.keys())[rnd]
				self.lblInfo.setText(i18n[key])
				self.oldTime=time.time()
			
		color=QColor(self.oldColor.red()+self.inc,self.oldColor.green()+self.inc,self.oldColor.blue()+self.inc)
		self.oldColor=color
		if color.red()<150:
			self.inc*=-1
		elif color.red()>254:
			self.inc*=-1
		#print(self.inc)
		self.pxm2.fill(color)
		self.pxm2.setMask(self.pxm.createMaskFromColor(Qt.transparent))
		self.lblPxm.setPixmap(self.pxm2)
		self.update()
		self.running=False
	#def _doProgress

	def _changeColor(*args):
		color2=QColor(122,122,122)
		pxm2.fill(color2)
		pxm2.setMask(pxm.createMaskFromColor(Qt.transparent))
		self.setPixmap(pxm2)
