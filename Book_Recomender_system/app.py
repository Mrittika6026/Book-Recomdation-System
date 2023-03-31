from flask import Flask, render_template, request, redirect, session, flash
import pickle
import numpy as np
import mysql.connector
import os
import csv
from csv import writer
import pandas as pd
from train import train
import re


popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)
app.secret_key=os.urandom(24)

conn = mysql.connector.connect(host="localhost", user="root", database="book_recommender_system")
cursor = conn.cursor()

def check(s):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat,s):
        # print("Valid Email")
        return True
    else:
        # print("Invalid Email")
        return False
@app.route('/index')
def index():
    if 'user_id' in session:
        return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
    else:
        return redirect('/')

@app.route('/')
def login_ui():
    return render_template('login.html')

@app.route('/signup')
def signup_ui():
    return render_template('signup.html')

@app.route('/recommend')
def recommend_ui():
    if 'user_id' in session:
        return render_template('recommend.html')
    else:
        return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    users=cursor.fetchall()
    if len(users)>0:
        session['user_id'] = users[0][0]
        id = users[0][0]
        return redirect("../index")
        # return render_template('index.html')
    else:
        return render_template('login.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')

    # check_email = request.form.get('uemail')
    # if(check(check_email)):
    email = request.form.get('uemail')
    # else:
    #     flash('Invalid email!')

    password = request.form.get('upassword')

    cursor.execute("""INSERT INTO `users` (`user_id`, `name`, `email`,`password`) VALUES (NULL,'{}', '{}','{}')""".format(name, email, password))
    conn.commit()
    return render_template('login.html')

@app.route('/user_rating')
def user_rating_ui():
    if 'user_id' in session:
        return render_template('user_rating.html')
    else:
        return redirect('/')
@app.route('/rating_books', methods=['POST'])
def rating_books():
    id = str(session["user_id"])
    book = request.form.get('book')
    user_rating = request.form.get('user_rating')
    # print(id)
    # print(type(id))

    book_df = pd.read_csv('books.csv')
    book_df.drop_duplicates(subset="Book-Title",
                        keep=False, inplace=True)

    result = book_df[book_df['Book-Title'] == book]
    result1 = result.reset_index(drop=True)

    book_ISBN = result1['ISBN'][0]
    new_entry = [id, book_ISBN, user_rating]

    print(new_entry)
    # print( user_rating)
    # print(book_ISBN)
    with open ('new_ratings.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(new_entry)
        f_object.close()
    # print(book_df)
    train()
    return render_template('user_rating.html')


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/recommend_books',methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)