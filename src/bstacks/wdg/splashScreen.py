#!/usr/bin/python3
from PySide6.QtWidgets import QMainWindow,QLabel
from PySide6.QtCore import Qt,QTimer

class QSplashWidget(QMainWindow):
	def __init__(self,icn,*args):
		super().__init__()
		self.setAttribute(Qt.WA_TranslucentBackground,True)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setMinimumSize(256,256)
		self.lbl=QLabel()
		self.setCentralWidget(self.lbl)
		self.setWindowIcon(icn)
		self.timer=QTimer()
		self.timer.timeout.connect(self.close)
	#def __init__
	
	def setIcon(self,pxm):
		self.lbl.setPixmap(pxm.scaled(256,256))
	#def setIcon

	def load(self):
		self.show()
		self.timer.start(3000)
	#def load
#class QSplashWidget
