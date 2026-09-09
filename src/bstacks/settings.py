#!/usr/bin/python3
import time
from PySide6.QtWidgets import QWidget,QGridLayout,QPushButton,QLabel,QSizePolicy,QCheckBox
from PySide6.QtCore import Qt,Signal
from wdg.topBar import QTopBar
from QtExtraWidgets import QStackedWindowItem
from extras.i18n import *
from extras.constants import *
from repoman.repomanager import manager

class QSettingsPane(QWidget):
	loadContent=Signal(str)
	ready=Signal()
	exception=Signal(str)
	def __init__(self,*args,parent=None,**kwargs):
		QWidget.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.repoman=manager()
		self.__initScreen__()
	#def __init__

	def _topBar(self):
		wdg=QTopBar()
		for chld in wdg.children():
			if isinstance(chld,QPushButton):
				chld.setText(i18n.get(chld.property("name"),chld.property("name")).upper())
		#wdg.loadHome.connect(self._goHome)
		wdg.loadNews.connect(self._loadContent)
		wdg.loadRecs.connect(self._loadContent)
		wdg.loadZmds.connect(self._loadContent)
		wdg.loadCats.connect(self._loadContent)
		return (wdg)
	#def _topBar

	def _loadContent(self,content):
		self.loadContent.emit(content)
	#def _loadContent

	def _exception(self,*args):
		self.exception.emit(*args)
	#def _exception

	def __initScreen__(self):
		lay=QGridLayout(self)
		lay.setContentsMargins(0,0,0,0)
		lay.setSpacing(0)
		topBar=self._topBar()
		lay.addWidget(topBar,0,0,1,self.layout().columnCount(),Qt.AlignTop|Qt.AlignCenter)
		self.chkRestricted=QCheckBox(i18n["SETTING_RESTRICTED_MODE"])
		lay.addWidget(self.chkRestricted,1,0,1,1)
		self.chkApt=QCheckBox(i18n["SETTING_PLUGIN_APT"])
		lay.addWidget(self.chkApt,2,0,1,1)
		self.chkApp=QCheckBox(i18n["SETTING_PLUGIN_APPIMAGE"])
		lay.addWidget(self.chkApp,3,0,1,1)
		self.chkFla=QCheckBox(i18n["SETTING_PLUGIN_FLATPAK"])
		lay.addWidget(self.chkFla,4,0,1,1)
		self.chkSna=QCheckBox(i18n["SETTING_PLUGIN_SNAP"])
		lay.addWidget(self.chkSna,5,0,1,1)
	#def __initScreen__

	def load(self):
		try:
			self.updateScreen()
		except Exception as e:
			print(e)
		self.ready.emit()
	#def load(self):

	def _checkExternalRepos(self):
		repos=self.repoman.getRepos()
		status=False
		for name,repoData in repos.items():
			if name.startswith("http://lliurex.net")==False:
				for repoRelease,repoInfo in repoData.items():
					status=repoInfo.get("enabled")
					if status==True:
						break
		return True
	#def _checkExternalRepos

	def updateScreen(self):
		settings=self.rebost.getConfig()
		self.chkRestricted.setChecked(settings.get("onlyVerified",False))
		self.chkApt.setChecked(self._checkExternalRepos())
		self.chkApp.setChecked(settings.get("appimage",True))
		self.chkSna.setChecked(settings.get("snap",True))
		self.chkFla.setChecked(settings.get("flatpak",True))
	#def updateScreen
