#!/usr/bin/python3
#License GPL-3  https://www.gnu.org/licenses/gpl-3.0.html 
#Copyright 2026 LliureX Team

'''This script loads the appsedu data file from rebost cache
and parses the content setting a score for the data quality

100 -> An app could be directly resolved with the included info
90 -> Included info fails for matching but there's valid column-8 data
80 -> App could be loaded through an alias
70 -> Appsedu claims app's state differs from rebost but could be resolved
60 -> App could not be resolved
50 -> App could not be resolved, and has a colum-8 that also could not be resolved
30 -> App has an unresolvable alias
20 -> App has insufficient data in any field
10 -> App has not data in any field
0 -> App only has name
'''

import os,json,sys
from rebost import store
from bs4 import BeautifulSoup as bs

def _debug(msg):
	if dbg==True:
		print(msg)
#def _debug(msg):

def _print(msg):
	if output==True:
		print(msg)
#def _print(msg):

def _readCache():
	with open(appseduCache,"r") as f:
		rawcontent=f.read()
	bscontent=bs(rawcontent,"html.parser")
	appInfo=bscontent.find_all("td",["column-1","column-2","column-5","column-7","column-8"])
	apps=[]
	app={"name":"","icon":"","categories":"","auth":"","column8":"","href":""}
	for column in appInfo:
		full=False
		if (column.attrs["class"][0]=="column-1"):
			app["icon"]=column.img
		if (column.attrs["class"][0]=="column-2"):
			app["name"]=column.text
			href=column.find_all("a",href=True)
			for data in href:
				app["href"]=data["href"]
			_debug(app["href"])
		if (column.attrs["class"][0]=="column-5"):
			app["categories"]=column.text
		if (column.attrs["class"][0]=="column-7"):
			app["auth"]=column.text
		if (column.attrs["class"][0]=="column-8"):
			app["column8"]=column.text
			#if len(app["categories"].strip())>0:
			full=True
		if full==True:
			apps.append(app)
			app={"name":"","icon":"","categories":"","auth":"","column8":"","href":""}
			continue
	return(apps)
#def _readCache

def _analyzeApp(app):
	_debug("Analyze {}".format(app["name"]))
	href=os.path.basename(app["href"].removesuffix("/"))
	if "botiga" not in app["auth"].lower():
		if app["auth"] not in result["auth"].keys():
			result["auth"][app["auth"]]={}
		result["auth"][app["auth"]].update({app["name"]:app["href"]})
	else:
		if app["name"].lower() in appMap["nodisplay"]:
			result["nodisplay"].update({app["name"]:app["href"]})
		elif app["column8"] in appMap["nodisplay"]:
			result["nodisplay8"].update({app["name"]:"{} || {}".format(app["column8"],app["href"])})
		elif href in appMap["nodisplay"]:
			result["nodisplayHref"].update({app["name"]:"{} || {}".format(href,app["href"])})
		elif app["name"].lower() in appMap["aliases"].keys():
			alias=appMap["aliases"][app["name"].lower()]
			result["aliases"].update({app["name"]:"{} || {}".format(alias,app["href"])})
		elif app["column8"] in appMap["aliases"].keys():
			alias=appMap["aliases"][app["column8"]]
			result["aliases8"].update({app["name"]:"{} || {} || {}".format(app["column8"],alias,app["href"])})
		elif href in appMap["aliases"].keys():
			alias=appMap["aliases"][href]
			result["aliasesHref"].update({app["name"]:"{} || {} || {}".format(href,alias,app["href"])})
		else:
			res=json.loads(rebost.showApp(app["name"].lower()))
			if len(res)<=0:
				if len(app["column8"])>0:
					res=json.loads(rebost.showApp(app["column8"].lower()))
				if len(res)<=0:
					res=json.loads(rebost.showApp(href))
					if len(res)<=0:
							heur=app["column8"].removeprefix("zero:")
							heur=heur.removesuffix("-lliurex")
							res=json.loads(rebost.showApp(heur))
							if len(res)<=0:
								heur=os.path.basename(app["href"].removesuffix("/"))
								heur=heur.removesuffix("-lliurex")
								res=json.loads(rebost.showApp(heur))
								if len(res)<=0:
									result["unknown"].update({app["name"]:"{} || {}".format(app["column8"],app["href"])})
								else:
									result["rebost"].update({app["name"]:"{} || {} || {}".format(app["column8"],heur,app["href"])})
							else:
								result["rebost"].update({app["name"]:"{} || {} || {}".format(app["column8"],heur,app["href"])})
					else:
						result["href"].update({app["name"]:app["href"]})
				else:
					result["column8"].update({app["name"]:"{} || {}".format(app["column8"],app["href"])})
				_debug("Unknown app: {}".format(app["name"]))
			else:
				result["known"].update({app["name"]:app["href"]})
