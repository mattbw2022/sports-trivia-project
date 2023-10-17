from helpers import db_no_paramater_query, db_query, get_db_connection, db_first
import random
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler

def create_easy_test():
    # Select applicable questions
    get_questions = db_no_paramater_query("SELECT * FROM questions WHERE point_value <= 4 AND date_used < JULIANDAY('now', '-30 days')")
    
    # Select applicable questions
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
    cur.execute("INSERT INTO tests (difficulty, creation_date, categories) VALUES('Easy', CURRENT_DATE, ?)",(categories, ))
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
        conn.execute("INSERT INTO users_tests_rel VALUES(?,?)",(users[i], test_id))
        conn.commit()
        i += 1
    # Close connection
    conn.close()
    return None
def create_medium_test():

        # Select applicable questions
    get_questions = db_no_paramater_query("SELECT * FROM questions WHERE point_value >= 4 AND point_value <= 6 AND date_used < JULIANDAY('now', '-30 days')")
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
    cur.execute("INSERT INTO tests (difficulty, creation_date, categories) VALUES('Medium', CURRENT_DATE, ?)", (categories, ))
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
        conn.execute("INSERT INTO users_tests_rel VALUES(?,?)",(users[i], test_id))
        conn.commit()
        i += 1
    # Close connection
    conn.close()
    return None

def create_hard_test():

        # Select applicable questions
    get_questions = db_no_paramater_query("SELECT * FROM questions WHERE point_value >= 6 AND date_used < JULIANDAY('now', '-30 days')")
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
    cur.execute("INSERT INTO tests (difficulty, creation_date, categories) VALUES('Hard', CURRENT_DATE, ?)", (categories, ))
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
        conn.execute("INSERT INTO users_tests_rel VALUES(?,?)",(users[i], test_id))
        conn.commit()
        i += 1
    # Close connection
    conn.close()
    return None

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
        conn.execute("INSERT INTO users_tests_rel VALUES(?,?)",(users[i], test_id))
        conn.commit()
        i += 1
    # Close connection
    conn.close()
    return None

scheduler = BackgroundScheduler()
scheduler.add_job(func=create_test, trigger="interval", hours=24)
scheduler.start()

while True:
    sleep(1)