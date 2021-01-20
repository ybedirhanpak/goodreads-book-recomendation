from typing import List
from book import Book
import utils
import time
import threading
import re
import urllib.request


class BookExtractor():
    '''
        This class extracts title, authors, description, recommendations and genres from book html
    '''

    def __clear_html_text(self, text: str) -> str:
        '''
            Removes inner html elements inside the text
            Replaces multiple spaces with single space
            Returns the cleared text
        '''
        cleared_text = re.sub(r'<.*?>', '', text)
        cleared_text = re.sub(r'\s{2,}', ' ', cleared_text).strip()
        return cleared_text

    def __extract_title(self, book_html: str) -> str:
        '''
            Extracts and returns the title from book_html
        '''
        title_match = re.findall(
            r'<h1 id="bookTitle".*?>(.*?)<\/h1>', book_html)
        if len(title_match) > 0:
            return self.__clear_html_text(title_match[0])
        return ''

    def __extract_authors(self, book_html: str) -> List[str]:
        '''
            Extracts and returns the authors from book_html
        '''
        authors_match = re.findall(
            r'<div class=\'authorName__container\'.*?>.*?<a class="authorName".*?><span.*?>(.*?)<\/div>', book_html)
        # Clear html inside text
        authors = [self.__clear_html_text(author_match)
                   for author_match in authors_match]
        # Remove paranthesis descripiton of authors
        authors = [re.sub('\(.*?\)', '', author).strip() for author in authors]
        return authors

    def __extract_description(self, book_html: str) -> str:
        '''
            Extracts and returns the description from book_html
        '''
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
            return self.__clear_html_text(span_text)
        return ''

    def __extract_recommendations(self, book_html: str) -> List[str]:
        '''
            Extracts and returns the recommendations from book_html
        '''
        recommendations_match = re.findall(
            r'<li class=\'cover\'.*?<a.*?href="(.*?)".*?<\/a>', book_html)
        return [utils.compress_book_url(str(recommendation)) for recommendation in recommendations_match]

    def __extract_genres(self, book_html: str) -> List[str]:
        '''
            Extracts and returns the genres from book_html
        '''
        genres_match = re.findall(
            r'<div class="elementList ">.*?<div class="left">.*?<a.*?>(.*?)<\/a>', book_html)
        return list(set([self.__clear_html_text(genre) for genre in genres_match]))

    def extract_book(self, book_url: str, book_html: str) -> Book:
        '''
            Extracts and returns the book from book_html
        '''
        compressed_url = utils.compress_book_url(book_url)
        book_html = re.sub(r'\n|\r', ' ', book_html)
        return Book(
            url=compressed_url,
            title=self.__extract_title(book_html),
            description=self.__extract_description(book_html),
            authors=self.__extract_authors(book_html),
            recommendations=self.__extract_recommendations(book_html),
            genres=self.__extract_genres(book_html)
        )


class BookDownloader():

    def __init__(self,
                 download_dir="out/books",
                 logs_file="out/download_logs.txt",
                 errors_file="out/download_errors.txt"
                 ):
        self.download_dir = download_dir
        self.logs_file = logs_file
        self.errors_file = errors_file
        self.books_dict = {}
        self.failed_downloads = []
        self.extractor = BookExtractor()
        # Create books directory
        utils.create_dir("out/books")

    def __download_book(self, index: int, url: str):
        '''
            Downloads a single book if it hasn't been downloaded before,
            If download is failed, adds the (index, url) tuple into failed_downloads
            index is positional index of the url in books.txt file
            url is the full url of the book
        '''
        with open(utils.get_file_path(self.logs_file), "a+") as log_file:
            with open(utils.get_file_path(self.errors_file), "a+") as error_file:
                if not utils.is_book_url(url):
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
                            print(
                                f"Book is saved into: {file_name}", file=log_file)
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
                        # Extract book and save into books
                        compressed_url = utils.compress_book_url(url)
                        self.books_dict[compressed_url] = self.extractor.extract_book(
                            book_url=url, book_html=book_html)
                    except Exception as e:
                        print(
                            f"Error while extracting book: {url}, {e}", file=error_file)

    def download_single_book(self, book_url) -> Book:
        '''
            Downloads and returns the book with in the book_url
        '''
        if not utils.is_book_url(book_url):
            print(f"Bad book_url: {book_url}")
            return
        book_html = ''
        book = None
        try:
            req = urllib.request.Request(book_url)
            with urllib.request.urlopen(req, timeout=60) as response:
                book_html = response.read().decode("utf-8")
        except Exception as e:
            print(f"Error while downloading book: {book_url}, {e}")
        if book_html and book_html != '':
            try:
                book = self.extractor.extract_book(
                    book_url=book_url, book_html=book_html)
            except Exception as e:
                print(
                    f"Error while extracting book: {book_url}, {e}")
        return book

    def download_books(self, books_file="data/books.txt") -> dict[str, Book]:
        '''
            Downloads books with their url in the books_file, 
            stores them in books dictionary.

            Returns the book dictionary
        '''
        print("Downloading the books, please wait...")

        # Read book urls from data/books.txt and download into books/{id}.html
        with open(utils.get_file_path(books_file)) as f:
            start_time = time.time()

            book_urls = f.read().splitlines()
            books_count = len(book_urls)

            # Create one thread to download a book
            initial_threads = [threading.Thread(target=self.__download_book, args=(
                index, url,)) for index, url in enumerate(book_urls)]

            # Run threads to download the books
            utils.run_threads_and_wait(initial_threads)

            # As long as there are some books which failed to download, try again to download
            while len(self.failed_downloads) > 0:
                failed = len(self.failed_downloads)
                print(
                    f"{books_count - failed} completed, {failed} failed, out of {books_count} documents. Waiting 1 minute to try again...")
                time.sleep(60)
                print("Downloading the books, please wait...")
                trial_threads = [threading.Thread(target=self.__download_book, args=(
                    index, url,)) for index, url in self.failed_downloads]
                self.failed_downloads.clear()
                utils.run_threads_and_wait(trial_threads)

            end_time = time.time()
            print(
                f"{books_count} documents has been downloaded and extracted in {end_time-start_time} seconds.")

            return self.books_dict

    def pickle_books(self, file_name: str = "out/books.pickle"):
        '''
            Pickles books dictionary to given file_name
        '''
        print(f"Pickling books_dict into '{file_name}'...")
        utils.pickle_object(self.books_dict, file_name)
