# Boğaziçi University - CMPE493  Introduction to Information Retrieval - Fall 2020 Assignment 3 - A Book Recommendation System - Yahya Bedirhan Pak - 2016400213

## Versions

* Python 3.9

## How to run

### Download books

In order to download the books, run this command:

```
python3 main.py relativepath-to-books.txt-file
python3 main.py data/books.txt
```

This command takes relative path from source code. For example if you provide `data/books.txt`, your project structure should be like this:
```
- data\
        - books.txt
- book.py
- download.py
- evaluation.py
- main.py
- utils.py
- vectorization.py
``` 

### Run Recommendation Calculation

In order to get recommendation, run this command:

```
python3 main.py url-of-the-book
python3 main.py https://www.goodreads.com/book/show/346074.G_W_Leibniz_s_Monadology
```

## Report

You can find the report at `Report.md`