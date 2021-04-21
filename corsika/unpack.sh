#!/bin/bash

# Fix all the HORRIBLE zero padding of these file names
# Strip it all out. Pointless.

#Usage: ./unpack evt_num

evt_num="$1"

longext='.long'

for i in {1..3}
do
	cd "$evt_num"_run$i
	# Decompress
	for j in {1..14}
	do
		tar -xf event"$evt_num"_$j.tar.gz
	done
	# Correct file names
	for j in DAT0*
	do
		if [[ "$j" == *"$longext"* ]]
		then
			continue
		fi
		mv $j $j".part"
	done
	for j in *.long
	do
		mv $j "`echo $j | sed 's/DAT0*//'`"
	done

	for j in *.part
	do
		mv $j "`echo $j | sed 's/DAT0*//'`"
	done

	# Fix ridiculous perms problem with the irods transfer
	chmod 644 *.gz

	# Go back to root path
	cd ..
done

