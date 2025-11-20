#!/usr/bin/python3
import os
import subprocess
from urllib.request import Request
from urllib.request import urlretrieve
from urllib import request
from bs4 import BeautifulSoup as bs
from constants import *

CACHE=os.path.join(CACHE,"html")

class helper():
	def __init__(self):
		self.dbg=False
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("DBG: {}".format(msg))
	#def _debug

	def _getCmdFromZmd(self,zmdPath):
		#Look if pkexec is needed
		appPath=zmdPath.replace(".zmd",".app")
		appPath=appPath.replace("zmds/","applications/")
		if appPath.endswith(".app")==False:
			appPath="{}.app".format(appPath)
		cmd=[zmdPath]
		if os.path.isfile(appPath):
			with open (appPath,'r') as f:
				flines=f.readlines()
			for l in flines:
				if "pkexec" in l:
					cmd.insert(0,"pkexec")
					break
		return(cmd)
	#def _getCmdFromZmd

	def runZmd(self,app):
		ret=-1
		cmd=[]
		zmdCmd=app.get('bundle',{}).get('unknown','')
		appName=app.get("pkgname","")
		if appName=="":
			appName=zmdCmd
		#Patch for zero-lliurex-adobereader
		if zmdCmd=="acroread.epi":
			zmdCmd="zero-lliurex-adobereader.zmd"
		if zmdCmd.endswith(".zmd")==zmdCmd.endswith(".epi")==False:
			zmdCmd+=".zmd"
		zmdCmd=zmdCmd.replace(".epi",".zmd")
		zmdPath=os.path.join("/usr/share/zero-center/zmds",zmdCmd)
		if os.path.exists(zmdPath)==False:
			alternatives=["zero-lliurex-{}".format(zmdCmd),"zero-installer-{}".format(zmdCmd),"zero-fp-{}".format(zmdCmd)]
			for f in os.scandir(os.path.dirname(zmdPath)):
				if f.name in alternatives:
					zmdPath=f.path
					break
		if os.path.exists(zmdPath):
			cmd=self._getCmdFromZmd(zmdPath)
			#subprocess.run(["pkexec",zmdPath])
			try:
				cmd.append(appName)
				proc=subprocess.run(cmd)
				ret=proc.returncode
			except Exception as e:
				print(e)
				ret=-1
			if ret>0:
				#Zmd could depend on a zmd-installer so let's search
				zmdFolder=os.path.dirname(zmdPath)
				searchZmd=".".join(zmdPath.split(".")[:-1])
				newPath=zmdPath
				for f in os.scandir(zmdFolder):
					if searchZmd in f.path and f.path!=zmdPath:
						newPath=f.path
						break
				if zmdPath!=newPath:
					cmd=self._getCmdFromZmd(newPath)
					#subprocess.run(["pkexec",zmdPath])
		return(ret)
	#def runZmd

	def getLauncherForBundle(self,app,bundle):
		launchers={"flatpak":["flatpak","run"],"snap":["snap","run"]}
		cmd=[]
		if bundle in launchers.keys():
			cmd=launchers[bundle]
			cmd.append(app["bundle"].get(bundle,""))
		return(cmd)
	#def getLauncherForBundle

	def getDesktopForCommand(self,command):
		cmd=[]
		dPaths=["/usr/share/applications",os.path.join(os.environ["HOME"],".local/share/applications")]
		dFile=""
		for path in dPaths:
			if os.path.isdir(path):
				for f in os.scandir(path):
					if "{}.desktop".format(command.lower()) in f.name.lower():
						if f.name.endswith(".desktop"):
							dFile=f.name
							break
			if dFile!="":
				break
		if dFile=="":
			#Deeper search
			for path in dPaths:
				if os.path.isdir(path):
					for f in os.scandir(path):
						if f.is_file()==False:
							continue
						if f.name.endswith(".desktop"):
							with open(f.path,"r") as fcontent:
								if command in "\n".join(fcontent.readlines()):
									dFile=f.name
									break
				if dFile!="":
					break
		if dFile!="":
			cmd=["gtk-launch",dFile]
		return(cmd)
	#def getDesktopForLauncher

	def getCmdForLauncher(self,app,bundle="",launcher=""):
		cmd=[]
		appname=""
		if len(launcher)>0:
			if os.path.exists(launcher)==True:
				cmd=["gtk-launch",os.path.basename(launcher)]
		if len(cmd)<=0:
			if bundle!="":
				appname=app["bundle"].get(bundle,"")
				if len(appname)>0:
					cmd=self.getLauncherForBundle(app,bundle)
		if len(cmd)<=0:
			if appname=="":
				appname=app["pkgname"]
			cmd=self.getDesktopForCommand(appname)
			if len(cmd)==0:
				for char in (".","-","_"):
					name=appname.split("char")[-1]
					cmd=self.getDesktopForCommand(name)
					if len(cmd)>0:
						break
		return(cmd)
	#def getCmdForLauncher

	def runApp(self,app,bundle,launcher=""): #TODO: QTHREAD
		cmd=self.getCmdForLauncher(app,bundle,launcher)
		proc=subprocess.run(cmd)
		if proc.returncode!=0:
			cmd=["gtk-launch",app.get("name",'')]
			proc=subprocess.run(cmd)
		return(proc)
	#def runApp(self,app,bundle)

	def getBundlesByPriority(self,app):
		priority=["epi","package","flatpak","snap","appimage","eduapp"]
		priorityIdx={}
		priorityTmp={}
		bundles=app.get('bundle',{})
		#If there's an epi remove the package
		if "unknown" in bundles and "package" in bundles:
			bundles.pop("package")

		for bundle in bundles:
			version=app.get('versions',{}).get(bundle,'lliurex')
			if bundle=="unknown":
				bundle="epi"
			if bundle in priority:
				fversion=version.split("+")[0][0:10]
				idx=priority.index(bundle)
				if bundle=="epi":
					bundle="unknown"
				release="{} {}".format(bundle,fversion)
				priorityTmp[idx]=release
		if len(priorityTmp)>0:
			sortedKeys=list(priorityTmp.keys())
			sortedKeys.sort()
			for i in sortedKeys:
				priorityIdx[i]=priorityTmp[i]
		return(priorityIdx)
	#def getBundlesByPriority

	def getAppseduDetails(self,url):
		details={"icon":"","description":"","summary":""}
		page=os.path.basename(url.removesuffix("/"))
		content=""
		if os.path.exists(os.path.join(CACHE,page)):
			with open(os.path.join(CACHE,page),"r") as f:
				content=f.read()
		else:
			req=Request(url, headers={'User-Agent':'Mozilla/5.0'})
			try:
				with request.urlopen(req,timeout=2) as f:
					content=f.read().decode('utf-8')
				if os.path.exists(os.path.join(CACHE))==False:
					os.makedirs(os.path.join(CACHE))
				with open(os.path.join(CACHE,page),"w") as f:
					f.write(content)
			except Exception as e:
				self._debug("Couldn't fetch {}".format(url))
				self._debug(e)
		if len(content)>0:
			bscontent=bs(content,"html.parser")
			appDesc=bscontent.find("div",["acf-view__descripcio-field"])
			if appDesc!=None:
				details["description"]=appDesc.text
			appIcon=bscontent.find("img",class_="acf-view__image")
			if appIcon!=None:
				details["icon"]=appIcon.get("src","")
		return(details)
	#def getAppseduDetails
		
