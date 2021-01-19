import sys
import utils
from download import BookDownloader
from preprocess import BookPreprocessor
from vectorization import BookVectorizer, Vector

utils.create_dir("out/pickle")

BOOKS_PICKLE = "out/pickle/books.pickle"
VOCABULARY_PICKLE = "out/pickle/vocabulary.pickle"
INVERTED_INDEX_PICKLE = "out/pickle/ie.pickle"
TERM_FREQUENCY_PICKLE = "out/pickle/tf.pickle"
DOCUMENT_FREQUENCY_PICKLE = "out/pickle/df.pickle"
BOOK_VECTORS_PICKLE = "out/pickle/book_vectors.pickle"


def vectorize_books(books_file: str):
    # Download books
    book_downloader = BookDownloader(books_pickle=BOOKS_PICKLE)
    book_downloader.download_books(books_file)

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


def get_recommendations_of_book(book_url: str):
    url = utils.compress_book_url(arg)
    print(url)
    # Download book
    book_downloader = BookDownloader()
    book = book_downloader.download_single_book(book_url)

    # Preprocess description and genres
    book_preprocessor = BookPreprocessor()

    description = book_preprocessor.tokenize_description(book)
    genres = book_preprocessor.tokenize_genres(book)

    # Calculate vector for description and genres
    book_vectorizer = BookVectorizer(
        books_pickle=BOOKS_PICKLE,
        vocabulary_pickle=VOCABULARY_PICKLE,
        ie_pickle=INVERTED_INDEX_PICKLE,
        tf_pickle=TERM_FREQUENCY_PICKLE,
        df_pickle=DOCUMENT_FREQUENCY_PICKLE,
        book_vectors_pickle=BOOK_VECTORS_PICKLE
    )

    query_vector = book_vectorizer.vectorize_query_book(book.url, description)
    book_vectors: dict(str, Vector) = utils.unpickle_object(
        BOOK_VECTORS_PICKLE)

    similarities = [(query_vector.calculate_similarity(book_vector), book_url)
                    for book_url, book_vector in book_vectors.items()]
    recommendations = sorted(similarities, reverse=True)[:18]
    print(recommendations)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No arugments provided.")
        print("These are the valid options:")
        print("main.py path-to-books-txt-file   ----> Downloads books in the books.txt file and creates tf-idf vectors")
        print("main.py url-of-the-book-to-query ----> Calculates 18 recommendations for given book")
    else:
        arg = sys.argv[1]
        if utils.is_book_url(arg):
            get_recommendations_of_book(arg)
        else:
            vectorize_books(arg)