#def _analyzeApp

def _addStoreButton(app):
	button="&nbsp&nbsp&nbsp<a href=\"appstream://{}\"><button>Store</button></a>".format(app)
	return(button)
#def _addStoreButton

def _writeHtmlHeader(f):
	f.write("<HTML>")
	f.write("<BODY>")
	f.write("<h1 id=\"index\">APPSEDU DATA</h1>")
#def _writeHtmlHeader

def _writeHtmlIndex(f,results):
	f.write("<ol>")
	f.write('<li><a href="#known">Apps well known ({0})</a></li>'.format(len(results["known"])));
	f.write('<li><a href="#column8">Apps finded by column8 ({0})</a></li>'.format(len(results["column8"])));
	f.write('<li><a href="#href">Apps finded by href detail ({0})</a></li>'.format(len(results["href"])));
	f.write('<li><a href="#aliased">Apps finded by custom map ({0})</a></li>'.format(len(results["aliases"])));
	f.write('<li><a href="#aliased8">Apps finded by custom map through column8 ({0})</a></li>'.format(len(results["aliases8"])));
	f.write('<li><a href="#aliasedHref">Apps finded by custom map through href detail {0})</a></li>'.format(len(results["aliasesHref"])));
	f.write('<li><a href="#rebost">Apps finded using Rebost heuristics {0})</a></li>'.format(len(results["rebost"])));
	f.write('<li><a href="#noauth">Apps with auth other than <em>Autoritzada-Botiga</em> ({0} cases)</a></li>'.format(len(results["auth"])));
	f.write('<ul>')
	for key,val in results["auth"].items():
		f.write("<li><a href=\"#{0}\">{0} ({1})</a></li>".format(key.replace(" ","_"),len(val)));
	f.write('</ul>')
	f.write('<li><a href="#nodisplay">Apps marked as NoDisplay ({0})</a></li>'.format(len(results["nodisplay"])));
	f.write('<li><a href="#nodisplay8">Apps marked as NoDisplay through Column8 ({0})</a></li>'.format(len(results["nodisplay8"])));
	f.write('<li><a href="#nodisplayHref">Apps marked as NoDisplay through href detail ({0})</a></li>'.format(len(results["nodisplayHref"])));
	f.write('<li><a href="#unknown">Unknown apps ({0})</a></li>'.format(len(results["unknown"])));
	f.write('</ol>')
#def _writeHtmlIndex

