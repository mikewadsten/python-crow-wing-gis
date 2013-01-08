#!/usr/bin/env python

import csv
import glob
import os
import sys
import util
from util import cull_the_herd

if __name__ != "__main__":
    print "What are you doing. Stahp. Seriously."
    sys.exit(1)

# Keep going...

base = "."
if len(sys.argv) == 1:
    # Running as a script. Let's use the directory the script is in as source.
    base = os.path.dirname(__file__)
elif len(sys.argv) == 2:
    # Run from command line with directory?
    arg = sys.argv[1]
    if not os.path.isdir(arg):
        print arg, "is not a directory. Dumbass."
        sys.exit(1)
    base = arg

os.chdir(base)

counties = {
    1: "Crow Wing",
    2: "Cass",
    3: "Aitkin"
}

print "Welcome to Mike's GIS CSV gathering script from hell."
print
print "Which county are we dealing with here?"
for num in sorted(counties.keys()):
    print "{}: {}".format(num, counties[num])

county = raw_input("Choose the county, wisely: ")
print

try:
    county = int(county)
except ValueError:
    print "That's not a number..."
    sys.exit(1)

if county not in counties:
    print "Hey! Enter a valid county number next time."
    sys.exit(1)

formats = {
    1: "Out-*-*-*.csv",
    2: "Cass-*.csv",
    3: "Aitkin-*.csv"
}

print "Gathering CSV files for {} County.".format(counties[county])
files = glob.glob(formats[county])

if len(files) < 1:
    # Nothing to be seen.
    print "Couldn't find any of our csv files."
    print "Goodbye!"
    sys.exit(1)

else:
    print "Found", len(files), "CSV file(s):",
    print ', '.join(files)
    # Here the magic begins.
    all_addrs = []
    for fname in files:
        with open(fname, 'r') as f:
            reader = csv.DictReader(f)
            for item in reader:
                all_addrs.append(item)
    # Now all_addrs should contain all the names/addresses...
    print "Total of", len(all_addrs), "addresses gathered."
    print
    print "Time to cull the herd!"
    addrs = cull_the_herd(all_addrs, county)
    print "Count after culling:", len(addrs)

    print
    print "Where should we save these to?"
    dest = raw_input("Enter filename: ")

    with open(dest, 'w') as f:
       writer = csv.DictWriter(f, fieldnames=util.HERD_FIELDS[county],
                               delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)
       writer.writeheader()
       writer.writerows(addrs)
    print '*'*60
    print
    print "Master file saved at", dest
    print "Goodbye!"
