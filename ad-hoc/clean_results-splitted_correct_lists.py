#!/usr/bin/env python3

import sys, json, os
from get_html_list import *

#TODO: create dest dir if is doesn't exist

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("USAGE: ./assemble_results sourceDir destDir")
    #results = []
    arbre = os.walk(sys.argv[1])
    sourceDir = sys.argv[1] if sys.argv[1][-1] == '/' else sys.argv[1] + '/'
    destDir = sys.argv[2] if sys.argv[2][-1] == '/' else sys.argv[2] + '/'
    #sourceDir = os.path.abspath(sys.argv[1])
    #destDir = os.path.abspath(sys.argv[2])
    if not os.path.exists(sys.argv[2]):
	    os.mkdir(sys.argv[2])
    #dir_dest = os.path.abspath(sys.argv[2])
    for filename in os.listdir(sourceDir):
    #for subrep in arbre:
    #    for filename in subrep[2]:
            try:
                with open(sourceDir+filename) as src_jsonfile:
                    with open(destDir+os.path.basename(filename), 'w') as dest_jsonfile:
                        results = json.load(src_jsonfile)["results"]
                        for artwork in results:
                            for key, value in artwork['_source']['ua']['artwork'].items():
                                #print(key)
                                #print(field)
                                if type(value) == str and '<ul>' in value:
                        	        artwork['_source']['ua']['artwork'][key] = get_list_from_html(value)
                        dest_jsonfile.write(json.dumps(results))
            except Exception as e:
                print("ERROR: can not read results from json data %s ; skipping file:\n%s: %s" % (src_jsonfile, type(e), e))
