#!/usr/bin/env python3
import sys
import subprocess
import os,shutil
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6 import QtGui
from QtExtraWidgets import QStackedWindow
import gettext
import time
gettext.textdomain('store')
_ = gettext.gettext

app=QApplication(["LliureX Store"])
mw=QStackedWindow()
icn=QtGui.QIcon.fromTheme("store")
mw.disableNavBar(True)
mw.setIcon(icn)
#Remove banner
i=mw.layout().itemAtPosition(0,0)
mw.layout().removeItem(i)

if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
mw.addStacksFromFolder(os.path.join(abspath,"stacks"))
mw.setObjectName("MAIN")
mw.layout().setContentsMargins(0,0,0,0)
mw.setStyleSheet("""QWidget#MAIN{background:#002c4f; color:#FFFFFF;margin:0px;padding:0px;border:0px;}""")
mw.show()
mw.setMinimumWidth(900)
mw.setMinimumHeight(600)
if len(sys.argv)>1:
	if ("://") in sys.argv[1] or os.path.isfile(sys.argv[1]):
		mw.setCurrentStack(3,parms=sys.argv[1])
app.exec()
