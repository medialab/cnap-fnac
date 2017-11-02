#!/usr/bin/env python3

#import pymongo
import re
import csv
import sys
import datetime
from expo_fields import *


# /!\ This code is **TAB-INDENTED** /!\

#def get_list_from_html(field):
#	regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
#	tab = regex_item.split(field)
#	new_tab = []
#	for item in tab:
#		if len(item) > 0 and 'ul>' not in item and item != '\n':
#			new_tab.append(item)
#	return new_tab

#def get_expo_title_other(record):
#	regex_title_other = re.compile('(.*)\\s?:\\s?((?:.*?(?:,| :)\\s?){2}.*[0-9]{4})', flags=re.S)
#	regex_title_other_fallback = re.compile('(.*)\\s?(?::|,)\\s(.* ?[0-9]{4})', flags=re.S)
#	m = regex_title_other.match(record)
#	if m is None:
#		m = regex_title_other_fallback.match(record)
#	if m is None:
#		return None
#	return {'title':m.group(1).strip(), 'other':m.group(2)}

def filter_operation_record(record):
	"""Get some basic info about operation, as well as the un-parsed tail.
	Returns {'date': `string: YYYY/MM/DD`, 'opcode':`string`, 'oplabel':`string`, 'additional_date':`string`}"""
	rslt = {}
	regex_basic_fields = re.compile('([0-9]{4}\\/[0-9]{1,2}\\/[0-9]{1,2}) - (.+?) - (.+?)(?: - (.+))?$', flags=re.S)
	m = regex_basic_fields.match(record)
	if m is None:
		return None
	rslt['date'] = m.group(1)
	rslt['opcode'] = m.group(2)
	rslt['oplabel'] = m.group(3)
	rslt['additional_data'] = m.group(4)
	#if additional_data is not None:
	return rslt

#def filter_operation_field(json, field):
#	if field in json:
#		tab = get_list_from_html(json[field])
#		#print(tab)
#		for item in tab:
#			#print(item)
#			#print(json['_id'], item)
#			basic_fields = filter_record(item)
#			if basic_fields is None:
#				print('Soucy !')
#			elif basic_fields['opcode'] == '302':
#				print(basic_fields)

def fuzzy_lower_dates(d1, d2):
	"""Return a fuzzy lower relationship between to dates.
	Useful for structured exhibition fields vs heuristic exhibitions from operations field range dates matching."""
	if d1 < d2:
		return 1.0
	if d1.year == d2.year:
		if d1.month == d2.month:
			return 0.7
		else:
			return 0.3
	else:
		return 0.0

def tag_one_expo_with_folder(exposition, ope_info):
	"""Tag one exhibition from a structured exhibition field with a category,
	using an op_info dict.
	op_info = { 'folder code':`return from get_from_operation_expo_heuristic_range called on that folder`, ... }
	Returns [(folder, basic_expo, start_date_expo, end_date_expo, max_score), ...],
	where basic_expo is the dict returned by get_expo_title_other."""
	expo_list = []
	basic_expo = get_expo_title_other(exposition)
	if basic_expo is not None:
		#print('Coucou')
		#dico_count += 1
		#print(basic_expo['title'])
		for folder, heuristics in ope_info.items():
			if basic_expo['title'] in heuristics:# and folder_dict[dico['title']][1] in dico['other']:#2nd condition: maybe, maybe not
				place_time_list = get_expo_place_time(basic_expo['other'])
				for place_time in place_time_list:
					if place_time is not None and place_time['time'] is not None:
						tab = extract_date(place_time['time'])
						for item in tab:# TODO Work on that !
							item[1] = '12' if item[1] == '00' else item[1]
							item[2] = '28' if item[2] == '00' else item[2]#28 because February
						start_date_expo = datetime.date(int(tab[0][0]), int(tab[0][1]), int(tab[0][2]))
						end_date_expo = datetime.date(int(tab[1][0]), int(tab[1][1]), int(tab[1][2]))
						#date alignment
						max_score = 0.0
						max_ope = None
						#print('Dah')
						for ope_date in heuristics[basic_expo['title']]:
							if ope_date[0] != '...' and ope_date[0] != '':
								start_date_raw = ope_date[0].split('/')
								start_date_raw[1] = '1' if start_date_raw[1] == '00' else start_date_raw[1]
								start_date_raw[2] = '1' if start_date_raw[2] == '00' else start_date_raw[2]
								#try:
								start_date_ope = datetime.date(int(start_date_raw[0]), int(start_date_raw[1]), int(start_date_raw[2]))
								#except:
								#	print(start_date_raw)
								#	raise
