class Book():
    def __init__(self, title, description, authors, recommendations, genres):
        self.title = title
        self.description = description
        self.authors = authors
        self.recommendations = recommendations
        self.genres = genres

    def print(self):
        print("Title:", self.title)
        print("Description:", self.description)
        print("Authors:", self.authors)
        print("Recommendations:", self.recommendations)
        print("Genres:", self.genres)
