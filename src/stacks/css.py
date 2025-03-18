#!/usr/bin/python3
import os
COLOR_BACKGROUND_LIGHT="#FFFFFF"
COLOR_BORDER="#AAAAAA"
COLOR_BORDER_DARK="#EEEEEE"
COLOR_BORDER_DARKEST="#DDDDDD"
COLOR_FONT="#FFFFFF"
MARGIN="8"
RADIUS="6"
RSRC=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"rsrc")

def detailPanel():
	css=""
	detail="""QWidget{
					padding:0px;
				border:0px;
				margin:0px;
				background:%s;
				color:unset;
			}"""%(COLOR_FONT)
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
	css=css+"\n"+qflow
	search="""#wsearch{
					border:0px solid #FFFFFF;
					background:#002c4f;
					border-radius:20px;
				}
				#search{
					color:#FFFFFF;
					background:#002c4f;
					border:0px solid;
					margin-left:12px;
				} 
				#bsearch{
					color:#FFFFFF;
					background:#002c4f;
					border:0px;
					margin-right:12px;
				}"""
	css=css+search
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
					margin-top:24px;
					margin-bottom:12px;
					margin-left:20%;
					margin-right:10%
			}"""
	css=css+banner
	cmbCategories="""#cmbCategories{
					color:#FFFFFF;
					background:#002c4f;
					border:1px;
					border-color:#FFFFFF;
					border-radius:5px;
					padding-left:30px;
					padding-right:30px;
					padding-bottom:5px;
					padding-top:5px;
					margin-top:32;
					} 
				#cmbCategories::item {
					background-color: transparent;color:#FFFFFF
				}"""
	css=css+cmbCategories
	certified="""#certified{
					color:#FFFFFF;
					background:#2e746c;
					border-radius:5px;
					padding:3px;
				}"""
	css=css+certified
	btnBar="""#btnBar{
					border-top:3px solid #AAAAAA;
					padding-top:12px;
				} 
				#btnHome{
					margin-top:24px;
					color:#002c4f;
					background:#FFFFFF;
					border:1px;
					border-color:#FFFFFF;
					border-radius:5px;
					padding-bottom:5px;
					padding-top:5px;
				}"""
	css=css+btnBar
	upgrades="""#upgrades{
					color:#002c4f;
					background:#FFFFFF;
					border:1px;
					border-color:#FFFFFF;
					border-radius:5px;
					padding:5px;
				}"""
	css=css+upgrades
	return(css)
