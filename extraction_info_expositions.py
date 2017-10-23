import pymongo
import re
import csv
import sys

# /!\ This code is **TAB-INDENTED** /!\

def get_list_from_html(field):
	regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
	tab = regex_item.split(field)
	new_tab = []
	for item in tab:
		if len(item) > 0 and 'ul>' not in item and item != '\n':
			new_tab.append(item)
	return new_tab

#def extract_expositions(json, field_dict, csvwriter):
def extract_expositions(json, csvwriter):
	if 'expositions' not in json:
		return 1
	#regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
	item_list = get_list_from_html(json['expositions'])
	regex_title_other = re.compile('(.*)(?: |	): ((?:.*?(?:, | : )){2}.*[0-9]{4})', flags=re.S)
	regex_title_other_fallback = re.compile('(.*) ?(?::|,) (.* ?[0-9]{4})', flags=re.S)
	regex_place_time = re.compile('(?:(.*)(?:, | : ))?(.*[0-9]{4})?')
	regex_museum_town = re.compile("(.+?), ?([\\w\\-']+ ?(?:\\(.+?\\))?)$")
	regex_town_museum = re.compile("([\\w\\-']+ ?(?:\\(.+?\\))?), ?(.+?)$")
	regex_end_year = re.compile('.*([0-9]{4})$')
	for item in item_list:
		#print('ITEM:', item, '$')
		#try:
			m = regex_title_other.match(item)
			if m is None:
				m = regex_title_other_fallback.match(item)
			if m is None:
				csvwriter.writerow([item, '', '', '','', ''])
			else:
				title = m.group(1)
			#print(title)
				other = m.group(2)
				place_time_list = other.split(' // ')
				for place_time in place_time_list:
					n = regex_place_time.match(place_time)
					place = n.group(1)
					#tab = 
					[town, museum] = ['', '']
					if place is not None:
						o = regex_museum_town.match(place)
						if o is None:
							o = regex_town_museum.match(place)
							if o is not None:
								[town, museum] = [o.group(1), o.group(2)]
						else:
							[town, museum] = [o.group(2), o.group(1)]
					time = n.group(2)
					year = regex_end_year.match(time).group(1) if time is not None else ''
					csvwriter.writerow([item, title, place, museum, town, time, year])
				#print(place, time, sep='|')
		#except:
		#	print('ITEM:', item, '$')
		#print(place_time_list)

def filter_fields(json, field_dict, csvwriter):
	#regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
	regex_addendum = re.compile('(.*?)(?: - (.*? - .*?)(?: - (.*))?)?$', flags=re.S)
	for field in field_dict:
		#print(field)
		if field in json:
			#print(field)
			tab = regex_item.split(json[field])
			#print(tab)
			for item in tab:
				if len(item) > 4 and item[4] == '/':
					#print(json['_id'], item)
					m = regex_addendum.match(item)
					row = [json['_id'], field, m.group(1)]
					if m.group(2) is not None:
						row.append(m.group(2))
						if m.group(3) is not None:
							row.append(m.group(3))
						else:
							row.append('')
					else:
						row += ['', '']
					csvwriter.writerow(row)					
	return

if len(sys.argv) < 2:
	sys.exit('Usage: '+sys.argv[0]+' [destinationCSVfile]')

field_dict = {"all_realized_operations_history":1, "hanging_history":1, "expositions":1}#, "hanging_history":1, "expositions_without_current":1, "expositions":1}
c = pymongo.MongoClient()
cursor = c.myproject.Artwork.find({},field_dict)
with open(sys.argv[1], 'w') as f:
	destCSV = csv.writer(f)
	header = ('Champ brut', 'Titre exposition', "Lieu d'exposition (brut)", "Musée d'exposition", 'Ville du musée', "Date d'exposition", "Année de fin d'exposition")
	destCSV.writerow(list(header))
	for doc in cursor:
		#filter_fields(doc, field_dict, destCSV)
		#print('ID:', doc['_id'])
		extract_expositions(doc, destCSV)
#	jsonToCSV
c.close()