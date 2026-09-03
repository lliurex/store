#!/usr/bin/python3
import os
import subprocess,time,json
from PySide6.QtWidgets import QMainWindow,QLabel
from PySide6.QtCore import Qt,Signal,QThread,QObject
from PySide6.QtGui import QIcon
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup as bs
from extras.constants import *
from wdg.splashScreen import QSplashWidget

CACHE=os.path.join(CACHE,"html")

class _epiLauncher(QThread):
	epiLaunched=Signal(str)
	def __init__(self,*args,parent=None):
		QThread.__init__(self, parent)
		icn=QIcon.fromTheme("lliurex-store")
		self.wdg=QSplashWidget(icn)
		self.finished.connect(self._close)
		self.zmdPath=""
		self.appId=""
	#def __init__

	def _close(self,*args):
		self.epiLaunched.emit("zmd")
	#def _close

	def _getZmdPath(self,epiCmd):
		zmdCmd=epiCmd.replace(".epi",".zmd")
		#Patch for zero-lliurex-adobereader
		if epiCmd=="acroread.epi":
			zmdCmd="zero-lliurex-adobereader.zmd"
		zmdPath=os.path.join("/usr/share/zero-center/zmds",zmdCmd)
		if zmdPath.endswith(".zmd")==False:
			zmdPath+=".zmd"
		if os.path.exists(zmdPath)==False:
			alternatives=["zero-lliurex-{}".format(zmdCmd),"zero-installer-{}".format(zmdCmd),"zero-fp-{}".format(zmdCmd)]
			for f in os.scandir(os.path.dirname(zmdPath)):
				if f.name in alternatives:
					zmdPath=f.path
					break
		return(zmdPath)
	#def _getZmdPath

	def setData(self,app,bundle,launcher,pxm):
		self.wdg.load()
		self.app=app
		self.bundle=bundle
		self.launcher=launcher
		self.appId=self.app["id"]
		if pxm!="":
			self.wdg.setIcon(pxm)
		epiCmd=self.app.get('bundle',{}).get('unknown','')
		if len(epiCmd)>0:
			self.zmdPath=self._getZmdPath(epiCmd)
	#def setData

	def _getCmdFromZmd(self):
		#Look if pkexec is needed
		appPath=self.zmdPath.replace(".zmd",".app")
		appPath=appPath.replace("zmds/","applications/")
		if appPath.endswith(".app")==False:
			appPath="{}.app".format(appPath)
		cmd=[self.zmdPath]
		if os.path.isfile(appPath):
			with open (appPath,'r') as f:
				flines=f.readlines()
			for l in flines:
				if "pkexec" in l:
					cmd.insert(0,"pkexec")
					break
		return(cmd)
	#def _getCmdFromZmd

	def run(self,*args):
		if len(self.zmdPath)>0:
			if os.path.exists(self.zmdPath):
				cmd=self._getCmdFromZmd()
				#subprocess.run(["pkexec",zmdPath])
				try:
					cmd.append(self.appId)
					proc=subprocess.run(cmd)
					ret=proc.returncode
				except Exception as e:
					print(e)
					ret=-1
		else:
			helper="/usr/share/store/helper/installer.py"	
			cmd=["pkexec",helper,self.app["bundle"][self.bundle],self.bundle,json.dumps(self.app)]
			proc=subprocess.run(cmd)
#class _epiLauncher

class _launcher(QThread):
	appLaunched=Signal(str)
	def __init__(self,*args,parent=None):
		QThread.__init__(self, parent)
		icn=QIcon.fromTheme("lliurex-store")
		self.wdg=QSplashWidget(icn)
		self.finished.connect(self._close)
	#def __init__

	def _close(self,*args):
		self.appLaunched.emit("")
	#def _close

	def setData(self,app,bundle,launcher,pxm):
		self.wdg.load()
		self.app=app
		self.bundle=bundle
		self.launcher=launcher
		if pxm!="":
			self.wdg.setIcon(pxm)
	#def setData

	def getLauncherForBundle(self):
		launchers={"flatpak":["gtk-launch"],"snap":["snap","run"]}
		cmd=[]
		if self.bundle in launchers.keys():
			cmd=launchers[self.bundle]
			appName=self.app["bundle"].get(self.bundle,"")
			if self.bundle=="flatpak":
				for name in appName.split("/"):
					if name.count(".")>=2:
						appName=name
						break
			cmd.append(appName)
		return(cmd)
	#def getLauncherForBundle

	def _validateDesktop(self,command,fname):
		validate=False
		content=""
		with open(fname,"r") as f:	
			content=f.read()
		if "Exec={}".format(command) in content:
			validate=True
		return(validate)
	#def _validateDesktop

	def getDesktopForCommand(self,command):
		cmd=[]
		dPaths=["/usr/share/applications",os.path.join(os.environ["HOME"],".local/share/applications")]
		dFile=""
		for path in dPaths:
			if os.path.isdir(path):
				for f in os.scandir(path):
					if "{}.desktop".format(command.lower()) in f.name.lower():
						if f.name.endswith(".desktop"):
							if self._validateDesktop(command,f.path)==True:
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
						if f.name.lower().endswith(".desktop"):
							with open(f.path,"r") as fcontent:
								try:
									if command in "\n".join(fcontent.readlines()):
										dFile=f.name
										break
								except:
									continue
				if dFile!="":
					break
		if dFile!="":
			cmd=["gtk-launch",dFile]
		return(cmd)
	#def getDesktopForLauncher

	def getCmdForLauncher(self):
		cmd=[]
		appname=""
		if len(self.launcher)>0:
			if os.path.exists(self.launcher)==True:
				cmd=["gtk-launch",os.path.basename(self.launcher)]
		if len(cmd)<=0:
			if self.bundle!="":
				appname=self.app["bundle"].get(self.bundle,"")
				if len(appname)>0:
					cmd=self.getLauncherForBundle()
		if len(cmd)<=0:
			if appname=="":
				appname=self.app["id"]
			cmd=self.getDesktopForCommand(appname)
			if len(cmd)==0:
				for char in (".","-","_"):
					name=appname.split("char")[-1]
					cmd=self.getDesktopForCommand(name)
					if len(cmd)>0:
						break
		return(cmd)
	#def getCmdForLauncher

	def run(self,*args):
		cmd=self.getCmdForLauncher()
		try:
			proc=subprocess.run(cmd)
		except:
			proc=None
		else:
			if proc.returncode!=0:
				cmd=["gtk-launch",self.app.get("name",'')]
				proc=subprocess.run(cmd)

