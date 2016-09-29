from pymongo import MongoClient
import re
import json
import itertools
import csvkit

client = MongoClient("localhost:27017")

db=client["myproject"]
authors = db.Author
artworks = db.Artwork

rdate=re.compile(r"((20|19|18|17)\d\d)")

authors_info={}


with open("../uniq_artworks_ids.csv","r") as f:
	ids_uniqus_artworks=dict([(v["_id"],"") for v in csvkit.DictReader(f)])

for artwork in artworks.find():
	if artwork["_id"] in ids_uniqus_artworks:
		if artwork["authors_notice"] not in authors_info:
			authors_info[artwork["authors_notice"]]={
				"name":artwork["authors_notice"],
				#"gender":author["gender"] if "gender" in author else "",
				#"nationality":(author["authors_nationality"] if "authors_nationality" in author else ''),
				#"birthdeathdates": [],
				"author_ids":artwork["authors"],
				"creation_years":[],
				"acquisition_years":[],
				"exhibition_dates":[],
				"transfert_dates":[],
				"deposit_dates":[]
			}

		author_info=authors_info[artwork["authors_notice"]]
		if int(artwork["acquisition_year"])!=0:
			author_info["acquisition_years"].append(artwork["acquisition_year"])
		if "date_creation" in artwork:
			creation=[int(g[0]) for g in rdate.findall(artwork["date_creation"])]
			if creation:
				author_info["creation_years"].append(max(creation))

		# birth=rdate.findall(artwork["authors_birth_death"])
		# if birth:
		# 	for g in birth:
		# 		author_info["birthdeathdates"].append(int(g[0]))
		if "expositions" in artwork:
			expositions=artwork["expositions"].replace("<ul>","")
			expositions=expositions.replace("</ul>","")
			expositions=expositions.replace("</li>","")

			expositions=expositions.split("<li>")
			for e in expositions:
				expo_dates=rdate.findall(e)
				if expo_dates:
					author_info["exhibition_dates"].append(min(int(g[0]) for g in expo_dates))
			# <ul><li>oeieorij1231</li></ul>
		if "localization_if_external" in artwork:
			transfert=[int(g[0]) for g in rdate.findall(artwork["localization_if_external"])]
			if transfert:
				author_info["transfert_dates"].append(max(transfert))
		if "localisation_if_deposit" in artwork:
			depot=[int(g[0]) for g in rdate.findall(artwork["localisation_if_deposit"])]
			if depot:
				author_info["deposit_dates"].append(max(depot))

		dates_weighted={}
		dates=sorted(author_info["acquisition_years"]+author_info["exhibition_dates"]+author_info["transfert_dates"]+author_info["deposit_dates"])
		for k,g in itertools.groupby(dates,key=lambda e:e):
			dates_weighted[k]=len(list(g))
		author_info["dates_weighted"]=dates_weighted

		authors_info[artwork["authors_notice"]]=author_info	



with open("authors_frequency.json","w") as f:
	json.dump(authors_info.values(),f,indent=4)


# Group artworks by artists :
# for each artwork 
# get date birth death "authors_birth_death"
# get date_achat "acquisition_year"
# get dates expos "expositions" / "exhibitions_history"
# get date transfert "localization_if_external"

