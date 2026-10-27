#!/usr/bin/python3
#from PySide6.QtWidgets import QListWidget,QListWidgetItem
from PySide6.QtWidgets import QTreeWidget,QTreeWidgetItem
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QCursor
from extras.constants import *
from extras.i18n import *
import gettext
_ = gettext.gettext

class QNavCategories(QTreeWidget):
	itemSelected=Signal(str)
	def __init__(self,rebost,parent=None):
		super().__init__()
		self.setObjectName("lstCategories")
		font=self.font()
		if font.pointSize()<14:
			font.setPointSize(font.pointSize()+(14-font.pointSize()))
		self.setHeaderHidden(True)
		self.setRootIsDecorated(False)
		self.setFont(font)
		self.setCursor(QCursor(Qt.PointingHandCursor))
		self.currentItemChanged.connect(self._decoreLstCategories)
		self.itemActivated.connect(self._emitSelected)
		self.itemClicked.connect(self._emitSelected)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setMinimumHeight(int(ICON_SIZE/3))
		self.setSizeAdjustPolicy(self.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
		self._rebost=rebost
		self._rebost.catEnded.connect(self._populateCategories)
		self.i18nCat={}
		self.catI18n={}
		self.oldCat=""
		self.load()
	#def __init__

	def _expandBranch(self,*args):
		if args[0].childCount()>0:
			expand=not(args[0].isExpanded())
			self.collapseAll()
			args[0].setExpanded(expand)
	#def _expandBranch

	def _emitSelected(self,*args):
		self._expandBranch(*args)
		cat=args[0].text(0)
		if self.oldCat==cat:
			return
		self.oldCat=cat
		category=self.i18nCat.get(cat,cat)
		self.itemSelected.emit(category)
	#def _emitSelected(self,*args):

	def load(self):
		self._rebost.blockSignals(False)
		self._rebost.setAction("getCategories")
		self._rebost.start()
	#def load

	def _populateCategories(self,cats):
		self.i18nCat={}
		self.catI18n={}
		self.categoriesTree=cats
		seenCats={}
		#Sort categories
		masterCategories=[]
		for mastercat,subcats in self.categoriesTree.items():
			#if cat.islower() it's a category from system without appstream info 
			cats=[]
			cats.append(mastercat)
			cats.extend(subcats)
			for cat in cats:
				if _(cat).capitalize() in self.i18nCat.keys() or cat.islower():
					continue
				if _(cat).capitalize() in self.i18nCat.keys() or cat.islower():
					continue
				self.i18nCat[_(cat).capitalize()]=cat
				self.catI18n[cat]=_(cat)
			masterCategories.append(_(mastercat).capitalize())
		masterCategories.sort()
		lowercats=[]
		for cat in masterCategories:
			if cat.lower() not in lowercats:
				item=QTreeWidgetItem(self)
				item.setText(0,cat)
				self.addTopLevelItem(item)
				subRawCat=self.i18nCat[_(cat).capitalize()]
				subcats=self.categoriesTree.get(subRawCat,[])
				subcats.sort()
				for subcat in subcats:
					if subcat.lower() not in lowercats:
						subitem=QTreeWidgetItem(item)
						subtext=self.catI18n.get(str(subcat),str(subcat))
						subitem.setText(0,subtext)
						subitem.setToolTip(0,subtext)
						#self.addChildren(item,subitem)
					lowercats.append(subcat.lower())
				
				item.setToolTip(0,cat)
				lowercats.append(cat.lower())
	#def _populateCategories

	def _decoreLstCategories(self,*args):
		if isinstance(args[0],QTreeWidgetItem):
			font=args[0].font(0)
			font.setBold(True)
			args[0].setFont(0,font)
		if len(args)>1:
			if isinstance(args[1],QTreeWidgetItem):
				font=args[1].font(0)
				font.setBold(False)
				args[1].setFont(0,font)
	#def _decoreLstCategories
	
	def unselectAll(self,*args):
		self.collapseAll()
		self._decoreLstCategories("",self.currentItem())
		self.clearSelection()
	#def unselectAll
