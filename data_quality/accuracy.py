import pandas as pd
import math
from scipy import stats
import numpy as np
import statistics

# applies preprocess_fn to column to transform to numerical values in order to calculate outliers
# some built-in preprocessing functions include date_to_nums, 
# can adjust outlier_tolerance - how many stdevs away from mean outliers must be
def numerical_outliers(df, col_name, preprocess_fn=None, id_col=None, outlier_tolerance=2):
	outlier_inds = []
	outlier_ids = []
	col_as_list = None
	new_indices = None
	if preprocess_fn != None:
		new_indices, col_as_list = preprocess_fn(df[col_name].tolist())
	else:
		col_as_list = df[col_name].tolist()
	index = 0
	# print("HERE")
	# print(col_as_array)
	u = statistics.mean(col_as_list)
	s = statistics.stdev(col_as_list)
	for cell_val in col_as_list:
		if (u-outlier_tolerance*s > cell_val) or (cell_val > u+outlier_tolerance*s):
			if new_indices == None:
				outlier_inds.append(index)
				if id_col != None: outlier_ids.append(df.iloc[index].loc[id_col]) 
			else:
				outlier_inds.append(new_indices[index])
				if id_col != None: outlier_ids.append(df.iloc[new_indices[index]].loc[id_col])
		index += 1
	if id_col == None: return outlier_inds
	else: return outlier_ids

def col_form_check(df, col_name, condition, id_col = None):
	issue_inds = []
	issue_ids = []
	index = 0
	for row in df.itertuples():
		cell_content = eval("row."+col_name)
		if eval(condition):
			pass
		else:
			issue_inds.append(index)
			if id_col != None:
				issue_ids.append(df.iloc[index].loc[id_col])
		index += 1
	if id_col == None: return issue_inds
	else: return issue_ids