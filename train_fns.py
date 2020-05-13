from flask import session
import pandas
from helpers import get_non_features

def process_filechoice(request):
    session['filechoice'] = request.form.get('filechoice')
    df = pandas.read_csv("uploads/"+session['filechoice'])
    session['df'] = df
    session['column_headers'] = list(df)
    session['feature_names'] = None

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

def select_features(request):
    feature_names = get_feature_names(request)
    session['feature_names'] = feature_names
    label_options = get_non_features(session['column_headers'], feature_names)
    session['label_options'] = label_options