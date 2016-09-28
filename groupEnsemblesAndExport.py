#!/usr/bin/env python
# -*- coding: utf-8

import re
from pymongo import MongoClient

db = MongoClient("localhost", 27017)["myproject"]

def format_field(val):
    if type(val) == bool:
        return "1" if val else "0"
    if type(val) == list:
        return u"|".join([v for v in val])
    if val == None:
        return ''
    return val if type(val) == unicode else unicode(val)
format_csv = lambda val: ('"%s"' % val.replace('"', '""') if "," in val or '"' in val else val).encode('utf-8').replace("\n", "|")
csv_line = lambda dat,keys: ",".join([format_csv(format_field(dat[k])) for k in keys])

fields = ["_id", "acquisition_year", "acquisition_mode", "date_creation", "type", "domain", "domain_leaf", "domain_deno_for_grid", "domain_description_mst", "mst", "collection", "collection_department", "recap_authors", "inventory", "authors_list", "authors_nationality", "authors_birth_death", "authors_name_complement", "title_notice", "title_list", "comments", "recap_description", "provenance", "provenance_type", "inscriptions", "description"]
med_fields = fields + ["url", "copyright", "legend", "max_width", "max_height"]

artworks = open("uniq_artworks.csv", "w")
print >> artworks, ",".join(fields)
images = open("images_with_urls.csv", "w")
print >> images, ",".join(med_fields)

ensembles = []
inventory = []
uniq_doubles = []
re_inv = re.compile(r"(FNAC(?: (?:FH|AP|DOC))?|AM|DOC|GOB|JP|GMTT|LUX[.O ]*|MV|INV\.?|RF|N|LP|Fh|MI)[\s]*([A-Z]*[\d\-\.]+)")
for a in db["Artwork"].find():
    dat = {}
    for key in fields:
        dat[key] = a.get(key, "")
    dat["description"] = dat["domain_description_mst"].replace(dat["domain"], "").replace(dat["mst"], "").replace(u"|", ", ")

    skip = False
    if a.get("ensemble_id", ""):
        if a["ensemble_id"] in ensembles:
            skip = True
        else:
            ensembles.append(a["ensemble_id"])
    if re_inv.match(a.get("inventory", "")):
        inv_id = "#".join(re_inv.search(a["inventory"]).groups() + (str(a["acquisition_year"]),))
        if inv_id in inventory:
            if not skip:
                if inv_id not in uniq_doubles:
                    print "skip duo inventory", inv_id
                    uniq_doubles.append(inv_id)
            skip = True
        else:
            inventory.append(inv_id)
        dat["inventory_id"] = inv_id
    else:
        print "missing inv", a.get("inventory")
    if not skip:
        print >> artworks, csv_line(dat, fields)

    for mid in a["medias"]:
        m = db["Media"].find_one({"_id": mid})
        if m["type"] != "image":
            continue
        med = dict(dat)
        med["url"] = m["url_template"].replace("{file_name}", m["file_name"])
        med["copyright"] = m.get("copyright", "")
        med["legend"] = m.get("legend", "")
        med["max_width"] = m.get("max_width", "")
        med["max_height"] = m.get("max_height", "")
        print >> images, csv_line(med, med_fields)

artworks.close()
images.close()

