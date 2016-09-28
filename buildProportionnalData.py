#!/usr/bin/env python
# -*- coding: utf-8

import re, csv
from groupEnsemblesAndExport import csv_line, format_csv, format_field
from pymongo import MongoClient
import networkx as nx

db = MongoClient("localhost", 27017)["myproject"]

with open("uniq_artworks.csv") as f:
    data = list(csv.DictReader(f))

keywords = u"""Guerr
Bataille
Combat
Soldat
Poilu
mort
morts
bless[eé]
hom+age
monument
prison+ier
ruines
fusill[eé]s
lib[eé]ratio
patrie
nation
déport[eé]s
barbel[eé]
tranch[eé]e
perm+is+ion
capitaine
mar[eé]chal
sergent
g[eé]n[eé]ral
com+andant
adjudant
amiral
of+icier
com+[eé]mor+ation
camp
exode
arm[eé]e
forces
r[eé]sistance
maquis
troupes
capitulation
armistice
bombardement
survivant
gloire
d[eé]barquement
paix
victoire
d[eé]fense
war
battle
soldier
colonel
1914
1915
1916
1917
1918
1939
1940
1944
1945
1870
1871"""

match_war = re.compile(ur'(%s)' % "|".join(keywords.split("\n")), re.I)
authors = {}

nat_codes = {}
def extract_natcode(nat):
    n = nat.lower()
    if "naissance" in n:
        if "avant" not in n:
            n = n.split('(')[1]
    accents = u"àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
    nocents = u"aaaaeeeeiiiioooouuuunc------";
    for i,c in enumerate(accents):
        n = n.replace(c, nocents[i])
    n = n[0:3]
    if n not in nat_codes:
        nat_codes[n] = 0
    nat_codes[n] += 1
    return n

def add_node(graph, nat):
    if not graph.has_node(nat):
        graph.add_node(nat, total=0)
    graph.node[nat]["total"] += 1

def add_edge_weight(graph, node1, node2):
    add_node(graph, node1)
    add_node(graph, node2)
    if not graph.has_edge(node1, node2):
        graph.add_edge(node1, node2, weight=0)
    graph[node1][node2]['weight'] += 1

G = nx.Graph()

toviz_fields = ["_id", "acquisition_year", "match_war", "is_command", "title_notice", "type"]
with open("artworks_viz_war.csv", "w") as f:
    print >> f, ",".join(toviz_fields)
    for a in data:
        a["title_notice"] = a["title_notice"].decode("utf-8")
        a["match_war"] = match_war.search(a["title_notice"]) is not None
        a["is_command"] = a.get("acquisition_mode", "") == "Achat par commande"
        print >> f, csv_line(a, toviz_fields)
        countries = []
        for aid in a["authors"].split("|"):
            if aid not in authors:
                aut = db["Author"].find_one({"_id": aid})
                aut["name"] = aut.get("name", {}).get("notice", "")
                aut["gender"] = aut.get("gender", "")
                aut["nationality"] = aut.get("nationality", "")
                aut["nat_code"] = extract_natcode(aut["nationality"])
                authors[aid] = aut
            if not "years" in authors[aid]:
                authors[aid]["years"] = {}
            if not a["acquisition_year"] in authors[aid]["years"]:
                authors[aid]["years"][a["acquisition_year"]] = 0
            authors[aid]["years"][a["acquisition_year"]] += 1
            a["decenial"] = str(a["acquisition_year"])[0:3]
            if not "decenials" in authors[aid]:
                authors[aid]["decenials"] = {}
            if not a["decenial"] in authors[aid]["decenials"]:
                authors[aid]["decenials"][a["decenial"]] = 0
            authors[aid]["decenials"][a["decenial"]] += 1
            if not "total" in authors[aid]:
                authors[aid]["total"] = 0
            authors[aid]["total"] += 1
            if authors[aid]["nat_code"] and authors[aid]["nat_code"] not in countries:
                for c in countries:
                    add_edge_weight(G, c, authors[aid]["nat_code"])
                countries.append(authors[aid]["nat_code"])

with open("authors_years.csv", "w") as f:
    print >> f, "year,artworks,name,gender,nationality,nat_code"
    for aid, aut in authors.items():
        for y, val in aut["years"].items():
            if y == "0": continue
            print >> f, ",".join([format_csv(format_field(el)) for el in [y, val, aut["name"], aut["gender"], aut["nationality"], aut["nat_code"]]])

with open("authors_decenials.csv", "w") as f:
    print >> f, "decenial,artworks,name,gender,nationality,nat_code"
    for aid, aut in authors.items():
        if not aut["nat_code"] or aut["nat_code"] == "fra": continue
        if nat_codes[aut["nat_code"]] < 25: continue
        for y, val in aut["decenials"].items():
            if y == "0": continue
            print >> f, ",".join([format_csv(format_field(el)) for el in [y+"0", val, aut["name"], aut["gender"], aut["nationality"], aut["nat_code"]]])

nx.write_gexf(G, "coauthors_countries.gexf")
