#!/usr/bin/python3
import lib.template

class templateApi():
	def __init__(self,parent=None):
		self._debug=False
		self.script=self._appTemplate()
	#def __init__

	def _getAppInstall(self):
		installCmd="/usr/share/appimage-manager/bin/appimage-helper.py install {@APPNAME} {@APPID}"
		return(installCmd)
	#def _getAppInstall

	def _getAppRemove(self):
		removeCmd="/usr/share/appimage-manager/bin/appimage-helper.py remove {@APPID}"
		return(removeCmd)
	#def _getAppRemove

	def _getAppStatus(self):
		statusCmd="TEST=$( ls \"{@APPID}\"  1>/dev/null 2>&1 && echo 'installed')"
		return(statusCmd)
	#def _getAppStatus

	def _appTemplate(self):
		appScript=template.script.replace("{@INSTALLCMD",self._getAppInstall())
		appScript=appScript.replace("{@REMOVECMD}",self._getAppRemove())
		appScript=appScript.replace("{@STATUSCMD}",self._getAppStatus())
		return(appScript)
	#def _appTemplate
#class templateApi

