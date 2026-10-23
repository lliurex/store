#!/usr/bin/python3
import os,grp
import dbus
import subprocess,time,json
from PySide2.QtWidgets import QMainWindow,QLabel
from PySide2.QtCore import Qt,Signal,QThread,QObject
from PySide2.QtGui import QIcon
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
			if self.app.get("webapp",False)==True:
				url=self.app["bundle"].get("webapp",self.app["infopage"])
				cmd=["xdg-open",url]
			else:
				bus=dbus.SystemBus()
				try:
					objbus=bus.get_object("net.lliurex.rebost","/net/lliurex/rebost")
					proxbus=dbus.Interface(objbus,"net.lliurex.rebost")
					config=proxbus.getConfig()
				except:
					print("D-Bus error. Rebost is not accesible")
					return
				else:
					installer=config.get("externalInstaller")
					cmd=["pkexec",installer,json.dumps(self.app),self.bundle]
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
		F
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
				with urlopen(req,timeout=2) as f:
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
			urlEditor=bscontent.find("a",["acf-view__url_editor-link acf-view__link"],href=True)
			if urlEditor!=None:
				details["url"]=urlEditor.get("href","")
			else:
				details["url"]=""
		return(details)
	#def getAppseduDetails

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

	def chkNetwork(self):
		state=False
		bus=dbus.SystemBus()
		try:
			objbus=bus.get_object("org.freedesktop.NetworkManager","/org/freedesktop/NetworkManager")
			proxbus=dbus.Interface(objbus,"org.freedesktop.NetworkManager")
			status=proxbus.state()
		except Exception as e:
			self._debug("Chk network: {}".format(e))
			state=True
		else:
			if status==70:
				state=True
		return(state)
	#def chkNetwork

	def _chkUserGroup(self):
		lockedUser=False
		grpData=grp.getgrnam("sudo")
		if grpData.gr_gid not in os.getgroups():
			userlocked=True
		return(lockedUser)
	#def _chkUserGroup(self):

	def getLockStatus(self,*args):
		jconfig=args[0]
		locked=jconfig.get("onlyVerified",False)
		lockedUser=self._chkUserGroup()
		if not isinstance(locked,bool):
			if int(locked)==0:
				locked=False
			else:
				locked=True
		return(locked,lockedUser)
	#def getLockStatus

	def getAppFromString(self,app):
		if isinstance(app,str):
			try:
				app=json.loads(app)
			except Exception as e:
				print(e)
			if isinstance(app,list):
				if len(app)>0:
					app=app[0]
					if isinstance(app,str):
						try:
							app=json.loads(app)
						except Exception as e:
							pass
				else:
					app={"ERR":True}
		return(app)
	#def getAppFromString
	
	def tokenizeTags(self,tags,exclude=[],extra=""):
		tokenized=""
		style="padding:1px;border-radius:3px;text-decoration:none;"
		exclude=[item.lower() for item in exclude]
		for keyword in tags:
			keyword=keyword.replace("#","")
			if len(keyword)==0 or keyword=="zomandos" or keyword.lower() in exclude:
				continue
			elif keyword.lower() in ["open","source","system","the","with","some","any","installer","zero"]:
				continue
			elif keyword.lower().endswith(".epi"):
				continue
			if keyword not in tokenized and len(keyword)>1:
				#Disabled as requisite  (250214-11:52)
				tokenized+="<a href=\"#{0}\" style=\"{1}\">#{0}</a> ".format(keyword,style)
		if tokenized.count(" ")<4:
			cont=0
			for word in extra.split(" "):
				if len(word)<3:
					continue
				elif word.lower() in ["open","source","system","the","with","some","any","installer","zero"]:
					continue
				b="".join([ w for w in word if w.isalpha() ])
				tokenized+="<a href=\"#{0}\" style=\"{1}\">#{0}</a> ".format(b,style)
				cont+=1
				if cont==4:
					break
		return("{}".format(tokenized.strip(" / ")))
	#def tokenizeTags

	def getAppFromStream(self,stream):
		name=""
		if isinstance(stream,str):
			cmd=stream.split("://")[-1]
			if cmd.startswith("install?"):
				ocs=cmd.split("&")[-1]
				idx=1
				for i in ocs.split("=")[-1]:
					if i.isalnum():
						idx+=1
					else:
						break
				name=ocs.split("=")[-1][:idx-1]
			else:
				name=cmd.replace(".desktop","").replace(".flatpakref","")
				if name.count(".")>1:
					if len(name.split(".")[0])==3:
						name=name.split(".")[-1]
		return(name)
	#def getAppFromStream
>>>>>>> master
