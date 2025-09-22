#!/usr/bin/python3
import os
import subprocess

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
		zmdCmd=app.get('bundle',{}).get('unknown','').replace(".epi","")+".zmd"
		appName=app.get("pkgname","")
		if appName=="":
			appName=zmdCmd
		if zmdCmd.endswith(".zmd")==True:
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
		elif zmdCmd.endswith(".epi"):
			cmd=["pkexec","epi-gtk",zmdCmd,appName]
			if len(cmd)>0:
				try:
					proc=subprocess.run(cmd,env=os.environ)
				except Exception as e:
					print(e)
					ret=-1

				if ret>=0:
					ret=proc.returncode
			else:
				self._zmdNotFound(zmdPath)
		return(ret)
	#def runZmd

	def _zmdNotFound(self,zmd):
	#	def _launchZeroCenter():
	#		dlg.close()
		cmd=["zero-center"]
		try:
			subprocess.run(cmd)
		except Exception as e:
			print(e)

	#	dlg=QDialog()
	#	dlg.setWindowTitle("Error")
	#	btns=QDialogButtonBox.Open|QDialogButtonBox.Cancel
	#	dlgBtn=QDialogButtonBox(btns)
	#	dlgBtn.accepted.connect(_launchZeroCenter)
	#	dlgBtn.rejected.connect(dlg.close)
	#	lay=QGridLayout()
	#	lbl=QLabel("{0}".format(i18n.get("ZMDNOTFOUND")))
	#	lay.addWidget(lbl)
	#	lay.addWidget(dlgBtn)
	#	dlg.setLayout(lay)
	#	dlg.exec()
	#def _zmdNotFound(self,zmd):

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
		priority=["zomando","package","flatpak","snap","appimage","eduapp"]
		priorityIdx={}
		bundles=app.get('bundle',{})
		for bundle in bundles:
			version=app.get('versions',{}).get(bundle,'lliurex')
			if bundle=="unknown":
				bundle="zomando"
			if bundle in priority:
				fversion=version.split("+")[0][0:10]
				idx=priority.index(bundle)
				if bundle=="zomando":
					bundle="unknown"
				release="{} {}".format(bundle,fversion)
				priorityIdx[idx]=release
		return(priorityIdx)
	#def getBundlesByPriority

