#!/usr/bin/python3
import os,subprocess,time
import libhelper
from PySide2.QtCore import Signal,QThread
import json,time,subprocess,random
import urllib
from urllib.request import Request
try:
       from lliurex import lliurexup
except:
       lliurexup=None

class llxup(QThread):
	chkEnded=Signal("PyObject")

	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
	#def __init__

	def run(self):
		upgrades=False
		if lliurexup!=None:
			llxup=lliurexup.LliurexUpCore()
			if len(llxup.getPackagesToUpdate())>0:
				upgrades=True
		self.chkEnded.emit(upgrades)
	#def run(self):
#class llxUp

class storeHelper(QThread):
	test=Signal("PyObject")
	gacEnded=Signal("PyObject")
	linEnded=Signal("PyObject")
	lckEnded=Signal()
	lucEnded=Signal(list)
	lstEnded=Signal("PyObject")
	lsgEnded=Signal("PyObject")
	shwEnded=Signal("PyObject")
	rfrEnded=Signal("PyObject")
	mtcEnded=Signal(list)
	srcEnded=Signal("PyObject")
	urlEnded=Signal("PyObject")
	rstEnded=Signal()
	staEnded=Signal(bool)
	cnfEnded=Signal("PyObject")
	catEnded=Signal("PyObject")

	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.rc=kwargs["rc"]
		self.args=[]
		self.action="upgrade"
		self.destroyed.connect(storeHelper._onDestroy)
	#def __init__

	def _onDestroy(*args):
		pass

	def setAction(self,action,*args):
		self.action=action
		if len(args)>0:
			self.args=args
		else:
			self.args=[]
	#def setAction
	
	def run(self):
		if  self.action=="test":
			self._test()
		elif self.action=="config":
			self._getConfig()
		elif self.action=="getAppsInstalledPerCategory":
			self._getAppsInstalledPerCategory()
		elif self.action=="getAppsPerCategory":
			self._getAppsPerCategory()
		elif self.action=="getAppSuggests":
			self._getAppSuggests()
		elif self.action=="getCategories":
			self._getFreedesktopCategories()
		elif self.action=="getLuck":
			self._getLuck()
		elif self.action=="installed":
			self._installed()
		elif self.action=="list":
			self._list()
		elif self.action=="lock":
			self._lock()
		elif self.action=="matchApps":
			self._matchApps()
		elif self.action=="refreshApp":
			self._refreshApp()
		elif self.action=="restart":
			self._restart()
		elif self.action=="search":
			self._search()
		elif self.action=="setAppState":
			self._setAppState()
		elif self.action=="show":
			self._show()
		elif self.action=="updatePkgData":
			self._updatePkgData()
		elif self.action=="urlSearch":
			self._searchByUrl()
		elif self.action=="unlock":
			self._unlock()
	#def run

	def _test(self):
		if self.rc!=None:
			apps=self.rc.execute("list","lliurex")
			if len(apps)==2:
				self.test.emit(False)
			else:
				self.test.emit(True)
		else:
			self.test.emit(False)
	#def _test

	def _getAppsInstalledPerCategory(self):
		apps=[]
		apps=self.rc.getAppsInstalledPerCategory()
		self.gacEnded.emit(apps)
	#def _getAppsInstalledPerCategory

	def _getAppsPerCategory(self):
		apps=[]
		apps=self.rc.getAppsPerCategory()
		self.gacEnded.emit(apps)
	#def _getAppsPerCategory

	def _getAppSuggests(self,*args):
		apps=[]
		if self.args[0]!="":
			limit=5
			if len(self.args)>1:
				limit=self.args[1]
			seen=[self.args[0].get("name")]
			suggests=self.args[0].get("suggests",[])
			keywords=self.args[0].get("keywords",[])
			categories=self.args[0].get("categories",[])
			extraTokens=keywords+categories
			random.shuffle(extraTokens)
			random.shuffle(apps)
			if len(extraTokens)>6:
				tokens=extraTokens[random.randint(0,int(len(extraTokens)/2)):random.randint(int(len(extraTokens)/2)+1,len(extraTokens))]
			else:
				tokens=extraTokens
			for extra in tokens:
				search=self.rc.searchApp(extra)
				jsearch=json.loads(search)
				for app in jsearch:
					if app.get("name") not in seen:
						seen.append(app.get("name"))
						apps.append(app)
			if len(apps)==0:
				if len(extraTokens)>6:
					tokens=extraTokens[random.randint(0,int(len(extraTokens)/2)):random.randint(int(len(extraTokens)/2)+1,len(extraTokens))]
				else:
					tokens=extraTokens
				for extra in tokens:
					search=self.rc.searchApp(extra)
					jsearch=json.loads(search)
					for app in jsearch:
						if app.get("hidden",False) == True:
							continue
						if app.get("name") not in seen:
							seen.append(app.get("name"))
							apps.append(app)
			random.shuffle(apps)
			for suggest in suggests:
				app=json.loads(self.rc.showApp(suggest))
				if len(app)>0:
					apps.insert(0,app[0])
			apps=apps[0:min(limit,len(apps))]
		self.lsgEnded.emit(apps)
	#def _getAppSuggests
	
	def _getConfig(self):
		config=self.rc.getConfig()
		self.cnfEnded.emit(config)
	#def _getConfig

	def _getFreedesktopCategories(self):
		cats=[]
		try:
			#cats=json.loads(self.rc.execute('getFreedesktopCategories'))[0]
			cats=self.rc.getFreedesktopCategories()
		except Exception as e:
			print("Th for categories failed: {}".format(e))
		self.catEnded.emit(cats)
	#def _getFreedesktopCategories

	def _getLuck(self):
		apps=json.loads(self.rc.getApps())
		luckApps=[]
		idx=0
		while len(luckApps)<10:
			app=apps[random.randint(0,len(apps)-1)]
			if app.get("forbidden",False)==True or app.get("unavailable",False)==True or app.get("hidden",False)==True:
				continue
			if app.get("origin","")=="verified" and len(app.get("screenshots",[]))>0:
				luckApps.append(app)
			idx+=1
			if idx>100:
				break
		self.lucEnded.emit(luckApps)
		return(luckApps)
	#def _getLuck

	def getLuck(self):
		return(self._getLuck())
	#def getLuck

	def _installed(self):
		apps=[]
		apps=self.rc.getAppsInstalled()
		self.linEnded.emit(apps)
	#def _installed

	def _list(self):
		apps=[]
		apps=self.rc.getAppsInCategory(self.args[0])
		self.lstEnded.emit(apps)
	#def _list

	def _lock(self):
		config=self.rc.toggleLock()
		self.lckEnded.emit()
	#def _lock

	def _matchApps(self,*args):
		apps=[]
		if len(self.args[0])>0:
			for app in self.args[0]:
				apps.append(self.rc.showApp(app))
		self.mtcEnded.emit(apps)
		return(app)
	#def _matchApps

	def _refreshApp(self,*args):
		app={}
		if self.args[0]!="":
			app=self.rc.refreshApp(self.args[0])
		self.rfrEnded.emit(app)
		return(app)
	#def _refreshApp

	def _restart(self):
		self.rc.restart()
		time.sleep(4)
		try:
			self.rc.getAppsInstalledPerCategory()
		except:
			pass
		self.rstEnded.emit()
	#def _restart

	def _search(self,*args):
		#apps=json.loads(self.rc.execute("search",self.args[0]))
		if self.args[0]=="":
			apps=self.rc.getApps()
		else:
			apps=self.rc.searchApp(self.args[0])
		self.srcEnded.emit(apps)
	#def _search(self):

	def _searchByUrl(self,*args):
		#apps=json.loads(self.rc.execute("search",self.args[0]))
		app=[]
		if self.args[0]!="":
			urls=self.args[0]
			for url in urls:
				if url!="":
					app=self.rc.searchAppByUrl(url)
					if len(app)>0:
						self.urlEnded.emit(app)
		return()
	#def _searchByUrl()

	def _setAppState(self,*args):
		if self.args[0]!="":
			temp=True
			if isinstance(self.args[-1],bool):
				temp=self.args[-1]
			if len(self.args)>3:
				app=self.rc.setAppState(self.args[0],self.args[1],self.args[2],temp)
			else:
				app=self.rc.setAppState(self.args[0],self.args[1],temp)
	#def _setAppState

	def _show(self,*args):
		#apps=json.loads(self.rc.execute("search",self.args[0]))
		app={}
		if self.args[0]!="":
			app=self.rc.refreshApp(self.args[0])
		self.shwEnded.emit(app)
	#def _show

	def _unlock(self):
		apps=[]
		self._lock()
	#def _unlock

	def _updatePkgData(self):
		if len(self.args)>0:
			self.rc.updatePkgData(self.args[0].get("name"),self.args[0])
	#def _updatePkgData
#class rebostHelper
