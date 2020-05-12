import os
from os import listdir
from os.path import isfile, join
import sys

def get_file_list():
    path = "uploads/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.remove('.DS_Store')
    return files

def save_file(request, path):
    f = request.files.get('file')
    if f.filename[-3]!='csv':
        return True
    f.save(os.path.join(path, f.filename))
    return False