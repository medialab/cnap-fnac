#!/usr/bin/env python

import sys, json

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("USAGE: ./assemble_results json1.json json2.json ...")
    results = []
    for jsonfile in sys.argv[1:]:
        try:
            with open(jsonfile) as jsonfile:
                results += json.load(jsonfile)["results"]
        except Exception as e:
            print >> sys.stderr, "ERROR: can not read results from json data %s ; skipping file:\n%s: %s" % (jsonfile, type(e), e)
    print >> sys.stderr, "INFO: %s total results assembled" % len(results)
    print(json.dumps(results))
