import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

import pickle

def train():
    books = pd.read_csv('books.csv')
    ratings = pd.read_csv('new_ratings.csv')
    print(ratings.shape[0])
    print('Updating model on new data...')

    ratings_with_name = ratings.merge(books, on='ISBN')

    num_rating_df = ratings_with_name.groupby('Book-Title').count()['Book-Rating'].reset_index()
    num_rating_df.rename(columns={'Book-Rating': 'num_ratings'}, inplace=True)

    avg_rating_df = ratings_with_name.groupby('Book-Title').mean()['Book-Rating'].reset_index()
    avg_rating_df.rename(columns={'Book-Rating': 'avg_rating'}, inplace=True)

    popular_df = num_rating_df.merge(avg_rating_df, on='Book-Title')

    popular_df = popular_df[popular_df['num_ratings'] >= 250].sort_values('avg_rating', ascending=False).head(50)
    popular_df = popular_df.merge(books, on='Book-Title').drop_duplicates('Book-Title')[
        ['Book-Title', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating']]

    x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
    educated_users = x[x].index  # boolean indexing

    filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(educated_users)]

    y = filtered_rating.groupby('Book-Title').count()['Book-Rating'] >= 50
    famous_books = y[y].index

    final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
    pt.fillna(0, inplace=True)

    similarity_scores = cosine_similarity(pt)
    similarity_scores.shape

    pickle.dump(popular_df, open('popular.pkl', 'wb'))
    books.drop_duplicates('Book-Title')

    pickle.dump(pt, open('pt.pkl', 'wb'))
    pickle.dump(books, open('books.pkl', 'wb'))
    pickle.dump(similarity_scores, open('similarity_scores.pkl', 'wb'))

    print('Model updated!')




