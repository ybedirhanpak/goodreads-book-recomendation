import os
import pickle
import re

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"

BOOKS_BASE_URL = "https://www.goodreads.com/book/show/"


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


def normalize_doc(doc: str):
    '''
        Replaces non-alphabet characters with space character
    '''
    return re.sub(f'[^{ALPHABET}]', ' ', doc.lower()).strip()


def normalize_token(token: str):
    '''
        Normalizes given token by removing trailing spaces 
    '''
    return token.strip()


def compress_book_url(book_url: str):
    return book_url.replace(BOOKS_BASE_URL, "")


def decompress_book_url(compressed_url: str):
    return f"{BOOKS_BASE_URL}/{compressed_url}"
