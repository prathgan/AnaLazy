def get_feature_names(request):
    feature_names = []
    for feature_name in request.form.keys():
        if feature_name != 'features_submit':
            feature_names.append(feature_name)
    return feature_names

def get_selected_label(request):
    for key in request.form.keys():
        if not key == 'label_submit':
            return key[:-6]