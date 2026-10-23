import sys,time,random
from PySide6.QtWidgets import QApplication, QProgressBar, QWidget, QLabel,QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal,QThread

class animation(QThread):
	tick=Signal()
	def __init__(self,*args):
		super().__init__()
		self.stopTh=False
		self.val=0
	#def __init__(self,*args):

	def run(self):
		while self.stopTh==False:
			t=random.randint(0,3)
			self.move()
			time.sleep(t)
	#def run

	def setBar(self,prg):
		self.prg=prg
	#def setBar

	def move(self):
		self.val+=1
		self.prg.setValue(self.val)
	#def move(self):

	def stop(self):
		self.stopTh=True
	#def stop(self):
#class animation

class QSplashWidget(QWidget):
	def __init__(self,*args):
		super().__init__()
		icn=args[0]
		pxm=args[1]
		lay=QVBoxLayout(self)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setWindowIcon(icn)
		lbl=QLabel()
		lbl.setPixmap(pxm)
		lay.addWidget(lbl)
		self.prg=QProgressBar()
		self.val=0
		self.prg.setRange(0,100)
		lay.addWidget(self.prg)
		self.animation=animation()
		self.animation.setBar(self.prg)
		self.animation.start()
	#def __init__

	def close(self):
		self.animation.stop()
		self.prg.setValue(100)
		QApplication.processEvents()
		time.sleep(0.2)
		self.destroy()

