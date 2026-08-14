#!/usr/bin/python3
from wdg.flowBar import QFlowBar
from lib import rss

class blogBar(QFlowBar):
	def __init__(self,*args,parent=None,**kwargs):
		QFlowBar.__init__(self, parent)
		self.defaultSize=128
		self.spacing=10
		self.rss=rss.rssParser()
		self.overlay=True
		self.rss.blogEnded.connect(self.updateScreen)
	#def __init__(self,*args):

	def loadBlog(self):
		self.rss.feed="blog"
		self.rss.loadCache()
		self.rss.start()
	#def loadBlog
