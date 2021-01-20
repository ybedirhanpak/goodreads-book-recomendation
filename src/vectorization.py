import math
import time
import utils
from book import Book
from typing import List, Tuple

DESCRIPTION_DATA_PICKLE = "out/pickle/description_data.pickle"
GENRE_DATA_PICKLE = "out/pickle/genre_data.pickle"


class Vector():
    def __init__(self, vocabulary_size):
        self.weight_dict = {}
        self.vocabulary_size = vocabulary_size

    def add_index_weight(self, index: int, weight: float):
        self.weight_dict[index] = weight

    def __str__(self):
        return repr(self.weight_dict)

    def __repr__(self) -> str:
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
        return cross_product / size_product

    def project(self, vocabulary) -> dict[str, str]:
        projection = {}
        for key, value in self.weight_dict.items():
            projection[key] = vocabulary
        return {vocabulary[key]: self.weight_dict[key] for key in self.weight_dict.keys()}


class BookData():
    def __init__(self, content_type: str) -> None:
        self.content_type = content_type
        self.vocabulary = set()
        self.inverted_index: dict[str, set] = {}
        self.term_frequency: dict[(str, str), int] = {}
        self.doc_frequency: dict[str] = {}

    def pickle(self, location: str):
        self.vocabulary = list(self.vocabulary)
        utils.pickle_object(self, location)


class BookPreprocessor():
    def __init__(self, books_dict: dict[str, Book] = None, books_dict_file: str = None):
        # If there is a file provided, use it to unpickle books dict
        if books_dict_file:
            self.books_dict = utils.unpickle_object(books_dict_file)
        else:
            self.books_dict = books_dict

        self.genre_data = BookData('genre')
        self.description_data = BookData('description')

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

    def preprocess_book_content(self, book: Book, content_type: str):
        book_url = book.url
        if content_type == 'description':
            # Description
            content_tokens = self.tokenize_description(book)
            book_data = self.description_data
        else:
            # Genre
            content_tokens = self.tokenize_genres(book)
            book_data = self.genre_data

        for token in content_tokens:
            # Add token into vocabulary
            book_data.vocabulary.add(token)

            # Add document into inverted index
            if token not in book_data.inverted_index:
                book_data.inverted_index[token] = {book_url}
            else:
                book_data.inverted_index[token].add(book_url)

            word_book_pair = (token, book_url)

            # Add 1 to frequency of a word occurrence in a book
            if word_book_pair not in book_data.term_frequency:
                book_data.term_frequency[word_book_pair] = 1
                # Add 1 to document frequency
                if token not in book_data.doc_frequency:
                    book_data.doc_frequency[token] = 1
                else:
                    book_data.doc_frequency[token] += 1
            else:
                book_data.term_frequency[word_book_pair] += 1

    def preprocess_book(self, book):
        self.preprocess_book_content(book, 'description')
        self.preprocess_book_content(book, 'genre')

    def preprocess_books(self):
        start_time = time.time()
        for book in self.books_dict.values():
            self.preprocess_book(book)

        end_time = time.time()
        print(f"It took {end_time - start_time} seconds to preprocess books")

    def pickle_book_data(self):
        self.description_data.pickle(DESCRIPTION_DATA_PICKLE)
        self.genre_data.pickle(GENRE_DATA_PICKLE)


