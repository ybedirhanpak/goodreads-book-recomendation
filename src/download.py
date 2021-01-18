from book import Book
import utils
import time
import threading
import re
import urllib.request


class BookExtractor():

    def __init__(self):
        self.books = {}

    def __clear_html_text(self, text: str):
        cleaned = re.sub(r'<.*?>|\(.*?\)|\\n|\\\'s', '', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
        return cleaned

    def __extract_title(self, book_html: str):
        title_match = re.findall(
            r'<h1 id="bookTitle".*?>(.*?)<\/h1>', book_html)
        if len(title_match) > 0:
            return self.__clear_html_text(title_match[0])
        return ''

    def __extract_authors(self, book_html: str):
        authors_match = re.findall(
            r'<div class=\\\'authorName__container\\\'.*?>.*?<a class="authorName".*?><span.*?>(.*?)<\/div>', book_html)
        authors = [self.__clear_html_text(author_match)
                   for author_match in authors_match]
        return authors

    def __extract_description(self, book_html: str):
        description_match = re.findall(
            r'<div id="descriptionContainer".*?<\/div>', book_html)
        if len(description_match) > 0:
            description = description_match[0]
            # freeText11251655968315975519
            free_text_match = re.findall(
                r'<span id="freeText\d+".*?>(.*?)<\/span>', description)
            span_text = ''
            if len(free_text_match) > 0:
                # Take long version
                span_text = free_text_match[0]
                pass
            else:
                # Take short version
                free_text_container_match = re.findall(
                    r'<span id="freeTextContainer\d+".*?>(.*?)<\/span>', description)
                if len(free_text_container_match) > 0:
                    span_text = free_text_container_match[0]
            # Remove internal html elements in the span text
            return re.sub(r'<.*?>', '', span_text)
        return ''

    def __extract_recommendations(self, book_html: str):
        recommendations_match = re.findall(
            r'<li class=\\\'cover\\\'.*?<a.*?href="(.*?)".*?<\/a>', book_html)
        return recommendations_match

    def __extract_genres(self, book_html: str):
        genres_match = re.findall(
            r'<div class="elementList ">.*?<div class="left">.*?<a.*?>(.*?)<\/a>', book_html)
        return genres_match

    def extract_book(self, book_url: str, book_html: str):
        title = self.__extract_title(book_html)
        description = self.__extract_description(book_html)
        authors = self.__extract_authors(book_html)
        recommendations = self.__extract_recommendations(book_html)
        genres = self.__extract_genres(book_html)

        self.books[book_url] = Book(
            title, description, authors, recommendations, genres)

    def pickle_books(self, location="out/books.pickle"):
        utils.pickle_object(self.books, location)


class BookDownloader():

    def __init__(self,
                 download_dir="out/books",
                 logs_file="out/logs.txt",
                 errors_file="out/errors.txt",
                 books_pickle="out/books.pickle"
                 ):
        self.download_dir = download_dir
        self.logs_file = logs_file
        self.errors_file = errors_file
        self.books_pickle = books_pickle
        self.books = {}
        self.failed_downloads = []
        self.extractor = BookExtractor()
        # Create books directory
        utils.create_dir("out/books")

    def __download_book(self, index, url):
        with open(utils.get_file_path(self.logs_file), "a+") as log_file:
            with open(utils.get_file_path(self.errors_file), "a+") as error_file:
                if not re.search("https://www.goodreads.com/book/show/", url):
                    print(f"Bad url: {url}", file=log_file)
                    return
                file_name = f"{self.download_dir}/{index}.html"
                book_html = ''
                if utils.file_exists(file_name):
                    print(f"Book already exists: {file_name}", file=log_file)
                    with open(utils.get_file_path(file_name), "r") as book_file:
                        book_html = book_file.read()
                else:
                    try:
                        req = urllib.request.Request(url)
                        with urllib.request.urlopen(req, timeout=60) as response:
                            book_html = response.read().decode("utf-8")
                            print(f"Book created: {file_name}", file=log_file)
                            # Save book into file
                            with open(utils.get_file_path(file_name), "w+") as f_out:
                                print(book_html, file=f_out)
                    except Exception as e:
                        print(
                            f"Error while downloading book: {url}, {e}", file=error_file)
                        # Add book into failed downloads
                        self.failed_downloads.append((index, url))
                if book_html and book_html != '':
                    try:
                        self.extractor.extract_book(
                            book_url=url, book_html=book_html)
                    except Exception as e:
                        print(
                            f"Error while extracting book: {url}, {e}", file=error_file)

    def download_books(self, books_file="data/books.txt"):
        print("Downloading the books, please wait...")

        # Read book urls from data/books.txt and download into books/{id}.html
        with open(utils.get_file_path(books_file)) as f:
            start_time = time.time()

            book_urls = f.read().splitlines()
            books_count = len(book_urls)

            # Create one thread to download a book
            initial_threads = [threading.Thread(target=self.__download_book, args=(
                index, url,)) for index, url in enumerate(book_urls)]

            utils.run_threads_and_wait(initial_threads)

            while len(self.failed_downloads) > 0:
                failed = len(self.failed_downloads)
                print(
                    f"{books_count - failed} completed, {failed} failed, out of {books_count} documents. Waiting 1 minutes to try again...")
                time.sleep(60)
                print("Downloading the books, please wait...")
                trial_threads = [threading.Thread(target=self.__download_book, args=(
                    index, url,)) for index, url in self.failed_downloads]
                self.failed_downloads.clear()
                utils.run_threads_and_wait(trial_threads)

            print(f"Extracting and saving into '{self.books_pickle}'...")
            self.extractor.pickle_books(self.books_pickle)

            end_time = time.time()
            print(
                f"{books_count} documents has been downloaded and extracted in {end_time-start_time} seconds.")
