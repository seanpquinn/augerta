#!/bin/bash

for d in */
do
	touch ${d%/}"_adelaide_tasd_sig_mev.txt"
	cd $d
	for f in *.dat
	do
		grep -P "^.*(5040 |5048 ).*$" $f >> ../${d%/}"_adelaide_tasd_sig_mev.txt"
	done
	cd ..
done
