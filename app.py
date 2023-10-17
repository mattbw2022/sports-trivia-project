import random
import threading
from flask import Flask
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
from helpers import test_needed, create_test, login_required, get_db_connection, check_username, check_email, check_password, db_first, db_query, db_insert_new_user, db_no_paramater_query
from flask import Flask, render_template, session, request, redirect, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from quiz import quiz_bp
from user_changes import user_change_bp
from login_assist import login_assist_bp
from flask_session import Session

app = Flask(__name__)
# register routes in other files
app.register_blueprint(quiz_bp)
app.register_blueprint(user_change_bp)
app.register_blueprint(login_assist_bp)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(__name__)
Session(app)
    

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
    conn.close()
    return None

def while_function():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_test,"cron", day='*', hour=11, minute=6)
    scheduler.start()

second_thread = threading.Thread(target=while_function)
second_thread.start()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/leaderboard")
@login_required
def leaderboard():
    leaderboard = db_no_paramater_query("SELECT * , rank() OVER (ORDER BY points DESC) rank FROM users")
    return render_template("leaderboard.html", leaderboard = leaderboard)

@app.route("/profile")
@login_required
def profile():
    user_id = session['user_id']
    user_info = db_query("SELECT * FROM users WHERE id = ?", user_id)
    ranking_info = db_query("SELECT * FROM (SELECT * , rank() OVER (ORDER BY points DESC) rank FROM users) WHERE id = ?", user_id)
    
    ranking = ranking_info [0]["rank"]
    firstname = user_info[0]["firstname"]
    points = user_info[0]["points"]
    tests_taken = user_info[0]["tests_taken"]

    test_history = {}
    if tests_taken != 0:
        test_history = db_query("SELECT * FROM users_tests_rel WHERE test_completed = 1 AND user_id = ?", user_id)

    active_tests = db_query("SELECT * FROM users_tests_rel WHERE correct_answers | wrong_answers > 0 AND test_completed = 0 AND user_id = ?", user_id)
    return render_template("profile.html", points = points, firstname = firstname, tests_taken = tests_taken, ranking = ranking, test_history = test_history, active_tests=active_tests)

@app.route("/play")
@login_required
def setup():
    new_test = test_needed()
    if new_test == True:
        create_test()

    user_id = session['user_id']
    tests = db_query("SELECT * FROM tests WHERE id IN(SELECT test_id FROM users_tests_rel WHERE test_completed = 0 AND user_id = ?)",user_id)

    if len(tests) == 0:
        return render_template("no_test.html")
    
    return render_template("setup.html", tests = tests)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Username is required, please enter a username.", "notify")
            return redirect("/login")

        # Ensure password was submitted
        elif not password:
            flash("Password is required, please enter a password.", "notify")
            return redirect("/login")

        # Query database for username
        user_info = db_query("SELECT * FROM users WHERE username = ?", username)  

        # Ensure username exists and password is correct
        if len(user_info) != 1 or not check_password_hash(user_info[0]["hash"], password):
            flash("Either the username or password entered is not correct, please try again.", "notify")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = user_info[0]["id"]

        # Redirect user to home page
        return redirect("/profile")

    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""


    if request.method == "GET":
        return render_template("signup.html")

    else:

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        security_question = request.form.get("security-question")
        security_answer = request.form.get("security-answer").lower()
        print(security_question)
        print(security_answer)

        unique_username = check_username(username)
        strong_password = check_password(password)
        valid_email = check_email(email)

        # make sure first name was entered
        if not firstname:
            flash("Please enter your first name.", "notify")
            return redirect("/signup")

        # make sure last name was entered
        if not lastname:
            flash("Please enter your last name.", "notify")
            return redirect("/signup")
        
        # make sure email was entered
        if not email:
            flash("Please enter your email.", "notify")
            return redirect("/signup")
        
        # make sure the email has not been used
        email_list_db = db_no_paramater_query("SELECT email FROM users")
        i = 0
        while i < len(email_list_db):
            if email_list_db[i]["email"] == email:
                flash("email already in use, please try another password.", "notify")
                return redirect("/signup")
            else:
                i += 1
        # check to see if email is valid
        if valid_email == False:
            flash("Please enter a valid email.", "notify")
            return redirect("/signup")

        # make sure username was entered
        if not username:
            flash("Please enter a username.", "notify")
            return redirect("/signup")

        # make sure username has not been used yet
        elif unique_username == False:
            flash("Username is already in use. Please enter a different username.", "notify")
            return redirect("/signup")

        # make sure password has been entered
        if not password:
            flash("Please enter a password.", "notify")
            return redirect("/signup")

        # check password strength
        elif strong_password == False:
            flash("Password must be a minimum 8 characters.\nThe alphabet must be between [a-z].\nAt least one alphabet should be of Upper Case [A-Z].\nAt least 1 number or digit between [0-9].", "notify")
            return redirect("/signup")
        
        if not security_question:
            flash("Please select a security question for password recovery.")
            return redirect("/signup")
        
        if not security_answer:
            flash("Please provide a security answer for password recovery.")
            return redirect("/signup")

        # create a hash
        hash = generate_password_hash(password)

        # create new user
        db_insert_new_user("INSERT INTO users (firstname, lastname, email, username, hash, security_question, security_answer) VALUES (?,?,?,?,?,?,?);",
        firstname, lastname, email, username, hash, security_question, security_answer)

        # Establish session
        id = db_query("SELECT id FROM users WHERE username = ?", username)
        session['user_id'] = id[0]["id"]
        session.modified = True
        
        user = session['user_id']
        user_info = db_query("SELECT * FROM users WHERE id = ?", user)

        # Add all current tests for new user
        tests = db_no_paramater_query("SELECT id FROM tests")
        test_list = []
        i = 0
        while i < len(tests):
            test = tests[i]["id"]
            test_list.append(test)
            i += 1

        i = 0
        conn = get_db_connection()
        while i < len(tests):
            conn.execute("INSERT INTO users_tests_rel (user_id, test_id) VALUES(?,?)",(user,test_list[i]))
            conn.commit()
            i += 1
        conn.close()
        return redirect("/profile")   
