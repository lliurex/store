#!/usr/bin/python3
import json,time
from functools import partial
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QHBoxLayout,QApplication
from PySide6.QtCore import Qt,Signal
from QtExtraWidgets import QSearchBox,QFlowTouchWidget
from PySide6.QtGui import QIcon,QPixmap
from extras.i18n import *
from extras.constants import *
from wdg import btnApp
from lib.threadLib import rebostQuery

class QAppsPane(QWidget):
	ready=Signal()
	beginLoad=Signal("PyObject")
	requestInstall=Signal("PyObject")
	search=Signal(str)
	def __init__(self,*args,parent=None,**kwargs):
		self.__EXIT__=False
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.actionAppBtn={}
		self.__initScreen__()
		self.destroyed.connect(partial(QAppsPane._onDestroy,self.__dict__))
		self.rebostQuery=rebostQuery(rebost=self.rebost)
		self.rebostQuery.queryCompleted.connect(self._loadGrid)
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		selfDict["__EXIT__"]=True
	#def _onDestroy

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

	def _defEmptyContainer(self):
		wdg=QWidget()
		glay=QGridLayout(wdg)
		lblIcn=QLabel()
		icn=QIcon.fromTheme("align-none")
		pxm=icn.pixmap(self.width(),self.height(),QIcon.Mode.Disabled)
		lblIcn.setPixmap(pxm)
		glay.addWidget(lblIcn,0,0,1,1)
		lblTxt=QLabel("<p><strong>{}</strong></p>".format(i18n["ERREMPTY"]))
		lblTxt.setStyleSheet("""padding:5px;""")
		fLbl=lblTxt.font()
		lblTxt.setAutoFillBackground(True)
		fLbl.setPointSize(fLbl.pointSize()+4)
		lblTxt.setFont(fLbl)
		glay.addWidget(lblTxt,0,0,1,1,Qt.AlignCenter|Qt.AlignCenter)
		return(wdg)
	#def _defEmptyContainer

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(SPACING,0,0,0)
		lay.setSpacing(SPACING)
		self.flow=self._defFlow()
		self.container=QWidget()
		hlay=QHBoxLayout(self.container)
		hlay.addSpacing(SPACING)
		hlay.addWidget(self.flow)
		self.layout().addWidget(self.container,0,0,1,self.layout().columnCount())
		self.emptyContainer=self._defEmptyContainer()
		self.layout().addWidget(self.emptyContainer,0,0,1,self.layout().columnCount(),Qt.AlignCenter|Qt.AlignCenter)
		self.emptyContainer.hide()
		
	#def __initScreen__

	def _installApp(self,*args):
		btn=self.flow.currentItem()
		self.requestInstall.emit(btn)
		self.actionAppBtn.update({btn.app["id"]:btn})
	#def _installApp

	def _loadGrid(self,apps):
		btnW=350+SPACING
		if len(apps)>0:
			self.emptyContainer.hide()
			self.container.show()
			apps.reverse()
			while apps:
				app=apps.pop()
				if app==None:
					continue
				if isinstance(app,str):
					app=json.loads(app)
				btn=btnApp.QAppButton(app)
				btn.setFixedWidth(btnW)
				if self.__EXIT__==False:
					self.flow.addWidget(btn)
					btn.clicked.connect(self._installApp)
				else:
					break
				if len(apps)>50:
					if len(apps)%50==0:
						time.sleep(0.1)
					if len(apps)%3==0:
						QApplication.processEvents()
				else:
					QApplication.processEvents()
		else:
			self.emptyContainer.show()
		if self.__EXIT__==False:
			self.ready.emit()
	#def _loadGrid

	def load(self,*args,category=False):
		self.flow.clean()
		self.blockSignals(False)
		if category==True:
			self.rebostQuery.setQuery("loadCategory",args[0])
		else:
			self.rebostQuery.setQuery("search",args[0])
		self.rebostQuery.start()
	#def load

