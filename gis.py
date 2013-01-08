#!/usr/bin/env python

import csv  # to handle csv crap
import json  # to parse
import requests
import sys

# This is where the fun begins.
BASE_URL = ("http://gis.co.crow-wing.mn.us/ArcGIS/rest/services/CROWWING"
            "SUBSCRIPTION/MapServer/0/query")
WHERE_LKNAME_FMT = "(UPPER(LKLAKD) = '{}') AND (ESTTOTVAL >= {})"
WHERE_LKNUM_FMT = "(APLAKN = {}) AND (ESTTOTVAL >= {})"

where = ("AND ((UPPER(TPCLS1) LIKE 'RESIDENTIAL 1%') OR "
         "(UPPER(TPCLS1) LIKE 'NON-COMM SEASONAL%'))")
WHERE_LKNAME_FMT += where
WHERE_LKNUM_FMT += where

if __name__ != "__main__":
    print "What are you doing. Stahp."
    sys.exit(1)

# __name__ == __main__, so we're running gis.py as a script, so we continue.

def get_ids(lake_name='', lake_num=0, min_val=0):
    """Given lake name (or lake number eventually) and minimum est. total value,
    get the list of matching object ids."""
    params = {'returnIdsOnly': True, 'f': 'json'}

    try:
        min_val = int(min_val)
    except ValueError:
        print "Invalid minimum value:", min_val
        sys.exit(1)

    if lake_name:
        params['where'] = WHERE_LKNAME_FMT.format(lake_name, min_val)
    elif lake_num:
        try:
            lake_num = int(lake_num)
        except ValueError:
            print "Invalid lake number value:", lake_num
            sys.exit(1)
        params['where'] = WHERE_LKNUM_FMT.format(lake_num, min_val)
    else:
        print "Must specify either a lake name or lake number, dumbass."
        sys.exit(1)

    sys.stdout.write("Making request to GIS server...")
    sys.stdout.flush()  # push text out
    resp = requests.get(BASE_URL, params=params)
    #print resp.url
    sys.stdout.write(" Done.\n")
    return json.loads(resp.text).get('objectIds', [])  # probably unreliable...

def get_data(ids=[]):
    """Given object IDs, get owner name and addresses."""
    params = {'f': 'json',
              'outFields': 'OWNAME,OWADR1,OWADR2,OWADR3,OWADR4'}
    count = len(ids)
    recvd = 0
    features = []
    ids = map(str, ids)  # ids are initially integers.
    chunksz = 100
    while recvd < count:
        _ids = ids[:chunksz]
        ids = ids[chunksz:]
        params['objectIds'] = ','.join(_ids)
        out = "Request for properties {} to {}...".format(
                            recvd + 1, recvd + len(_ids))
        sys.stdout.write(out)
        sys.stdout.flush()  # push text out
        resp = requests.get(BASE_URL, params=params)
        sys.stdout.write(" Done.\n")
        if resp.status_code != 200:
            print "Request came back with status", resp.status_code
        else:
            respdict = json.loads(resp.text)
            _features = respdict.get('features', [])
            # We don't care about the property geometry.
            _features = [f['attributes'] for f in _features]
            recvd += len(_features)
            features += _features
    return features

def cull_the_herd(features=[]):
    """Remove duplicate names/addresses."""
    def make_hasher(t):
        return '|'.join([ t['OWNAME'], t['OWADR1'], t['OWADR2'],
                          t['OWADR3'], t['OWADR4'] ])

    hash_to_dicts = {}
    retval = []

    for d in features:
        h = make_hasher(d)
        hash_to_dicts.setdefault(h, d)

    # Get the addresses out in alphabetical order by owner name?
    for key in sorted(hash_to_dicts.keys()):
        retval += [ hash_to_dicts[key] ]

    return retval

#####################################################################
# I/O begins here

print "Welcome to Mike's Crow Wing County GIS searcher thing..."
print "NOTE: Leave 'Lake name' empty if you want to provide a lake number."
print "NOTE: If 'Lake name' is non-empty, that is used instead of lake number."
print

lname = raw_input('Lake name: ')
lnum = ''
if not lname:
    lnum = raw_input('Lake number: ')
min_val = raw_input('Value: ')
ids = get_ids(lake_name=lname, lake_num=lnum, min_val=min_val)

print
print "Count for initial query:", len(ids)
data = get_data(ids)
print "Initial count:", len(data)
data = cull_the_herd(data)
print "Count after duplicate removal:", len(data)
print

if len(data) < 1:
    # No data to speak of.
    print "No entries were returned. Goodbye!"
    sys.exit(0)

fname = "Out-{}-{}-{}.csv".format(lname, lnum, min_val)
print "Writing data out to", fname

with open(fname, 'w') as f:
    fieldnames = ["OWNAME", "OWADR1", "OWADR2", "OWADR3", "OWADR4"]
    writer = csv.DictWriter(f, fieldnames=fieldnames,
                            delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(data)
print '*'*60
print

print "Here's the data, for your enjoyment."
print

with open(fname, 'r') as f:
    print f.read()

# End of line.
