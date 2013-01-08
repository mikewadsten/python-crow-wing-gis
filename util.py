# Utility functions for the GIS crap.

CROW_WING = 1
CASS = 2
AITKIN = 3

HERD_FIELDS = {
    CROW_WING: ['OWNAME', 'OWADR1', 'OWADR2', 'OWADR3', 'OWADR4'],
    CASS: ['Taxpayer', 'Addr1', 'Addr2', 'Addr3', 'Addr4', 'Zip5'],
    AITKIN: ['Owner Name', 'Owner Address 1', 'Owner Address 2',
             'Owner Address 3', 'Owner Address 4']
}

def cull_the_herd(features=[], county=CROW_WING):
    """Remove duplicate names/addresses."""
    def make_hasher(t):
        return '|'.join([ t[key] for key in HERD_FIELDS[county] ])

    hash_to_dicts = {}
    retval = []

    for d in features:
        h = make_hasher(d)
        hash_to_dicts.setdefault(h, d)

    # Get the addresses out in alphabetical order by owner name?
    for key in sorted(hash_to_dicts.keys()):
        retval += [ hash_to_dicts[key] ]

    return retval
