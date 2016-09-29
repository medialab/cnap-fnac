import json
import csvkit
import math

with open("../artists_profils_sequences.json","r") as  f :
    artists_profils=json.load(f)
    er_authors_whitelist=[]
    with open("../er_artists_artworks.json","r") as f:
        for artist,artworks in json.load(f).iteritems():
            for artwork in artworks:
                er_authors_whitelist.append(artwork["authors"])
        er_authors_whitelist=er_authors_whitelist
        
    with open("artists_node_attribute.csv","w") as of:
        output=csvkit.DictWriter(of,fieldnames=["ID","Label","sequence_length_type","ER_member"])
        output.writeheader()
        short_nb=0
        medium_nb=0
        large_nb=0

        for a in artists_profils:
            if len(a["event_sequence_with_0"])<40:
                seq_len_type="short"
                short_nb+=1
            elif len(a["event_sequence_with_0"])>=40 and len(a["event_sequence_with_0"])<190:
                seq_len_type="medium"
                medium_nb+=1
            elif len(a["event_sequence_with_0"])>=190:
                seq_len_type="large"
                large_nb+=1
            else:
                seq_len_type="oups"
            if a["author_ids"] in er_authors_whitelist:
                print a["name"]
            output.writerow({"ID":a["name"],
                            "Label":a["name"],
                            "sequence_length_type":seq_len_type,
                            "ER_member":a["author_ids"] in er_authors_whitelist})
        def C(n,r):
            return math.factorial(n)/math.factorial(r)/math.factorial(n-r)

        print "short %s combi %s => %s hours"%(short_nb,C(short_nb,2),C(short_nb,2)/1000/60/60)
        print "medium %s combi %s => %s hours"%(medium_nb,C(medium_nb,2),C(medium_nb,2)/1000/60/60)
        print "large %s combi %s => %s hours"%(large_nb,C(large_nb,2),C(large_nb,2)/1000/60/60)

