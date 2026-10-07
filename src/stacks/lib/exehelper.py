#!/usr/bin/python3
import subprocess,json
from PySide2.QtCore import Signal,QThread
import lib.libhelper as libhelper

class zmdLauncher(QThread):
	zmdEnded=Signal("PyObject","PyObject")
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
		self.zmdEnded.emit(self.app,ret)
	#def run
#class zmdLauncher

class appLauncher(QThread):
	runEnded=Signal("PyObject","PyObject")
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.cmd=""
		self.app={}
		self.url=""
		self.args=''
	#def __init__

	def setArgs(self,cmd,**kwargs):
		self.cmd=cmd
		self.app=kwargs.get("app","{}")
		if isinstance(self.app,str):
			self.app=json.loads(self.app)
		bundle=kwargs.get("bundle","")
		if bundle in self.app["bundle"].keys()==False:
			bundle="unknown"
		print("BUNDLE: {}".format(bundle))
		if len(bundle)>0:
			self.app["bundle"]={bundle:self.app["bundle"][bundle]}
		self.args=kwargs.get("args",[])
	#def setArgs

	def setUrl(self,app):
		self.app=app
		self.url=app["bundle"]["webapp"]
	#def setUrl

	def run(self):
		if len(self.cmd)>0:
			print("RUNNING")
			cmd=["pkexec",self.cmd,json.dumps(self.app)]
			cmd.extend(self.args)
			try:
				proc=subprocess.run(cmd,stderr=subprocess.PIPE,universal_newlines=True)
			except Exception as e:
				print("** ERROR executing thread **")
				print(e)
				print("** **")
		self.runEnded.emit(self.app,None)
	#def run
#class appLauncher