def _writeKnown(f,results):
	f.write("<li><h3 id='known'>Apps well known ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["known"])))
	for key,href in results["known"].items():
		button=_addStoreButton(key)
		f.write("<a href=\"{0}\">{1}</a>{2}<br>".format(href,key,button))
		_print("{0} || {1} ".format(key,href))
#def _writeKnown

def _writeColumn8(f,results):
	f.write("<li><h3 id='column8'>Apps finded through column8 ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["column8"])))
	for key,app in results["column8"].items():
		alias,href=app.split("||")
		button=_addStoreButton(alias)
		f.write("<a href=\"{0}\">{1}</a> -> {2}{3}<br>".format(href,key,alias,button))
		_print("{0} ({1}) || {2} ".format(key,alias,href))
#def _writeColumn8

def _writeHref(f,results):
	f.write("<li><h3 id='href'>Apps finded through href detail ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["href"])))
	for key,app in results["href"].items():
		aliasHref=os.path.basename(app.removesuffix("/"))
		button=_addStoreButton(aliasHref)
		f.write("<a href=\"{0}\">{1}</a> -> {2}{3}<br>".format(app,key,aliasHref,button))
		_print("{0} ({1}) || {2} ".format(key,aliasHref,app))
#def _writeHref

def _writeAliased(f,results):
	f.write("<li><h3 id='aliased'>Apps finded through custom map ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["aliases"])))
	for key,app in results["aliases"].items():
		alias,href=app.split("||")
		button=_addStoreButton(alias)
		f.write("<a href=\"{0}\">{1}</a> -> {2}{3}<br>".format(href,key,alias,button))
		_print("{0} || {1} ".format(key,app))
#def _writeAliased

def _writeAliased8(f,results):
	f.write("<li><h3 id='aliased8'>Column8 finded through custom map ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["aliases8"])))
	for key,app in results["aliases8"].items():
		alias,column8,href=app.split("||")
		button=_addStoreButton(alias)
		f.write("<a href=\"{0}\">{1} ({3})</a> -> {2}{4}<br>".format(href,key,alias,column8,button))
		_print("{0} || {1} ".format(key,app))
#def _writeAliased8(f,results):

def _writeAliasedHref(f,results):
	f.write("<li><h3 id='aliasedHref'>Detail href finded through custom map ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["aliasesHref"])))
	for key,app in results["aliasesHref"].items():
		column8,alias,href=app.split("||")
		button=_addStoreButton(alias.strip())
		f.write("<a href=\"{0}\">{1} ({2})</a> -> {3}{4}<br>".format(href,key,column8,alias,button))
		_print("{0} || {1} ".format(key,app))
#def _writeAliasedHref(f,results):

def _writeRebost(f,results):
	f.write("<li><h3 id='rebost'>Apps find using heuristics from Rebost ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["aliasesHref"])))
	for key,app in results["rebost"].items():
		column8,alias,href=app.split("||")
		button=_addStoreButton(alias)
		f.write("<a href=\"{0}\">{1} ({3})</a> -> {2}{4}<br>".format(href,key,column8,alias,button))
		_print("{0} || {1} ".format(key,app))
#def _writeAliasedHref(f,results):

def _writeAuthApps(f,results):
	f.write("<li><h3 id='noauth'> Apps with auth other than \"Autoritzada botiga\" ({0} cases)&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["auth"])))
	for key,apps in results["auth"].items():
		f.write("<h4 id={0}>{1}</h4>".format(key.replace(" ","_"),key))
		_print(" * {0} ({1})".format(key,len(apps)))
		for app,href in apps.items():
			f.write("<a href={0}>{1}</a><br>".format(href,app))
			_print("{0} ({1})".format(app,href))
#def _writeAuthApps

def _writeNoDisplay(f,results):
	f.write("<li><h3 id='nodisplay'>Apps marked as NoDisplay in rebost ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["nodisplay"])))
	for key,app in results["nodisplay"].items():
		f.write("{0} || {1} ".format(key,app))
		_print("{0} || {1} ".format(key,app))
#def _writeNodisplay(f,results):

def _writeNoDisplay8(f,results):
	f.write("<li><h3 id='nodisplay8'>Column8 marked as NoDisplay in rebost ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["nodisplay8"])))
	for key,app in results["nodisplay8"].items():
		column8,href=app.split("||")
		f.write("<a href=\"{0}\">{1}</a> -> {2}<br>".format(href,key,column8))
		_print("{0} || {1} ".format(key,app))
#def _writeNoDisplay8(f,results):

def _writeNoDisplayHref(f,results):
	f.write("<li><h3 id='nodisplay8'>Detail href marked as NoDisplay in rebost ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["nodisplayHref"])))
	for key,app in results["nodisplayHref"].items():
		column8,href=app.split("||")
		f.write("<a href=\"{0}\">{1}</a> -> {2}<br>".format(href,key,column8))
		_print("{0} || {1} ".format(key,app))
#def _writeNoDisplayHref(f,results):

def _writeUnknown(f,results):
	f.write("<li><h3 id='unknown'>Unknown Apps ({0})&nbsp&nbsp&nbsp<a href=\"#index\"><button>Return</button></a></li></h3>".format(len(results["unknown"])))
	for key,app in results["unknown"].items():
		column8,href=app.split("||")
		f.write("<a href=\"{1}\">{0} ({2})</a><br>".format(key,href,column8))
		_print("{0} || {1} ".format(key,app))
#def _writeUnknown

def _endHtmlDoc(f):
	f.write("</BODY>")
	f.write("</HTML>")
	f.close()
#def _endHtml(f):

def _writeResults(results):
	f=open(foutput,"w")
	_writeHtmlHeader(f)
	_writeHtmlIndex(f,results)
	f.write("<hl>")
	f.write("<ul>")
	_print("==================================")
	_print(" ** Well known apps ({0}) **".format(len(results["known"])))
	_writeKnown(f,results)
	_print(" ** Apps finded using column8 ({0}) **".format(len(results["column8"])))
	_writeColumn8(f,results)
	_print(" ** Apps finded using href of detail ({0}) **".format(len(results["href"])))
	_writeHref(f,results)
	_print(" ** Custom mapped Apps ({0}) **".format(len(results["aliases"])))
	_writeAliased(f,results)
	_print(" ** Custom mapped column8 ({0}) **".format(len(results["aliases8"])))
	_writeAliased8(f,results)
	_print(" ** Custom mapped detail href ({0}) **".format(len(results["aliasesHref"])))
	_writeAliasedHref(f,results)
	_print(" ** Apps finded through rebost heuristics {0}) **".format(len(results["rebost"])))
	_writeRebost(f,results)
	_print(" ** Apps with auth other than \"Autoritzada botiga\" **")
	_writeAuthApps(f,results)
	_print(" ** Apps marked as NoDisplay in rebost ({0}) **".format(len(results["nodisplay"])))
	_writeNoDisplay(f,results)
	_print(" ** Column8 marked as NoDisplay in rebost ({0}) **".format(len(results["nodisplay8"])))
	_writeNoDisplay8(f,results)
	_print(" ** Detail href marked as NoDisplay in rebost ({0}) **".format(len(results["nodisplay8"])))
	_writeNoDisplayHref(f,results)
	_print(" ** Unknown Apps ({0}) **".format(len(results["unknown"])))
	_writeUnknown(f,results)
	f.write("</ul>")
	_endHtmlDoc(f)
#def _writeResults

### MAIN ###

dbg=False # for development purposes only
output=False
cache="/var/cache/rebost/raw"
appseduCache=os.path.join(cache,"appsedu.raw")
foutput="/tmp/output.html"
h=False

if len(sys.argv)>1:
	args=sys.argv[1:]
	args.reverse()
	while args:
		arg=args.pop()
		if arg.lower().replace("-","") in ["v","verbose"]:
			output=True
		elif arg.lower().replace("-","") in ["i","input"]:
			appseduCache=args.pop()
		elif arg.lower().replace("-","") in ["o","output"]:
			foutput=args.pop().replace(" ","_")
			if foutput.endswith(".html")==False:
				foutput+=".html"
		else:
			h=True
	if h==True:
		print("Usage:")
		print("\t{0} [-v || --verbose] [-h || --help] [-i || --input file] [-o || --output file".format(sys.argv[0]))
		print("")
		print("\t -h --help: Show this message")
		print("\t -v --verbose: Print output")
		print("\t -i --input: file: Path to a downloaded appsedu webpage, {} by default".format(appseduCache))
		print("\t -o --output: file: Output file, /tmp/output.html by default")
		sys.exit(0)

apps=[]
result={"known":{},
	"href":{},
	"column8":{},
	"auth":{},
	"unknown":{},
	"rebost":{},
	"aliases":{},
	"aliases8":{},
	"aliasesHref":{},
	"nodisplay":{},
	"nodisplay8":{},
	"nodisplayHref":{}
}

if os.path.exists(appseduCache):	
	try:
		apps=_readCache()
	except Exception as e:
		print("{0}: {1}".format(appseduCache,e))
	if len(apps)>0:
		rebost=store.client()
		appMap=rebost.getMaps()
		for app in apps:
			_analyzeApp(app)
		_writeResults(result)
		print("-------========-------")
		print("Output file generated: {}".format(foutput))

else:
	print("Could not find input file {}".format(appseduCache))
sys.exit(0)
