# coding=UTF8
from pymongo import MongoClient
import re
import json
import itertools
import csvkit
from pprint import pprint

client = MongoClient("localhost:27017")

db=client["myproject"]
authors = db.Author
artworks_collection = db.Artwork

rdate=re.compile(r"((20|19|18|17)\d\d)")
rfirstnameName= re.compile(r"([\w|ø]+) (.*)")

artists_names=[]
with open("artists_name_esthetic_relational.txt","r") as f:
	artists=[l.strip("\n") for l in f.readlines()]
	for a in artists:
		(name,firstname)=(rfirstnameName.match(a).group(2,1))
		artists_names.append(name+" "+firstname if firstname!="ø" else name)


with open("../uniq_artworks_ids.csv","r") as f:
	ids_uniqus_artworks=dict([(v["_id"],"") for v in csvkit.DictReader(f)])

total_artwork=0
total_artist=0
artworks_by_artists={}
artworks=[]
for artwork in artworks_collection.find({"authors_list":{"$regex":".*"+"|".join(artists_names)+".*"}}):
	if artwork["_id"] in ids_uniqus_artworks:
		artworks.append(artwork)
		if artwork["authors_list"] in artworks_by_artists:
			artworks_by_artists[artwork["authors_list"]].append(artwork)
		else:
			artworks_by_artists[artwork["authors_list"]]=[artwork]

print "total_artwork %s"%len(artworks)

for artist,nb_artwork in sorted([(k,len(v)) for (k,v) in artworks_by_artists.iteritems()],key=lambda t:t[1]):
	print "%s %s"%(artist,nb_artwork)
	total_artwork+=nb_artwork
	total_artist+=1
print total_artist
print total_artwork

with open("er_artists_artworks.json","w") as f:
	json.dump(artworks_by_artists,f,indent=4)

artworks_info=[]
for artwork in artworks:

	artwork_info={
		"title":artwork["title_list"],
		"author(s)":artwork["authors_list"],
		"creation_year": None,
		"acquisition_year": int(artwork["acquisition_year"]) if artwork["acquisition_year"]!=0 else None,
		"exhibition_dates":[],
		"transfert_dates":[],
		"deposit_dates":[]
	}
	
	if "expositions" in artwork:
		expositions=artwork["expositions"].replace("<ul>","")
		expositions=expositions.replace("</ul>","")
		expositions=expositions.replace("</li>","")

		expositions=expositions.split("<li>")
		for e in expositions:
			expo_dates=rdate.findall(e)
			if expo_dates:
				artwork_info["exhibition_dates"].append(min(int(g[0]) for g in expo_dates))
	#int(artwork["date_creation"]) if artwork["date_creation"]!=0 else None,
	if "date_creation" in artwork:
		creation=[int(g[0]) for g in rdate.findall(artwork["date_creation"])]
		if creation:
			artwork_info["creation_year"]=max(creation)
	if "localization_if_external" in artwork:
		transfert=[int(g[0]) for g in rdate.findall(artwork["localization_if_external"])]
		if transfert:
			artwork_info["transfert_dates"].append(max(transfert))
	if "localisation_if_deposit" in artwork:
		depot=[int(g[0]) for g in rdate.findall(artwork["localisation_if_deposit"])]
		if depot:
			artwork_info["deposit_dates"].append(max(depot))
				
	dates_weighted={}
	dates=sorted([artwork_info["creation_year"],artwork_info["acquisition_year"]]+artwork_info["exhibition_dates"]+artwork_info["transfert_dates"]+artwork_info["deposit_dates"])
	for k,g in itertools.groupby(dates,key=lambda e:e):
		dates_weighted[k]=len(list(g))
	artwork_info["dates_weighted"]=dates_weighted	
	artworks_info.append(artwork_info)


with open("er_artworks_frequency.json","w") as f:
	json.dump(artworks_info,f,indent=4)


# Group artworks by artists :
# for each artwork 
# get date birth death "authors_birth_death"
# get date_achat "acquisition_year"
# get dates expos "expositions" / "exhibitions_history"
# get date transfert "localization_if_external"

