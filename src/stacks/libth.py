#!/usr/bin/python3
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
	lstEnded=Signal("PyObject")
	gacEnded=Signal("PyObject")
	srcEnded=Signal("PyObject")
	shwEnded=Signal("PyObject")
	urlEnded=Signal("PyObject")
	lckEnded=Signal()
	rstEnded=Signal()
	staEnded=Signal(bool,bool)
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
	
	def run(self):
		if  self.action=="test":
			self._test()
		elif self.action=="list":
			self._list()
		elif self.action=="search":
			self._search()
		elif self.action=="urlSearch":
			self._searchByUrl()
		elif self.action=="show":
			self._show()
		elif self.action=="updatePkgData":
			self._updatePkgData()
		elif self.action=="unlock":
			self._unlock()
		elif self.action=="lock":
			self._lock()
		elif self.action=="restart":
			self._restart()
		elif self.action=="status":
			self._getLockStatus()
		elif self.action=="getCategories":
			self._getFreedesktopCategories()
		elif self.action=="getAppsPerCategory":
			self._getAppsPerCategory()
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

	def _getAppsPerCategory(self):
		apps=[]
		apps=self.rc.getAppsPerCategory()
		self.gacEnded.emit(apps)
	#def _getAppsPerCategory

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
			url=self.args[0]
			print("URL Search: {}".format(url))
			if url!="":
				app=self.rc.searchAppByUrl(url)
			print("Res: {}".format(app))
		self.urlEnded.emit(app)
	#def _show(self):

	def _show(self,*args):
		#apps=json.loads(self.rc.execute("search",self.args[0]))
		app={}
		if self.args[0]!="":
			apps=self.rc.showApp(self.args[0])
		self.shwEnded.emit(app)
	#def _show

	def _updatePkgData(self):
		if len(self.args)>0:
			self.rc.updatePkgData(self.args[0].get("name"),self.args[0])
	#def _updatePkgData

	def _lock(self):
		apps=[]
		cmd=subprocess.run(["pkexec","/usr/share/rebost/helper/unlock-rebost.py","lock"])
		if cmd.returncode==0:
			self.rc.update(True)
		self.lckEnded.emit()
	#def _lock

	def _unlock(self):
		apps=[]
		cmd=subprocess.run(["pkexec","/usr/share/rebost/helper/unlock-rebost.py"])
		if cmd.returncode==0:
			self.rc.update(True)
		self.lckEnded.emit()
	#def _unlock

	def _restart(self):
		self.rc.update(True)
		self.rstEnded.emit()
	#def _unlock

	def _getLockStatus(self):
		lock=True
		userLock=True
		try:
			cmd=subprocess.run(["pkexec","/usr/share/rebost/helper/test-rebost.py"])
			if cmd.returncode==0:
				userLock=False
		except:
			userLock=True
		lock=self.rc.getLockStatus()
		self.staEnded.emit(lock,userLock)
	#def _getLockStatus

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
					app=json.loads(self.rc.showApp(args[0]))
				except:
					try:
						app=json.loads(self.rc.showApp(args[0]))
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
				app=json.loads(self.rc.showApp(self.app.get('id','')))[0]
			except:
				print("Error finding {}".format(self.app.get("id","")))
				app=self.app.copy()
				app["ERR"]=True
			finally:
				if isinstance(app,str):
					app=json.loads(app)
				self.showEnded.emit(app)
	#def run
#class thShowApp
