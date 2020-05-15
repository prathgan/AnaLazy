from flask import session, redirect, url_for, jsonify
import pandas
from multiprocessing import Process
import pickle

#import ML models
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor

def process_filechoice(request):
    session['filechoice'] = request.form.get('filechoice')
    df = pandas.read_csv("uploads/"+session['filechoice'])
    session['column_headers'] = list(df)

def init_vars():
    session['feature_names'] = None
    session['selected_label'] = None
    session['label_options'] = None
    session['column_headers'] = None
    session['filechoice'] = None
    session['model_selection'] = None
    session['model_params'] = None

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

def get_non_features(column_headers, feature_names):
	return list(set(column_headers) - set(feature_names))

def get_model_selection(request):
    for key in request.form.keys():
        if not key == 'model_submit':
            session['model_selection'] = request.form.get(key)

def set_mlpnn_params(request):
    mlpnn_type = request.form.get('mlpnn_type')
    solver_type = request.form.get('solver_type')
    hidden_layer_sizes = request.form.get('hidden_layer_sizes') if request.form.get('hidden_layer_sizes')!='' else "(100)"
    activation_function = request.form.get('activation_function')
    alpha = request.form.get('alpha') if request.form.get('alpha')!='' else 0.0001
    batch = request.form.get('batch') if request.form.get('batch')!='' else "auto"
    random_state = request.form.get('random_state') if request.form.get('random_state')!='' else "None"
    session['model_params'] = {'MLP Type' : mlpnn_type, 'Solver' : solver_type, 'Hidden Layer Sizes' : hidden_layer_sizes,\
        'Activation Function' : activation_function, 'Alpha' : alpha, 'Batch Size' : batch, 'Random State' : random_state}

def get_name(request):
    for key in request.form.keys():
        if not key == 'name_submit':
            session['model_name'] = request.form.get(key)

def train_model(sess):
    clf = None
    X = None
    y = None

    if session['model_selection'] == 'MLP Neural Network':
        if (session['model_params']).get('MLP Type') == 'classification':
            print("YAYAYAYAY WE GOT IT")
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

                

            except Exception as e:
                return e
            
            return None

        if session['mlpnn_type'] == 'regression':
            try:
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

                
            
            except Exception as e:
                return e
            
            return None

def run_in_parallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()