#!/usr/bin/python3
import os,sys,json,shutil
import tempfile,subprocess

class epiFile():
	def __init__(self,*args,**kwargs):
		pass

	#def epiFromPkg(app,bundle,user='',remote=False,postaction=""):
	def epiForPkg(self,tmpDir,pkg,bundle,app,postaction=""):
		#if os.path.isdir("/tmp/rebost")==False:
		#	os.makedirs("/tmp/rebost")
		#	os.chmod("/tmp/rebost",0o777)
		#tmpDir=tempfile.mkdtemp(dir="/tmp/rebost")
		#os.chmod(tmpDir,0o755)
		try:
			epiJson,epiContent=self._jsonForEpi(tmpDir,app,pkg,bundle)
		except Exception as e:
			print(e)
		episcript=self._shForEpi(epiJson,app,pkg,bundle,postaction)
		return(epiJson,episcript)
	#def epiFromPkg
		
	def _jsonForEpi(self,tmpDir,app,pkg,bundle):
		epiJson="{}_{}.epi".format(os.path.join(tmpDir.name,app.get("id").replace(".","_")),bundle)
		epiScript="{}_{}.sh".format(os.path.join(tmpDir.name,app.get("id").replace(".","_")),bundle)
		#if not os.path.isfile(epiJson):
		name=app.get('name').strip()
		pkgname=app.get('bundle',{}).get(bundle)
		icon=app.get('icon','')
		iconFolder=''
		if icon:
			iconFolder=os.path.dirname(icon)
			icon=os.path.basename(icon)
		epiContent={}
		epiContent["type"]="file"
		epiContent["pkg_list"]=[{"name":name,"key_store":name,'url_download':'','custom_icon':icon,'version':{'all':pkgname}}]
		epiContent["script"]={"name":epiScript,'download':True,'remove':True,'getStatus':True,'getInfo':True}
		epiContent["custom_icon_path"]=iconFolder
		epiContent["required_root"]=True
		epiContent["check_zomando_state"]=False
		with open(epiJson,'w') as f:
			f.write(json.dumps(epiContent))
		return(epiJson,epiContent)
	#def _jsonForEpi

	def _shForEpi(self,epiJson,app,pkg,bundle,postaction=""):
		tmpDir=os.path.dirname(epiJson)
		epiScript="{}_{}.sh".format(os.path.join(tmpDir,app.get("id").replace(".","_")),bundle)
		if not (os.path.isfile(epiScript) and remote==False):
			self._populateEpi(epiScript,app,pkg,bundle,postaction)
			if os.path.isfile(epiScript):
				os.chmod(epiScript,0o755)
		return(epiScript)
	#def _shForEpi

	def _populateEpi(self,epiScript,app,pkg,bundle,postaction=""):
		commands=self._getCommandsForBundle(bundle,app)
		with open(epiScript,'w') as f:
			f.write("#!/bin/bash\n")
			f.write("function getStatus()\n{")
			f.write("\t\t{}\n".format(commands.get('statusTestLine')))
			f.write("\t\tif [ \"$TEST\" == 'installed' ];then\n")
			f.write("\t\t\tINSTALLED=0\n")
			f.write("\t\telse\n")
			f.write("\t\t\tINSTALLED=1\n")
			f.write("\t\tfi\n")
			f.write("}\n")

			f.write("ACTION=\"$1\"\n")
			f.write("ERR=0\n")
			f.write("case $ACTION in\n")
			f.write("\tremove)\n")
			f.write("\t\t{}\n".format(commands.get('removeCmd')))
			for command in commands.get('removeCmdLine',[]):
				f.write("\t\t{}\n".format(command))
			#if postaction!="":
			#	f.write("\t\t{}\n".format(postaction))
			f.write("\t\t;;\n")
			f.write("\tinstallPackage)\n")
			f.write("\t\t{}\n".format(commands.get('installCmd')))
			for command in commands.get('installCmdLine',[]):
				f.write("\t\t{}\n".format(command))
			if postaction!="":
				f.write("\t\t{}\n".format(postaction))
			f.write("\t\t;;\n")
			f.write("\ttestInstall)\n")	
			f.write("\t\techo \"0\"\n")
			f.write("\t\t;;\n")
			f.write("\tgetInfo)\n")
			f.write("\t\techo \"{}\"\n".format(app['description']))
			f.write("\t\t;;\n")
			f.write("\tgetStatus)\n")
			f.write("\t\tgetStatus\n")
			f.write("\t\techo $INSTALLED\n")
			f.write("\t\t;;\n")
			f.write("\tdownload)\n")
			f.write("\t\techo \"Installing...\"\n")
			f.write("\t\t;;\n")
			f.write("esac\n")
			f.write("[ $ERR -gt 0 ] && exit 1 || exit 0\n")
	#def _populateEpi

	def _getCommandsForBundle(self,bundle,app,user=''):
		commands={}
		installCmd=''
		installCmdLine= []
		removeCmd=''
		removeCmdLine=[]
		statusTestLine=''
		if bundle=='package':
			(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForPackage(app,user)
		elif bundle=='snap':
			(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForSnap(app,user)
		elif bundle=='flatpak':
			(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForFlatpak(app,user)
		elif bundle=='appimage':
			(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForAppimage(app,user)
		elif bundle=='zomando':
			zpath=app["bundle"]["zomando"]
			if os.path.exists(zpath)==False:
				(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForPackage(app,user)
			else:
				(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=self._getCommandsForZomando(app,user)
		commands['installCmd']=installCmd
		commands['installCmdLine']=installCmdLine
		commands['removeCmd']=removeCmd
		commands['removeCmdLine']=removeCmdLine
		commands['statusTestLine']=statusTestLine
		return(commands)
	#def _getCommandsForBundle

	def _getCommandsForPackage(self,app,user):
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		#installCmd="pkcon install --allow-untrusted -y {} 2>&1;ERR=$?".format(app['pkgname'])
		#pkcon has a bug detecting network if there's no network under NM (fails with systemd-networkd)
		#Temporary use apt until bug fix
		#FIX PKGNAME
		pkgname=app.get("bundle",{}).get("package",app["pkgname"])
		installCmd="export DEBIAN_FRONTEND=noninteractive"
		installCmdLine.append("export DEBIAN_PRIORITY=critical")
		installCmdLine.append("apt-get -qy -o \"Dpkg::Options::=--force-confdef\" -o \"Dpkg::Options::=--force-confold\" install {} 2>&1;ERR=$?".format(pkgname))
		#removeCmd="pkcon remove -y {} 2>&1;ERR=$?".format(app['pkgname'])
		removeCmd="apt remove -y {} 2>&1;ERR=$?".format(pkgname)
		removeCmdLine.append("TEST=$(pkcon resolve --filter installed {0}| grep {0} > /dev/null && echo 'installed')".format(pkgname))
		removeCmdLine.append("if [ \"$TEST\" == 'installed' ];then")
		removeCmdLine.append("exit 1")
		removeCmdLine.append("fi")
		statusTestLine=("TEST=$(pkcon resolve --filter installed {0}| grep {0} > /dev/null && echo 'installed')".format(pkgname))
		return(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)
	#def _getCommandsForPackage

	def _getCommandsForSnap(self,app,user):
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		installCmd="snap install {} 2>&1;ERR=$?".format(app['bundle']['snap'])
		removeCmd="snap remove {} 2>&1;ERR=$?".format(app['bundle']['snap'])
		statusTestLine=("TEST=$( snap list 2> /dev/null| grep {} >/dev/null && echo 'installed')".format(app['bundle']['snap']))
		return(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)
	#def _getCommandsForSnap

	def _getCommandsForFlatpak(self,app,user):
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		#installCmd="sudo -u {0} flatpak  --user -y install {1} 2>&1;ERR=$?".format(user,app['bundle']['flatpak'])
		#removeCmd="sudo -u {0} flatpak --user -y uninstall {1} 2>&1;ERR=$?".format(user,app['bundle']['flatpak'])
		#statusTestLine=("TEST=$(sudo -u {0} flatpak --user list 2> /dev/null| grep $'{1}\\t' >/dev/null && echo 'installed')".format(user,app['bundle']['flatpak']))
		installCmd="flatpak  --system -y install {1} 2>&1;ERR=$?".format(user,app['bundle']['flatpak'])
		removeCmd="flatpak --system -y uninstall {1} 2>&1;ERR=$?".format(user,app['bundle']['flatpak'])
		flatpak=app['bundle']['flatpak']
		if "/" in flatpak:
			flatpak=flatpak.split("/")[1]
		statusTestLine=("TEST=$(flatpak --system list 2> /dev/null| grep $'{0}' >/dev/null && echo 'installed')".format(flatpak))
		return(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)
	#def _getCommandsForFlatpak

	def _getCommandsForAppimage(self,app,user):
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		#user=os.environ.get('USER')
		installCmd=""
		installCmd="wget -O /tmp/{}.appimage {} 2>&1;ERR=$?".format(app['pkgname'],app['bundle']['appimage'])
		destdir="/opt/appimages"
		if user!='root' and user:
			destdir=os.path.join("/home",user,".local","bin")
		installCmdLine.append("mkdir -p {}".format(destdir))
		installCmdLine.append("mv /tmp/{0}.appimage {1}".format(app['pkgname'],destdir))
		destPath=os.path.join(destdir,"{}.appimage".format(app['pkgname']))
		deskName="{}-appimage.desktop".format(app['pkgname'])
		installCmdLine.append("chmod +x {}".format(destPath))
		installCmdLine.append("/usr/share/app2menu/app2menu-helper.py {0} \"{1}\" \"{2}\" \"{3}\" \"{4}\" /usr/share/applications/{6} {4}".format(app['pkgname'],app['icon'],app['summary'],";".join(app['categories']),destPath,user,deskName))
		removeCmd="rm {0} && rm /home/{1}/.local/share/applications/{2}-appimage.desktop;ERR=$?".format(destPath,user,app['pkgname'])
		statusTestLine=("TEST=$( ls {}  1>/dev/null 2>&1 && echo 'installed')".format(destPath))
		return(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)
	#def _getCommandsForAppimage

	def _getCommandsForZomando(self,app,user):
		(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)=("",[],"",[],"")
		zdir="/usr/share/zero-center/zmds/"
		zpath=app['bundle']['zomando']
	#	if zdir not in zpath:
		#zpath=os.path.join("exec /usr/share/zero-center/zmds/",app['bundle']['zomando'])
		epath=os.path.basename(app["bundle"]["zomando"].replace(".zmd",".epi"))
		installCmd="epic install -u -nc {} {}".format(epath,app["name"])
		removeCmd="epic uninstall -u -nc {} {}".format(epath,app["name"])
		statusTestLine=("TEST=$(epic showinfo %s | grep installed.*%s | grep -o installed)"%(epath,app["name"]))
	#	else:
	#		installCmd="exec {}".format(zpath)
	#		removeCmd="exec {}".format(zpath)
	#		statusTestLine=("TEST=$([ -e %s ]  && echo installed || n4d-vars getvalues ZEROCENTER | tr \",\" \"\\n\"|awk -F ',' 'BEGIN{a=0}{if ($1~\"%s\"){a=1};if (a==1){if ($1~\"state\"){ b=split($1,c,\": \");if (c[b]==1) print \"installed\";a=0}}}')"%(zpath,os.path.basename(zpath).replace(".zmd","")))
		return(installCmd,installCmdLine,removeCmd,removeCmdLine,statusTestLine)
	#def _getCommandsForZomando
		
pkg=sys.argv[1]
bundle=sys.argv[2]
app=json.loads(sys.argv[3])
try:
	epi=epiFile()
except Exception as e:
	print(e)
tmpDir=tempfile.TemporaryDirectory()
os.chmod(tmpDir.name,0o755)
epiFile,epiScript=epi.epiForPkg(tmpDir,pkg,bundle,app)
cmd=["/usr/sbin/epi-gtk",epiFile]
proc=subprocess.run(cmd)
cmd=[epiScript,"getStatus"]
status=subprocess.check_output(cmd,encoding="utf8",universal_newlines=True)
tmpDir.cleanup()
sys.exit(status)
