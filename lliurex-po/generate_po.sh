#!/bin/bash

GUI_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p store

xgettext $GUI_FILES -o store/store.pot

#Categories
CAT=$(qdbus net.lliurex.rebost /net/lliurex/rebost net.lliurex.rebost.getCategories)
if [[ $? -eq 0 ]]
then
	CAT=${CAT/[/}
	CAT=${CAT/]/}
	CAT=${CAT//,/}
	#CAT=($CAT)
	echo "" >> store/store.pot
	IFS=$'\"'
	for i in ${CAT}
	do
		if [[ x${i// /} != "x" ]]
		then
			echo "msgid \"${i//_/}\"" >> store/store.pot
			echo "msgstr \"\"" >> store/store.pot
			echo "" >> store/store.pot
		fi
	done
fi


