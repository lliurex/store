#!/usr/bin/python3
import lib.template

class templatePkg():
	def __init__(self,parent=None):
		self._debug=False
		self.script=self._appTemplate()
	#def __init__

	def _getAppInstall(self):
		installCmd="export DEBIAN_FRONTEND=noninteractive\n"
		installCmd+="export DEBIAN_PRIORITY=critical\n"
		installCmd+="apt-get -qy -o \"Dpkg::Options::=--force-confdef\" -o \"Dpkg::Options::=--force-confold\" "
		installCmd+="install {@APPNAME} 2>&1;ERR=$?"
		return(installCmd)
	#def _getAppInstall

	def _getAppRemove(self):
		removeCmd="apt remove -y {@APPNAME} 2>&1;ERR=$?"
		removeCmd+="TEST=$(pkcon resolve --filter installed {@APPNAME}| grep {@APPNAME} > /dev/null && echo 'installed')\n"
		removeCmd+="if [ \"$TEST\" == 'installed' ];then\n"
		removeCmd+="exit 1\n"
		removeCmd+="fi"
		return(removeCmd)
	#def _getAppRemove

	def _getAppStatus(self):
		statusCmd="TEST=$(pkcon resolve --filter installed {@APPNAME}| grep {@APPNAME} > /dev/null && echo 'installed')"
		return(statusCmd)
	#def _getAppStatus

	def _appTemplate(self):
		appScript=template.script.replace("{@INSTALLCMD}",self._getAppInstall())
		appScript=appScript.replace("{@REMOVECMD}",self._getAppRemove())
		appScript=appScript.replace("{@STATUSCMD}",self._getAppStatus())
		return(appScript)
	#def _appTemplate
#class templatePkg

