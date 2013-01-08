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

    if lake_name:
        params['where'] = WHERE_LKNAME_FMT.format(lake_name, min_val)
    elif lake_num:
        params['where'] = WHERE_LKNUM_FMT.format(lake_num, min_val)
    else:
        print "Must specify either a lake name or lake number."
        sys.exit(1)

    print "Request to GIS server being made..."
    resp = requests.get(BASE_URL, params=params)
    print resp.url
    print "Request to GIS server has completed."
    return json.loads(resp.text).get('objectIds', [])  # probably unreliable...

def get_data(ids=[]):
    """Given object IDs, get owner name and addresses."""
    params = {'f': 'json',
              'outFields': 'OWNAME,OWADR1,OWADR2,OWADR3,OWADR4'}
    count = len(ids)
    recvd = 0
    features = []
    ids = map(str, ids)  # ids are initially integers.
    while recvd < count:
        _ids = ids[:30]
        ids = ids[30:]
        params['objectIds'] = ','.join(_ids)
        print "Request for properties", recvd, "to", recvd + len(_ids), "in progress."
        resp = requests.get(BASE_URL, params=params)
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
    # TODO
    return features

ids = get_ids(lake_name=raw_input('Lake name: '),
              min_val=int(raw_input('Value: ')))
print len(ids)
data = get_data(ids)
print "Initial count:", len(data)
data = cull_the_herd(data)
print "Count after duplicate removal:", len(data)
print

print "Writing data out to out.csv"
with open('out.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys(),
                            delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(data)
print '*'*60
print

print "Here's the data, for your enjoyment."
print

with open('out.csv', 'r') as f:
    print f.read()

# End of line.