#class _launcher

class appHelper(QObject):
	procEnded=Signal(dict)
	def __init__(self):
		super().__init__()
		self.dbg=False
		self.launcher=_launcher()
		self.launcher.appLaunched.connect(self._endProc)
		self.epiLauncher=_epiLauncher()
		self.epiLauncher.epiLaunched.connect(self._endProc)
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("DBG: {}".format(msg))
	#def _debug

	def _endProc(self,*args):
		if args[0]=="zmd":
			self.procEnded.emit(self.epiLauncher.app)
		else:
			self.procEnded.emit(self.launcher.app)
		return
	#def _endProc

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

	def runZmd(self,app,bundle,launcher="",pxm=""): #TODO: QTHREAD
		if bundle=="":
			bundle=self.getInstalledBundle(app)
		epiCmd=app.get('bundle',{}).get('unknown','')
		if epiCmd=="" and bundle=="":
			bundles=self.getBundlesByPriority(app)
			for b in bundles.values():
				bundle=b.split(" ")[0]
				break
		self.epiLauncher.setData(app,bundle,launcher,pxm)
		self.epiLauncher.start()
		return
		ret=-1
		cmd=[]
		epiCmd=app.get('bundle',{}).get('unknown','')
		print(epiCmd)
		return
		appName=app.get("pkgname","")
		if appName=="":
			appName=zmdCmd
		if epiCmd.endswith(".epi")==False:
			epiCmd+=".epi"
		zmdCmd=epiCmd.replace(".epi",".zmd")
		#Patch for zero-lliurex-adobereader
		if epiCmd=="acroread.epi":
			zmdCmd="zero-lliurex-adobereader.zmd"
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
			cmd=["epic","showinfo",os.path.basename(epiCmd)]
			try:
				status=subprocess.check_output(cmd,encoding="utf8",universal_newlines=True)
			except:
				cmd=["epic","showinfo",os.path.basename(epiCmd.replace("zero-lliurex-",""))]
				try:
					status=subprocess.check_output(cmd,encoding="utf8",universal_newlines=True)
				except:
					status=""
			installed=False
			for l in status.split("\n"):
				if app["id"] in l:
					if "already installed" in l.lower():
						installed=True
						break
				elif "status: installed" in l.lower():
					installed=True
					break
		else:
			installed=None
		return(installed)
	#def runZmd

	def runApp(self,app,bundle,launcher="",pxm=""): #TODO: QTHREAD
		if bundle=="":
			bundle=self.getInstalledBundle(app)
		self.launcher.setData(app,bundle,launcher,pxm)
		self.launcher.start()
	#def runApp(self,app,bundle)

	def getBundlesByPriority(self,app):
		priority=["epi","package","flatpak","snap","appimage","eduapp","webapp"]
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

	def getInstalledBundle(self,app):
		installBundle=""
		bundles=app.get("bundle",{})
		states=app.get("status",{})
		zmd=False
		if bundles.get("unknown")!=None and bundles.get("package")==None and len(bundles)==1:
			#It's an app coming from a specific installer (zmd with only one app)
			#Fake states
			states.update({"unknown":states.get("package","1")})
		if len(states)>0:
			for bundle,state in states.items():
				if int(state)==0 and bundle in bundles: #zmd are of kind unknown, but installs as packagekind
					installBundle=bundle
					break
				elif "unknown" in bundles and int(state)==0:
					if bundles["unknown"]!=app["id"]: #if == then seems a zmd, fake it
						installBundle=bundle
						if installBundle not in bundles:
							bundles[installBundle]=app["id"]
						break
		if installBundle!="":
			if bundles[installBundle]==bundles.get("unknown","") and len(bundles)>1:
				installBundle=""
		return installBundle
	#def getInstalledBundle

class auxiliary():
	def __init__(self,*args):
		self.dbg=False
	#def __init__

	def getRgbColorFromTxt(self,txt):
		rgb=0
		htxt=hash(txt)
		rgb=abs(htxt)
		b = (rgb >> 16) & 0xFF
		g = (rgb >> 8) & 0xFF
		r = rgb & 0xFF
		gamma=(r+g+b)/3
		if gamma>200: 
			r=min(255,r*0.8)
			g=min(255,g*0.8)
			b=min(255,b*0.8)
		return "#{:02X}{:02X}{:02X}".format(int(r),int(g),int(b))
	#def _getRgbColorFromTxt
