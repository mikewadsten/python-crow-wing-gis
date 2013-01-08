#!/usr/bin/env python

#import csv  # to handle csv crap
import json  # to parse
import requests
import sys

# This is where the fun begins.
BASE_URL = ("http://gis.co.crow-wing.mn.us/ArcGIS/rest/services/CROWWING"
            "SUBSCRIPTION/MapServer/0/query")
WHERE_LKNAME_FMT = "(UPPER(LKLAKD) = '{}') AND (ESTTOTVAL >= {})"
WHERE_LKNUM_FMT = "(APLAKN = {}) AND (ESTTOTVAL >= {})"

if __name__ != "__main__":
    print "What are you doing. Stahp."
    sys.exit(1)

# __name__ == __main__, so we're running gis.py as a script, so we continue.

def get_ids(lake_name='', lake_num=0, min_val=0):
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
    print "Request to GIS server has completed."
    return json.loads(resp.text).get('objectIds', []) # probably unreliable...

print get_ids(lake_name=raw_input('Lake name: '), min_val=int(raw_input('Value: ')))

# End of line.
