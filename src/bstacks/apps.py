#!/usr/bin/python3
import json
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QHBoxLayout,QApplication
from PySide6.QtCore import Qt,Signal
from QtExtraWidgets import QSearchBox,QFlowTouchWidget,QPushInfoButton
from extras.i18n import *
from extras.constants import *
from wdg import btnApp


class QAppsPane(QWidget):
	ready=Signal()
	beginLoad=Signal("PyObject")
	def __init__(self,*args,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.__initScreen__()
		self.beginLoad.connect(self._loadGrid)
	#def __init__

	def _defSearch(self):
		wdg=QSearchBox()
		wdg.txtSearch.setPlaceholderText(i18n["SEARCH"])
		return(wdg)
	#def _defSearch

	def _defFlow(self):
		wdg=QFlowTouchWidget()
		wdg.setFocusPolicy(Qt.NoFocus)
		wdg.setObjectName("qFlow")
		wdg.setSpacing(SPACING)
		#wdg.leaveEvent=self.tableLeaveEvent
		wdg.setAttribute(Qt.WA_AcceptTouchEvents)
		wdg.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		return(wdg)
	#def _defFlow

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(SPACING,0,0,0)
		lay.setSpacing(SPACING)
		searchBox=self._defSearch()
		searchBox.setMinimumWidth(512)
		self.layout().addWidget(searchBox,0,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.flow=self._defFlow()
		wdg=QWidget()
		hlay=QHBoxLayout(wdg)
		hlay.addSpacing(SPACING)
		hlay.addWidget(self.flow)
		self.layout().addWidget(wdg,1,0,1,self.layout().columnCount())
		self.layout().setRowStretch(1,1)
	#def __initScreen__

	def _loadGrid(self,apps):
		wSize=(self.sizeHint().width()/2)+SPACING*4
		if len(apps)>0:
			for app in apps:
				if app==None:
					continue
				if isinstance(app,str):
					app=json.loads(app)
				btn=btnApp.QAppButton(app)
				self.flow.addWidget(btn)
				QApplication.processEvents()
				#btn.setMinimumWidth((self.width()+9*SPACING)/3)
				btn.setFixedWidth(wSize)
		self.ready.emit()

	def load(self,*args,category=False):
		self.flow.clean()
		if category==True:
			apps=json.loads(self.rebost.getAppsInCategory(args[0]))
			apps=apps[args[0]]
		else:
			apps=json.loads(self.rebost.searchApp(args[0]))
		self.beginLoad.emit(apps)
	#def load

