import os
import pickle


def create_dir(dir_name: str):
    if not os.path.exists(get_file_path(dir_name)):
        os.makedirs(get_file_path(dir_name))


def get_file_path(file_name: str):
    return os.path.join(os.path.dirname(__file__), file_name)


def file_exists(file_name):
    return os.path.isfile(get_file_path(file_name))


def run_threads_and_wait(threads: list):
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def pickle_object(object, location):
    with open(get_file_path(location), 'wb') as file:
        pickle.dump(object, file, protocol=pickle.HIGHEST_PROTOCOL)


def unpickle_object(location):
    with open(get_file_path(location), 'rb') as file:
        obj = pickle.load(file)
    return obj