#								if start_date_raw != '' else datetime.date(1,1,1) # typically: didn't catch last expo before it goes to 211I
							else:
								start_date_ope = datetime.date(1, 1, 1)
							if ope_date[1] != '...':
								end_date_raw = ope_date[1].split('/')
								end_date_raw[1] = '12' if end_date_raw[1] == '00' else end_date_raw[1]
								end_date_raw[2] = '28' if end_date_raw[2] == '00' else end_date_raw[2]
								end_date_ope = datetime.date(int(end_date_raw[0]), int(end_date_raw[1]), int(end_date_raw[2]))
							else:
								end_date_ope = datetime.date.today()
							#print(basic_expo['title'], start_date_ope.isoformat(), end_date_ope.isoformat())
							#if start_date_ope < start_date_expo and end_date_expo < end_date_ope:
							#	print('M20', basic_expo['title'], start_date_ope.isoformat(), start_date_expo.isoformat(), end_date_expo.isoformat(), end_date_ope.isoformat())
							cur_score = fuzzy_lower_dates(start_date_ope, start_date_expo) * fuzzy_lower_dates(end_date_expo, end_date_ope)
							if cur_score > max_score:
								max_score = cur_score
								max_ope = ope_date
						if max_score > 0.0:
							#print('M20', basic_expo['title'], max_ope[0].replace('/', '-'), start_date_expo.isoformat(), end_date_expo.isoformat(), max_ope[1].replace('/', '-'))
							expo_list.append((folder, basic_expo, start_date_expo, end_date_expo, max_score))
	return expo_list

def tag_expo_with_folder(json, folder_list):
	"""Apply tag_one_expo_with_folder on multiple structure exhibitions field records."""
	#folder_dict = {}
	#opcount = 0
	#dico_count = 0
	#for operation in get_list_from_html(json["all_realized_operations_history"]):
	#	basic_fields = filter_operation_record(operation)
	#	if basic_fields is not None and basic_fields['additional_data'] is not None:
	#		if basic_fields['opcode'] == '302' and 'M20' in basic_fields['additional_data']:
	#			m = re.match('.+ - M20 - (.+)$', basic_fields['additional_data'])
	#			if m is not None:
	#				folder_dict[m.group(1)] = ('M20', basic_fields['date'][0:4])
	#				opcount += 1
	ope_info = {}
	expo_list = []
	for folder, anchor_ope in folder_list.items():
		#print(folder)
		ope_info[folder] = get_from_operation_expo_heuristic_range(get_list_from_html(json['all_realized_operations_history']), anchor_ope[0], anchor_ope[1], folder, 0, 0)
	#print(ope_info)
	#print(ope_info)
	#print(ope_dates)
	for exposition in get_list_from_html(json['expositions_without_current']):
		#print('Yah')
		expo_list += tag_one_expo_with_folder(exposition, ope_info)
	return expo_list
				#print(basic_expo['title'], 'M20', ope_info[basic_expo['title']])#folder_dict[basic_expo['title']][0])
	#		else:
	#			print(dico['title'],'$',sep='')
	#print(folder_dict)
	#return (opcount, dico_count)

#def get_operation_expo_title(operation):
#	regex_operation_title = re.compile('.+ - [MI][0-9]{2} - (.+)$')
#	m = regex_operation_title.match(operation)
#	if m is None:
#		return None
#	else:
#		return m.group(1)

def get_from_operation_expo_heuristic_range(field, opcode_start_list, opcode_end_list, opcode_trip_list, folder_category, year_limit = 0, complete_range = 0):
	#operation_list = get_list_from_html(field)
	operation_list = field
	#print(operation_list)
	# Order: last operation first
	#print('230E' in opcode_start_list, opcode_end_list)
	in_range = False
	in_end = False
	in_start = False
	range_dates = {}
	#today_date = datetime.date.today().isoformat().replace('-', '/')
	end_date = ''
	start_date = ''
	current_expo = ''
	current_offset = 0
	#missing_title = False
	for operation in operation_list:
		opdict = filter_operation_record(operation)
		if opdict['additional_data'] is not None and folder_category in opdict['additional_data']:
			if int(opdict['date'][0:4]) < year_limit:
				if not in_range:
					return range_dates
				else:
					if not complete_range:
						return range_dates
					#elif complete_range < 0:
						#range_dates.append('...', end_date)
						#for key, item in range_dates.items():
						#	if item[0] == '':
						#		item[0] = '...'
					#	range_dates[current_expo][0] = '...'
					#	return range_dates
			title = get_operation_expo_title(operation)
			#print(range_dates)
			if title is None:
				title = ''
			if opdict['opcode'] not in opcode_trip_list and ((opdict['opcode'] in opcode_start_list and in_start) or (opdict['opcode'] in opcode_end_list and in_end)):
				if opdict['opcode'] in opcode_end_list and in_end and title == current_expo:#Narrow the range
					range_dates[title][current_offset][0] = opdict['date']
				continue
			#elif opdict['opcode'] not in opcode_start_list and opdict['opcode'] not in opcode_end_list:
			#	in_end = in_start = False
			if (opdict['opcode'] in opcode_start_list and in_range) or (opdict['opcode'] in opcode_end_list and (not in_range or (in_range and not in_start and not in_end))):
				if opdict['opcode'] in opcode_start_list and in_range:
					in_end = False
					start_date = opdict['date']
					#range_dates.append((start_date, end_date))
					#if missing_title:
					#	range_dates[title] = [[start_date, end_date]]
					#else:
					#	range_dates[title][current_offset][0] = start_date
					# Tracking trip exhibitions, where title can be different
					if title == current_expo:#No brain
						range_dates[title][current_offset][0] = start_date
					else:
						range_dates[current_expo][current_offset][0] = start_date
					#missing_title = True if opdict['opcode'] in opcode_trip_list else False
					in_start = True if opdict['opcode'] not in opcode_trip_list else False
					in_range = False
					# ***DEBUG***
					#print(range_dates)
				if opdict['opcode'] in opcode_end_list and (not in_range or (in_range and not(in_start or in_end))):
				# Not elif because trip opcodes must go there too
				# (not in_start and not in_end) because we want to catch trips with partial departure info
					in_start = False
					if in_range and not(in_start or in_end): #We must complete previous trip
						#print(opdict)
						range_dates[current_expo][current_offset][0] = opdict['date']
					end_date = opdict['date']
					if title not in range_dates:
						range_dates[title] = [['', end_date]]
						current_offset = 0
					else:
						range_dates[title].append(['', end_date])
						current_offset = len(range_dates[title])-1
					in_range = True
