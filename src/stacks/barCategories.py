#!/usr/bin/python3
import os
import json
from PySide2.QtWidgets import QLabel,QApplication
from PySide2.QtCore import Qt,Signal
from QtExtraWidgets import QFlowTouchWidget
from constants import *
import css
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

class QToolBarCategories(QFlowTouchWidget):
	requestLoadCategory=Signal(str)
	def __init__(self,*arg,**kwargs):
		super().__init__()
		self.setObjectName("categoriesBar")
		#self.setStyleSheet("margin-left:{}".format(MARGIN))
		#self.setAttribute(Qt.WA_StyledBackground, True)
		self.currentItemChanged.connect(self._catDecorate)
		self.setVisible(False)
	#def __init__

	def _categoryLinkClicked(self,*args):
		cat=args[0].replace("#","")
		self.requestLoadCategory.emit(cat)
	#def _categoryLinkClicked(self,*args)

	def _catDecorate(self,*args):
		current=args[1]
		if current.property("decorated")==False:
			current.setProperty("decorated",True)
	#def _catDecorate

	def _catUndecorate(self,*args):
		for idx in range(0,self.count()):
			current=self.itemAt(idx).widget()
			current.setProperty("decorated",False)
	#def _catUndecorate

	def populateCategories(self,*args):
		self.clean()
		self.leaveEvent=self._catUndecorate
		subcategories=[]
		category=""
		if len(args)>0:
			for arg in args:
				if isinstance(arg,str):
					category=arg
				elif isinstance(arg,list):
					subcategories=arg
		if category not in subcategories and category!="":
			subcategories.insert(0,category)
		h=0
		for subcategory in subcategories:
			wdg=QLabel()
			wdg.setObjectName("categoryTag")
			if subcategory!=category:
				text="<a href=\"#{0}\" style='color:#FFFFFF;text-decoration:none'>{0}</a>".format(_(subcategory))
			else:
				text="<a href=\"#{0}\" style='color:#FFFFFF;text-decoration:none'><strong>{0}</strong></a>".format(_(subcategory))
			wdg.setText(text)
			wdg.setAttribute(Qt.WA_Hover,True)
			wdg.setAttribute(Qt.WA_StyledBackground, True)
			wdg.setOpenExternalLinks(False)
			wdg.linkActivated.connect(self._categoryLinkClicked)
			wdg.setCursor(Qt.PointingHandCursor)
			self.addWidget(wdg)
			h=wdg.sizeHint().height()
		if h>0:
			self.setFixedHeight((h*2)+int(MARGIN))
	#def populateCategories
#class categoriesBar

