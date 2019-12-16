import json
import logging
import os
import pandas as pd
import sys

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from pandas.io.json import json_normalize
from urllib.request import urlopen

from db_book import *
from logging.config import dictConfig

app = Flask('book_app')
app.logger.setLevel(logging.INFO)

print(os.getcwd())
os.chdir('c:/Users/silaz/github/capstone/final_project')


@app.route('/', methods=['POST', 'GET'])
def login():

    dbHandle = db_work.getHandle()
    db_work.createDB(dbHandle)
    cursor = dbHandle.cursor()
    app.logger.info(f"Got conn handle {dbHandle}")

    if request.method == 'POST':
        app.logger.info("Getting posted data")
        user = request.form['email']
        pw = request.form['password']
        app.logger.info(f"The user is {user}")
        session['user'] = user
        #TO DO, check for user

        cnt = db_work.does_user_exist(dbHandle, user, pw)
        app.logger.info(f"Return from does_user_exist {cnt}.")

        if cnt == 2:
            app.logger.info(f"The user does not exit.")
            db_work.insertUser(user, pw, dbHandle)
            cursor.execute("SELECT id FROM users where username = ?", (user,))
            u = cursor.fetchall()
            user_id = u[0][0]
            session['user_id'] = user_id
            return redirect(url_for('books'))
        if cnt == 1:
            app.logger.info(f"The user exits but the pw was wrong.")
            return redirect(url_for('login'))
        if cnt == 0:
            app.logger.info(f"The user exits and pw is correct.")
            cursor.execute("SELECT id FROM users where username = ?", (user,))
            u = cursor.fetchall()
            user_id = u[0][0]
            session['user_id'] = user_id
            app.logger.info(f"Session for user_id {session['user_id']}")
            return redirect(url_for('books'))

    else:
        app.logger.info("Loading index.html")
        return render_template('index.html')

@app.route('/books', methods=['POST', 'GET'])
def books():

    dbHandle = db_work.getHandle()
    if request.method == 'POST':
        # Search for isbn
        try:
            url = (f"https://www.googleapis.com/books/v1/volumes?q={request.form['isbn']}")
            response = urlopen(url)
            app.logger.info(url)
            json_data = response.read().decode('utf-8', 'replace')
            d = json.loads(json_data)
            if d['totalItems'] < 1:
                raise Exception(f"Didn't find any books with isbn {request.form['isbn']}")
            assert d['totalItems'] > 0
            print(f"In book/POST")
            print(d['items'][0])
            print(f'VolumeInfo')
            print(d['items'][0]['volumeInfo'])
        except Exception as e:
            app.logger.info('Did not find a book')
            return render_template('search_results.html', error = e, book_info = {})

        app.logger.info(f"In book/POST")
        book_info = {}
        book_info['author'] = d['items'][0]['volumeInfo']['authors'][0]
        book_info['title'] = d['items'][0]['volumeInfo']['title']
        book_info['page_count'] = d['items'][0]['volumeInfo']['pageCount']
        try:
            book_info['avg_rating'] = d['items'][0]['volumeInfo']['averageRating']
        except:
            book_info['avg_rating'] = 'no ratings'
        df = json_normalize(d['items'])
        df = df[['volumeInfo.title', 'volumeInfo.authors']]
        #return render_template('search_results.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        return render_template('search_results.html', book_info = book_info)
    if request.method == 'GET':
        app.logger.info(f"Session for user_id {session['user_id']}")
        q = f"""select * from books where user_id = {session['user_id']};"""
        df = pd.read_sql_query(q, dbHandle)
        app.logger.info(df)
        titles = ['na', 'My Books']
        return render_template('books.html', tables=[df.to_html()], titles=titles)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        df = pd.read_sql_query("select * from books;", dbHandle)

@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    dbHandle = db_work.getHandle()
    titles = ['na', 'My Books']
    if request.method == 'POST':
        app.logger.info(request.data)
        #book_info = request.form.to_dict()
        book_info = {'author': request.form['author'],
                    'title': request.form['title'],
                    'page_count': request.form['page_count'],
                    'avg_rating': request.form['avg_rating']
                    }
        app.logger.info(request.form)
        print("add book")
        db_work.addBook(session['user'], book_info, dbHandle)
        df = pd.read_sql_query("select * from books;", dbHandle)
        app.logger.info(df)
        #df.drop([0, 1], axis=1, inplace=True)
        #return redirect(url_for('books', tables=[df.to_html()], titles = titles))
        return render_template('books.html', tables=[df.to_html()], titles = titles)

    if request.method == 'GET':
        df = pd.read_sql_query("select * from books;", dbHandle)
        app.logger.info(df.columns)
        df.drop('id', axis=1, inplace=True)
        df.drop('user_id', axis=1, inplace=True)
        #return redirect(url_for('books', tables=[df.to_html()], titles = titles))
        return render_template('books.html', tables=[df.to_html()], titles = titles)

@app.route('/delete_book', methods=['POST', 'GET'])
def delete_book():
    dbHandle = db_work.getHandle()
    cursor = dbHandle.cursor()
    titles = ['na', 'My Books']
    if request.method == 'POST':
        book_id = request.form['book_id']
        cursor.execute("DELETE FROM books where id = ?", (book_id,))
        dbHandle.commit()
        df = pd.read_sql_query("select * from books;", dbHandle)
        return render_template('books.html', tables=[df.to_html()], titles = titles)
    if request.method == 'POST':
        return redirect(url_for('books'))

if __name__ == '__main__':
    print(app.root_path)
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
