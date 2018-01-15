import pandas as pd
from collections import Counter


def get_books(csv_file):
    """
    INPUT:
    csv filename
    OUTPUT:
    DataFrame with the following columns:
    'book_id', 'title','isbn', 'isbn13', 'country_code',
    'language_code', 'description', 'work_id', 'best_book_id', 'original_title'
    """
    df_books = pd.read_csv(csv_file, usecols=['book_id', 'title',
                           'isbn', 'isbn13', 'country_code',
                           'language_code', 'description', 'work_id',
                           'best_book_id', 'original_title'])
    df_books = df_books[df_books['language_code'].map(lambda x: x in ['eng', 'en-US', 'en-GB', 'en-CA', 'en'])]
    return df_books


def get_classified_authors(csv_file):
    """
    INPUT:
    csv filename
    OUTPUT:
    DataFrame with the following columns:
    'author_id', 'name', 'race', 'gender', 'image_url',
    'about', 'influences', 'works_count', 'hometown', 'born_at', 'died_at'
    """
    df_authors = pd.read_csv(csv_file, usecols=['author_id', 'name', 'race', 'gender', 'image_url',
       'about', 'influences', 'works_count', 'hometown', 'born_at', 'died_at'])
    df_authors['race'] = df_authors['race'].map(lambda x: upper_strip(x))
    df_authors['gender'] = df_authors['gender'].map(lambda x: upper_strip(x))
    # List of races and genders from EEO values
    races = ['BLACK', 'WHITE', 'ASIAN', 'LATINO', 'NATIVE AMERICAN', 'MIXED',
             'PACIFIC ISLANDER']
    genders = ['FEMALE', 'MALE']
    # Invalid values will be replaced with majority of class
    race_majority = Counter(df_authors['race']).most_common()[0][0]
    gender_majority = Counter(df_authors['gender']).most_common()[0][0]
    df_authors['race'] = df_authors['race'].map(lambda x: replace_invalid_values(x, races, race_majority))
    df_authors['gender'] = df_authors['gender'].map(lambda x: replace_invalid_values(x, genders, gender_majority))
    df_authors = df_authors[df_authors['race'].isnull() == False]
    return df_authors


def upper_strip(value):
    try:
        return value.upper().strip()
    except AttributeError:
        return value


def replace_invalid_values(value, valid_values, replacement):
    """
    INPUT:
    csv filename
    INPUT:
    -value
    -list of valid values
    OUTPUT:
    valid value
    """
    if value in valid_values:
        return value
    return replacement


def get_books_to_authors(csv_file):
    """
    INPUT:
    csv filename
    OUTPUT:
    DataFrame with the following columns:
    'book_id', 'author_id', 'name', 'role'
    """
    df_authors_books = pd.read_csv(csv_file, usecols=['book_id',
                                   'author_id', 'name', 'role'])
    return df_authors_books


def get_isbn_to_best_book_id(csv_file, our_best_book_ids=None):
    """
    INPUT:
    csv filename
    set of the best book ID's we care about if we would like to limit the file
    OUTPUT:
    DataFrame with the following columns:
    'isbn', 'best_book_id'
    """
    pass
    df_isbn_best_book_id = pd.read_csv(csv_file, header=None,
                                       names=['isbn', 'best_book_id'])
    df_isbn_best_book_id = df_isbn_best_book_id[df_isbn_best_book_id['best_book_id'].isnull() == False]
    if our_best_book_ids:
        df_isbn_best_book_id = df_isbn_best_book_id[df_isbn_best_book_id['best_book_id'].map(lambda x: x in our_best_book_ids)]
    df_isbn_best_book_id['best_book_id'] = df_isbn_best_book_id['best_book_id'].map(lambda x: int(x))
    return df_isbn_best_book_id


