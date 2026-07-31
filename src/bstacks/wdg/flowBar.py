#!/usr/bin/python3
from PySide6.QtCore import Qt,QSize
from PySide6.QtWidgets import QScrollArea,QHBoxLayout,QWidget,QGridLayout,QPushButton,QHeaderView
from PySide6.QtGui import QIcon,QColor,QPainter,QLinearGradient
from QtExtraWidgets import QTableTouchWidget,QPushInfoButton

class QFlowBar(QScrollArea):
	def __init__(self,*args,parent=None,**kwargs):
		QScrollArea.__init__(self, parent)
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		self.setWidgetResizable(True)
		self.table=QTableTouchWidget()
		self.table.setColumnCount(0)
		self.table.setRowCount(0)
		self.table.setRowCount(1)
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
		self.itemsPerPage=1
		self.spacing=0
		self.defaultSize=0
		self.table.horizontalHeader().hide()
		self.table.verticalHeader().hide()
		self.table.setShowGrid(False)
		self.showScrollBar(False)
		self.content={}
	#def __init__

	def showScrollBar(self,show):
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		if show==False:
			self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			self.btnNext.show()
			self.btnPrev.show()
		else:
			self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
			#self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
			self.btnNext.hide()
			self.btnPrev.hide()

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
		btn=QPushInfoButton(overlay=self.overlay)
		btn.label.setAlignment(Qt.AlignLeft)
		img=data.get("img")
		btn.setDescription(data.get("summary"))
		if self.defaultSize!=0:
			btn.defaultSize=self.defaultSize
		btn.loadImg(img)
		return(btn)
	#def _infoBtn

	def _simpleBtn(self,data):
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
		return(btn)
	#def _simpleBtn

	def updateScreen(self,*args):
		if len(args)==2:
			bheight=0
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
					btn.setText(data.get("title"))
					wsize=self.width()/self.itemsPerPage
					btn.setFixedWidth(wsize-5)
					spacing=0
					if self.table.columnCount()>1:
						spacing=self.spacing
					wdg=QWidget()
					lay=QHBoxLayout(wdg)
					lay.addSpacing(spacing)
					lay.addWidget(btn)
					self.table.setCellWidget(0,self.table.columnCount()-1,wdg)
					self.table.setColumnWidth(self.table.columnCount()-1,wsize)
					if bheight==0:
						bheight=btn.height()
			if bheight>0:
				self.table.setFixedHeight(bheight+20)
				self.table.setRowHeight(0,bheight+10)
			elif bheight==0:
				self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.btnNext.setIconSize(QSize(32,self.table.rowHeight(0)/2))
		self.btnPrev.setIconSize(self.btnNext.iconSize())
	#def updateScreen
		

