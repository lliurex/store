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
<<<<<<<< HEAD:src/store.py
gettext.textdomain('store')
========
gettext.textdomain('lliurex-store')
>>>>>>>> devel:src/lliurex-store.py
_ = gettext.gettext

def closeEvent(*args):
	portrait=mw.widget(0)
	mw.hide()
	portrait._closeEvent()

app=QApplication(["LliureX Store"])
mw=QStackedWindow()
<<<<<<<< HEAD:src/store.py
icn=QtGui.QIcon.fromTheme("store")
========
mw.closeEvent=closeEvent
icn=QtGui.QIcon.fromTheme("llxstore")
>>>>>>>> devel:src/lliurex-store.py
mw.disableNavBar(True)
mw.setIcon(icn)
#Remove banner
banner=mw.layout().itemAtPosition(0,0)
mw.layout().removeItem(banner)

if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
mw.addStacksFromFolder(os.path.join(abspath,"stacks"))
mw.setObjectName("MAIN")
mw.layout().setContentsMargins(0,0,0,0)
mw.setStyleSheet("""QWidget#MAIN{background:#002c4f; color:#FFFFFF;margin:0px;padding:0px;border:0px;}""")
mw.show()
mw.setMinimumWidth(1048)
mw.setMinimumHeight(600)
if len(sys.argv)>1:
	if ("://") in sys.argv[1] or os.path.isfile(sys.argv[1]):
<<<<<<<< HEAD:src/store.py
		mw.setCurrentStack(3,parms=sys.argv[1])
app.exec()
========
		wdg=mw.getCurrentStack()
		wdg.setParms(sys.argv[1])
app.exec_()
>>>>>>>> devel:src/lliurex-store.py
