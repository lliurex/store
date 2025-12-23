#!/bin/bash

GUI_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p lliurex-store

xgettext $GUI_FILES -o lliurex-store/lliurex-store.pot

#Categories
CATs=$(qdbus --system --literal net.lliurex.rebost /net/lliurex/rebost net.lliurex.rebost.getFreedesktopCategories)
if [[ $? -eq 0 ]]
then
	CATs=${CATs//[/}
	CATs=${CATs//]/}
	CATs=${CATs//\{/}
	CATs=${CATs//\}/}
	CATs=${CATs//,/}
	CATs=${CATs//:/}
	CATs=${CATs//=/}
	SEEN=""
	#CAT=($CAT)
	echo "" >> lliurex-store/lliurex-store.pot
	IFS=$'\"'
	for i in ${CATs}
	do
		echo $i
		b=${i/ /}
		[ ${#i} -ne ${#b} ] && continue
		[ ${#i} -lt 2 ] && continue
		if [ x${i// /} != "x" ]
		then
			[ $(grep msgid.*\"$i\"$ lliurex-store/lliurex-store.pot >/dev/null 2>&1;echo $?) -eq 0 ] && continue
			echo "">> lliurex-store/lliurex-store.pot
			echo "#">> lliurex-store/lliurex-store.pot
			echo "msgid \"${i//_/}\""  >> lliurex-store/lliurex-store.pot
			echo "msgstr \"\"" >> lliurex-store/lliurex-store.pot
		fi
	done
fi

#Polkit

PK_FILES="../polkit/actions/*policy"
for pk_file in ${PK_FILES}
do
	msg=$(grep gettext-domain ${pk_file} | sed -e 's/.*\">//g;s/<\/.*//g')
	echo "msgid \"${msg//_/}\""  >> lliurex-store/lliurex-store.pot
	echo "msgstr \"\"" >> lliurex-store/lliurex-store.pot
	echo "#">> lliurex-store/lliurex-store.pot
done
	
