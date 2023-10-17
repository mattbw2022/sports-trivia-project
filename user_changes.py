from flask import Blueprint
from helpers import login_required, get_db_connection, db_first, db_no_paramater_query, check_password
from flask import render_template, session, request, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash

user_change_bp = Blueprint('user_changes', __name__)

@user_change_bp.route("/delete_account", methods = ["GET", "POST"])
@login_required
def delete_account():
    # establish user
    user_id = session["user_id"]

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # ensure fields have been completed
        if not email or not password:
            flash("Email and password are required to delete account.", "notify")
            return redirect("/delete_account")
        
        # get user hash
        email_hash_db = db_first("SELECT hash, email FROM users WHERE id = ?", user_id)
        user_email = email_hash_db["email"]
        user_hash = email_hash_db["hash"]

        # check email entered
        if email != user_email:
            flash("Email entered does not match user email, please try again.", "notify")
            return redirect("/delete_account")

        try:
            # check user password
            check_password_hash(user_hash, password)
            flash("Account Successfully deleted.", "notify")

        except:
            # notify of invalid password
            flash("Password entered does not match user password, please try again.", "notify")
            return redirect("/delete_account")

        # delete user's answers
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM answers WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except:
            # if no answers continue
            no_answers = True
        # delete test rels
        conn = get_db_connection()
        conn.execute("DELETE FROM users_tests_rel WHERE user_id = ?",(user_id,))
        conn.commit()
        conn.close()

        # delete user
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        session.clear()

        return redirect("/")

    # get user first name for rendering
    first_name_db = db_first("SELECT firstname FROM users WHERE id = ?", user_id)
    first_name = first_name_db["firstname"]  

    return render_template("delete_account.html", first_name=first_name)

@user_change_bp.route("/change_username", methods = ["GET", "POST"])
@login_required
def change_username():

    user_id = session["user_id"]

    if request.method == "POST":
        # get user input
        new_username = request.form.get("new_username")
        # check that field has been entered
        if not new_username:
            flash("Please enter the desired username", "notify")
            return redirect("/change_username")
        # get all usernames
        check_username_db = db_no_paramater_query("SELECT username FROM users")

        # create list of usernames
        i = 0
        username_list = []
        for item in check_username_db:
            username = check_username_db[i]['username']
            username_list.append(username)
            i += 1

        # loop through list and check for matches
        for item in username_list:
            if new_username == item:
                # notify user the entered user name is being used, redirect
                flash(f"{new_username} is currently in use. Please enter a different username.", "notify")
                return redirect("/change_username")

        # if no matches change username
        conn = get_db_connection()
        conn.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
        conn.commit()
        conn.close()

        # notify of successful change and redirect
        flash("Username successfully changed!", "notify")
        return redirect("/profile")

    return render_template("change_username.html")
        
@user_change_bp.route("/change_password", methods = ["GET", "POST"])
@login_required
def change_password():
    user_id = session["user_id"]

    if request.method == "POST":
        # get user input
        password = request.form.get("password")
        new_password = request.form.get("new_password")

        # ensure fields were entered
        if not password or new_password:
            flash("Current and new passwords are required to change your password.", "notify")
            return redirect("/change_password")

        # get user's current hash
        hash_db = db_first("SELECT hash FROM users WHERE id = ?", user_id)
        user_hash = hash_db["hash"]

        # ensure the new password is different
        if password == new_password:
            flash("New password cannot be the same as the current password.", "notify")
            return redirect("/change_password")

        try:

            # check for valid password
            check_password_hash(user_hash,password)

            # check new password strength
            strong_password = check_password(new_password)
            if strong_password == False:
                flash("Password must be a minimum 8 characters.\nThe alphabet must be between [a-z].\nAt least one alphabet should be of Upper Case [A-Z].\nAt least 1 number or digit between [0-9].", "notify")
                return redirect("/change_password")

            # create new hash and update db
            new_hash = generate_password_hash(new_password)
            conn = get_db_connection()
            conn.execute("UPDATE users SET hash = ? WHERE id = ?", (new_hash,user_id))
            conn.commit()
            conn.close()
            flash("Password successfully changed!", "notify")
            return redirect("/profile")

        except:     
        # prompt another attempt
            flash("Incorrect current password. Please enter your current password.", "notify")
            return render_template("change_password.html")

    return render_template("change_password.html")