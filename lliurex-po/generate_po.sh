#!/bin/bash

GUI_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p appsedu

xgettext $GUI_FILES -o appsedu/appsedu.pot


