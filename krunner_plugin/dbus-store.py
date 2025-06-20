#!/usr/bin/python3
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from rebost import store
import json
import subprocess

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
			match.update({japp["name"]:(japp["name"],"Install {}".format(japp["name"]),icon,100,1.0,{"subtext":japp["summary"]})})
		matches.extend(match.values())
		return (matches)

		return(matches)
		#return [["action1", "Action Text", "document-edit", 100, 1.0, {}]]
	
	@dbus.service.method(IFACE, in_signature="ss")
	def Run(self, matchId, actionId):
		print(matchId)
		subprocess.run(["/usr/bin/lliurex-store","appsedu://{}".format(matchId)])
		return

if __name__ == '__main__':
	runner = storeRunner()
	loop = GLib.MainLoop()
	loop.run()
