import json
import csvkit

import numpy as np
import global_align as ga

import itertools
import math

from random import randint,sample

# config
artists_random_select_percentage=None
event_sequence_length_min=190
er_authors_filtered=None
er_authors_whitelist=[]

output_filename="artists_comparision_links_%s.csv"%(
                (str(artists_random_select_percentage) if artists_random_select_percentage else "")+
                (str(event_sequence_length_min) if event_sequence_length_min else "")+
                ("ERonly" if er_authors_filtered else ""))

# er author filter
if er_authors_filtered:
    with open("../er_artists_artworks.json","r") as f:
        for artist,artworks in json.load(f).iteritems():
            for artwork in artworks:
                er_authors_whitelist+=artwork["authors"]
        er_authors_whitelist=set(er_authors_whitelist)
        print "we will filter on %s artistis identified as member of ER"%len(er_authors_whitelist)
       
with open("../artists_profils_sequences.json","r") as  f :
    artists_profils=json.load(f)

    # tracing sequences length ditribution
    sequences_length_distribution={}
    for ap in artists_profils:
        nb=len(ap["event_sequence_with_0"])
        sequences_length_distribution[nb]=sequences_length_distribution[nb]+1 if nb in sequences_length_distribution else 1
    with open("artists_sequences_length_distribution.csv","w") as ff:
        ff.write("seq_len,nb\n")
        for seq_len,nb in sequences_length_distribution.iteritems():
            ff.write("%s,%s\n"%(seq_len,nb))

    def makeArray(l):
        return np.array(zip(range(len(l)),l),dtype=np.double)

    def compare(artists):
        seq1=artists[0]["event_sequence_with_0"]
        seq2=artists[1]["event_sequence_with_0"]
        T1=makeArray(seq1) 
        T2=makeArray(seq2)

        # len_diff=max(len(seq1),len(seq2))-min(len(seq1),len(seq2))

        # S1=makeArray(seq1 if len(seq1)>=len(seq2) else seq1+range(len_diff))
        # S2=makeArray(seq2 if len(seq2)>=len(seq1) else seq2+range(len_diff)) 
        # print S1
        # print S2
        # define the sigma parameter
        sigma = 10*(len(seq1)+len(seq2))/2 * np.sqrt((len(seq1)+len(seq2))/2)
        # compute the global alignment kernel value for different triangular parameters
        val = ga.tga_dissimilarity(T1, T2, sigma, 0)
        kval = np.exp(-val)
        return kval

    #filtering profile on sequence length
    if event_sequence_length_min:
        artists_profils=[a for a in artists_profils if len(a["event_sequence_with_0"])>=event_sequence_length_min]
    #filtering profile on ER
    if er_authors_filtered:
        artists_profils=[a for a in artists_profils if set(a["author_ids"])&er_authors_whitelist]
    if artists_random_select_percentage:
        artists_profils=sample(artists_profils,int(len(artists_profils)*artists_random_select_percentage))
    print "filtered artists to %s"%len(artists_profils)
    artists_comparision_matrix=[]
    print "computing..."
    counter=0
    # n! / r! / (n-r)!
    total= math.factorial(len(artists_profils))/math.factorial(2)/math.factorial(len(artists_profils)-2)
    print "computing... %s combinations"%total
    for artists in itertools.combinations(artists_profils,2):
        counter+=1
        if counter%10000==0:
            print "processed %s combinations %.4f%%"%(counter,counter/total*100)
            with open(output_filename,"w") as ff:
                output=csvkit.DictWriter(ff,fieldnames=['Source','Target','Weight'])
                output.writeheader()
                output.writerows(artists_comparision_matrix)

        kval=compare(artists)
        #print kval
        artists_comparision_matrix.append({
            "Source":artists[0]["name"],
            "Target":artists[1]["name"],
            "Weight":kval})
    print "done"
    with open(output_filename,"w") as ff:
        output=csvkit.DictWriter(ff,fieldnames=['Source','Target','Weight'])
        output.writeheader()
        output.writerows(artists_comparision_matrix)

