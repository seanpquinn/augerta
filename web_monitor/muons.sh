#!/bin/bash
d=$1
./anamu -i $d -o /dev/stdout | tr -s ' '| cut -d ' ' -f 2 > muon_tmp.txt
truncate -s -"$(tail -n1 muon_tmp.txt | wc -c)" muon_tmp.txt
truncate -s -"$(tail -n1 muon_tmp.txt | wc -c)" muon_tmp.txt
truncate -s -"$(tail -n1 muon_tmp.txt | wc -c)" muon_tmp.txt
