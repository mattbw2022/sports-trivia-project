from datetime import date
import random
import sqlite3
import re
import time
from flask import redirect, session, render_template
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None and session.get("temp_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('database.db', timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def check_username(username):
    user_query = db_query("SELECT COUNT(username) FROM users WHERE username = ?", username)
    if user_query[0]["COUNT(username)"] == 0:
        return True
    else:
        return False

def check_email(email):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat, email):
        return True
    else:
        return False

def check_password(password):
    l, u, d, p = 0, 0, 0, 0
    special_chars = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+','`','~','{','}','|','[',']',':',';','"',"'",'<',',','>','.','?','/']
    s = password
    if (len(s) >= 8):
        for i in s:

            # counting lowercase alphabets
            if (i.islower()):
                l+=1           

            # counting uppercase alphabets
            if (i.isupper()):
                u+=1           

            # counting digits
            if (i.isdigit()):
                d+=1           
            # counting special characters
            if(i in special_chars):
                p+=1 
    if (l>=1 and u>=1 and d>=1 and l+u+d+p==len(s)):
        return True
    else:
        return False

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}
        
def db_query(query, parameters):
    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute(query, (parameters,))
    query_info = row.fetchall()
    conn.close()
    return query_info

def db_first(query, parameters):
    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute(query, (parameters,))
    query_info = row.fetchone()
    conn.close()
    return query_info

def db_no_paramater_query(query):
    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute(query)
    query_info = row.fetchall()
    conn.close()
    return query_info

def db_insert_new_user(query, parameter1, parameter2, parameter3, paramater4, paramater5, paramater6, paramater7):
    conn = get_db_connection()
    conn.execute(query, (parameter1, parameter2, parameter3, paramater4, paramater5, paramater6, paramater7))
    conn.commit()
    conn.close()


def test_needed():
    test_needed = True
    latest_test_db = db_no_paramater_query("SELECT creation_date FROM tests ORDER BY rowid DESC")
    latest_test = latest_test_db[0]["creation_date"]

    current_date = date.today()
    if latest_test == current_date:
        test_needed = False

    return test_needed

def create_test():
    get_questions = db_no_paramater_query("SELECT * FROM questions WHERE JULIANDAY(date_used) < JULIANDAY('now', '-30 days')")
    questions = []

    # Add question ids into a list
    i = 0
    while i < len(get_questions):
        id = get_questions[i]["id"]
        questions.append(id)
        i += 1

    # randomize order of questions
    random.shuffle(questions)

    # Select 10 questions
    i = 0
    selected_questions = []
    while i < 10:
        
        selected_questions.append(questions[i])
        i += 1

    # get categories in test
    categories_list = []
    i = 0
    for item in selected_questions:

        categories_db = db_first("SELECT category FROM questions WHERE id = ?", selected_questions[i])
        category = categories_db["category"]
        
        if i == 0:
            categories_list.append(category)
            i += 1
            continue
        else:
            duplicate = (category in categories_list)

            if duplicate == False:
                categories_list.append(category)
        i += 1

    i = 0
    for item in categories_list:
        if i == 0:
            categories = categories_list[i]
            i += 1
        else:
            categories = categories + ", " + categories_list[i]
            i += 1

    # Create Test
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tests (difficulty, creation_date, categories) VALUES('Random', CURRENT_DATE, ?)", (categories, ))
    conn.commit()
    cur.close()
    conn.close()

    #Retrieve new test identifiers
    test_id_db = db_no_paramater_query("SELECT MAX(id) FROM tests;")
    test_id = test_id_db[0]["MAX(id)"]
    test_date_db = db_query("SELECT (creation_date) FROM tests WHERE id = ?", test_id)
    test_date = test_date_db[0]["creation_date"]

    # Associate questions with test
    conn = get_db_connection()
    i = 0
    while i < len(selected_questions):

        conn.execute("INSERT INTO questions_tests_rel VALUES(?,?)",(test_id, selected_questions[i]))
        conn.commit()
        conn.execute("UPDATE questions SET date_used = ? WHERE id = ?",(test_date, selected_questions[i]))
        conn.commit()
        i += 1
    conn.close()
    # Add test for current users
    users_db = db_no_paramater_query("SELECT id FROM users")
    i = 0
    users = []
    while i < len(users_db):
        user_id = users_db[i]["id"]
        users.append(user_id)
        i += 1

    i = 0
    conn = get_db_connection()
    while i < len(users):
        conn.execute("INSERT INTO users_tests_rel (user_id, test_id) VALUES(?,?)",(users[i], test_id))
        conn.commit()
        i += 1
    # Close connection
    conn.close()
    return None