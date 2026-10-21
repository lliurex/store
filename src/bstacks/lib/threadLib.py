#!/usr/bin/python3
import os,subprocess
import json
from PySide6.QtCore import Qt,Signal,QThread

class rebostQuery(QThread):
	queryCompleted=Signal("PyObject")
	exception=Signal(str)
	def __init__(self,*args,parent=None,**kwargs):
		QThread.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.query=None
		self.queryData=None
	#def __init__

	def setQuery(self,query,data=None):
		self.query=query
		if data!=None:
			self.queryData=data
	#def setQuery
	
	def run(self):
		resultSet={}
		try:
			if self.query=="refresh":
				resultSet=json.loads(self.rebost.refreshVerifiedApp(self.queryData))[0]
			elif self.query=="show":
				resultSet=json.loads(self.rebost.showApp(self.queryData))[0]
			elif self.query=="search":
				resultSet=json.loads(self.rebost.searchApp(self.queryData))
			elif self.query.lower()=="loadcategory":
				apps=json.loads(self.rebost.getAppsInCategory(self.queryData))
				apps=apps[self.queryData]
				resultSet=sorted(apps, key=lambda x: x["name"].lower())
			elif self.query.lower()=="getfreedesktopcategories":
				resultSet=self.rebost.getFreedesktopCategories()
			elif self.query.lower()=="showapps":
				resultSet={}
				for appId in self.queryData:
					app=json.loads(self.rebost.showApp(appId))
					resultSet.update({len(resultSet):app})
		except Exception as e:
			self.exception.emit(e)
			return(False)
		self.queryCompleted.emit(resultSet)
	#def run
#class rebostQuery

class runner(QThread):
	def __init__(self,*args,parent=None,**kwargs):
		QThread.__init__(self, parent)
		self.action=""
		self.data=""
	#def __init__
	
	def setAction(self,action,data=None):
		self.action=action
		self.data=data
	#def setAction

	def run(self):
		subprocess.run([self.action,self.data])
	#def run
#class runner
