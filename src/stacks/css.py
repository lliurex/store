#!/usr/bin/python3
import os
from constants import *

def detailPanel():
	css=""
	detail="""QWidget{
					background:%s;
			}
			QWidget#detailPanel{
					padding:0px;
					margin:0px;
					color:unset;
			}"""%(COLOR_FONT_LIGHT)
	css=css+detail
	frame="""QWidget#frame{
					border:1px solid %s;
					margin:0px;
					margin-left:%spx;
					padding:0px;
				}"""%(COLOR_BORDER_DARKEST,int(MARGIN)*2)
	css=css+frame
	resources="""QWidget#resources{
					margin-top:%spx;
				}"""%(MARGIN)
	css=css+resources

	btnBack="""#btnBack{
						margin-right:%spx;
						margin-bottom:0px;
				}
				QPushButton#btnBack:pressed
				{
					border:2px inset %s;
				}
				"""%(int(MARGIN)*0,COLOR_BACKGROUND_DARK)
	css=css+btnBack

	lblIcon="""#lblIcon{
					margin-left:%spx;
					margin-top:0;
				}"""%(int(MARGIN)*2)
	css=css+lblIcon
	lblName="""#lblName{
					margin-right:%spx;
					margin-top:0
				}"""%(int(MARGIN)*3)
	css=css+lblName
	lblSummary="""#lblSummary{
					margin-right:%spx;
					margin-top:0;
				}"""%(int(MARGIN)*3)
	css=css+lblSummary
	btnInstall="""QPushButton#btnInstall{
					color:%s;
					background: qlineargradient(x1:0, y1:0, x2:0, y2:4, stop:0 %s, stop:1 %s);
					border:1px solid %s;
					border-radius:%spx;
					padding-bottom:%spx;
					padding-top:%spx;
				}
				QPushButton#btnInstall:pressed
				{
					border:2px inset %s;
				}

				"""%(COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,COLOR_BACKGROUND_DARKEST,COLOR_BORDER,RADIUS,int(MARGIN)/2,int(MARGIN)/2,COLOR_BACKGROUND_DARK)
	css=css+btnInstall

	boxBundles="""#boxBundles{
					border:0px;
					margin:0px;
					padding:0px;
					}"""
	css=css+boxBundles

	cmbBundles="""#cmbBundles{
					padding:%spx;
					color:#000000;
					margin:1px;
					border:1px solid;
					border-color:%s;
					border-radius:%spx;
					}
				QComboBox#cmbBundles::drop-down{ subcontrol-origin: padding;
					subcontrol-position: top right;
					border-top-right-radius: %spx; /* same radius as the QComboBox */
					border-bottom-right-radius: %spx;
				}
				QComboBox#cmbBundles {
					background: qlineargradient(x1:0, y1:0, x2:0, y2:3, stop:0 %s, stop:1 %s);
				}
				QComboBox#cmbBundles::down-arrow {
					image: url("%s/drop-down16x16.png");
					right:%spx;
					border-left:1px solid %s;
					padding:%spx;
					margin-left:%spx;
				}
				QComboBox#cmbBundles::down-arrow:on { /* shift the arrow when popup is open */
					top: 1px;
					right: %spx;
				}
				"""%(MARGIN,COLOR_BORDER,RADIUS,RADIUS,RADIUS,COLOR_BACKGROUND_LIGHT,COLOR_BACKGROUND_DARKEST,RSRC,int(MARGIN)*2,COLOR_BORDER,MARGIN,int(MARGIN)*2,int(MARGIN)*1.9)
	css=css+cmbBundles
	screenshot="""#screenshot{
					margin:0px;
					padding:0px;
				}"""
	css=css+screenshot

	lblTags="""#lblTags{
					border:0px;
					margin-top:%spx;
					margin-left:%spx;
				}"""%(MARGIN,MARGIN)

	css=css+lblTags

	lstLinks="""#lstLinks{
					border:0px;
					margin-left:%spx;
				}"""%(MARGIN)

	css=css+lstLinks

	lblDesc="""#lblDesc{
					border:0px;
					border-left:%spx solid;
					border-radius:1px;
					border-left-color:%s;
				}
				"""%(int(MARGIN)/2,COLOR_BORDER_DARK)
	css=css+lblDesc

	return(css)
#def detailPanel

def tablePanel():
	css=""
	mp="""#mp{
					padding:0px;
					border:0px;
					margin:0px;
					background:%s;
				}"""%(COLOR_BACKGROUND_LIGHT)
	css=css+mp
	qflow="""#qFlow{
					border:0px; 
					background:%s;
					margin-left:%spx;
					margin-right:%spx;
				} 
				#qFlow::item{
					padding:%spx;
				}
				"""%(COLOR_BACKGROUND_LIGHT,int(MARGIN*2),MARGIN,int(MARGIN)/4)
	css=css+qflow
	flyIcon="""#flyIcon{background:transparent;}"""
	css=css+flyIcon
	iconUri="""#iconUri{
					margin-top: %spx;
					margin-right:%spx;
					margin-bottom:%spx;
				}"""%(int(MARGIN)*1.5,int(MARGIN)*1.5,int(MARGIN)*1.5)
	css=css+iconUri
	iconPrg="""#iconPrg{
					margin-top: %spx;
					margin-right:%spx;
					margin-bottom:%spx;
					margin-left:%spx;
				}"""%(int(MARGIN)/2,int(MARGIN)/2,int(MARGIN)/2,int(MARGIN)/2)
	css=css+iconPrg

	return(css)
