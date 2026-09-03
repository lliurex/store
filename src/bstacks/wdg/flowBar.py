#!/usr/bin/python3
import os
from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtWidgets import QScrollArea,QHBoxLayout,QWidget,QGridLayout,QPushButton,QHeaderView,QSizePolicy
from PySide6.QtGui import QIcon,QColor,QPainter,QLinearGradient
from QtExtraWidgets import QTableTouchWidget,QPushInfoButton
from extras.constants import *

class QFlowBar(QScrollArea):
	selected=Signal("PyObject")
	def __init__(self,*args,parent=None,**kwargs):
		QScrollArea.__init__(self, parent)
		self.cache=os.path.join(os.environ["HOME"],".cache","store","imgs")
		self._initGui()
		self.setWidgetResizable(True)
		self.itemsPerPage=1
		self.spacing=0
		self.defaultSize=0
		self.showScrollBar(False)
		self.overlay=False
		self.overlayGradientFrom=(224,214,255,50)
		self.overlayGradientTo=(220,150,120,110)
		self.onlyImg=False
		self.overlayTextImg=False
		self.content={}
		self.loadImgSync=False
		self.wsize=0
	#def __init__

	def wheelEvent(self, event):
		yDir=event.angleDelta().y()
		xPos=self.table.horizontalScrollBar().value()-yDir
		self.table.horizontalScrollBar().setValue(xPos)
		event.accept()
	#def wheelEvent

	def clean(self):
		self.content={}
		self.table.setColumnCount(0)
	#def clean

	def count(self):
		return(self.table.columnCount())
	#def count

	def _initGui(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.table=QTableTouchWidget()
		self.table.setColumnCount(0)
		self.table.setRowCount(1)
		self.table.horizontalHeader().hide()
		self.table.setAutoScroll(False)
		self.table.verticalHeader().hide()
		self.table.setShowGrid(False)
		self.table.cellClicked.connect(self._emit)
		self.table.itemActivated.connect(self._emit)
		lay.addWidget(self.table,0,1,1,1)
		self.btnPrev=QPushButton()
		self.btnPrev.setIcon(QIcon.fromTheme("go-previous"))
		self.btnPrev.clicked.connect(self._movePrev)
		lay.addWidget(self.btnPrev,0,0,1,1,Qt.AlignLeft)
		self.btnNext=QPushButton()
		self.btnNext.clicked.connect(self._moveNext)
		self.btnNext.setIcon(QIcon.fromTheme("go-next"))
		lay.addWidget(self.btnNext,0,2,1,1,Qt.AlignRight)
		self.setWidget(wdg)
	#def _initGui_

	def showScrollBar(self,show):
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		if show==False:
			self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			self.btnNext.show()
			self.btnPrev.show()
		else:
			self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
			#self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
			self.btnNext.hide()
			self.btnPrev.hide()
	#def showScrollBar

	def _moveNext(self):
		tsize=self.table.columnCount()*self.table.columnWidth(0)
		tpos=self.table.horizontalScrollBar().value()
		npos=min(tsize,tpos+self.table.columnWidth(0)-self.btnNext.iconSize().width())
		self.table.horizontalScrollBar().setValue(npos)
	#def _moveNext

	def _movePrev(self):
		tpos=self.table.horizontalScrollBar().value()
		npos=max(0,tpos-self.table.columnWidth(0)+self.btnPrev.iconSize().width())
		self.table.horizontalScrollBar().setValue(npos)
	#def _movePrev

	def _chkContents(self,feed,data):
		exists=False
		if data.get("title","").replace(" ","") in self.content.get(feed,[]):
			exists=True
		if feed not in self.content.keys():
			self.content[feed]=[]
		self.content[feed].append(data.get("title","").replace(" ",""))
		return(exists)
	#def _chkContents

	def _infoBtn(self,data):
		def mousePressEvent(event):
			event.ignore()
		btn=QPushInfoButton(overlay=self.overlay)
		btn.setCacheDir(self.cache)
		btn.mousePressEvent=mousePressEvent
		btn.label.setAlignment(Qt.AlignLeft)
		img=data.get("img")
		if self.defaultSize!=0:
			btn.defaultSize=self.defaultSize
		if data.get("summary","")=="":
			btn.lblDesc.hide()
		else:
			btn.setDescription(data.get("summary"))
		btn.setText(data.get("title"))
		if self.loadImgSync==False:
			btn.loadImg(img)
		else:
			btn.loadImgSync(img)
		if self.onlyImg==True:
			btn.layout().addWidget(btn.icon,0,0,2,2,Qt.AlignCenter)
			btn.lblDesc.hide()
			btn.label.setVisible(self.overlayTextImg)
			if self.overlayTextImg==True:
				btn.label.setFixedWidth(self.defaultSize)
				btn.label.setAutoFillBackground(True)
				btn.label.setAlignment(Qt.AlignCenter)
				btn.layout().addWidget(btn.label,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		if self.overlay==True:
			btn.lblDesc.label.setGradient(self.overlayGradientFrom,self.overlayGradientTo)
		#btn.setFixedHeight(self.defaultSize)
		return(btn)
	#def _infoBtn

	def _simpleBtn(self,data):
		def mousePressEvent(event):
			event.ignore()
		def _paintEvent(self,event):
			painter = QPainter(self)
			painter.setRenderHint(QPainter.Antialiasing)
			gradient = QLinearGradient(0, 0, 50, 50)
			lcolor=QColor(hcolor).lighter(50)
			gradient.setColorAt(0, QColor(hcolor)) 
			gradient.setColorAt(1, QColor(lcolor))
			painter.fillRect(self.rect(), gradient)
			painter.setPen(Qt.white)
			painter.drawText(self.rect(), Qt.AlignCenter|Qt.AlignCenter, self.text())
			painter.end()

		btn=QPushButton()
		hcolor=data["img"]
		btn.paintEvent=_paintEvent.__get__(btn,QPushButton)
		btn.setCursor(Qt.PointingHandCursor)
		btn.mousePressEvent=mousePressEvent
		if self.defaultSize!=0:
			btn.setFixedHeight(self.defaultSize)
		if self.onlyImg==False:
			btn.setText(data.get("title"))
		return(btn)
	#def _simpleBtn

	def updateScreen(self,*args):
		if len(args)==2:
			bheight=0
			if self.wsize==0:
				self.wsize=(self.viewport().width()/self.itemsPerPage)+self.spacing
			wsize=self.wsize
			if isinstance(args[1],dict):
				for idx,data in args[1].items():
					if self._chkContents(args[0],data)==True:
						bheight=-1
						continue
					self.table.setColumnCount(self.table.columnCount()+1)
					if hasattr(self,"simpleButtons"):
						btn=self._simpleBtn(data)
					else:
						btn=self._infoBtn(data)
					btn.setProperty("feed",args[0])
					btn.setProperty("metadata",data.get("metadata",""))
					btn.setFixedWidth(wsize-self.spacing*2)
					spacing=0
					if self.table.columnCount()>1:
						spacing=self.spacing
					wdg=QWidget()
					#btn.setAttribute(Qt.WA_TransparentForMouseEvents,True)
					lay=QHBoxLayout(wdg)
					lay.addWidget(btn)
					self.table.setCellWidget(0,self.table.columnCount()-1,wdg)
					self.table.setColumnWidth(self.table.columnCount()-1,wsize)
					if bheight==0:
						bheight=btn.height()
			if bheight>0:
				self.table.setFixedHeight(bheight+MARGIN*2)
				self.table.setRowHeight(0,bheight+MARGIN)
			elif bheight==0:
				self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.btnNext.setIconSize(QSize(32,self.table.rowHeight(0)/2))
		self.btnPrev.setIconSize(self.btnNext.iconSize())
	#def updateScreen
		
	def _emit(self,*args):
		wdg=self.table.cellWidget(self.table.currentRow(),self.table.currentColumn())
		for chld in wdg.children():
			if hasattr(chld,"text"):
				self.selected.emit(chld)
				break

