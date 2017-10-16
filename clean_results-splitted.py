#!/usr/bin/env python3

import sys, json, os

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("USAGE: ./assemble_results sourceDir destDir")
    results = []
    arbre = os.walk(sys.argv[1])
    #dir_dest = os.path.abspath(sys.argv[2])
    for subrep in arbre:
        for filename in subrep[2]:
            try:
                with open(sys.argv[1]+filename) as src_jsonfile:
                    with open(sys.argv[2]+os.path.basename(filename), 'w') as dest_jsonfile:
                        results += json.load(src_jsonfile)["results"]
                        dest_jsonfile.write(json.dumps(results))
                        results = []
            except Exception as e:
                print("ERROR: can not read results from json data %s ; skipping file:\n%s: %s" % (jsonfile, type(e), e))
