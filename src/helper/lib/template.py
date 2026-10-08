#!/usr/bin/python3

script='''#!/bin/bash\n
function getStatus()\n\t\t{
\t\t{@STATUSCMD}
\t\tif [ \"$TEST\" == 'installed' ];then
\t\t\tINSTALLED=0
\t\telse
\t\t\tINSTALLED=1
\t\tfi
}

ACTION=\"$1\"
ERR=0
case $ACTION in
\tremove)
\t\t{@REMOVECMD}
\t\t;;
\tinstallPackage)
\t\t{@INSTALLCMD}
\t\t;;
\ttestInstall)	
\t\techo \"0\"
\t\t;;
\tgetInfo)
\t\techo \"{@DESCRIPTION}\"
\t\t;;
\tgetStatus)
\t\tgetStatus
\t\techo $INSTALLED
\t\t;;
\tdownload)
\t\techo \"Installing...\"
\t\t;;
esac
[ $ERR -gt 0 ] && exit 1 || exit 0'''

epi='''{
\t\"type\":\"file\",
\t\"pkg_list\":[{\"name\":\"{@APPNAME}\",\"custom_name\":\"{@DESCNAME}\",\"custom_icon\":\"{@ICON}\"}],
\t\"script\":{\"name\":\"{@SCRIPT}\",\"remove\":true,\"download\":true,\"getStatus\":true,\"getInfo\":true},
\t\"custom_icon_path\":\"{@ICONPATH}\",
\t\"check_zomando_state\":false
}'''


