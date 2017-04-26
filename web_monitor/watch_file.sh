#!/bin/sh

# get the current path
CURPATH=`pwd`

MONITOR=/home/augta/data/south/t2

inotifywait -mr --timefmt '%d/%m/%y %H:%M' --format '%T %w %f' \
-e close_write $MONITOR | while read date time dir file; do

	FILECHANGE=${dir}${file}
	# convert absolute path to relative
	#echo "At ${time} on ${date}, file $FILECHANGE"
	cp $FILECHANGE .
	FILECHANGEREL=${FILECHANGE##*/}
	python3 get_southt2_daily.py $FILECHANGEREL
	rm $FILECHANGEREL
	./south_t2_plot.sh 
done
