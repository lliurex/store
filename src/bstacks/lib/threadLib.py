#!/usr/bin/python3
import os,subprocess
import json
from PySide6.QtCore import Qt,Signal,QThread

class rebostQuery(QThread):
	queryCompleted=Signal("PyObject")
	def __init__(self,*args,parent=None,**kwargs):
		QThread.__init__(self, parent)
		self.rebost=kwargs.get("rebost")
		self.appId=""
		self.app={}
	#def __init__

	def setQuery(self,query,data=None):
		self.query=query
		if data!=None:
			self.appId=""
			self.app={}
			if isinstance(data,str):
				self.appId=data
			if isinstance(data,dict):
				self.app=data
	#def setQuery
	
	def run(self):
		if self.query=="refresh":
			resultSet=json.loads(self.rebost.refreshVerifiedApp(self.appId))[0]
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
