from flask import Blueprint
from postmarker.core import PostmarkClient
from helpers import login_required, get_db_connection, db_first, db_no_paramater_query, check_password, db_query, dict_factory
from flask import render_template, session, request, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash

login_assist_bp = Blueprint('login_assist', __name__)

@login_assist_bp.route("/forgot_username", methods=["GET", "POST"])
def forgot_username():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # make sure email and password were entered
        if not email or not password:
            flash("Email and password are required to retrieve username.", "notify")
            return redirect("/forgot_username")
        
        # check that the email is valid
        try:
            user_info = db_query("SELECT * FROM users WHERE email = ?", email)
            user_id = user_info[0]["id"]
            firstname = user_info[0]["firstname"]
            username = user_info[0]["username"]
        
        #notify of invalid email
        except:
            flash("The email entered is not associated with an account.", "notify")
            return redirect("/forgot_username")

        # get users hash
        hash_db = db_first("SELECT hash FROM users WHERE id = ?", user_id)
        user_hash = hash_db["hash"]

        try:
            # check user password
            check_password_hash(user_hash, password)
            
            #provide username to user
            flash(f"Hello {firstname}, your username is {username}.", "notify")

        except:

            # notify of invalid password
            flash("Password entered is not correct for email entered. Please try again.", "notify")
            return redirect("/forgot_username")

        return redirect("/forgot_username")

    return render_template("forgot_username.html")

@login_assist_bp.route("/forgot_password", methods=["GET", "POST"])
def auth_user():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        print(username)
        print(email)
        if not username or not email:
            flash('Email and username must be provided.', 'notify')
            return redirect("/forgot_password")
        try:
            conn = get_db_connection()
            conn.row_factory = dict_factory
            row = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            result = row.fetchall()
            conn.close()
            session["temp_id"] = result[0]["id"]
        except:
            flash("Unable to find a matching account. The form is case sensitive, please check your inputs and try again.", "notify")
            return redirect('/forgot_password')
        return redirect("/password_reset_auth")
    else:
        return render_template('forgot_password.html')

@login_assist_bp.route("/password_reset_auth", methods=["GET", "POST"])
@login_required
def reset_auth():
    if session.get("user_id") is None:
        user_id = session["temp_id"]
    else:
        user_id = session["user_id"]
    if request.method == "GET":
        question = db_query("SELECT security_question FROM users WHERE id = ?", user_id)
        return render_template('password_reset_auth.html', question = question[0]["security_question"])
    else:
        answer = request.form.get('security-answer').lower()

        if not answer:
            flash('An answer is required to reset password', "notify")
            return redirect('/password_reset_auth')
        result = db_query("SELECT security_answer FROM users WHERE id = ?", user_id)
        user_answer = result[0]["security_answer"]
        if user_answer != answer:
            flash('Answer given does match the answer on file. Please try again.', "notify")
            return redirect('/password_reset_auth')
        else:
            return redirect('/password_reset')

@login_assist_bp.route("/password_reset", methods=["GET", "POST"])
@login_required
def reset_password():
    user_id = session['user_id']
    if request.method == "POST":
        password = request.form.get('new_password')
        strong_password = check_password(password)
        if not password:
            flash("Please enter a password.", "notify")
            return redirect("/password_reset")
        if strong_password == False:
            flash("Password must be a minimum 8 characters.\nThe alphabet must be between [a-z].\nAt least one alphabet should be of Upper Case [A-Z].\nAt least 1 number or digit between [0-9].", "notify")
            return redirect("/password_reset")
        try:
            conn = get_db_connection()
            hash = generate_password_hash(password)
            conn = get_db_connection()
            conn.execute("UPDATE users SET hash = ? WHERE id = ?",(hash, user_id))
            conn.commit()
            conn.close()
        except:
            flash('Unable to update password. Please try again later.')
            return redirect('/password_reset')
        flash('Password reset successfully!', "notify")
        return redirect('/profile')
    else:
        return render_template('reset_password_form.html')      