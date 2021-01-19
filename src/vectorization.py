import math
import time
import utils
from functools import reduce
from preprocess import BookPreprocessor
from typing import List


class Vector():
    def __init__(self, vocabulary_size):
        self.weight_dict = {}
        self.vocabulary_size = vocabulary_size

    def add_index_weight(self, index: int, weight: float):
        self.weight_dict[index] = weight

    def __str__(self):
        return repr(self.weight_dict)

    def get_size(self):
        return math.sqrt(sum([x ** 2 for x in self.weight_dict.values()]))

    def get_cross_product(self, other_vector):
        return sum([self.weight_dict[key] * other_vector.weight_dict[key] for key in self.weight_dict.keys() if key in other_vector.weight_dict.keys()])

    def calculate_similarity(self, other_vector):
        cross_product = self.get_cross_product(other_vector)
        size_product = self.get_size() * other_vector.get_size()
        if size_product == 0:
            return 0
        print(f"Cross product: {cross_product}, self size: {self.get_size()}, other size: {other_vector.get_size()}")
        return cross_product / size_product


class BookVectorizer():
    def __init__(self,
                 preprocessor=None,
                 books_pickle="out/books.pickle",
                 vocabulary_pickle="out/vocabulary.pickle",
                 ie_pickle="out/ie.pickle",
                 tf_pickle="out/tf.pickle",
                 df_pickle="out/df.pickle",
                 book_vectors_pickle="out/book_vectors.pickle"):
        self.preprocessor: BookPreprocessor = preprocessor
        if self.preprocessor != None:
            self.books = self.preprocessor.books
            self.vocabulary_list = self.preprocessor.vocabulary_list
            self.inverted_index = self.preprocessor.inverted_index
            self.term_frequency = self.preprocessor.term_frequency
            self.doc_frequency = self.preprocessor.doc_frequency
        else:
            self.books = utils.unpickle_object(books_pickle)
            self.vocabulary_list = utils.unpickle_object(vocabulary_pickle)
            self.inverted_index = utils.unpickle_object(ie_pickle)
            self.term_frequency = utils.unpickle_object(tf_pickle)
            self.doc_frequency = utils.unpickle_object(df_pickle)
        self.book_vectors_pickle = book_vectors_pickle
        self.book_count = len(self.books)
        self.book_vectors = {}

    def get_tf_weight(self, word, book_url, tf_dict: dict):
        word_book_pair = (word, book_url)
        tf_weight = 0
        if tf_dict and word in tf_dict:
            tf = tf_dict[word]
            tf_weight = 1 + (math.log10(tf))
        elif word_book_pair in self.term_frequency:
            tf = self.term_frequency[(word, book_url)]
            tf_weight = 1 + (math.log10(tf))
        return tf_weight

    def get_idf_weight(self, word):
        idf_weight = 0
        if word in self.doc_frequency:
            df = self.doc_frequency[word]
            idf_weight = math.log10(self.book_count/df)
        return idf_weight

    def get_tf_idf_weight(self, word, book_url):
        return self.get_tf_weight(word, book_url, None) * self.get_idf_weight(word)

    def vectorize_book(self, book_url):
        vector = Vector(len(self.vocabulary_list))
        for index, word in enumerate(self.vocabulary_list):
            tf_idf_weight = self.get_tf_idf_weight(word, book_url)
            if tf_idf_weight > 0:
                vector.add_index_weight(index, tf_idf_weight)
        return vector

    def vectorize_query_book(self, book_url, list_of_words: List[str]):
        term_frequencies = {word: list_of_words.count(
            word) for word in list_of_words if word in self.vocabulary_list}

        vector = Vector(len(self.vocabulary_list))
        for index, word in enumerate(self.vocabulary_list):
            tf_idf_weight = self.get_tf_weight(
                word, book_url, term_frequencies) * self.get_idf_weight(word)
            if tf_idf_weight > 0:
                vector.add_index_weight(index, tf_idf_weight)

        return vector

    def vectorize_books(self):
        start_time = time.time()
        for book_url in self.books.keys():
            # Calculate vector
            vector = self.vectorize_book(book_url)
            self.book_vectors[book_url] = vector
        utils.pickle_object(self.book_vectors, self.book_vectors_pickle)
        end_time = time.time()
        print(f"It took {end_time - start_time} seconds to vectorize books")
