#!/usr/bin/python3
import os
COLOR_BORDER="#AAAAAA"
COLOR_BORDER_DARK="#EEEEEE"
COLOR_BORDER_DARKEST="#DDDDDD"
COLOR_FONT="#FFFFFF"
MARGIN="8"
RADIUS="6"
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")

def detailPanel():
	css=""
	detail="""QWidget{padding:0px;border:0px;margin:0px;background:%s;color:unset;}"""%(COLOR_FONT)
	css=css+detail
	frame="""QWidget#frame{margin:0px;padding:0px;border:1px solid %s;}"""%(COLOR_BORDER_DARKEST)
	css=css+frame
	resources="""QWidget#resources{margin-top:%spx;border-right:%spx solid;border-radius:1px;border-right-color:%s;}"""%(MARGIN,int(MARGIN)/2,COLOR_BORDER_DARK)
	css=css+resources
	lblIcon="""#lblIcon{margin-left:%spx;margin-top:0}"""%(int(MARGIN)*2)
	css=css+lblIcon
	lblName="""#lblName{margin-right:%spx;margin-top:0}"""%(int(MARGIN)*3)
	css=css+lblName
	lblSummary="""#lblSummary{margin-right:%spx;margin-top:0}"""%(int(MARGIN)*3)
	css=css+lblSummary
	btnInstall="""QLabel#btnInstall{margin-bottom:%spx}"""%(MARGIN*2)
	css=css+btnInstall
	lstInfo="""#lstInfo{padding:%spx;margin:1px;border:1px solid;border-color:%s;border-radius:%spx;}
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
	screenshot="""#screenshot{margin:0px;padding:0px;}"""
	css=css+screenshot
	lblTags="""#lblTags{margin:0px;padding:0px;border:0px;bottom:0px}"""
	css=css+lblTags
	return(css)
