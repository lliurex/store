#!/usr/bin/python3
import os
import libhelper
from PySide6.QtCore import Signal,QThread
import json,time,subprocess,random
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
	lstEnded=Signal("PyObject")
	lsgEnded=Signal("PyObject")
	shwEnded=Signal("PyObject")
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
		elif self.action=="list":
			self._list()
		elif self.action=="installed":
			self._installed()
		elif self.action=="search":
			self._search()
		elif self.action=="urlSearch":
			self._searchByUrl()
		elif self.action=="show":
			self._show()
		elif self.action=="updatePkgData":
			self._updatePkgData()
		elif self.action=="getAppSuggests":
			self._getAppSuggests()
		elif self.action=="unlock":
			self._unlock()
		elif self.action=="lock":
			self._lock()
		elif self.action=="restart":
			self._restart()
		elif self.action=="config":
			self._getConfig()
		elif self.action=="getCategories":
			self._getFreedesktopCategories()
		elif self.action=="getAppsPerCategory":
			self._getAppsPerCategory()
		elif self.action=="getAppsInstalledPerCategory":
			self._getAppsInstalledPerCategory()
		elif self.action=="setAppState":
			self._setAppState()
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

	def _list(self):
		apps=[]
		apps=self.rc.getAppsInCategory(self.args[0])
		self.lstEnded.emit(apps)
	#def _list

	def _installed(self):
		apps=[]
		apps=self.rc.getAppsInstalled()
		self.linEnded.emit(apps)
	#def _installed

	def _getAppsPerCategory(self):
		apps=[]
		apps=self.rc.getAppsPerCategory()
		self.gacEnded.emit(apps)
	#def _getAppsPerCategory

	def _getAppsInstalledPerCategory(self):
		apps=[]
		apps=self.rc.getAppsInstalledPerCategory()
		self.gacEnded.emit(apps)
	#def _getAppsInstalledPerCategory

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

	def _show(self,*args):
		#apps=json.loads(self.rc.execute("search",self.args[0]))
		app={}
		if self.args[0]!="":
			app=self.rc.refreshApp(self.args[0])
		self.shwEnded.emit(app)
	#def _show

	def _getAppSuggests(self,*args):
		apps=[]
		if self.args[0]!="":
			limit=10
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
	
	def _setAppState(self,*args):
		if self.args[0]!="":
			temp=True
			if len(self.args)>2:
				temp=self.args[2]
			app=self.rc.setAppState(self.args[0],self.args[1],temp)
	#def _setAppState

	def _updatePkgData(self):
		if len(self.args)>0:
			self.rc.updatePkgData(self.args[0].get("name"),self.args[0])
	#def _updatePkgData

	def _lock(self):
		config=self.rc.toggleLock()
		self.lckEnded.emit()
	#def _lock

	def _unlock(self):
		apps=[]
		self._lock()
	#def _unlock

	def _restart(self):
		self.rc.restart()
		self.rstEnded.emit()
	#def _restart

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
#class rebostHelper

#This class loads data from arguments and updates the db
class updateAppData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.apps=kwargs.get("apps",{})
		self.rc=kwargs["rc"]
		self.dbg=False
		self.newApps={}
		self.updates=[]
		self._stop=False
		self._pause=False
		self.cont=0
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("updateApp: {}".format(msg))

	def setApps(self,*args):
		self.newApps=args[0]
	#def setApps

	def addApps(self,*args):
		self._pause=True
		apps=list(args[0].items())
		time.sleep(0.2)
		random.shuffle(apps)
		self.apps.update(dict(apps))
		self._pause=False
	#def addApp(self,*args)

	def run(self):
		app={}
		self._stop=False
		if len(self.newApps)>0:
			self.apps=self.newApps.copy()
			self.newApps={}
		self._debug("Launching info thread for {} apps".format(len(self.apps)))
		#apps = dict(reversed(list(self.apps.items())))
		while self.apps:
			if self._pause==True:
				while self._pause==True:
					time.sleep(0.2)
			if len(self.newApps)>0:
				#apps = dict(reversed(list(self.newApps.items())))
				self.apps=self.newApps.copy()
				self.newApps={}
				#self._stop==False
			if self._stop==True:
				break
			while self.cont>4:
				if self._stop==True:
					break
				time.sleep(0.3)
			key=list(self.apps.keys())[0]
			data=(key,self.apps.pop(key))
			name=data[0]
			app=data[1].app #btnRebost app 
			self.cont+=1
			if isinstance(app,dict):
				self._debug("Update for {}".format(app["name"]))
				self.rc.updatePkgData(app["name"],app)
			time.sleep(0.1)
		#	self._emitDataLoaded(name)
	#def run

	def stop(self):
		self._stop=True
		self.apps={}
		self.newApps={}
		self.cont=0
	#def stop

	def _emitDataLoaded(self,*args):
		app={}
		if self._stop==False:
			if len(args)>0 and isinstance(args[0],str):
				try:
					app=json.loads(self.rc.refreshApp(args[0]))
				except:
					try:
						app=json.loads(self.rc.refreshApp(args[0]))
					except:
						app={}
				finally:
					self.dataLoaded.emit(app)
		self.cont-=1
	#def _emitDataLoaded
#class updateAppData

class getData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self._stop=False
	#def __init__
		self.destroyed.connect(getData._onDestroy)
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		pass

	def setApps(self,apps):
		self.apps=apps
		self._stop=False
	#def setApps
	
	def run(self):
		if self._stop==False:
			self.dataLoaded.emit(self.apps)
	#def run

	def stop(self,st=True):
		self._stop=st
	#def stop
#class getData

class thShowApp(QThread):
	showEnded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.rc=kwargs["rc"]
		self.app={}
		self.mapFile="/usr/share/rebost/lists.d/eduapps.map"
		self.helper=libhelper.helper()
	#def __init__

	def setArgs(self,*args):
		if isinstance(args[0],str):
			self.app={}
			self.app["name"]=args[0]
		else:
			self.app=args[0]
	#def setArgs(self:

	def run(self):
		if len(self.app.keys())>0:
			try:
				app=self.app.copy()
				apps=json.loads(self.rc.refreshApp(self.app.get('id','')))
			except Exception as e:
				print("Error finding {}".format(self.app.get("id","")))
				print(e)
				app=self.app.copy()
				app["ERR"]=True
			finally:
				if len(app)<=2:
					if os.path.exists(self.mapFile):
						fcontent={}
						with open(self.mapFile,"r") as f:
							fcontent=f.read()
						jcontent=json.loads(fcontent)
						vname=jcontent.get(name,"")
						self._debug("Find virtual pkg {0} for  {1}".format(vname,name))
						if len(vname)>0:
							name=vname
					apps=json.loads(self.rc.refreshApp(self.app.get('id','')))
				if len(apps)>0:
					app=apps[0]
			if isinstance(app,str):
				app=json.loads(app)
			homepage=app.get('homepage','')
			if isinstance(homepage,str)==False:
				homepage=""
			if homepage.startswith("https://portal.edu.gva.es/appsedu")==True and app["description"].count(" ")<3:
				content=self.helper.getAppseduDetails(homepage)
				if len(content)>len(app["description"]):
					app["description"]=content
			self.showEnded.emit(app)
	#def run
#class thShowApp
