import os
from os import listdir
from os.path import isfile, join
import sys

from flask import session
import pickle

def get_models_list():
    path = "models/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    temp = []
    try:
        files.remove('.DS_Store')
    except:
        pass
    for f in files:
        temp.append(f[:-7])
    return temp

def process_model_choice(request):
    session['model_apply_choice'] = request.form.get('filechoice')
    session['active_clf'] = pickle.load( open( "models/"+request.form.get('filechoice')+".pickle", "rb" ) )
    session['active_features'] = session['active_clf'].feature_names
    session['active_label'] = session['active_clf'].label_name

def make_prediction(request):
    temp = []
    for key in request.form:
        if key == 'apply_submit':
            pass
        else:
            temp.append(float(request.form.get(key)))
    print(temp)
    return session['active_clf'].predict([temp])
