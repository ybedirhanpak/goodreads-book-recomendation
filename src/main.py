import sys
import utils
from download import BookDownloader
from vectorization import BookVectorizer

utils.create_dir("out/pickle")

BOOKS_PICKLE = "out/pickle/books.pickle"
VOCABULARY_PICKLE = "out/pickle/vocabulary.pickle"
INVERTED_INDEX_PICKLE = "out/pickle/ie.pickle"
TERM_FREQUENCY_PICKLE = "out/pickle/tf.pickle"
DOCUMENT_FREQUENCY_PICKLE = "out/pickle/df.pickle"
BOOK_VECTORS_PICKLE = "out/pickle/book_vectors.pickle"


def vectorize_books(books_file: str):
    # Download and pickle the books
    book_downloader = BookDownloader()
    books_dict = book_downloader.download_books(books_file)
    book_downloader.pickle_books(file_name=BOOKS_PICKLE)

    # Calculate and pickle vectors of all books
    book_vectorizer = BookVectorizer()
    book_vectorizer.vectorize_book_dict(books_dict)
    book_vectorizer.pickle_vectors()

    # # Preprocess books
    # book_preprocessor = BookPreprocessor(
    #     books_dict=books_dict,
    #     books_pickle=BOOKS_PICKLE,
    #     vocabulary_pickle=VOCABULARY_PICKLE,
    #     ie_pickle=INVERTED_INDEX_PICKLE,
    #     tf_pickle=TERM_FREQUENCY_PICKLE,
    #     df_pickle=DOCUMENT_FREQUENCY_PICKLE
    # )
    # book_preprocessor.preprocess_books()

    # # Vectorize books
    # book_vectorizer = BookVectorizer(
    #     books_dict=books_dict,
    #     preprocessor=book_preprocessor
    # )

    # book_vectorizer.vectorize_books()


def get_recommendations_of_book(book_url: str):
    url = utils.compress_book_url(arg)
    print(url)

    # Download book
    book_downloader = BookDownloader()
    book = book_downloader.download_single_book(book_url)

    # Preprocess description and genres
    book_vectorizer = BookVectorizer(books_dict_file=BOOKS_PICKLE)
    similarities = book_vectorizer.calculate_similarities(book)

    ranked_similarities = sorted(similarities, reverse=True)[:19]
    print(ranked_similarities)

    print("Calculated recommendations:")

    for ranking, book_url in ranked_similarities:
        print(f"{ranking}, {utils.decompress_book_url(book_url)}")

    print("Original recommendations:")
    for book_url in book.recommendations:
        print(book_url)

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
