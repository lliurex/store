#!/usr/bin/env python3
import sys
import os
import json
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
from PySide2 import QtGui
from QtExtraWidgets import QStackedWindow
from initSplash import QSplashWidget

def closeEvent(*args):
	portrait=mw.widget(0)
	mw.hide()
	portrait._closeEvent()

if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)

app=QApplication(["LliureX Store"])
icn=QtGui.QIcon.fromTheme("llxstore")
banner=os.path.join(abspath,"rsrc","bbanner.svg")
pxm=QtGui.QPixmap(banner)
spl=QSplashWidget(icn,pxm)
scr=QtGui.QGuiApplication.primaryScreen()
geo=scr.availableGeometry()
spl.move((geo.width()-spl.width())//2,(geo.height()-spl.height())//2)
spl.show()
app.processEvents()
mw=QStackedWindow()
app.processEvents()
mw.addStacksFromFolder(os.path.join(abspath,"stacks"))
app.processEvents()

if len(sys.argv)>1:
	if ("://") in sys.argv[1]:
		sys.argv[1]=sys.argv[1].removesuffix("-lliurex")
		wdg=mw.getCurrentStack()
		wdg.setParms(sys.argv[1])
mw.closeEvent=closeEvent
mw.disableNavBar(True)
mw.setIcon(icn)
#Remove banner
banner=mw.layout().itemAtPosition(0,0)
app.processEvents()
mw.layout().removeItem(banner)
mw.setObjectName("MAIN")
mw.layout().setContentsMargins(0,0,0,0)
mw.setStyleSheet("""QWidget#MAIN{background:#002c4f; color:#FFFFFF;margin:0px;padding:0px;border:0px;}""")
#Get screen size available for us
(w,h) = app.primaryScreen().size().toTuple()
mw.setMinimumWidth(int(w*0.9))
mw.setMinimumHeight(int(h*0.9))
mw.show()
spl.close()
app.exec_()
