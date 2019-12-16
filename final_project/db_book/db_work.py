import sqlite3 as sql
import logging

log = logging.getLogger('book_app.sub')

def getHandle():
    log.info("GetHandle and make db")
    #dbHandle = sql.connect('file:final_project.db?mode=rw', uri=True)
    dbHandle = sql.connect('file:final_project.db', uri=True)
    return dbHandle

def createDB(dbHandle):
    cursor = dbHandle.cursor()
    log.info("Create table if NOT exists")
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                id integer PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                UNIQUE(username))
            ''')
    dbHandle.commit()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS books(
                id integer PRIMARY KEY,
                user_id integer NOT NULL,
                book_title TEXT NOT NULL,
                book_author TEXT NOT NULL,
                book_page_count TEXT NOT NULL,
                book_avg_rating integer NOT NULL,
                UNIQUE(user_id, book_title, book_author))
            ''')
    dbHandle.commit()

def insertUser(username,password, dbHandle):
    log.info("Insert into users...")
    cursor = dbHandle.cursor()
    cursor.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
    dbHandle.commit()

def addBook(user, book_info, dbHandle):
    log.info(f"Adding book...for {user} with book_info {book_info}")
    cursor = dbHandle.cursor()
    cursor.execute("SELECT id FROM users where username = ?", (user,))
    u = cursor.fetchall()
    user_id = u[0][0]
    try:
        cursor.execute('''INSERT INTO books
                (user_id, book_title, book_author, book_page_count, book_avg_rating)
                VALUES(?, ?, ?, ?, ?)''', (user_id, book_info['title'], book_info['author'],
                book_info['page_count'], book_info['avg_rating']))
    except:
        log.info("already have this book")
    dbHandle.commit()

def retrieveUsers(dbHandle):
    log.info("Get users...")
    cursor = dbHandle.cursor()
    cursor.execute("SELECT username, password FROM users")
    users = cursor.fetchall()
    return users

def does_user_exist(dbHandle, user, password):
    log.info(f"Does {user} exist")
    cursor = dbHandle.cursor()
    cursor.execute("SELECT count(username) FROM users where username = ? ", (user,))
    users = cursor.fetchall()
    log.info(f"Count from select user --> {users}")
    if users[0][0] == 1:
        log.info(f"{user} exists, is pw {password} correct?")
        cursor.execute("SELECT count(username) FROM users where username = ? and password = ?", (user,password,))
        login = cursor.fetchall()
        log.info(f"Return from select username,password {login}")
        if login[0][0] == 1:
            log.info(f"pw is correct")
            return 0
        else:
            log.info(f"pw is NOT correct")
            return 1
    else:
        return 2

    return users
