import pymongo
import re
import csv
import sys
from get_html_list import *

# /!\ This code is **TAB-INDENTED** /!\


def extract_date(date_field):
	regex_date = re.compile('(?:(?:([0-9]{1,2})(?:er)?\\s?)?(?:([\\w]+?)\\s?)?([0-9]{4})?\\s?[\\-–]\\s?)?(?:([0-9]{1,2})(?:er)?\\s?)?(?:([\\w]+?)\\s?)?([0-9]{4})')
	month2number = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')
	m = regex_date.match(date_field)
	if m:
		end_year = m.group(6)
		end_month = '00'
		if m.group(5) is not None:
			end_month = str(month2number.index(m.group(5))+1) if m.group(5) in month2number else '00'
		end_day = m.group(4) if m.group(4) is not None else '00'
		start_year = m.group(3) if m.group(3) is not None else end_year
		start_month = end_month
		if m.group(2) is not None:
			start_month = str(month2number.index(m.group(2))+1) if m.group(2) in month2number else end_month
		start_day = m.group(1) if m.group(1) is not None else end_day
		#print(start_year+'-'+start_month+'-'+start_day, end_year+'-'+end_month+'-'+end_day)
		return [(start_year, start_month, start_day), (end_year, end_month, end_day)]
	else:
		return None

#def extract_expositions(json, field_dict, csvwriter):
def get_expo_title_other(record):
	regex_title_other = re.compile('(.*)\\s?:\\s?((?:.*?(?:,| :)\\s?){2}.*[0-9]{4})', flags=re.S)
	regex_title_other_fallback = re.compile('(.*)\\s?(?::|,)\\s(.* ?[0-9]{4})', flags=re.S)
	m = regex_title_other.match(record)
	if m is None:
		m = regex_title_other_fallback.match(record)
	if m is None:
		return None
	return {'title':m.group(1).strip(), 'other':m.group(2)}


def get_expo_place_time(placeTimeList):
	regex_place_time = re.compile('(?:(.*)(?:,\\s|\\s:\\s))?(.*[0-9]{4})?')
	place_time_list = placeTimeList.split(' // ')
	rslt = []
	for place_time in place_time_list:
		m = regex_place_time.match(place_time)
		if m is None:
			rslt.append(None)
		else:
			rslt.append({'place':m.group(1), 'time':m.group(2)})
	return rslt

def get_town_museum(place):
	regex_museum_town = re.compile("(.+?),\\s?([\\w\\-']+\\s?(?:\\(.+?\\))?)$")
	regex_town_museum = re.compile("([\\w\\-']+\\s?(?:\\(.+?\\))?(?:,\\s[A-Z]{2})?),\\s?(.+?)$")
	regex_town_museum_fallback = re.compile('([\\w]+,?\\s[\\w]+(?:\\s\\(.+?\\))?),\\s?(.+?)$')
	regex_museum_town_fallback = re.compile('(.+?),\\s([\\w]+,?\\s[\\w]+(?:\\s\\(.+?\\))?)?$')
	[town, museum] = ['', '']
#	rslt = {}
	o = regex_museum_town.match(place)
	if o is None:
		o = regex_town_museum.match(place)
		if o is None:
			o = regex_town_museum_fallback.match(place)
		if o is not None:
			[town, museum] = [o.group(1), o.group(2)]
		else:
			o = regex_museum_town_fallback.match(place)
			if o is not None:
				[town, museum] = [o.group(2), o.group(1)]
			else:
				return None
					#unplaced_num += 1
	else:
		[town, museum] = [o.group(2), o.group(1)]
	return {'town': town, 'museum': museum}

def extract_expositions(json, csvwriter):
	unmatched_num = 0
	undated_num = 0
	unplaced_num = 0
	[town, museum, start_date, end_date] = ['', '', '', '']
	if 'expositions' not in json:
		return -1
	item_list = get_list_from_html(json['expositions'])
	for item in item_list:
		m = get_expo_title_other(item)
		if m is None:
			csvwriter.writerow([item, '', '', '','', '', '', ''])
			#unmatched_num += 1
		else:
			title = m['title']
			other = m['other']
			#place_time_list_raw = other.split(' // ')
			place_time_list_clean = get_expo_place_time(other)
			for place_time in place_time_list_clean:
				[museum, town] = ['', '']
				[start_date, end_date] = ['', '']
				if place_time is not None:
					place = place_time['place']
					time = place_time['time']
					if place is not None:
						town_museum = get_town_museum(place)
						if town_museum is not None:
							museum = town_museum['museum']
							town = town_museum['town']
					#else:
					#	place = ''
					if time is not None:
						tab = extract_date(time)
						if tab is not None:
							end_date = str(tab[1][0])+'-'+str(tab[1][1])+'-'+str(tab[1][2])
							start_date = str(tab[0][0])+'-'+str(tab[0][1])+'-'+str(tab[0][2])
						#else:
						#	
					else:
						time = ''
				csvwriter.writerow([item, title, place, museum, town, time, start_date, end_date])