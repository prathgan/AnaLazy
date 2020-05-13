import pandas as pd
import collections

def dup_row_count(df):
	try:
		return df.duplicated().value_counts()[True]
	except:
		return 0

def dup_row_locs(df, id_col=None):
	dups = df.duplicated()
	dup_inds = dups[dups == True]
	if id_col != None:
		dup_ids = []
		index = 0
		for dup in dup_inds:
			dup_ids.append(df.iloc[index, id_col])
			index += 1
		return dup_ids
	else:
		return dup_inds

def dup_elems(df, col_name, id_col=None):
	a = df[col_name].tolist()
	return [item for item, count in collections.Counter(a).items() if count > 1]
