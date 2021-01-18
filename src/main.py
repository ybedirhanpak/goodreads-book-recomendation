from download import BookDownloader
from preprocess import BookPreprocessor

BOOKS_FILE = "data/books.txt"
BOOKS_PICKLE = "out/books.pickle"

# Download books
book_downloader = BookDownloader(books_pickle=BOOKS_PICKLE)
book_downloader.download_books(books_file=BOOKS_FILE)

# Preprocess books
book_preprocessor = BookPreprocessor(books_pickle=BOOKS_PICKLE)
book_preprocessor.preprocess_books()
