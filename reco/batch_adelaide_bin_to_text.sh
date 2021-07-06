#!/bin/bash

name_pattern="TA_response*"

find . -maxdepth 3 -mindepth 1 -type f -name $name_pattern | while read dir
do
        ./sampleRead_exe $dir
done