def merge_to_classify_books(df_authors_books, df_authors, df_books):
    """
    INPUT:
    df_authors_books created by function get_books_to_authors
    df_authors created by function get_classified_authors
    df_books created by function get_books
    OUTPUT:
    DataFrame with the following columns:
    'book_id', 'title', 'isbn', 'isbn13', 'country_code', 'language_code',
    'description', 'work_id', 'best_book_id', 'original_title', 'author_id',
    'name_x', 'role', 'race', 'gender', 'image_url', 'about',
    'influences', 'works_count', 'hometown', 'born_at', 'died_at'
    """
    df_authors_books_classified = pd.merge(df_authors_books, df_authors,
                                           right_on='author_id',
                                           left_on='author_id', how='inner')
    df_books_classified = pd.merge(df_books, df_authors_books_classified,
                                   right_on='book_id', left_on='book_id',
                                   how='left')
    df_books_classified = df_books_classified[['book_id', 'title', 'isbn',
                                               'isbn13', 'country_code',
                                               'language_code', 'description',
                                               'work_id', 'best_book_id',
                                               'original_title', 'author_id',
                                               'name_x', 'role', 'race',
                                               'gender', 'image_url',
                                               'about', 'influences',
                                               'works_count', 'hometown',
                                               'born_at', 'died_at']]
    return df_books_classified


def get_amazon_review_text(csv_file):
    """
    INPUT:
    - json file with Amazon reveiws
    - dictionary of ISBNs (subset we care about) to GoodReads best book id
    OUTPUT:
    Series of aggregated reviews grouped by GoodReads best book id
    """
    df_reviews = pd.read_csv('new_less_reviews.csv', header=None,
                             names=['best_book_id', 'asin', 'summary',
                                    'review_text'])
    df_reviews = df_reviews[df_reviews['reviewText'].isnull() == False]
    df_reviews_agg = df_reviews.groupby('best_book_id')['reviewText'].agg(lambda col: ' '.join(col))
    return df_reviews_agg


def get_amazon_ratings(csv_file):
    """
    INPUT:
    - csv file with Amazon reveiws
    - dictionary of ISBNs (subset we care about) to GoodReads best book id
    OUTPUT:
    DataFrame with the following columns:
    'user_id', 'book_id', 'rating'
    """
    df_a_ratings = pd.read_csv(csv_file, header=None,
                               names=['book_id', 'asin', 'user_ID',
                                      'helpful', 'rating', 'unix_review_time'])
    df_a_ratings = df_a_ratings[['user_id', 'book_id', 'rating']]
    return df_a_ratings


def get_goodread_data(csv_file, books_csv):
    """
    INPUT:
    From Kaggle dataset
    - ratings_csv - book_id (nothing to do with goodreads), user_id (who knows),
      rating
    - book_csv - we will use this to get the Kaggle book ID to the goodreads
      best book id
    OUTPUT:
    DataFrame with the following columns:
    'user_id','book_id','rating'
    """
    df_ratings = pd.read_csv(ratings_csv)
    df_books = pd.read_csv(books_csv, usecols=['book_id', 'best_book_id'])
    dict_best_id = df_books.set_index(['book_id'])['best_book_id'].to_dict()
    df_ratings['book_id'] = df_ratings['book_id'].map(lambda x: dict_best_id.get(x))
    return df_ratings


if __name__ == '__main__':
    # Created from GoodReads API
    book_file = 'data/updated_books.csv'
    # Created from GoodReads API, and manual classification
    author_file = 'data/classified_authors.csv'
    # Created from GoodReads API
    author_book_file = 'data/author_books.csv'
    # Created from Amazon Review file for ASIN and GoodReads API
    asin_best_file = 'data/asin_best_book_id.csv'
    # From Kaggle's Goodbooks-10K
    k_rating_file = 'data/goodbooks-10k/ratings.csv'
    k_book_file = 'data/goodbooks-10k/books.csv'
    # Created from Amazon Review file
    a_ratings_file = 'data/limited_amazon_ratings.csv'
    a_reviews_file = 'data/limited_amazon_reviews.csv'

    df_books = get_books(book_file)
    df_authors = get_classified_authors(author_file)
    df_authors_books = get_books_to_authors(author_book_file)
    our_best_book_ids = set(df_books['best_book_id'])
    df_isbn_best_book_id = get_isbn_to_best_book_id(asin_best_file, our_best_book_ids)

    df_books_classified = merge_to_classify_books(df_authors_books, df_authors,
                                                  df_books)

    df_k_ratings = get_goodread_data(k_rating_file, k_book_file)
    df_a_ratings = get_amazon_ratings(a_ratings_file)
    df_reviews_agg = get_amazon_review_text(a_reviews_file)