class BookVectorizer():
    def __init__(self, books_dict_file: str = None):

        if books_dict_file:
            self.books_dict: dict[str, Book] = utils.unpickle_object(
                books_dict_file)
            self.description_data: BookData = utils.unpickle_object(
                DESCRIPTION_DATA_PICKLE)
            self.genre_data: BookData = utils.unpickle_object(
                GENRE_DATA_PICKLE)
            self.book_count = len(self.books_dict)

    def get_tf_weight(self, key, tf_dict: dict):
        tf_weight = 0
        if tf_dict and key in tf_dict:
            tf = tf_dict[key]
            tf_weight = 1 + (math.log10(tf))
        return tf_weight

    def get_idf_weight(self, key, df_dict: dict[str, int]):
        idf_weight = 0
        if key in df_dict:
            df = df_dict[key]
            idf_weight = math.log10(self.book_count/df)
        return idf_weight

    def vectorize_book(self, book_content: List[str], vocabulary: List[str], df_dict: dict[str, int]):
        term_frequencies = {word: book_content.count(
            word) for word in book_content if word in vocabulary}

        vector = Vector(len(vocabulary))
        for index, word in enumerate(vocabulary):
            tf_idf_weight = self.get_tf_weight(
                word, term_frequencies) * self.get_idf_weight(word, df_dict)
            if tf_idf_weight > 0:
                vector.add_index_weight(index, tf_idf_weight)

        return vector

    def vectorize_book_data(self, book_url: str, book_data: BookData) -> Vector:
        vector = Vector(len(book_data.vocabulary))
        for index, word in enumerate(book_data.vocabulary):
            tf_key = (word, book_url)
            df_key = word
            tf_weight = self.get_tf_weight(tf_key, book_data.term_frequency)
            idf_weight = self.get_idf_weight(df_key, book_data.doc_frequency)
            tf_idf_weight = tf_weight * idf_weight
            if tf_idf_weight > 0:
                vector.add_index_weight(index, tf_idf_weight)
        return vector

    def vectorize_book_dict(self, books_dict: dict[str, Book]) -> Tuple[dict]:
        book_preprocessor = BookPreprocessor(books_dict=books_dict)
        book_preprocessor.preprocess_books()
        book_preprocessor.pickle_book_data()

        print("Vectorizing books_dict...")

        description_data = book_preprocessor.description_data
        genre_data = book_preprocessor.genre_data

        self.book_count = len(books_dict)

        self.description_vectors = {book_url: self.vectorize_book_data(book_url, description_data)
                                    for book_url in books_dict.keys()}

        self.genre_vectors = {book_url: self.vectorize_book_data(book_url, genre_data)
                              for book_url in books_dict.keys()}

        return (self.description_vectors, self.genre_vectors)

    def pickle_vectors(self):
        print("Pickling the vectors...")
        utils.pickle_object(self.description_vectors,
                            "out/pickle/description_vectors.pickle")
        utils.pickle_object(self.genre_vectors,
                            "out/pickle/genre_vectors.pickle")

    def combine_description_genre_similarity(self, description_similarity: float, genre_similarity: float) -> float:
        return 0.5 * description_similarity + 0.5 * genre_similarity

    def calculate_similarities(self, book: Book):
        book_preprocessor = BookPreprocessor()
        book_url = book.url
        description = book_preprocessor.tokenize_description(book)
        genre = book_preprocessor.tokenize_genres(book)

        # Get vectors of query book
        description_vector: Vector = self.vectorize_book(
            description, self.description_data.vocabulary, self.description_data.doc_frequency)
        genre_vector: Vector = self.vectorize_book(
            genre, self.genre_data.vocabulary, self.genre_data.doc_frequency)

        # Get vectors of other books
        description_vectors: dict[str, Vector] = utils.unpickle_object(
            "out/pickle/description_vectors.pickle")
        genre_vectors: dict[str, Vector] = utils.unpickle_object(
            "out/pickle/genre_vectors.pickle")

        similarities = []
        for book_url in description_vectors.keys():
            if book_url in genre_vectors:
                # Other book's vectors
                other_desc_vector = description_vectors[book_url]
                other_genre_vector = genre_vectors[book_url]
                # Calculate similarities
                desc_similarity = description_vector.calculate_similarity(
                    other_desc_vector)
                genre_similarity = genre_vector.calculate_similarity(
                    other_genre_vector)
                # Combine similarities
                similarity = self.combine_description_genre_similarity(
                    desc_similarity, genre_similarity)
                similarities.append((similarity, book_url))

        return similarities
