from typing import List
import utils
import time
from book import Book


class BookPreprocessor():
    def __init__(self,
                 books_pickle="out/books.pickle",
                 vocabulary_pickle="out/vocabulary.pickle",
                 ie_pickle="out/ie.pickle",
                 tf_pickle="out/tf.pickle",
                 df_pickle="out/df.pickle"
                 ):
        # Pickle file locations
        self.books_pickle = books_pickle
        self.vocabulary_pickle = vocabulary_pickle
        self.ie_pickle = ie_pickle
        self.tf_pickle = tf_pickle
        self.df_pickle = df_pickle

        self.books = {}
        self.vocabulary = set()
        self.inverted_index = {}
        self.term_frequency = {}
        self.doc_frequency = {}

    def __tokenize_text(self, text: str):
        # Remove punctuation of the document
        normalized_text = utils.normalize_doc(text)

        token_list = []

        # Preprocess each token in the document
        for token in normalized_text.split(" "):
            # Normalize the token
            n_token = utils.normalize_token(token)

            # Skip empty characters
            if n_token == '':
                continue

            token_list.append(n_token)

        return token_list

    def tokenize_description(self, book: Book) -> List[str]:
        return self.__tokenize_text(book.description)

    def tokenize_genres(self, book: Book) -> List[str]:
        return [' '.join(self.__tokenize_text(genre)) for genre in book.genres]

    def __preprocess_book(self, book: Book):
        book_id = book.url
        book_content = book.title + " " + book.description

        # Remove punctuation of the document
        normalized_doc = utils.normalize_doc(book_content)

        # Preprocess each token in the document
        for token in normalized_doc.split(" "):
            # Normalize the token
            n_token = utils.normalize_token(token)

            # Skip empty characters
            if n_token == '':
                continue

            # Add token into vocabulary
            self.vocabulary.add(n_token)

            # Add document into inverted index
            if n_token not in self.inverted_index:
                self.inverted_index[n_token] = {book_id}
            else:
                self.inverted_index[n_token].add(book_id)

            word_book_pair = (n_token, book_id)

            # Add 1 to frequency of a word occurrence in a book
            if word_book_pair not in self.term_frequency:
                self.term_frequency[word_book_pair] = 1
                # Add 1 to document frequency
                if n_token not in self.doc_frequency:
                    self.doc_frequency[n_token] = 1
                else:
                    self.doc_frequency[n_token] += 1
            else:
                self.term_frequency[word_book_pair] += 1

    def preprocess_books(self):
        start_time = time.time()
        self.books: dict = utils.unpickle_object(self.books_pickle)
        for book in self.books.values():
            self.__preprocess_book(book)

        self.vocabulary_list = list(self.vocabulary)

        utils.pickle_object(self.vocabulary_list, self.vocabulary_pickle)
        utils.pickle_object(self.inverted_index, self.ie_pickle)
        utils.pickle_object(self.doc_frequency, self.df_pickle)
        utils.pickle_object(self.term_frequency, self.tf_pickle)

        end_time = time.time()
        print(f"It took {end_time - start_time} seconds to preprocess books")
