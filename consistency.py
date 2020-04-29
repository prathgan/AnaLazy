import pandas as pd
import math

# ask user to give an expression to check for completeness and then use exec()
# OVERLOADED
def col_form_check(df, col_name, condition, id_col = None):
	issue_inds = []
	issue_ids = []
	index = 0
	for row in df.itertuples():
		cell_content = eval("row."+col_name)
		try:
			if eval(condition):
				pass
			else:
				issue_inds.append(index)
				if id_col != None:
					issue_ids.append(df.iloc[index].loc[id_col])
		except:
			print("issue at index " + str(index) + " with value " + str(cell_content))
		index += 1
	if id_col == None: return issue_inds
	else: return issue_ids

def get_uniques(df):
	col_names = df.columns
	uniques = {}
	for col_name in col_names:
		try:
			uniques.update({col_name : get_uniques_col(df, col_name)})
		except:
			pass
	return uniques

def get_uniques_col(df, col_name):
	return eval('df.'+col_name+'.unique()')