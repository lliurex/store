#!/usr/bin/python3
import lib.template

class templateFlt():
	def __init__(self,parent=None):
		self._debug=False
		self.script=self._appTemplate()
	#def __init__

	def _getAppInstall(self):
		installCmd="flatpak  --system -y install {@APPNAME} 2>&1;ERR=$?"
		return(installCmd)
	#def _getAppInstall

	def _getAppRemove(self):
		removeCmd="flatpak --system -y uninstall {@APPNAME} 2>&1;ERR=$?"
		return(removeCmd)
	#def _getAppRemove

	def _getAppStatus(self):
		statusCmd="TEST=$(flatpak --system list 2> /dev/null| grep $'{@APPNAME}' >/dev/null && echo 'installed')"
		return(statusCmd)
	#def _getAppStatus

	def _appTemplate(self):
		appScript=template.script.replace("{@INSTALLCMD",self._getAppInstall())
		appScript=appScript.replace("{@REMOVECMD}",self._getAppRemove())
		appScript=appScript.replace("{@STATUSCMD}",self._getAppStatus())
		return(appScript)
	#def _appTemplate
#class templateFlt

