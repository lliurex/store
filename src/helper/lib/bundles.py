#!/usr/bin/python3
import os,sys
import tempfile
import json
from enum import Enum
import lib.template
from lib.templatePkg import templatePkg
from lib.templateFlt import templateFlt
from lib.templateSnp import templateSnp
from lib.templateApi import templateApi


class kind(Enum):
	EPIC=0
	PACKAGE=1
	FLATPAK=2
	SNAP=3
	APPIMAGE=4
	ZOMANDO=5
#class kind

class bundle():
	def __init__(self,app=None,parent=None):
		self.kind=None
		self.app=app
	#def __init__

	def _appFromString(self,app):
		if isinstance(app,str):
			try:
				app=json.loads(app)
			except:
				app={}
		return(app)
	#def _appFromString

	def setApp(self,app):
		app=self._appFromString(app)
		if isinstance(app,list):
			app=self._appFromString(app[0])
		if isinstance(app,dict):
			self.app=app
	#def setApp

	def getApp(self):
		return(self.app)
	#def getApp

	def setKind(self,bundleKind):
		self.kind=kind(bundleKind)
	#def setKind

	def getKind(self):
		return(self.kind)
	#def getKind

	def generateEpi(self):
		epi=template.epi
		script=None
		if self.kind!=None:
			episcript=None
			if self.kind==kind.PACKAGE:
				episcript=templatePkg()
			elif self.kind==kind.FLATPAK:
				episcript=templateFlt()
			elif self.kind==kind.SNAP:
				episcript=templateSnp()
			elif self.kind==kind.APPIMAGE:
				episcript=templateApi()
			script=episcript.script
		return(epi,script)
