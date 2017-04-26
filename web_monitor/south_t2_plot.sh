#!/bin/sh

tail -n 14 T2south_record.txt > recent_t2south.txt
python3 make_14day_south_plot.py
