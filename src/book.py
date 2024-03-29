from typing import List


class Book():
    def __init__(self, url: str, title: str, description: str, authors: List[str], recommendations: List[str], genres: List[str]):
        self.url = url
        self.title = title
        self.description = description
        self.authors = authors
        self.recommendations = recommendations
        self.genres = genres

    def __str__(self) -> str:
        return f"Book {self.url}"

    def print(self):
        print("URL:", self.url)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Authors:", self.authors)
        print("Recommendations:", self.recommendations)
        print("Genres:", self.genres)
