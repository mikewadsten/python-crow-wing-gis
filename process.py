#!/usr/bin/env python

# Process raw downloaded CSV for Cass or Aitkin and trim it down to
# the criteria we're going on.

import csv
import glob
import os
import sys

if __name__ != "__main__":
    print "What are you doing. Stahp."
    sys.exit(1)

def int_or_zero(val):
    if not val:
        return 0
    return int(val)

# cd to current directory because things.
os.chdir(os.path.dirname(__file__))

formats = { 1: "Cass *.csv", 2: "Aitkin *.csv" }
valkeys = { 1: "Est Total Val", 2: "Est. Total Value" }
clskeys = { 1: "Assmt Class1", 2: "Class 1 Desc." }

print "Welcome to Mike's raw GIS CSV processing script."
print
print "Which county (1 = Cass, 2 = Aitkin) are we dealing with?"
county = raw_input("Enter 1 or 2: ")
try:
    county = int(county)
    if county not in (1, 2):
        raise ValueError, "Lol"
except ValueError:
    print "That's an invalid county number."
    sys.exit(1)

fmt = formats[county]
files = glob.glob(fmt)

if len(files) < 1:
    print "Couldn't seem to find csv for that county. Goodbye!"
    sys.exit(0)

print "Found", len(files), "files:"

for fn in files:
    curr = []
    sys.stdout.write(fn + ": Reading... ")
    sys.stdout.flush()
    with open(fn, 'r') as f:
        reader = csv.DictReader(f)
        for item in reader:
            curr.append(item)

    sys.stdout.write("Processing... ")
    sys.stdout.flush()
    # list-comprehend the shit out of these things
    curr = [r for r in curr if int_or_zero(r[ valkeys[county] ]) > 200000 and
            (r[ clskeys[county] ].startswith("Residential 1") or
             r[ clskeys[county] ].startswith("Non-Comm"))]

    sys.stdout.write("Writing... ")
    sys.stdout.flush()
    with open(fn, 'w') as f:
        # Makes the assumption 'curr' contains at least 1 item.
        writer = csv.DictWriter(f, fieldnames=curr[0].keys(),
                                delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(curr)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()

