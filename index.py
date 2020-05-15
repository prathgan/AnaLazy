# https://github.com/smoqadam/PyFladesk
from pyfladesk import init_gui

import os
from os import listdir
from os.path import isfile, join
import sys

import random, threading, webbrowser

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from flask_dropzone import Dropzone

from threading import Thread

import pandas
import sklearn

# import data quality analysis functions
import data_quality.accuracy
import data_quality.completeness
import data_quality.consistency
import data_quality.currency
import data_quality.uniqueness
import data_quality.utilities

# import page-based functions
from page_fns import upload_fns, train_fns, models_fns

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
    # print(request.form)
    # print(session)
    try:
        if session['filechoice'] is not None:
            pass
    except:
        train_fns.init_vars()
        return render_template('train.html', filelist=upload_fns.get_file_list(), feature_names = None, selected_label = None, model_params = None)

    if request.form.get('filechoice') is not None:
        train_fns.process_filechoice(request)

    if request.form.get('features_submit') is not None:
        train_fns.select_features(request)
    
    if request.form.get('label_submit') is not None:
        session['selected_label'] = train_fns.get_selected_label(request)

    if request.form.get('model_submit') is not None:
        train_fns.get_model_selection(request)

    if request.form.get('mlpnn_type') is not None:
        train_fns.set_mlpnn_params(request)
    
    return render_template('train.html', filelist = upload_fns.get_file_list(), filechoice=session['filechoice'],\
        column_headers = session['column_headers'], feature_names = session['feature_names'], \
        selected_label = session['selected_label'], label_options = session['label_options'], \
        model_selection = session['model_selection'], model_params = session['model_params'])

@app.route('/training', methods=['POST', 'GET'])
def training():
    if request.form.get('name_submit') is not None:
        train_fns.get_name(request)
    
    global th
    global finished
    finished = False
    th = Train_Model()
    th.start()


    return render_template('training.html', finished = False, model_name = session['model_name'], e = None)
    
    # while training:
    # return render_template('training.html', finished = False, model_name = session['model_name'], e = None)

    # after training:
    # return render_template('training.html', finished = True, model_name = session['model_name'])

@app.route('/train_err', methods=['POST', 'GET'])
def train_err():
    pass

@app.route('/train_done', methods=['POST', 'GET'])
def train_done():
    return render_template('training_done.html', finished = True, model_name = session['model_name'], e = None)

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/quality')
def quality():
    return render_template('quality.html')


@app.route('/status')
def thread_status():
    return jsonify(dict(status=('finished' if finished else 'running')))

class Train_Model(Thread):
    def __init__(self):
        Thread.__init__(self)
        temp = {}
        for key, item in session.items():
            temp.update({key:item})
        self.temp = temp

    def run(self):
        global finished
        with app.test_request_context():
            train_fns.train_model(self.temp)
            finished = True


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




""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@app.route('/trainingold', methods=['POST', 'GET'])
def traininold():

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