#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6 import QtGui
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('lliurex-store')
_ = gettext.gettext

def closeEvent(*args):
	portrait=mw.widget(0)
	mw.hide()
	#portrait._closeEvent()

if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)

app=QApplication(["Botiga"])
mw=QStackedWindow()
mw.addStacksFromFolder(os.path.join(abspath,"bstacks"))
if len(sys.argv)>1:
	if ("://") in sys.argv[1]:
		sys.argv[1]=sys.argv[1].removesuffix("-lliurex")
		wdg=mw.getCurrentStack()
		wdg.setParms(sys.argv[1])
mw.closeEvent=closeEvent
icn=QtGui.QIcon.fromTheme("llxstore")
mw.disableNavBar(True)
mw.setIcon(icn)
mw.setBanner("/usr/share/botiga/rsrc/bbanner.svg")
#Get screen size available for us
(w,h) = app.primaryScreen().size().toTuple()
mw.setMinimumWidth(int(w*0.5))
mw.setMinimumHeight(int(h*0.7))
mw.lblBanner.setPixmap(mw.lblBanner.pixmap().scaled(w*0.15,h*0.07))
mw.lblBanner.setStyleSheet("""padding:6px""")
mw.show()
app.exec()
