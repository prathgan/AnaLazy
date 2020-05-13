# https://github.com/smoqadam/PyFladesk
from pyfladesk import init_gui

import os
from os import listdir
from os.path import isfile, join
import sys

import random, threading, webbrowser

from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_dropzone import Dropzone

import pandas
import sklearn

from process_dash_posts import process_post
from helpers import get_non_features

# import data quality analysis functions
import accuracy
import completeness
import consistency
import currency
import uniqueness
import utilities

# import page-based functions
import upload_fns
import train_fns

#import ML models
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.secret_key = 'devkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    # DROPZONE_ALLOWED_FILE_TYPE='image',
    # DROPZONE_MAX_FILE_SIZE=3,
    # DROPZONE_MAX_FILES=30,
)

dropzone = Dropzone(app)

@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    warning=None
    if request.method == 'POST':
        warning = upload_fns.save_file(request, app.config['UPLOADED_PATH'])
    files = upload_fns.get_file_list()
    return render_template('upload.html',filelist=files, warning=warning)

@app.route('/train', methods=['POST', 'GET'])
def train():
    print(request.form)
    print(session)
    if request.form.get('filechoice') != None:
        train_fns.process_filechoice(request)

    if request.form.get('features_submit') is not None:
        train_fns.select_features(request)
    
    try:
        return render_template('train.html', filelist = upload_fns.get_file_list(), filechoice=session['filechoice'],\
        column_headers = session['column_headers'], feature_names = session['feature_names'])
    except:
        return render_template('train.html', filelist = upload_fns.get_file_list(), feature_names = None)

"""
@app.route('/train', methods=['POST', 'GET'])
def train():
    files = upload_fns.get_file_list()

    try:
        temp = session['filechoice']
    except:
        session['filechoice'] = None
        session['feature_names'] = None
        session['selected_label'] = None
        session['label_options'] = None

    filechoice = request.form.get('filechoice')

    return render_template('train.html', filelist=files, filepick=filechoice)
"""

@app.route('/datadash_init')
def dashboard_init():
    path = "uploads/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.remove('.DS_Store')
    session['filechoice'] = None
    session['feature_names'] = None
    session['selected_label'] = None
    session['label_options'] = None
    return render_template('dashboard.html', filelist = files)

@app.route('/train_dep', methods=['POST', 'GET'])
def train_dep():

    print(session)

    files = None
    filepick = None
    warning = False
    column_headers = None

    try:
        feature_names = session['feature_names']
        label_options = session['label_options']
        selected_label = session['selected_label']
    except:
        session['filechoice'] = None
        session['feature_names'] = None
        session['selected_label'] = None
        session['label_options'] = None
        session['column_headers'] = None

    filechoice = request.form.get('filechoice')
    try:
        if filechoice != session['filechoice']:
            session['label_options'] = None
    except:
        pass

    if request.form.get('features_submit') is not None:
        feature_names = train_fns.get_feature_names(request)
        session['feature_names'] = feature_names
        label_options = get_non_features(session['column_headers'], feature_names)
        session['label_options'] = label_options

    if request.form.get('label_submit') is not None:
        session['selected_label'] = train_fns.get_selected_label(request)
        pass

    files = upload_fns.get_file_list()

    if not filechoice == None:
        if not filechoice[-3:]=='csv':
            warning = True
        else:
            df = pandas.read_csv("uploads/"+filechoice)
            session['df'] = df
            session['filechoice'] = filechoice
            column_headers = list(df)
            session['column_headers'] = column_headers
    else:
        filechoice = session['filechoice']
        column_headers = session['column_headers']
        

    return render_template('train.html', filelist = files, filepick = filechoice, \
        warning = warning, column_headers = column_headers, feature_names = session['feature_names'], \
        label_options = session['label_options'], selected_label = session['selected_label'])


#TODO: visual tracking of training progress
@app.route('/trainer', methods=['POST', 'GET'])
def trainer():

    show_params_selection = False

    if request.form.get('reselect_params') is not None:
        show_params_selection = True

    if request.form.get('model_submit') is not None:
        for key in request.form.keys():
            if not key == 'model_submit':
                session['model_selection'] = request.form.get(key)

    try:
        model_selection = session['model_selection']
    except:
        session['model_selection'] = None
    try:
        params_selections = session['params_selections']
    except:
        session['params_selections'] = None
    
    if session['params_selections'] == None:
        show_params_selection = True
    feature_names = session['feature_names']
    selected_label = session['selected_label']
    
    return render_template('trainer.html', feature_names = session['feature_names'],\
        selected_label = session['selected_label'], model_selection = session['model_selection'],\
        show_params_selection = True)

