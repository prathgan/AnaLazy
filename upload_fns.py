def get_file_list():
    path = "uploads/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.remove('.DS_Store')
    return files