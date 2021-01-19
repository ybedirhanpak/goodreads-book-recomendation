import math
import time
import utils
from preprocess import BookPreprocessor


class BookVectorizer():
    def __init__(self, preprocessor=None) -> None:
        self.preprocessor: BookPreprocessor = preprocessor
        self.book_count = len(self.preprocessor.books)
        self.book_vectors = {}

    def get_tf_weight(self, word, book):
        word_book_pair = (word, book.url)
        tf_weight = 0
        if word_book_pair in self.preprocessor.term_frequency:
            tf = self.preprocessor.term_frequency[(word, book.url)]
            tf_weight = 1 + (math.log10(tf))
        return tf_weight

    def get_idf_weight(self, word):
        idf_weight = 0
        if word in self.preprocessor.doc_frequency:
            df = self.preprocessor.doc_frequency[word]
            idf_weight = math.log10(self.book_count/df)
        return idf_weight

    def get_tf_idf_weight(self, word, book):
        return self.get_tf_weight(word, book) * self.get_idf_weight(word)

    def vectorize_books(self):
        start_time = time.time()
        for book in self.preprocessor.books.values():
            # Calculate vector
            vector = [self.get_tf_idf_weight(
                word, book) for word in self.preprocessor.vocabulary_list]
            self.book_vectors[book.url] = vector
        utils.pickle_object(self.book_vectors, "out/pickle/book_vectors.pickle")
        end_time = time.time()
        print(f"It took {end_time - start_time} seconds to vectorize books")
