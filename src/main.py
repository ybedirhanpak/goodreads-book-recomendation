import sys
import utils
from download import BookDownloader
from vectorization import BookVectorizer
import evaluation

utils.create_dir("out/pickle")

BOOKS_PICKLE = "out/pickle/books.pickle"


def vectorize_books(books_file: str):
    # Download and pickle the books
    book_downloader = BookDownloader()
    books_dict = book_downloader.download_books(books_file)
    book_downloader.pickle_books(file_name=BOOKS_PICKLE)

    # Calculate and pickle vectors of all books
    book_vectorizer = BookVectorizer()
    book_vectorizer.vectorize_book_dict(books_dict)
    book_vectorizer.pickle_vectors()


def get_recommendations_of_book(book_url: str):
    compressed_url = utils.compress_book_url(arg)
    print(f"Calculating recommendations for {compressed_url}...")

    # Download book
    book_downloader = BookDownloader()
    book = book_downloader.download_single_book(book_url)

    # Preprocess description and genres
    book_vectorizer = BookVectorizer(books_dict_file=BOOKS_PICKLE)
    similarities = book_vectorizer.calculate_similarities(book)

    # Get calculated_recommendations
    ranked_similarities = sorted(similarities, reverse=True)
    calculated_recommendations = [url for rank, url in ranked_similarities if url != compressed_url][:18]

    # Get goodread's recommendations
    goodreads_recommendations = book.recommendations[:18]

    print("---------------------------")
    print("Goodread's recommendations:")
    print("---------------------------")
    for book_url in goodreads_recommendations:
        print(utils.decompress_book_url(book_url))

    print("---------------------------")
    print("Calculated recommendations:")
    print("---------------------------")
    for book_url in calculated_recommendations:
        print(utils.decompress_book_url(book_url))

    precision, average_precision = evaluation.evaluate_precision(
        goodreads_recommendations, calculated_recommendations)

    print("---------------------------")
    print("Precision:", precision)
    print("Average precision:", average_precision)
    print("---------------------------")


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
