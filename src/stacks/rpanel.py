#!/usr/bin/python3
import os
from PySide6.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget,QSizePolicy,QCheckBox,QGraphicsDropShadowEffect
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize,Signal,QThread
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QInfoLabel,QFlowTouchWidget
from lblLnk import QLabelLink
import css
import gettext
_ = gettext.gettext

ICON_SIZE=128
MINTIME=0.2
LAYOUT="appsedu"
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")
i18n={
	"ALL":_("All"),
	"AVAILABLE":_("Available"),
	"CATEGORIESDSC":_("Filter by category"),
	"CERTIFIED":_("Certified by Appsedu"),
	"CONFIG":_("Portrait"),
	"DESC":_("Navigate through all applications"),
	"FILTERS":_("Filters"),
	"FILTERSDSC":_("Filter by formats and states"),
	"HOME":_("Home"),
	"HOMEDSC":_("Main page"),
	"INSTALLED":_("Installed"),
	"LLXUP":_("Launch LliurexUp"),
	"MENU":_("Show applications"),
	"NEWDATA":_("Updating info"),
	"SEARCH":_("Search"),
	"SORTDSC":_("Sort alphabetically"),
	"TOOLTIP":_("Portrait"),
	"UPGRADABLE":_("Upgradables"),
	"UPGRADES":_("There're upgrades available")
	}

class mainPanel(QWidget):
	tagpressed=Signal(str)
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.maxCol=1
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("mp")
		self.setStyleSheet(css.tablePanel())
		lay=QVBoxLayout()
		lay.addSpacing(32)
		lay.setSpacing(24)
		self.searchGeometry=QSize(0,0)
		self.search=self._defSearch()
		hlay=QHBoxLayout()
		wdg=QWidget()
		wdg.setLayout(hlay)
		hlay.addWidget(self.search,Qt.AlignRight)
		lay.addWidget(wdg)
		if LAYOUT=="appsedu":
			self.search.setVisible(True)

		self.topBar=self._defCategoriesBar()
		self.topBar.setObjectName("categoriesBar")
		self.topBar.setVisible(False)
		self.topBar.setAttribute(Qt.WA_StyledBackground, True)
		lay.addWidget(self.topBar,Qt.AlignTop|Qt.AlignCenter)

		self.table=self._defTable()
		if LAYOUT=="appsedu":
			tableCol=1
		else:
			tableCol=0
		lay.addWidget(self.table)
		
		self.setLayout(lay)
	#def __init__

	def _defCategoriesBar(self):
		wdg=QFlowTouchWidget(self)
		lbl=QLabel("#{}".format(_("ALL")))
		wdg.addWidget(lbl)
		return(wdg)
	#def _defCategoriesBar

	def _tagNav(self,*args):
		print(args)
		cat=args[0].replace("#","")
		self.tagpressed.emit(cat)
	#def _tagNav(self,*args)


	def populateCategories(self,cats):
		self.topBar.clean()
		for cat in cats:
			wdg=QLabel("<a href=\"#{0}\">#{0}</a>".format(_(cat),css))
			wdg.setAttribute(Qt.WA_StyledBackground, True)
			wdg.setOpenExternalLinks(False)
			wdg.setObjectName("categoryTag")
			wdg.setStyleSheet("""text-decoration:none;color:#FFFFFF""")
			wdg.linkActivated.connect(self._tagNav)
			self.topBar.addWidget(wdg)
		if len(cats)>1:
			self.topBar.setVisible(True)
		else:
			self.topBar.setVisible(False)
	#def populateCategories

	def _defTable(self):
		table=QFlowTouchWidget(self)
		table.setObjectName("qFlow")
		table.flowLayout.setSpacing(24)
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		#if LAYOUT=="appsedu":
		#	table.setStyleSheet("""QFlowTouchWidget{border:0px; background:#FFFFFF;margin-left:100%;margin-right:1%;} QFlowTouchWidget::item{padding:2px}""")
		return(table)
	#def _defTable

	def tableLeaveEvent(self,*args):
		#self.table.setAutoScroll(False)
		return(False)
	#def enterEvent

	def tableKeyPressEvent(self,*args):
	#	if self.table.doAutoScroll()==None:
	#		self.table.setAutoScroll(True)
		return(False)
	#def tableKeyPressEvent

	def _defSearch(self):
		wdg=QWidget()
		#wdg.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)
		wdg.setAttribute(Qt.WA_StyledBackground, True)
		wdg.setObjectName("wsearch")
		self.searchBox=QLineEdit()
		self.searchBox.setObjectName("search")
		lay=QHBoxLayout()
		lay.setSpacing(0)
		self.btnSearch=QPushButton()
		self.btnSearch.setObjectName("bsearch")
		icn=QtGui.QIcon(os.path.join(RSRC,"search.png"))
		self.btnSearch.setIcon(icn)
		self.btnSearch.setMinimumSize(int(ICON_SIZE/4),int(ICON_SIZE/4))
		self.searchBox.setToolTip(i18n["SEARCH"])
		self.searchBox.setPlaceholderText(i18n["SEARCH"])
		self.searchGeometry=QSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		self.btnSearch.setIconSize(self.searchGeometry)
		lay.addWidget(self.searchBox)#,Qt.AlignCenter|Qt.AlignCenter)
		lay.addWidget(self.btnSearch)
		wdg.setLayout(lay)
		#wdg.setStyleSheet("""#wsearch{border:0px solid #FFFFFF;background:#002c4f;border-radius:20px}#search{color:#FFFFFF;background:#002c4f;border:0px solid;margin-left:12px;} #bsearch{color:#FFFFFF;background:#002c4f;border:0px;margin-right:12px}""")
		wdg.setMaximumWidth(450)
		return(wdg)
	#def _defSearch


	def setBtnIcon(self,icn=""):
		if icn!="":
			icn=QtGui.QIcon(os.path.join(RSRC,"{}.png".format(icn)))
		if len(self.searchBox.text())>0:
			icn=QtGui.QIcon(os.path.join(RSRC,"cancel.png"))
			self.btnSearch.setIconSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		else:
			icn=QtGui.QIcon(os.path.join(RSRC,"search.png"))
			self.btnSearch.setIconSize(self.searchGeometry)
		self.btnSearch.setIcon(icn)
	#def _resetSearchBtnIcon
