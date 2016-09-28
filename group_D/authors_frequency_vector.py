import json

with open("authors_frequency.json","r") as f:
	afs=json.load(f)
	lengths={}
	filtered_artist_profils=[]
	for af in afs:
		n=sum(nb for k,nb in af["dates_weighted"].iteritems())
		lengths[n]=lengths[n]+1 if n in lengths else 1
		if n>3:
			filtered_artist_profils.append(af["dates_weighted"].values())
			
	lengths=dict([(nb_event,nb_artist) for (nb_event,nb_artist) in lengths.iteritems() if nb_event>3]) 

	with open("authors_frequency_filtered.json","w") as ff:
		json.dump(filtered_artist_profils,ff,indent=4)