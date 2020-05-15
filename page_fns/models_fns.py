import os
from os import listdir
from os.path import isfile, join
import sys

def get_models_list():
    path = "models/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    try:
        files.remove('.DS_Store')
    except:
        pass
    for f in files:
        f = f[:-7]
    return files