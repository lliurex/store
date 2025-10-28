#!/usr/bin/python3
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from rebost import store
import json,os,subprocess
from urllib.request import Request
from urllib.request import urlretrieve
from urllib import request
from bs4 import BeautifulSoup as bs

import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

DBusGMainLoop(set_as_default=True)
OBJPATH = "/"
IFACE="org.kde.krunner1"
SERVICE = "net.lliurex.store"
CACHE=os.path.join(os.environ.get("HOME"),".cache","store")

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
	
	@dbus.service.method(IFACE, in_signature="ss", out_signature="s")
	def show(self, query,extra):
		result=[]
		if len(query)>1:
			app=json.loads(self.rebost.showApp(query))[0]

			homepage=app.get('homepage','')
			if isinstance(homepage,str)==False:
				homepage=""
			if homepage.startswith("https://portal.edu.gva.es/appsedu")==True and app["description"].count(" ")<3:
				details={"icon":"","description":"","summary":""}
				page=os.path.basename(homepage.removesuffix("/"))
				if os.path.exists(os.path.join(CACHE,page)):
					with open(os.path.join(CACHE,page),"r") as f:
						content=f.read()
				else:
					req=Request(homepage, headers={'User-Agent':'Mozilla/5.0'})
					try:
						with request.urlopen(req,timeout=2) as f:
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
				if len(details.get("description",""))>len(app["description"]):
					app["description"]=details["description"]
				if len(details.get("icon",""))>0:
					app["icon"]=details["icon"]
		return(json.dumps([json.dumps(app)]))

	@dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
	def Match(self, query):
		matches=[]
		match={}
		seen=[]
		result=""
		if len(query)>2:
			result=self.rebost.searchApp(query)
		jmatches=json.loads(result)
		for japp in jmatches:
			if japp["name"] in match.keys():
				if japp["summary"]=="":
					continue
			states=japp.get("status",{}).copy()
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
