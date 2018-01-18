import pandas as pd
import numpy as np
import gzip
import json
import csv
import os
import requests
from xml.etree import ElementTree
import time
import matplotlib.pyplot as plt
import load_data
from xml_to_csv import get_text


def get_user_read_books(user_id, api_key, df_isbn_best_book_id, page=1, ratings=None):
    '''
    INPUT
    - isbn to look up
    - GoodReads API key
    OUTPUT
    - goodreads book ID and goodreads best book ID
    '''
    if ratings is None:
        ratings = []
    user_reviews = 'https://www.goodreads.com/review/list/{}.xml?key={}&v=2&shelf=read&per_page=200&page={}'.format(user_id, api_key, page)
    response = requests.get(user_reviews)
    no_books = 0
    tree = ElementTree.fromstring(response.content)
    for review in tree.findall('reviews/review'):
        book_id = get_text(review.find('book/id'))
        isbn = get_text(review.find('book/isbn'))
        rating = int(get_text(review.find('rating')))
        no_books += 1
        ratings.append([book_id, isbn, rating])
    if no_books == 200:
        get_user_read_books(user_id, api_key, df_isbn_best_book_id, page + 1, ratings)
    df_u_ratings = pd.DataFrame(ratings, columns=['book_id', 'isbn', 'rating'])
    return user_book_id_to_best(df_u_ratings, df_isbn_best_book_id)


def user_book_id_to_best(df_u_ratings, df_isbn_best_book_id):
    """
    INPUT:
    - DataFrame with the user ratings
    - Dictionary of ISBN to best book ID
    OUTPUT:
    -
    """
    dict_isbn_best_id = df_isbn_best_book_id.set_index(['isbn'])['best_book_id'].to_dict()
    df_u_ratings['book_id'] = df_u_ratings['isbn'].map(lambda x: dict_isbn_best_id.get(x))
    df_u_ratings = df_u_ratings[df_u_ratings['book_id'].isnull() == False]
    df_u_ratings = df_u_ratings[df_u_ratings['rating'] > 0]
    return df_u_ratings


def create_user_authorbook_classified(df_isbn_best_book_id, df_u_ratings,
                                      df_books_classified):
    """
    INPUT:

    OUTPUT:
    Data Frame grouped by race and gender including these columns
    'race'
    'gender'
    'authorbook_id' - count of unique author book id which is a compound key
                    - if the book was written by multiple authors you will get
                      one record per author
                    - if you have read multiple books by an author it will
                      count each one uniquely
    'percentage'
    """
    # dict_isbn_best_id = df_isbn_best_book_id.set_index(['isbn'])['best_book_id'].to_dict()
    # df_u_ratings['best_book_id'] = df_u_ratings['isbn'].map(lambda x: dict_isbn_best_id.get(x))
    # df_u_ratings = df_u_ratings[df_u_ratings['best_book_id'].isnull() == False]
    df_u_books_classified = pd.merge(df_u_ratings, df_books_classified,
                                     left_on='book_id',
                                     right_on='best_book_id', how='inner')
    df_u_books_classified['authorbook_id'] = df_u_books_classified['best_book_id'].map(str) + ' ' + df_u_books_classified['author_id'].map(str)
    df_u_ab_classified = df_u_books_classified.groupby(['race', 'gender'])['authorbook_id'].nunique().reset_index()
    df_u_ab_classified['percentage'] = df_u_ab_classified['authorbook_id'] / df_u_ab_classified['authorbook_id'].sum()
    return df_u_ab_classified


def plot_user_authorbook_classified(df_u_ab_classified):
    """
    INPUT
    DataFrame counting unique author book combos classified
    OUTPUT
    plots bar chart
    """
    ax = df_u_ab_classified['authorbook_id'].plot(kind='bar',
                                    title="Books Read by Race and Gender",
                                    legend=False, fontsize=12)
    plt.xticks(rotation=0)
    x_labels = list(df_u_ab_classified['race'] + '\n' + df_u_ab_classified['gender'])
    ax.set_xticklabels(map(lambda x: x.title(), x_labels))
    ax.set_ylabel("Unique Author Books Combos", fontsize=12)
    rects = ax.patches
    labels = list(df_u_ab_classified['percentage'].map(lambda x: "{:.2%}".format(x)))
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height, label,
                ha='center', va='bottom')
    plt.show()


if __name__ == '__main__':
    api_key = os.environ['GOODREADS_API_KEY']

    import load_data
    # Created from Amazon Review file for ASIN and GoodReads API
    asin_best_file = '../data/asin_best_book_id.csv'
    df_isbn_best_book_id = load_data.get_isbn_to_best_book_id(asin_best_file)

    df_cristine = get_user_read_books(2624891, api_key, df_isbn_best_book_id)
    print(len(df_cristine))

    # df_cristine = get_user_read_books(2624891, api_key, df_isbn_best_book_id)
    # print(len(df_cristine))
    # df_user_ratings = get_user_read_books(2624891, api_key)
    #
    # # Created from GoodReads API, should be the top 10K rated books
    # book_file = '../data/updated_books.csv'
    # # Created from GoodReads API, and manual classification
    # author_file = '../data/classified_authors.csv'
    # # Created from GoodReads API
    # author_book_file = '../data/author_books.csv'
    # # Created from Amazon Review file for ASIN and GoodReads API
    # asin_best_file = '../data/asin_best_book_id.csv'
    #
    # df_books = load_data.get_books(book_file)
    # df_authors = load_data.get_classified_authors(author_file)
    # df_authors_books = load_data.get_books_to_authors(author_book_file)
    # df_isbn_best_book_id = load_data.get_isbn_to_best_book_id(asin_best_file)
    # df_books_classified = load_data.merge_to_classify_books(df_authors_books,
    #                                                         df_authors,
    #                                                         df_books)
    #
    # df_user_authorsbooks_classified = create_user_authorbook_classified(
    #                                             df_isbn_best_book_id,
    #                                             df_user_ratings,
    #                                             df_books_classified)
    # # plot_user_authorbook_classified(df_user_authorsbooks_classified)
    #
    # items_matrix = np.load('../data/item_matrix.npy')
    # items_matrix_books = items_matrix[::, 0]
    # matrix_u_rate = user_ratings_for_recommender(df_user_ratings,
    #                                              df_isbn_best_book_id,
    #                                              items_matrix_books)
    # print(matrix_u_rate)
