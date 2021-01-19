import utils
from download import BookDownloader
from preprocess import BookPreprocessor
from vectorization import BookVectorizer

utils.create_dir("out/pickle")

BOOKS_FILE = "data/books.txt"
BOOKS_PICKLE = "out/pickle/books.pickle"
VOCABULARY_PICKLE = "out/pickle/vocabulary.pickle"
INVERTED_INDEX_PICKLE = "out/pickle/ie.pickle"
TERM_FREQUENCY_PICKLE = "out/pickle/tf.pickle"
DOCUMENT_FREQUENCY_PICKLE = "out/pickle/df.pickle"

# Download books
book_downloader = BookDownloader(books_pickle=BOOKS_PICKLE)
book_downloader.download_books(books_file=BOOKS_FILE)

# Preprocess books
book_preprocessor = BookPreprocessor(
    books_pickle=BOOKS_PICKLE,
    vocabulary_pickle=VOCABULARY_PICKLE,
    ie_pickle=INVERTED_INDEX_PICKLE,
    tf_pickle=TERM_FREQUENCY_PICKLE,
    df_pickle=DOCUMENT_FREQUENCY_PICKLE
)
book_preprocessor.preprocess_books()

# Vectorize books
book_vectorizer = BookVectorizer(
    preprocessor=book_preprocessor
)

book_vectorizer.vectorize_books()
