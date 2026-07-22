#!/usr/bin/python3
import os,sys,json,shutil
import tempfile,subprocess
import importlib.util
from rebost import store
import gi
gi.require_version('AppStreamGlib', '1.0')
from gi.repository import AppStreamGlib as appstream
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

i18n={"ASK":_("includes more than one package.<br>What to do?"),
	"BTN_NO":_("Install later"),
	"BTN_YES":_("Install one")
	}

#pkg=sys.argv[1]
#epiFileCmd=["dpkg","-L",pkg]
#try:
#	epiFileOut=subprocess.check_output(epiFileCmd,encoding="utf8",universal_newlines=True)
#except:
#	epiFileOut=""
#epiFile=""
#for l in epiFileOut.split("\n"):
#	if l.endswith(".epi"):
#		epiFile=l
#		break
rebost=store.client()
rebost.DBG=False
rebost.CACHE="/var/cache/rebost"
rebost.appstream=appstream
rebost.langs=["ca","es","en"]
spec = importlib.util.spec_from_file_location("engine","/usr/share/rebost/plugins/epic.py")
pluginlib = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = pluginlib
spec.loader.exec_module(pluginlib)
pluginEpic=pluginlib.engine(rebost)

spec = importlib.util.spec_from_file_location("engine","/usr/share/rebost/rebostHelper.py")
pluginlib = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = pluginlib
spec.loader.exec_module(pluginlib)
pluginHelp=pluginlib


pluginEpic.mapFixes=rebost.getMaps()
epiFile=sys.argv[1]
if os.path.exists(epiFile):
	epiInfo={}
	#Generate an yml file for this epic and add to rebost
	try:
		with open (epiFile,"r") as f:
			epiInfo=json.load(f)
	except Exception as e:
		print("Error reading {}".format(epiFile))
		print(e)
		
	pkgInfoList=epiInfo.get("pkg_list",[])
	for pkgItem in pkgInfoList:
		name=pkgItem.pop("name").strip()
		epiInfo.update({name:pkgItem})
	epiList=pluginEpic.epiManager.all_available_epis
	apps=[]
	for epi in epiList:
		for name,data in epi.items():
			if name==os.path.basename(epiFile):
				apps=pluginEpic._getAppsFromEpic([{name:data}])
				break
	for app in apps:
		for bundle in app.get_bundles():
			if bundle.get_kind()==rebost.appstream.BundleKind.PACKAGE:
				continue
			if bundle.get_id().endswith(".epi")==False:
				bundle.set_id(os.path.basename(epiFile))
		#app.add_pkgname(os.path.basename(epiFile))
		a=app.to_xml()
		fxml="/tmp/{}.xml".format(app.get_id())
		with open(fxml,"w") as f:
			f.write(a.str)
		if os.path.exists(fxml):
			fyml=fxml.replace(".xml",".yml")
			subprocess.run(["appstreamcli","convert",fxml,fyml])
			res=rebost.showApp(app.get_id())
			if len(res)==0:
				rebost.addAppFromYml(fyml,"unkown",os.path.basename(epiFile))

	epicCmd=["epic","-u","-nc","install",epiFile]
	epicProc=subprocess.Popen(epicCmd,encoding="utf8",universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	try:
		out,err=epicProc.communicate()
	except Exception as e:
		print(e)
	else:
		if "executeshowinfo" in out.lower().replace(" ",""):
			name=os.path.basename(epiFile).removesuffix(".epi")
			dlg=["kdialog","--title","Lliurex-Store","--icon","lliurex-store","--yesno","<p><strong>{0}</strong> {1}</p>".format(name,i18n["ASK"]),"--yes-label",i18n["BTN_YES"],"--no-label",i18n["BTN_NO"]]
			try:
				out=subprocess.check_call(dlg)
				epiCmd=["epi-gtk","-nc","install",epiFile]
				subprocess.run(epiCmd)
			except:
				print("SHOIN")

