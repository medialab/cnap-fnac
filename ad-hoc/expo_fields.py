import pymongo
import re
import csv
import sys
from get_html_list import *

# /!\ This code is **TAB-INDENTED** /!\

def extract_date(date_field):
	"""Extract date from given date_field (aka 'time' field from get_expo_place_time).
	Returns [[start_year, start_month, start_day], [end_year, end_month, end_day]] or None if no match.
	"""
	regex_date = re.compile(r'(?:(?:([0-9]{1,2})(?:er)?\s*)?(?:([\w^\d]+?)\.?\s*)?([0-9]{4})?\s*[\-–]\s*)?(?:([0-9]{1,2})(?:er)?\s*)?(?:([\w^\d]+?)\.?\s*)?([0-9]{4})')
	regex_date_fallback = re.compile('.*([0-9]{4})')
	month2number = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')
	abbr2number = ('janv', 'fév', 'mars', 'avril', 'mai', 'juin', 'juil', 'août', 'sept', 'oct' 'nov', 'déc')
	m = regex_date.match(date_field)
	if m:
		end_year = m.group(6)
		end_month = '00'
		if m.group(5) is not None:
			month = m.group(5).strip()
			end_month = str(month2number.index(m.group(5))+1) if m.group(5) in month2number else end_month
			end_month = str(abbr2number.index(m.group(5))+1) if m.group(5) in abbr2number else end_month
		end_day = m.group(4) if m.group(4) is not None else '00'
		start_year = m.group(3) if m.group(3) is not None else end_year
		start_month = end_month
		if m.group(2) is not None:
			start_month = str(month2number.index(m.group(2))+1) if m.group(2) in month2number else end_month
		if m.group(1) is not None:
			start_day = m.group(1)
		elif m.group(2) is not None or m.group(3) is not None:
			start_day = '00'
		else:
			start_day = end_day
		end_month = end_month if len(end_month) > 1 else '0'+end_month
		start_month = start_month if len(start_month) > 1 else '0'+start_month
		#print(start_year+'-'+start_month+'-'+start_day, end_year+'-'+end_month+'-'+end_day)
		return [[start_year, start_month, start_day], [end_year, end_month, end_day]]
	else:
		m = regex_date_fallback.match(date_field)
		if m:
			return [(m.group(1), '00', '00'), (m.group(1), '00', '00')]
		else:
			return None

def get_list_from_html(field):
	"""Convert an html list into a python list."""
	regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
	tab = regex_item.split(field)
	new_tab = []
	for item in tab:
		if len(item) > 0 and 'ul>' not in item and item != '\n':
			new_tab.append(item)
	return new_tab

#def extract_expositions(json, field_dict, csvwriter):
def get_expo_title_other(record):
	"""From a given exhibition raw field, extract title and the rest.
	Returns {'title':`string`, 'other':`string`} or None if no match"""
	regex_title_other = re.compile(r'(.*)\s*:\s*((?:.*?(?:,| :)\s*){2}.*[0-9]{4})', flags=re.S)
	regex_title_other_fallback = re.compile(r'(.*)\s*(?::|,)\s+(.* ?[0-9]{4})', flags=re.S)
	m = regex_title_other.match(record)
	if m is None:
		m = regex_title_other_fallback.match(record)
	if m is None:
		return None
	return {'title':m.group(1).strip() if m.group(1) is not None else None,\
	'other':m.group(2).strip() if m.group(2) is not None else None}

def get_expo_place_time(placeTimeList):
	"""From a placeTimeList (aka 'other' field from get_expo_title_other),
	extract a list of places and times.
	Returns a list of {'place':`string`, 'time':`string`}.
	/!\\ Elements splitting is distinct from place_time matching, therefore
	some elements in the list can be None (no match at all). Also, keep in mind
	that this is partial matching (ie place or time can be '')"""
	regex_place_time = re.compile(r'(?:(.*)(?:,\s+|\s+:\s+))?(.*[0-9]{4})?')
	place_time_list = placeTimeList.split('//')
	rslt = []
	for place_time in place_time_list:
		m = regex_place_time.match(place_time.strip())
		if m is None:
			rslt.append(None)
		else:
			rslt.append({'place':m.group(1).strip() if m.group(1) is not None else None,\
			'time':m.group(2).strip() if m.group(2) is not None else None})
	return rslt

def get_town_museum(place):
	"""From a place (aka 'place' field from get_expo_place_time) extract
	institution name and town.
	Returns {'town':̀`string`, 'museum':`string`} or None if no match."""
	regex_museum_town = re.compile(r"(.+?),\s*([\w\-']+\s*(?:\(.+?\))?)$")
	regex_town_museum = re.compile(r"([\w\-']+\s*(?:\(.+?\))?(?:,\s+[A-Z]{2})?),\s*(.+?)$")
	regex_town_museum_fallback = re.compile(r"([\w\-']+,?\s+[\w\-']+(?:\s+\(.+?\))?),\s*(.+?)$")
	#regex_museum_town_fallback = re.compile(r"(.+?),\s+([\w\-']+,?\s+[\w\-']+(?:\s+\(.+?\))?)?$")
	regex_museum_town_fallback = re.compile(r"(.+?),\s+([\w\-']+,?\s+[\w\-']+(?:\s+\(.+?\))?)$")
	regex_town_museum_fallback2 = re.compile(r"(.+\s*?\(.+?\)),\s*(.+?)$")
	regex_museum_town_fallback2 = re.compile(r"(.+?),\s*(.+\s*?\(.+?\))$")
	[town, museum] = ['', '']
#	rslt = {}
	o = regex_museum_town.match(place)
	if o is None:
		o = regex_town_museum.match(place)
		if o is None:
			o = regex_town_museum_fallback.match(place)
		if o is None:
			o = regex_town_museum_fallback2.match(place)
		if o is not None:
			[town, museum] = [o.group(1), o.group(2)]
		else:
			o = regex_museum_town_fallback.match(place)
			if o is None:
				o = regex_museum_town_fallback2.match(place)
			if o is not None:
				[town, museum] = [o.group(2), o.group(1)]
			else:
				return None
					#unplaced_num += 1
	else:
		[town, museum] = [o.group(2), o.group(1)]
	return {'town': town.strip(), 'museum': museum.strip()}

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