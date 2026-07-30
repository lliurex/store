#!/usr/bin/python3
import json
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QHBoxLayout
from PySide6.QtCore import Qt
from QtExtraWidgets import QSearchBox,QFlowTouchWidget,QPushInfoButton
from extras.i18n import *
from extras.constants import *

class QAppsPane(QWidget):
	def __init__(self,*args,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.__initScreen__()
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

	def load(self,*args):
		self.flow.clean()
		apps=json.loads(self.rebost.searchApp(args[0]))
		if len(apps)>0:
			for app in apps:
				btn=QPushInfoButton(scroll=True)
				btn.loadImg(app["icon"])
				btn.setText(app["name"])
				btn.setDescription(app["summary"])
				self.flow.addWidget(btn)
				btn.setMinimumWidth((self.width()+9*SPACING)/3)
		self.flow.repaint()
		self.repaint()
		self.show()
		for btn in self.flow.children():
			btn.show()
			btn.repaint()
			print(btn)
	#def load

