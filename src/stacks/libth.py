#!/usr/bin/python3

from PySide2.QtCore import Signal,QThread
import json,time,subprocess

class storeHelper(QThread):
	chkEnded=Signal("PyObject")
	test=Signal("PyObject")
	lstEnded=Signal("PyObject")
	srcEnded=Signal("PyObject")
	lckEnded=Signal()
	rstEnded=Signal()
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
	
	def run(self):
		if self.action=="upgrade":
			self._chkUpgrades()
		elif self.action=="test":
			self._test()
		elif self.action=="list":
			self._list()
		elif self.action=="search":
			self._search()
		elif self.action=="updatePkgData":
			self._updatePkgData()
		elif self.action=="unlock":
			self._unlock()
		elif self.action=="lock":
			self._lock()
		elif self.action=="restart":
			self._restart()
	#def run

	def _chkUpgrades(self):
		upgrades=False
		apps=json.loads(self.rc.getUpgradableApps())
		if len(apps)>0:
			upgrades=True
		else:
			if lliurexup!=None:
				llxup=lliurexup.LliurexUpCore()
				if len(llxup.getPackagesToUpdate())>0:
					upgrades=True
		self.chkEnded.emit(upgrades)
	#def _chkUpgrades(self):

	def _test(self):
		if self.rc!=None:
			self.rc.execute("list","lliurex")
			self.test.emit(True)
		else:
			self.test.emit(False)
	#def _test

	def _list(self):
		apps=[]
		if len(self.args)==1:
			apps.extend(json.loads(self.rc.execute('list',"({})".format(self.args[0]))))
		elif len(self.args)==2:
			apps.extend(json.loads(self.rc.execute('list',"{}".format(self.args[0]),self.args[1])))
		self.lstEnded.emit(apps)
	#def _list

	def _search(self):
		apps=json.loads(self.rc.execute("search",self.args[0]))
		self.srcEnded.emit(apps)
	#def _search(self):

	def _updatePkgData(self):
		if len(self.args)>0:
			self.rc.updatePkgData(self.args[0].get("pkgname"),self.args[0])
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

	def isLocked(self):
		lock=True
		userLock=True
		try:
			cmd=subprocess.run(["pkexec","/usr/share/rebost/helper/test-rebost.py"])
			if cmd.returncode==0:
				userLock=False
		except:
			userLock=True
		lock=self.rc.getLockStatus()
		return(lock,userLock)
#class rebostHelper

class updateAppData(QThread):
	dataLoaded=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.apps=kwargs.get("apps",{})
		self.rc=kwargs["rc"]
		self.dbg=True
		self.newApps={}
		self.updates=[]
		self._stop=False
		self.cont=0
		self.ctl=0
	#def __init__
		self.destroyed.connect(updateAppData._onDestroy)
	#def __init__

	def _onDestroy(*args):
		pass

	def _debug(self,msg):
		if self.dbg==True:
			print("updateApp: {}".format(msg))

	def setApps(self,*args):
		self.newApps=args[0]
	#def setApps

	def run(self):
		app={}
		self._stop=False
		if len(self.newApps)>0:
			self.apps=self.newApps.copy()
			self.newApps={}
		self._debug("Launching info thread for {} apps".format(len(self.apps)))
		apps = dict(reversed(list(self.apps.items())))
		while apps:
			self.ctl+=1
			if len(self.newApps)>0:
				apps = dict(reversed(list(self.newApps.items())))
				self.apps=self.newApps.copy()
				self.newApps={}
				#self._stop==False
			if self._stop==True:
				break
			while self.cont>2:
				if self._stop==True:
					break
				time.sleep(0.4)
			name=apps.popitem()[0]
			self._emitDataLoaded(name)
			self.cont+=1
			time.sleep(0.2)
			if int(self.ctl)%5==0:
				self.rc.commitData()
				self.ctl=0
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
		applist=[]
		for strapp in self.apps:
			if self._stop==True:
				break
			jsonapp=json.loads(strapp)
			applist.append(jsonapp)
		if self._stop==False:
			self.dataLoaded.emit(applist)
	#def run

	def stop(self,st=True):
		self._stop=st
	#def stop
#class getData
