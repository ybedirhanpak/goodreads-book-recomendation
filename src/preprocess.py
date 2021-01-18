import utils
from book import Book


class BookPreprocessor():
    def __init__(self, books_pickle="out/books.pickle"):
        self.books_pickle = books_pickle
        self.books = {}
        self.vocabulary = set()
        self.inverted_index = {}
        self.term_frequency = {}
        self.doc_frequency = {}

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
        self.books: dict = utils.unpickle_object(self.books_pickle)
        for book in self.books.values():
            self.__preprocess_book(book)
        self.vocabulary_list = list(self.vocabulary)

        print("Vocabulary", len(self.vocabulary))
        print("Doc frequency", len(self.doc_frequency.keys()))
        print("Term frequency", len(self.term_frequency.keys()))
        print("Inverted index", len(self.inverted_index.keys()))
