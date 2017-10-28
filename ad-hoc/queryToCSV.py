import pymongo
import sys
import csv
import json

if len(sys.argv) < 4:
	sys.exit("USAGE: " + sys.argv[0] + " 'mongo find dict' 'mongo field dict' [destCSV]")

#Truc chiants:
# on veut mettre la requete en argument => DONE
# on veut mettre la collection en argument

c = pymongo.MongoClient()
#find_dict = {"$text":{"$search": "\"Une histoire – art, architecture et design des années 1980 à nos jours\""}}
#field_dict = {"_id":1, "type":1, "title_notice":1, "authors_notice":1, "date_creation":1}
find_dict = json.loads(sys.argv[1])
field_dict = json.loads(sys.argv[2])
cursor = c.myproject.Artwork.find(find_dict,field_dict)

with open(sys.argv[3], 'w') as f:
	destCSV = csv.writer(f)
	line_header = []
	for field in field_dict.keys():
		line_header.append(field)
	destCSV.writerow(line_header)
	for doc in cursor:
		doc_line = []
		for field in field_dict.keys():
			if field in doc:
				doc_line.append(doc[field])
			else:
				doc_line.append('')
		destCSV.writerow(doc_line)
print('Done')