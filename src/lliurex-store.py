#!/usr/bin/env python3
import sys
import os
import json
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
from PySide2 import QtGui
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

def closeEvent(*args):
	portrait=mw.widget(0)
	mw.hide()
	portrait._closeEvent()

app=QApplication(["LliureX Store"])
mw=QStackedWindow()
mw.closeEvent=closeEvent
icn=QtGui.QIcon.fromTheme("llxstore")
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
#Get screen size available for us
(w,h) = app.primaryScreen().size().toTuple()
mw.setMinimumWidth(int(w*0.9))
mw.setMinimumHeight(int(h*0.8))
mw.show()
if len(sys.argv)>1:
	if ("://") in sys.argv[1] or os.path.isfile(sys.argv[1]):
		wdg=mw.getCurrentStack()
		wdg.setParms(sys.argv[1])
app.exec()
