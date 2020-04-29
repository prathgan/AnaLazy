import pandas
from datetime import date, timedelta

def missing_dates(df, col_name):
	d = []
	col_rep = df[col_name]
	for cell in col_rep:
		d.append((cell.to_pydatetime()).date())
	date_set = set(d[0] + timedelta(x) for x in range((d[-1] - d[0]).days))
	missing = sorted(date_set - set(d))
	return missing