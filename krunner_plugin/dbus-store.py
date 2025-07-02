#!/usr/bin/python3
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from rebost import store
import json,os,subprocess

import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

DBusGMainLoop(set_as_default=True)
OBJPATH = "/"
IFACE="org.kde.krunner1"
SERVICE = "net.lliurex.store"

class storeRunner(dbus.service.Object):
	def __init__(self):
		dbus.service.Object.__init__(
			self,
			dbus.service.BusName(SERVICE, dbus.SessionBus()),
			OBJPATH,
			)

		self.rebost=store.client()
	
	@dbus.service.method(IFACE, out_signature="a(sss)")
	def Actions(self,*args):
		return [("id", "Tooltip", "lliurex-store")]
	
	@dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
	def Match(self, query):
		matches=[]
		match={}
		seen=[]
		result=""
		if len(query)>2:
			result=self.rebost.searchApp(query)
		jmatches=json.loads(result)
		for app in jmatches:
			japp=json.loads(app)
			if japp["name"] in match.keys():
				if japp["summary"]=="":
					continue
			states=japp.get("state",{}).copy()
			zmd=states.get("zomando","0")
			installed=False
			if len(states)>0:
				for bundle,state in states.items():
					if bundle=="package" and zmd=="1":
						if japp["bundle"]["package"].startswith("zero"):
							continue
					if state=="0":# and zmdInstalled!="0":
						installed=True
			if installed==True:
				continue
			icon="llxstore"
			if isinstance(japp["icon"],str):
				if "://" not in japp["icon"]:
					icon=japp["icon"]
				else:
					stripName=''.join(ch for ch in os.path.basename(japp["icon"]) if ch.isalnum())
					MAX=96
					if (len(stripName)>MAX):
						stripName=os.path.basename(stripName[len(stripName)-MAX:])
					if stripName.endswith(".png")==False:
						if stripName.endswith("png")==True:
							stripName=stripName.replace("png",".png")
						else:
							stripName+=".png"
					cacheDirs=[os.path.join(os.environ["HOME"],".cache","rebost","imgs")]
					for d in cacheDirs:
						candidate=os.path.join(d,stripName)
						if os.path.exists(candidate) or os.path.exists(candidate.lower()):
							icon=os.path.join(d,stripName)
			match.update({japp["name"]:(japp["name"],"{} {}".format(_("Install"),japp["name"]),icon,100,1.0,{"subtext":japp["summary"]})})
		matches.extend(match.values())
		return (matches)
		#return [["action1", "Action Text", "document-edit", 100, 1.0, {}]]
	
	@dbus.service.method(IFACE, in_signature="ss")
	def Run(self, matchId, actionId):
		subprocess.run(["/usr/bin/lliurex-store","appsedu://{}".format(matchId)])
		return

if __name__ == '__main__':
	runner = storeRunner()
	loop = GLib.MainLoop()
	loop.run()
