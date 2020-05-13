import pandas as pd
import math

def empty_counts(df):
	col_names = df.columns
	incomplete_counts = {}
	for col_name in col_names:
		incomplete_counts.update({col_name : 0})
	for row in df.itertuples():
		for col_name in col_names:
			try:
				if pd.isnull(eval("row."+col_name)):
					incomplete_counts.update({col_name : int(incomplete_counts.get(col_name))+1})
			except:
				pass
	return incomplete_counts

# overloaded method, returns in format empty inds, empty ids if id_col is provided
def col_empty_locs(df, col_name, id_col = None):
	empty_inds = []
	empty_ids = []
	index = 0
	for row in df.itertuples():
		if pd.isnull(eval("row."+col_name)):
			empty_inds.append(index)
			if id_col != None:
				empty_ids.append(df.iloc[index].loc[id_col])
		index += 1
	if id_col == None: return empty_inds
	else: return empty_ids