#					if opdict['opcode'] not in opcode_trip_list:
#						in_end = True
					in_end = True if opdict['opcode'] not in opcode_trip_list else False
					current_expo = title
			elif opdict['opcode'] in opcode_start_list and not in_range:
				if range_dates == {}:#still in the expo now
					range_dates[title] = [[opdict['date'], '...']]
				elif title != current_expo: #didn't trace the older return, but we have the departure
					if title not in range_dates:
						range_dates[title] = [[opdict['date'], range_dates[current_expo][current_offset][0]]] # heuristic
					else:
						range_dates[title].append([opdict['date'], range_dates[current_expo][current_offset][0]])
				else:
					print(opdict)
					raise RuntimeWarning
				current_expo = title
				current_offset = 0
				in_start = True if opdict['opcode'] not in opcode_trip_list else False
				in_range = not in_start
			elif opdict['opcode'] in opcode_end_list and in_range:
				print(opdict)
				raise RuntimeWarning
	return range_dates

def get_state_range(doc):
	start_date = ''
	end_date = ''
	ope_list = []
	location = '??'
	init_passed = False
	init_opcodes = ('220I', '220E', '299I', '299E')
	change_state = {'212I':'MNAM (accrochage)', '213I':'MNAM',\
	'221I':'MNAM', '241I':'MNAM (dépôt)', '242I':'MNAM', '260I':'MNAM (réserve)',\
	'261I':'MNAM', '262I':'MNAM (déménagement)', '210E':'Ext', '212E':'Ext (accrochage)',\
	'213E':'Ext', '240E':'Ext (itinérance)'}#...
	state_ranges = {}
	operation_list = reversed(get_list_from_html(doc["all_realized_operations_history"]))
	for index, operation in enumerate(operation_list):
		op_dict = filter_operation_record(operation)
		if not index:
			start_date = op_dict['date']
		if not init_passed and op_dict['opcode'] in init_opcodes:
			if ope_list != []:
				end_date = op_dict['date']
				state_ranges[(start_date, end_date)] = (location, ope_list)
				ope_list = []
				start_date = op_dict['date']
				end_date = ''
			else:
				start_date = op_dict['date']
			if op_dict['opcode'][-1] == 'E':
				location = 'Ext (init)'
			elif op_dict['opcode'][-1] == 'I':
				location = 'MNAM (init)'
			init_passed = True
		if op_dict['opcode'] in change_state:
			end_date = op_dict['date']
			state_ranges[(start_date, end_date)] = (location, ope_list)
			location = change_state[op_dict['opcode']]
			ope_list = []
			start_date = op_dict['date']
			end_date = ''
		ope_list.append(op_dict)
	return state_ranges

#if len(sys.argv) < 2:
#	sys.exit('Usage: '+sys.argv[0]+' [destinationCSVfile]')

#if __name__ == "main":
#field_dict = {"all_realized_operations_history":1, "expositions_without_current":1}#, "hanging_history":1, "expositions_without_current":1, "expositions":1}
#c = pymongo.MongoClient()
#cursor = c.myproject.Artwork.find({'_id':'150000000030904'},field_dict)#'_id':'150000000030904', 150000000461389
#opc = 0
#dc = 0
#folder_list = {'M20':('230E', '221I'), 'M22':('230E', '221I'), 'M25':('230E', '221I'), 'M29':('230E', '221I'), 'M30':('230E', '221I'), 'M32':('230E', '221I'), 'M36':('230E', '221I'), 'M99':('230E', '221I')}#, 'M34':('212I', '213I')
#for doc in cursor:
#	if "all_realized_operations_history" in doc and "expositions_without_current" in doc:
#		print(tag_expo_with_folder(doc, folder_list))
	#print(get_state_range(doc))
#print(tu)
#	opc += tu[0]
#	dc += tu[1]
#print(opc, dc)
	#filter_field(doc, "all_realized_operations_history")
		#print(doc)
	#expos_operation = get_from_operation_expo_heuristic_range(doc['all_realized_operations_history'], '230E', '221I', 'M20', 0, 0)
