# https://github.com/smoqadam/PyFladesk
from pyfladesk import init_gui

import os
from os import listdir
from os.path import isfile, join
import sys

import pickle

import random, threading, webbrowser

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from flask_dropzone import Dropzone

from threading import Thread

import pandas
import sklearn

# import data quality analysis functions
from data_quality.accuracy import * 
from data_quality.completeness import *
from data_quality.consistency import *
from data_quality.currency import *
from data_quality.uniqueness import *
from data_quality.utilities import *

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

@app.route('/train_err', methods=['POST', 'GET'])
def train_err():
    pass

@app.route('/train_done', methods=['POST', 'GET'])
def train_done():
    return render_template('training_done.html', finished = True, model_name = session['model_name'], e = None)

# TODO: add delete model function
@app.route('/models', methods=['POST', 'GET'])
def models():
    prediction = None
    models_list = models_fns.get_models_list()
    if request.form.get('filechoice') is not None:
        models_fns.process_model_choice(request)
    if request.form.get('apply_submit') is not None:
        prediction = models_fns.make_prediction(request)

    try:
        return render_template('models.html', models_list = models_list, modelchoice = session['model_apply_choice'],\
            features = session['active_features'], label = session['active_label'], prediction = prediction)
    except:
        return render_template('models.html', models_list = models_list, prediction = None)

@app.route('/quality')
def quality():
    return render_template('quality.html')


@app.route('/status')
def thread_status():
    return jsonify(dict(status=('finished' if finished else 'running')))

@app.route('/qual_run', methods=['POST', 'GET'])
def qual_run():
    command = request.args['data']
    result = None
    try:
        result = eval(command)
        if result != None:
            result = str(result)
    except:
        try:
            exec(command)
        except Exception as e:
            result = str(e)
    return "completed" if result == None else result

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
    if '--web' in sys.argv:
        if '--debug' in sys.argv:
            app.run(debug=True)
        else:
            port = 5000
            url = "http://127.0.0.1:{0}".format(port)
            threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
            app.run(debug=False)
    elif '--gui' in sys.argv:
        init_gui(app, window_title="AnaLazy")
    else:
        init_gui(app, window_title="AnaLazy", width=1000, height=800)




#TODO: upload spreadsheet with unlabeled features and app labels them
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