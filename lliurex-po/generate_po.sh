#!/bin/bash

GUI_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p appsedu

xgettext $GUI_FILES -o appsedu/appsedu.pot

#Categories
CAT=$(qdbus net.lliurex.rebost /net/lliurex/rebost net.lliurex.rebost.getCategories)
if [[ $? -eq 0 ]]
then
	CAT=${CAT/[/}
	CAT=${CAT/]/}
	CAT=${CAT//,/}
	#CAT=($CAT)
	echo "" >> appsedu/appsedu.pot
	IFS=$'\"'
	for i in ${CAT}
	do
		if [[ x${i// /} != "x" ]]
		then
			echo "msgid \"${i//_/}\"" >> appsedu/appsedu.pot
			echo "msgstr \"\"" >> appsedu/appsedu.pot
			echo "" >> appsedu/appsedu.pot
		fi
	done
fi


