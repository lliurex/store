#/usr/bin/python3
import os
from PySide2.QtWidgets import QApplication

MINTIME=0.5
LAYOUT="appsedu"
APPNAME="LliureX Store"
COLOR_BACKGROUND_LIGHT="#FFFFFF"
COLOR_BACKGROUND_DARK="#002c4f"
COLOR_BACKGROUND_DARKEST="#2e746c"
COLOR_BORDER="#AAAAAA"
COLOR_BORDER_DARK="#EEEEEE"
COLOR_BORDER_DARKEST="#DDDDDD"
COLOR_FONT_LIGHT="#FFFFFF"
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")
CACHE=os.path.join(os.environ.get("HOME"),".cache","store")
MARGIN=8
ICON_SIZE=72
IMAGE_PREVIEW=256
RADIUS=6
RADIUS_HIGH=10
if QApplication.primaryScreen().size().width()<=1024:
	MARGIN=1
	IMAGE_PREVIEW=208
	#RADIUS=2
	#RADIUS_HIGH=4
elif QApplication.primaryScreen().size().width()<=1300:
	MARGIN=2
	IMAGE_PREVIEW=224
	RADIUS=4
	RADIUS_HIGH=6
elif QApplication.primaryScreen().size().width()<=1400:
	MARGIN=3
	IMAGE_PREVIEW=224
	RADIUS=5
	RADIUS_HIGH=8
