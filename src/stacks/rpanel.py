#!/usr/bin/python3
import os
from PySide2.QtWidgets import QApplication, QLabel,QPushButton,QGridLayout,QHeaderView,QHBoxLayout,QComboBox,QLineEdit,QWidget,QMenu,QProgressBar,QVBoxLayout,QListWidget,QSizePolicy,QCheckBox,QGraphicsDropShadowEffect
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize,Signal,QThread
from QtExtraWidgets import QSearchBox,QCheckableComboBox,QTableTouchWidget,QInfoLabel,QFlowTouchWidget
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
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.maxCol=1
		self.setAttribute(Qt.WA_StyledBackground, True)
		lay=QVBoxLayout()
		lay.addSpacing(32)
		lay.setSpacing(24)
		self.search=self._defSearch()
		hlay=QHBoxLayout()
		wdg=QWidget()
		wdg.setLayout(hlay)
		#self.searchBox.setVisible(False)
		hlay.addWidget(self.search,Qt.AlignRight)
		lay.addWidget(wdg)
		if LAYOUT=="appsedu":
			#btnHome.setVisible(False)
			self.search.setVisible(True)
		self.table=self._defTable()
		#self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		if LAYOUT=="appsedu":
			tableCol=1
		else:
			tableCol=0
		lay.addWidget(self.table)
		
		#self.table.setCellWidget(0,0,self.flow)
		self.setLayout(lay)
		self.setObjectName("mp")
		self.setStyleSheet("""QWidget#mp{padding:0px;border:0px;margin:0px;background:#FFFFFF}""")

	def _defTable(self):
		#table=QTableTouchWidget()
		#table.setColumnCount(1)
		#table.setRowCount(1)
		#table.setAutoScroll(False)
		table=QFlowTouchWidget()
		table.flowLayout.setSpacing(10)
		table.leaveEvent=self.tableLeaveEvent
		table.setAttribute(Qt.WA_AcceptTouchEvents)
		#table.setColumnCount(self.maxCol)
		#table.setShowGrid(False)
		#table.verticalHeader().hide()
		#table.horizontalHeader().hide()
		#table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		if LAYOUT=="appsedu":
			table.setStyleSheet("""QFlowTouchWidget{border:0px; background:#FFFFFF;margin-left:100%;margin-right:1%;} QFlowTouchWidget::item{padding:2px}""")
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
		self.btnSearch.setIconSize(QSize(self.searchBox.sizeHint().height(),self.searchBox.sizeHint().height()))
		lay.addWidget(self.searchBox)#,Qt.AlignCenter|Qt.AlignCenter)
		lay.addWidget(self.btnSearch,Qt.Alignment(-1))
		wdg.setLayout(lay)
		wdg.setStyleSheet("""#wsearch{border:0px solid #FFFFFF;background:#002c4f;border-radius:20px}#search{color:#FFFFFF;background:#002c4f;border:0px solid} #bsearch{color:#FFFFFF;background:#002c4f;border:0px;}""")
		wdg.setMaximumWidth(450)
		return(wdg)
	#def _defSearch

	def _resetSearchBtnIcon(self):
		txt=self.searchBox.text()
		if txt==self.oldSearch:
			icn=QtGui.QIcon.fromTheme("dialog-cancel")
		else:
			icn=QtGui.QIcon.fromTheme("search")
	#def _resetSearchBtnIcon
