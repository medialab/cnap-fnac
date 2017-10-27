import requests
import csv
import sys
import json

if len(sys.argv) < 4:
	sys.exit("USAGE: " + sys.argv[0] + " [sourceCSVfile] [destCSVfile] [columnNumber]")

USERNAME = ""
museums_coordinates = {}

url_header = 'http://api.geonames.org/searchJSON?q='
#Mus%C3%A9e+national+Picasso
url_footer = '&maxRows=10&featureCode=MUS&fuzzy=0.8&username='+USERNAME

with open(sys.argv[1], 'r') as f, open(sys.argv[2], 'w') as g:
	sourceCSV = csv.reader(f)
	destCSV = csv.writer(g)
	for line, record in enumerate(sourceCSV):
		if not line:
			destCSV.writerow(record+['latitude', 'longitude'])
			print('Champs de recherche:', record[int(sys.argv[3])-1])
		else:
			adress = record[int(sys.argv[3])-1].replace(', ', '+').replace(',', '+').replace(' ', '+')
			couple_coord = ['', '']
			if adress != '':
				if adress not in museums_coordinates:
					url = url_header+adress+url_footer
					print(url)
		#jsonDoc = json.loads(requests.get(url).text)
					jsonDoc = requests.get(url).json()
					if jsonDoc['totalResultsCount'] > 0:
						count = 0
						while count > 0 and count < jsonDoc['totalResultsCount']:
							if jsonDoc['geonames'][count]['fcode'] == "MUS":
								#destCSV.writerow(record+[jsonDoc['geonames'][count]['lat'], jsonDoc['geonames'][count]['lng']])
								museums_coordinates[adress] = [jsonDoc['geonames'][count]['lat'], jsonDoc['geonames'][count]['lng']]
								count = -1
							print(jsonDoc['geonames'][count])
						couple_coord = museums_coordinates[adress]
			destCSV.writerow(record+couple_coord)
print('Done')

