#!/bin/bash

GUI_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p lliurex-store

xgettext $GUI_FILES -o lliurex-store/lliurex-store.pot

#Categories
CATs=$(qdbus6 net.lliurex.rebost /net/lliurex/rebost net.lliurex.rebost.getFreedesktopCategories)
if [[ $? -eq 0 ]]
then
	CATs=${CATs//[/}
	CATs=${CATs//]/}
	CATs=${CATs//\{/}
	CATs=${CATs//\}/}
	CATs=${CATs//,/}
	#CAT=($CAT)
	echo "" >> lliurex-store/lliurex-store.pot
	IFS=$'\"'
	for i in ${CATs}
	do
		if [[ x${i// /} != "x" ]]
		then
			echo "msgid \"${i//_/}\""  >> lliurex-store/lliurex-store.pot
			echo "msgstr \"\"" >> lliurex-store/lliurex-store.pot
			echo "#">> lliurex-store/lliurex-store.pot
		fi
	done
fi


