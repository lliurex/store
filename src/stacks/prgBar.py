#!/usr/bin/python3
import os,time
import json
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QGraphicsDropShadowEffect,QSizePolicy,QWidget
from PySide2.QtCore import Qt,Signal,QThread,QCoreApplication,QTimer
from PySide2.QtGui import QIcon,QCursor,QMouseEvent,QPixmap,QImage,QPalette,QColor,QMovie
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")

class progress(QThread):
	updated=Signal()
	def __init__(self,*args,**kwargs):
		QThread.__init__(self)
		self.running=True
		self.inc=1
		self.color=QColor(255,255,255)
		self.oldColor=QColor(253,253,253)
		self.lbl=args[0]
		self.pxm=args[1]
		self.updated.connect(self._doProgress)

	def run(self):
		self.running=True
		while self.running==True:
			print("EMITIENDO")
			self.updated.emit()
			#self._doProgress()
			time.sleep(0.05)

	def _doProgress(self,*args):
		color=QColor(self.oldColor.red()+self.inc,self.oldColor.green()+self.inc,self.oldColor.blue()+self.inc)
		self.oldColor=color
		if color.red()<150:
			self.inc*=-1
		elif color.red()>254:
			self.inc*=-1
		#print(self.inc)
		print(color.red())
		pxm2=QPixmap(self.pxm.size())
		pxm2.fill(color)
		pxm2.setMask(self.pxm.createMaskFromColor(Qt.transparent))
		self.lbl.setPixmap(pxm2)

	def stop(self):
		print("ME DETIENEN")
		self.running=False

class QProgressImage(QLabel):
	def __init__(self,*args,**kwargs):
		QLabel.__init__(self)
		#lblProgress=QLabel(i18n["NEWDATA"])
		#vbox.addWidget(lblProgress)#,Qt.AlignCenter|Qt.AlignBottom)
		img=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc","side1.png")
		self.color=QColor(255,255,255)
		self.pxm=QPixmap(img).scaled(172,172,Qt.KeepAspectRatio,Qt.SmoothTransformation)
		self.pxm2=QPixmap(self.pxm.size())
		#self.updateTimer=QTimer()
		#self.updateTimer.timeout.connect(self._doProgress)
		#self.updateTimer.start(1)
		self.updateTimer=progress(self,self.pxm,self.pxm2)
		self.updateTimer.updated.connect(self._doProgress)
		#self.setPixmap(self.pxm)
		mov=QMovie()
		self.setMovie(mov)
		self.setAlignment(Qt.AlignCenter)
		self.inc=5
		self.oldColor=QColor(255-self.inc,255-self.inc,255-self.inc)
		self.running=False
		self.setStyleSheet("""QWidget{background:#002c4f}""")

	def start(self):
		self.updateTimer.start()
		self.setVisible(True)

	def stop(self):
		self.updateTimer.stop()
		self.setVisible(False)
		
	def _beginDoProgress(self,*args):
		if self.running==False:
			self._doProgress()

	def _doProgress(self,*args):
		print("HEY")
		self.running=True
		color=QColor(self.oldColor.red()+self.inc,self.oldColor.green()+self.inc,self.oldColor.blue()+self.inc)
		self.oldColor=color
		if color.red()<150:
			self.inc*=-1
		elif color.red()>254:
			self.inc*=-1
		#print(self.inc)
		print(color.red())
		self.pxm2.fill(color)
		self.pxm2.setMask(self.pxm.createMaskFromColor(Qt.transparent))
		self.setPixmap(self.pxm2)
		self.update()
		self.running=False

	def _changeColor(*args):
		color2=QColor(122,122,122)
		print(color2)
		pxm2.fill(color2)
		pxm2.setMask(pxm.createMaskFromColor(Qt.transparent))
		self.setPixmap(pxm2)
