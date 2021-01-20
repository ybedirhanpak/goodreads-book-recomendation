# Boğaziçi University - CMPE493 Introduction to Information Retrieval - Fall 2020 Assignment 3 - A Book Recommendation System - Yahya Bedirhan Pak - 2016400213

## Downloading

- When you give `books.txt` as input to the `main.py`, `BookDownloader` downloads all books and creates `Book` objects for each book. Then it pickles them into `out/pickle/books.pickle` for further use.
- When you give `book-url` as input to the `main.py`, `BookDownloader` downloads the book and creates the `Book` object.

## Preprocessing and Vectorization

- After downloading all of the books, `BookVectorizer` first passes data to `BookPreprocessor` to preprocess the data. This preprocessing includes:

  - Case folding
  - Punctuation removal
  - Tokenization of description and genre fields
  - Creating inverted index, term frequencies, document frequencies, vocabulary separately for description and genre.
  - Pickling the results into `out/pickle/description_data.pickle` and `out/pickle/genre_data.pickle` which has a type of `BookData` located in `vectorization.py`

- After preprocessing the books, `BookVectorizer` vectorizes all of the books in corpus, then pickles them into `out/pickle/description_vectors.pickle` and `out/pickle/genre_vectors.pickle`
  - I've created `Vector` class for vector operations. Since the vectors are very sparse, containing 0 in most of the indices and non-zero in some indices
  - This `Vector` class contains a dictionary that holds non-zero values and their indices
  - By doing that, vector size is compressed and calculations are done faster.

## Calculating recommendations

- When you create a `BookVectorizer` with an input of the file path to the books, it unpickles the books, description vectors and genre vectors.
- After that, you can calculate a book's similarities with all other books with `book_vectorizer.calculate_similarities(book)`.
- Then you can rank the similarities and get the first 18 of them.

## Evaluation

- When you download a book with `BookDownloader`, it extracts the goodread's recommendations for that book in `recommendations` field.
- `evaluate_precision` function in `evaluate.py` takes `original_list` which is known results and `calculated_list` which is our ranked list. It returns `precision` and `average_precision` from them.

## Summary

- (a) Describe the model you used to encode the genres of the book

I've used the genre itself as a term and created **vocabulary, inverted_index, term frequency, document frequency** from them. For example my genre vocabulary is like this:

```
['novels', 'feminism', 'animals', 'politics', 'contemporary', 'games', 'pop culture', 'academic', 'history', 'short stories', 'school stories' ... ]
```

- (b) Describe the model parameters (minimum/maximum thresholds, number of
terms, weight variants, α, etc.)

## TF-IDF Weight
I've used tf-idf weighting with
```
tf_id_weight = tf_weight * idf_weight
```
### Tf_weight

In order to calculate term-frequency weight, I've used this:

```
If term frequency == 0 --> 0,
If term frequency > 0 --> 1 + log10(tf)
```

This is the function that calculates it:

```
def get_tf_weight(self, key, tf_dict: dict):
    tf_weight = 0
    if tf_dict and key in tf_dict:
        tf = tf_dict[key]
        tf_weight = 1 + (math.log10(tf))
    return tf_weight
```

tf_dict contains the term_frequencies of a key which could be a single word or (word, book_url) tuple.

### Idf_weight

In order to calculate inverted-documen-frequency weight, I've used this:

```
If document frequency == 0 --> 0,
If document frequency > 0 --> log10(N/df) 
    where N is number of books
```

This is the function that calculates it:

```
def get_idf_weight(self, key, df_dict: dict[str, int]):
    idf_weight = 0
    if key in df_dict:
        df = df_dict[key]
        idf_weight = math.log10(self.book_count/df)
    return idf_weight
```

df_dict contains the document frequencies of a key which could be a description token or genre.

## Final similarity score
I've given equal weight to description similarity score and genre similarity score (α = 0.5):

```
def combine_description_genre_similarity(self, description_similarity: float, genre_similarity: float) -> float:
    return 0.5 * description_similarity + 0.5 * genre_similarity
```
