Sean Quinn
Aug 25 2015

This program reads a T3.out file and returns the corresponding
event information in individual folders. Data include PMT traces, histograms,
calibration info, etc.


# 0. DEPENDENCIES/REQUIRED SOFTWARE

The code is written using a combination of C and Python 3. Some third party
Python packages (matplotlib, numpy) are also used. In order to run 
the software you must have the following items installed:

-Python 3.2+
-matplotlib 1.3+
-numpy 1.5+
-gcc (or favorite C compiler)

# 1. INPUT DATA
	
The program will use the "T3.out" data file. This is a text file with
hex values that contain the station data. T3.out must be in the same
directory as the programs.

# 2. INSTALLATION

The only module that needs to be compiled is "x2.c" It's a simple program and uses
only standard libraries. To compile please execute

```
gcc -o x2 x2.c
```

# 3. EXECUTING PROGRAM

The alias for the Python 3 interpreter on my Debian system is python3. To run the program
type in the terminal

```
python3 unhex.py
```

using the correct alias on your machine.


# 4. OUTPUT DATA

When run, the program will generate a folder for each T3 event with various contents.
Folders are named using EVTID_GPSSECOND_GPSNANOSECOND.
It will save text files with FADC trace, histogram data, and calibration info. It will
also save PDF plots of charge, peak and shape histograms. A binary decompressed data
file is also stored. CAUTION: for a large T3 file it will create potentially thousands of
new directories. Currently it doesn't store events by month or date.

5.		ISSUES

-The program will encounter a run time error if the T3.out file is not perfectly formatted. So if ends halfway through an event it will crash

-The axes on the plots are not labeled. The units need to be researched. Ricardo or other CDAS expert probably knows what these are.
