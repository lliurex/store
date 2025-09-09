#!/usr/bin/python3
import os,json

CONF="/usr/share/rebost/rebost.conf"

if os.path.exists(CONF):
	with open (CONF,"r") as f:
		jconf=json.loads(f.read())
		jconf["onlyVerified"]=not(jconf.get("onlyVerified",True))
with open (CONF,"w") as f:
	f.write(json.dumps(jconf))
