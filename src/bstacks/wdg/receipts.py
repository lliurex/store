#!/usr/bin/python3
from wdg.flowBar import QFlowBar
from extras.i18n import *

class recsBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.itemsPerPage=2
		self.defaultSize=128
		self.overlay=False
		self.onlyImg=True
		self.overlayTextImg=True
		self.spacing=10
	#def __init__(self,*args):

	def loadRecs(self):
		llxReleases={"LliureX 25":
						{"url":"https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Receptes+LliureX+25",
						"desc":i18n["RECS_LLX25"],
						"img":"https://wiki.edu.gva.es/lliurex/tiki-download_file.php?fileId=7276"
						},
					"LliureX 23":
						{"url":"https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Receptes+LliureX+23",
						"desc":i18n["RECS_LLX23"],
						"img":"https://wiki.edu.gva.es/lliurex/tiki-download_file.php?fileId=6747"
						},
					"LliureX 21":
						{"url":"https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Receptes+LliureX+21",
						"desc":i18n["RECS_LLX21"],
						"img":"https://wiki.edu.gva.es/lliurex/tiki-download_file.php?fileId=5601"
						},
					"LliureX":
						{"url":"https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Receptes",
						"desc":i18n["RECS_LLX"],
						"img":"https://wiki.edu.gva.es/lliurex/tiki-download_file.php?fileId=4546"
						}}
		data={}
		for release,info in llxReleases.items():
			data[len(data)]={"title":info["desc"],
					"summary":"<a href=\"{0}\">{1}</a>".format(info["url"],info["desc"]),
					"metadata":"<a href=\"{0}\">{1}</a>".format(info["url"],info["desc"]),
					"img":info["img"],
					"link":info["url"]}

		self.updateScreen("receipts",data)
	#def loadRecs
