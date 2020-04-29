# https://github.com/smoqadam/PyFladesk
from pyfladesk import init_gui

import os
from os import listdir
from os.path import isfile, join

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
def upload():
    path = "uploads/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.remove('.DS_Store')
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    else:
        return render_template('upload.html',filelist=files)

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

@app.route('/datadash', methods=['POST', 'GET'])
def datadash():

    files = None
    filepick = None
    warning = False
    column_headers = None
    feature_names = session['feature_names']
    label_options = session['label_options']
    selected_label = session['selected_label']

    filechoice = request.form.get('filechoice')

    if request.form.get('features_submit') is not None:
        feature_names = []
        for feature_name in request.form.keys():
            if feature_name != 'features_submit':
                feature_names.append(feature_name)
        session['feature_names'] = feature_names
        label_options = get_non_features(session['column_headers'], feature_names)
        session['label_options'] = label_options

    if request.form.get('label_submit') is not None:
        for key in request.form.keys():
            if not key == 'label_submit':
                selected_label = key[:-6]
        session['selected_label'] = selected_label
        return redirect(url_for('trainer'))

    path = "uploads/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.remove('.DS_Store')

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
        

    return render_template('dashboard.html', filelist = files, filepick = filechoice, \
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
        init_gui(app, window_title="AnaLazy")
