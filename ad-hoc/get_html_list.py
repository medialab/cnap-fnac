import re

def get_list_from_html(field):
	regex_item = re.compile('<li>(.*?)<\/li>', flags=re.S)
	tab = regex_item.split(field)
	new_tab = []
	for item in tab:
		if len(item) > 0 and 'ul>' not in item and item != '\n':
			new_tab.append(item)
	return new_tab