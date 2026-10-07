#!/usr/bin/env python3
import sys,os
import json,tempfile
import subprocess
import bundles

DEBUG_F="/tmp/storeInstaller.log"
DEBUG=True

def _debug(*args):
	if DEBUG==True:
		print("storeInstaller: {}".format(args))
	#with open(DEBUG_F,'a') as f:
	#	f.write(args)
#def debug

def _replaceEpiTemplate(epi,appname,appid,script,descname,iconpath):
	epi=epi.replace("{@APPNAME}",appname)
	epi=epi.replace("{@APPID}",appid)
	epi=epi.replace("{@DESCNAME}",descname)
	#epi=epi.replace("{@SCRIPT}",script)
	icon=os.path.basename(iconpath)
	iconpath=os.path.dirname(iconpath)
	epi=epi.replace("{@ICONPATH}",iconpath)
	epi=epi.replace("{@ICON}",icon)
	return(epi)
#def _replaceEpiTemplate

def _replaceScriptTemplate(script,appname,appid,description):
	script=script.replace("{@APPNAME}",appname)
	script=script.replace("{@APPID}",appid)
	script=script.replace("{@DESCRIPTION}",description)
	return(script)
#def _replaceEpiTemplate

def _wroteEpiDisk(epi,script,appId):
	epiF=None
	scriptF=None
	if script!=None:
		wrkdir=tempfile.mkdtemp()
		epiF=os.path.join(wrkdir,"{}.epi".format(appId))
		scriptF=os.path.join(wrkdir,"{}_script".format(appId))
		with open(epiF,"w") as f:
			epi=epi.replace("{@SCRIPT}",scriptF)
			f.write(epi)
		try:
			with open(scriptF,"w") as f:
				f.write(script)
			os.chmod(scriptF,0o755)
		except Exception as e:
			print(e)
	return(epiF,scriptF)
#def _wroteEpiDisk

def _installApp(app):
	bundle=list(app["bundle"].keys())[0]
	_debug("About to install")
	_debug("bundle: {}".format(bundle))
	_debug("pkgname: {}".format(app["pkgname"]))
	if bundle=="webapp":
		url=app["bundle"].get("webapp","")
		if url=="":
			url=app["homepage"]
		cmd=["xdg-open",url]
		#Launch browser
	elif bundle=="unknown":
		#Launch epi, use pkgname as parm
		zmdName=app["bundle"]["unknown"]
		pkgName=app["pkgname"]
		cmd=[zmdName,pkgName]
		if zmdName.endswith(".epi"):
			cmd.insert(0,"epi-gtk")
		#else:
		#	appName=zmdName.replace("zmds","applications").replace(".zmd",".app")
		#	if os.path.exists(appName):
		#		content=[]
		#		with open(appName,"r") as f:
		#			content=f.readlines()
		#		for l in content:
		#			if l.lower().strip()=="using=pkexec":
		#				cmd.insert(0,"pkexec")
	else:
		if bundle=="package":
			#Generate epi file for bundle
			appBundle=bundles.bundle()
			appBundle.setKind(bundles.kind.PACKAGE)
		elif bundle=="flatpak":
			#Generate epi file for bundle
			pass
		elif bundle=="snap":
			#Generate epi file for bundle
			pass
		elif bundle=="appimage":
			#Generate epi file for bundle
			pass
		appBundle.setApp(app)
		epi,script=appBundle.generateEpi()
		try:
			epi=_replaceEpiTemplate(epi,appname=app["bundle"][bundle],appid=app["id"],script="",iconpath=app["icon"],descname=app["name"])
		except Exception as e:
			print(e)
		try:
			script=_replaceScriptTemplate(script,appname=app["bundle"][bundle],appid=app["id"],description=app["description"])
		except Exception as e:
			print(e)
		try:
			epiF=_wroteEpiDisk(epi,script,app["id"])[0]
		except Exception as e:
			print(e)
		cmd=["epi-gtk",epiF]
	_debug(cmd)
	subprocess.run(cmd)

if len(sys.argv)>1:
	installer=sys.argv[0]
	app=sys.argv[1]
	args=None
	if len(sys.argv)>2:
		args=sys.argv[2]
	try:
		app=json.loads(app)
	except:
		_debug("Error parsing app")
	else:
		_installApp(app)
	