@app.route('/training', methods=['POST', 'GET'])
def training():

    session['mlpnn_type'] = request.form.get('mlpnn_type')
    session['solver_type'] = request.form.get('solver_type')
    session['hidden_layer_sizes'] = request.form.get('hidden_layer_sizes') if request.form.get('hidden_layer_sizes')!='' else "(100)"
    session['activation_function'] = request.form.get('activation_function')
    session['alpha'] = request.form.get('alpha') if request.form.get('alpha')!='' else 0.0001
    session['batch'] = request.form.get('batch') if request.form.get('batch')!='' else "auto"
    session['random_state'] = request.form.get('random_state') if request.form.get('random_state')!='' else "None"



    if session['model_selection'] == 'MLP Neural Network':
        return render_template('training.html', model_selection = session['model_selection'], \
            mlpnn_type=session['mlpnn_type'], solver_type=session['solver_type'], \
            hidden_layer_sizes=session['hidden_layer_sizes'], activation_function=session['activation_function'],\
            alpha = session['alpha'], batch = session['batch'], random_state = session['random_state'], e=None)

@app.route('/in_progress', methods=['POST', 'GET'])
def in_progress():
    
    clf = None
    X = None
    y = None

    if session['model_selection'] == 'MLP Neural Network':
        if session['mlpnn_type'] == 'classification':
            try:

                clf = eval("MLPClassifier(solver='"+session['solver_type']+"', hidden_layer_sizes="+session['hidden_layer_sizes']+\
                ", activation='"+session['activation_function']+"', alpha="+str(session['alpha'])+", batch_size='"+session['batch']+\
                "', random_state="+session['random_state']+")")
            
                X = []
                df = pandas.read_csv("uploads/"+session['filechoice'])
                y = df[session['selected_label']].tolist()
                for feature_name in session['feature_names']:
                    X.append(df[feature_name].tolist())
                X = list(zip(*X))

                clf.fit(X,y)

                session['clf'] = clf

            except Exception as e:
                return render_template('training.html', model_selection = session['model_selection'], \
                mlpnn_type=session['mlpnn_type'], solver_type=session['solver_type'], \
                hidden_layer_sizes=session['hidden_layer_sizes'], activation_function=session['activation_function'],\
                alpha = session['alpha'], batch = session['batch'], random_state = session['random_state'], e = e)

        if session['mlpnn_type'] == 'regression':
            clf = eval("MLPRegressor(solver='"+session['solver_type']+"', hidden_layer_sizes="+session['hidden_layer_sizes']+\
            ", activation='"+session['activation_function']+"', alpha="+str(session['alpha'])+", batch_size='"+session['batch']+\
            "', random_state="+session['random_state']+")")

            X = []
            df = pandas.read_csv("uploads/"+session['filechoice'])
            y = df[session['selected_label']].tolist()
            for feature_name in session['feature_names']:
                X.append(df[feature_name].tolist())
            X = list(zip(*X))

            clf.fit(X,y)

            session['clf'] = clf

    return render_template('apply.html', prediction_result=None)

#TODO: upload spreadsheet with unlabeled features and app labels them
#TODO: use feature names to create a form that allows you to enter features next to feature names (table-type thing)
@app.route('/apply', methods=['POST', 'GET'])
def apply():

    prediction_features = request.form.get('prediction_features')
    prediction_features_list = eval(prediction_features)
    clf = session['clf']

    prediction_result = None
    if prediction_features != None:
        prediction_result = eval("clf.predict("+prediction_features+")")
        prediction_result = list(zip(prediction_features_list, prediction_result))

    return render_template('apply.html', prediction_result = prediction_result)

@app.route('/models')
def models():
    return "store trained models here"

if __name__ == '__main__':
    if 'web' in sys.argv:
        if 'debug' in sys.argv:
            app.run(debug=True)
        else:
            port = 5000
            url = "http://127.0.0.1:{0}".format(port)
            threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
            app.run(debug=False)
    elif 'gui' in sys.argv:
        init_gui(app, window_title="AnaLazy")
    else:
        init_gui(app, window_title="AnaLazy", width=1000, height=800)