#def tablePanel

def portrait():
	css=""
	port="""#portrait{
					padding:0px;
					border:0px;
					margin:0px;
			}"""
	css=css+port
	search="""#wsearch{
					border:0px solid %s;
					background:%s;
					border-radius:%spx;
				}
				#search{
					color:%s;
					background:%s;
					border:0px solid;
					margin-left:%spx;
				} 
				#bsearch{
					color:%s;
					background:%s;
					border:0px;
					margin-right:%spx;
				}
				#wdgsearch{
					background:%s;
				}"""%(COLOR_BORDER,COLOR_BACKGROUND_DARK,int(RADIUS)*3,COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,int(MARGIN)*1.5,COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,int(MARGIN),COLOR_BACKGROUND_LIGHT)
	css=css+search

	categoriesBar="""#categoriesBar{border:0px;
					margin:0px;
					background:%s;
					padding-left:%spx;
				}
				"""%(COLOR_BACKGROUND_LIGHT,int(MARGIN)*12)
	css=css+categoriesBar

	categoryTag="""#categoryTag{
					background:%s;
					color:%s;
					padding:1px;
					padding-bottom:3px;
					border-radius:%spx;
					}"""%(COLOR_BACKGROUND_DARK,COLOR_FONT_LIGHT,RADIUS_HIGH)
	css=css+categoryTag

	error="""#errorMsg{
			background: %s;
			}"""%(COLOR_BACKGROUND_LIGHT)
	css=css+error
	banner="""#banner{
					margin-top:%spx;
					margin-bottom:%spx;
					margin-left:%spx;
					margin-right:%spx;
			}"""%(int(MARGIN)*3,int(MARGIN)*1,int(MARGIN)*3,int(MARGIN)*2)
	css=css+banner
	lstCategories="""#lstCategories{
					color:%s;
					background:%s;
					border:1px;
					border-color:%s;
					border-radius:%spx;
					padding-left:%spx;
					padding-right:%spx;
					padding-bottom:%spx;
					padding-top:%spx;
					margin-top:%spx;
					} 
				#lstCategories::item {
					background-color: transparent;
					color:%s;
				}
				#lstCategories::item:hover {
					background-color: %s;
				}"""%(COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,RADIUS,int(MARGIN)*4,int(MARGIN)*4,MARGIN,MARGIN,int(MARGIN)*4,COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARKEST)
	css=css+lstCategories
	certified="""#certified{
					color:%s;
					border:0px solid %s;
					border-radius:%spx;
				}
				#certifiedChk
				{
					padding:%spx;
					margin:0px;
					border:0px;
				}
				"""%(COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARKEST,RADIUS,int(MARGIN)/2)
	css=css+certified
	btnBar="""#btnBar{
					border-top:%spx solid %s;
					padding-top:%spx;
				} 
				#btnHome{
					margin-top:%spx;
					color:%s;
					background: qlineargradient(x1:0, y1:0, x2:0, y2:2, stop:0 %s, stop:1 %s);
					border-color:%s;
					border-radius:%spx;
					padding-bottom:%spx;
					padding-top:%spx;
				}
				QPushButton#btnHome:pressed
				{
					border:2px inset %s;
				}
				"""%(int(MARGIN)/2,COLOR_BORDER,int(MARGIN)*1.5,int(MARGIN)*3,COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,COLOR_BACKGROUND_DARKEST,COLOR_BORDER,RADIUS,int(MARGIN)/2,int(MARGIN)/2,COLOR_BACKGROUND_DARK)
	css=css+btnBar
	upgrades="""#upgrades{
					color:%s;
					background:%s;
					border:1px;
					border-color:%s;
					border-radius:%spx;
					padding:%spx;
				}"""%(COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,COLOR_BORDER,RADIUS,MARGIN)
	css=css+upgrades
	working="""#working{
					color:%s;
					font-size:20px;
					background:%s;
					border:0px solid;
					border-top:0px;
					border-color:%s;
					border-bottom-left-radius:%spx;
				}"""%(COLOR_FONT_LIGHT,COLOR_BACKGROUND_LIGHT,COLOR_BORDER,RADIUS)
	css=css+working
	return(css)
#def portrait

def prgBar():
	css=""
	prg="""#prgBar{
					background:%s;
					padding:0px;
					border:0px;
					margin:0px;
			}"""%(COLOR_BACKGROUND_DARK)
	css=css+prg
	lblInfo="""
				#lblInfo{
					padding:0px;
					border:0px;
					margin:0px;
					font-size:24px;
					color:%s;
			}"""%(COLOR_FONT_LIGHT)
	return(css)
#def prgBar
