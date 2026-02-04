#!/usr/bin/python3
import subprocess,json
from PySide2.QtCore import Signal,QThread
import libhelper

class zmdLauncher(QThread):
	zmdEnded=Signal("PyObject")
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.helper=libhelper.helper()
		self.app=None
	#def __init__

	def setApp(self,app):
		self.app=app
	#def setApp

	def run(self):
		ret=None
		if self.app:
			ret=self.helper.runZmd(self.app)
		self.zmdEnded.emit(self.app)
	#def run
#class zmdLauncher

class appLauncher(QThread):
	runEnded=Signal("PyObject","PyObject")
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.app={}
		self.url=""
		self.args=''
	#def __init__

	def setArgs(self,app,args,bundle="",pk=True):
		if isinstance(app,str):
			self.app={}
			self.app["name"]=app
		else:
			self.app=app
		self.args=args
		#if bundle:
		#	oldBundle=self.app.get('bundle')
		#	newBundle={bundle:oldBundle.get(bundle)}
		#	self.app['bundle']=newBundle
	#def setArgs

	def setUrl(self,app):
		self.app=app
		self.url=app["bundle"]["webapp"]
	#def setUrl

	def run(self):
		if (self.app and self.args) or (len(self.url)>0):
			proc=None
			if "attempted" not in self.app.keys():
				self.app["attempted"]=[]
			if " ".join(self.args[1:]) not in self.app["attempted"]:
				self.app["attempted"].append(" ".join(self.args[1:]))
			try:
				if self.url=="":
					cmd=self.args.copy()
					cmd.append(json.dumps(self.app))
					cmd.insert(0,"pkexec")
				else:
					cmd=["xdg-open",self.url]
					self.url=""
				proc=subprocess.run(cmd,stderr=subprocess.PIPE,universal_newlines=True)
			except Exception as e:
				print(e)
		self.runEnded.emit(self.app,proc)
	#def run
#class appLauncher

