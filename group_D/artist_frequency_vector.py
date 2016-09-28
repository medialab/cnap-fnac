import json

with open("authors_frequency.json","r") as f:
	afs=json.load(f)
	lengths={}
	filtered_artist_profils=[]
	for af in afs:
		n=sum(nb for k,nb in af["dates_weighted"].iteritems())
		lengths[n]=lengths[n]+1 if n in lengths else 1
		if n>3:

			
			#print af["dates_weighted"]
			date_nb_tuples=[(int(date),nb) for (date,nb) in af["dates_weighted"].iteritems()]
			date_nb_tuples.sort(key=lambda t:t[0])
			dates_weighted_with_0={}
			for i,(date,nb) in enumerate(date_nb_tuples):
				dates_weighted_with_0[date]=nb
				#print "%s %s %s"%(i,date,nb)
				if i<len(date_nb_tuples)-1 :
					#print "looping on range(%s)"%(date_nb_tuples[i+1][0]-date)
					for j in range(date_nb_tuples[i+1][0]-date):
						dates_weighted_with_0[date+j+1]=0
			 
			filtered_artist_profils.append(
				{
				"name": af["name"],
		        "nationality": af["nationality"], 
		        "gender": af["gender"], 
		        "birthdeathdates":af["birthdeathdates"],
				"event_sequence_with_0":[v for k,v in sorted(list(dates_weighted_with_0.iteritems()),key=lambda t:t[0])],
				"event_sequence_without_0":[v for k,v in sorted(list(af["dates_weighted"].iteritems()),key=lambda t:t[0])],
				"first_date":[k for k,v in sorted(list(dates_weighted_with_0.iteritems()),key=lambda t:t[0])][0],
				"dates_weighted":af["dates_weighted"]
				}
			)
			if len(filtered_artist_profils[-1]["event_sequence_with_0"])>2000:
				print filtered_artist_profils[-1]
	#lengths=dict([(nb_event,nb_artist) for (nb_event,nb_artist) in lengths.iteritems() if nb_event>3])


	with open("artists_profils_sequences.json","w") as ff:
		json.dump(filtered_artist_profils,ff,indent=4)