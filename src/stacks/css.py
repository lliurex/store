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
					border:0px;
					margin:0px;
					color:unset;
			}"""%(COLOR_FONT_LIGHT)
	css=css+detail
	frame="""QWidget#frame{
					margin:0px;
					padding:0px;
					border:1px solid %s;
				}"""%(COLOR_BORDER_DARKEST)
	css=css+frame
	resources="""QWidget#resources{
					margin-top:%spx;
					border-right:%spx solid;
					border-radius:1px;
					border-right-color:%s;
				}"""%(MARGIN,int(MARGIN)/2,COLOR_BORDER_DARK)
	css=css+resources
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
	btnInstall="""QLabel#btnInstall{
					margin-bottom:%spx
				}"""%(MARGIN*2)
	css=css+btnInstall
	lstInfo="""#lstInfo{
					padding:%spx;
					color:#000000;
					margin:1px;
					border:1px solid;
					border-color:%s;
					border-radius:%spx;}
					QComboBox#lstInfo::drop-down{ subcontrol-origin: padding;
					subcontrol-position: top right;
					border-top-right-radius: %spx; /* same radius as the QComboBox */
					border-bottom-right-radius: %spx;
				}
				QComboBox#lstInfo::down-arrow {
					image: url("%s/drop-down16x16.png");
					right:%spx;
					border-left:1px solid %s;
					padding:%spx;
					margin-left:%spx;
				}
				QComboBox#lstInfo::down-arrow:on { /* shift the arrow when popup is open */
					top: 1px;
					right: %spx;
				}
				"""%(MARGIN,COLOR_BORDER,RADIUS,RADIUS,RADIUS,RSRC,int(MARGIN)*2,COLOR_BORDER,MARGIN,int(MARGIN)*2,int(MARGIN)*1.9)
	css=css+lstInfo
	screenshot="""#screenshot{
					margin:0px;
					padding:0px;
				}"""
	css=css+screenshot
	lblTags="""#lblTags{
					margin:0px;
					padding:0px;
					border:0px;
					bottom:0px
				}"""
	css=css+lblTags
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
				}"""%(COLOR_BACKGROUND_LIGHT,int(MARGIN*2),MARGIN,int(MARGIN)/4)
	css=css+qflow
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
				}"""%(COLOR_BORDER,COLOR_BACKGROUND_DARK,int(RADIUS)*3,COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,int(MARGIN)*1.5,COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,int(MARGIN))
	css=css+search
	flyIcon="""#flyIcon{background:transparent;}"""
	css=css+flyIcon
	iconUri="""#iconUri{
					margin-top: %spx;
					margin-right:%spx;
					margin-bottom:%spx;
				}"""%(int(MARGIN)*1.5,int(MARGIN)*1.5,int(MARGIN)*1.5)
	css=css+iconUri

	categoriesBar="""#categoriesBar{border:0px;
					margin-left:%spx;
					margin-right:%spx;
					margin-bottom:%spx;
				}"""%(int(MARGIN*2),MARGIN,int(MARGIN)/4)
	css=css+categoriesBar

	categoryTag="""#categoryTag{text-decoration:none;background:%s;color:%s;padding:1px;padding-bottom:3px;border-radius:10;}"""%(COLOR_BACKGROUND_DARK,COLOR_FONT_LIGHT)
	css=css+categoryTag

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
				}"""%(COLOR_FONT_LIGHT,COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,RADIUS,int(MARGIN)*4,int(MARGIN)*4,MARGIN,MARGIN,int(MARGIN)*4,COLOR_FONT_LIGHT)
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
					background:%s;
					border-color:%s;
					border-radius:%spx;
					padding-bottom:%spx;
					padding-top:%spx;
				}
				"""%(int(MARGIN)/2,COLOR_BORDER,int(MARGIN)*1.5,int(MARGIN)*3,COLOR_BACKGROUND_DARK,COLOR_BACKGROUND_LIGHT,COLOR_BORDER,RADIUS,int(MARGIN)/2,int(MARGIN)/2)
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
	css=css+lblInfo
	return(css)
#def prgBar
