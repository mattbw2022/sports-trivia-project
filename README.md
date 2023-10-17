# Sports Trivia
#### Video Demo: https://youtu.be/RL1sLy5bJ_s
#### Description:

App.py:

This is the main file setting up the flask application. It also includes some of the basic functions and app routes. 

create_test:
This method runs every day at 12:30 AM to create a new test. The method pulls question ids from the database that have not been used in the last 30 days. It will randomly select 10 question ids to create a test with and assign to all current users.

/leaderboard:
@login_required - if no user is logged in redirect to /login.


This route simply runs a query for to return all users in descending order by total points.

/profile:

This route provides user test history with links to individual test summaries should the user wan to review their performance or answers.

The route provides any in progress tests for the user to resume their any test that has recorded an answer.

/play:

The play route provides the user with a list of tests available to the user. If the test has been completed it will no longer be available to the user. 

/login & /logout:

These routes do exactly what you think. Logout clears the session and redirects to index.html. Login validates login credentials and redirects to the user's profile.

/signup:

The user enters their information to signup. 
The username, email and password are checked to make sure it is unique from those currently in the database.

The password must have a certain strength or it will not be accepted.

The email must contain an @ and a . in the correct position or it will not be accepted. I debated using an API but decided against spending the money. There is a function in werkzurg but it requried a downgrade in python version which would have caused other issues.

Once all checks are met the user is added to the database. Their session is established,  a confirmation email is sent, all tests in the database are added in relation to the user. The user is redirected to /unconfirmed where they cannot access any of the features until email is confirmed.

/unconfirmed:

Here the user is prompted to check their email for the confirmation email. The user may click a button to resend the link as well.

/confirmed/<user_id>:

The email confirmation link goes to this route and the confirmed status is updated in the database and the user is redirected to their profile.


helpers.py

login_required (see above)

get_db_connection - returns a connection to the database.

check_username - returns true if a query searching for the entered username is 0 showing no matches and false otherwise

check_email - returns true if the email contains text@text.text and false if not in this structure

check_password - ensures that the password is at least 8 characters long or returns false. Also must contain a special char, uppercase letter, lowercase letter and a digit.

dict_factory - returns a dictionary

db_query - shortcut to run a query with one parameter and fetches all rows

db_first - same as db_query but only fetches one row.

db_no_paramater_query - shortcut to run a query with no parameters.

db_insert_new_user - shortcut to adding a new user in the database.


init_db.py:

creates a connection to the database.


login_assist.py:

/forgot_username - allows the user to recover their username with valid email and password.

/forgot_password - allows user to request a password reset email with a vaild email submission. If valid a link is sent to their email. The link redirects to /reset_password.

/reset_password - users will be prompted for a new_password, confirmation of that password and their username (provided in reset password email). Password is checked for uniquness and strenght and username is checked for validity. If all checks are met records are updated and user is redirected to /login.


quiz.py:

/test/<test_id>:

After a user has selected a test from /play initialize_test checks if any answers have been submitted from the current test. If so, the user is returned to their next unanswerd question. If not, the user begins on question 1.

/test/<int:test_id>/question/<int:index>

getNextQuestion - Gets the next question information based on the index and the user's current quiz and total points, as well as user's firstname for rendering.

/test/<int:test_id>/question/<int:index>

answerQuestion - gets user answer and checks against the correct answer. All answers are recorded for the user and counted. 

Points are distributed for correct answers based on the assigned value. 

Total and quiz points are updated.

Index is checked to make sure there are more questions, if so, redirect to GetNextQuestion.
If not, points earned, tests taken are updated and the test is marked as completed for the user and they are redirected to /test_summary/<int:test_id>.


/test_summary/<int:test_id> - the results of each question and total test score is displayed for the user. This can be accessed for any completed test via user profile.


user_changes.py:

/delete_account - The user can delete their account by submitting valid email and password. If valid the user's answers, test relationships and the user are deleted from the database. The session is cleared and they are redirected to index.html.

/change_username - A user can change their username at any time as long as the username is not in use by any current user.

/change_password - The user can change their password with a vaild current password and a unique and strong new password. These are checked as in previous routes/methods.


