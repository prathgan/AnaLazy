def get_non_features(column_headers, feature_names):
	return list(set(column_headers) - set(feature_names))