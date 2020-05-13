import pandas as pd
import math
from datetime import datetime
# UNCOMMENT FOR USE: from textblob import TextBlob

# OVERLOADED
def import_excel(path, ws_name = None):
	if ws_name == None:
		return pd.read_excel(path)
	else:
		return pd.read_excel(pd.ExcelFile(path), ws_name)

def describe(df):
	return df.describe()

# dates as string in FORMAT: 
def dates_to_nums(list):
	index = 0
	new_list = []
	new_indices = []
	for date in list:
		try:
			new_list.append(datetime.fromisoformat(str(date)).timestamp())
			new_indices.append(index)
			index+=1
		except:
			index+=1
	return new_indices, new_list

def match_cells(df, col_name, condition, id_col = None):
	target_inds = []
	target_ids = []
	index = 0
	for row in df.itertuples():
		cell_content = eval("row."+col_name)
		if eval(condition):
			target_inds.append(index)
			if id_col != None:
				target_ids.append(df.iloc[index].loc[id_col])
		else:
			pass
		index += 1
	if id_col == None: return target_inds
	else: return target_ids

def spellcheck(word):
	return str(TextBlob(word).correct()) == word
