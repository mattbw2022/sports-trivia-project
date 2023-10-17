from flask import Blueprint

import random
from helpers import dict_factory, login_required, get_db_connection, db_first, db_query
from flask import render_template, session, request, redirect, flash

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route("/test/<test_id>", methods = ["POST"])
@login_required
def initialize_test(test_id):
    user_id = session["user_id"]
    index = 0
    
    # check to see if user has answered any questions for this test previously
    conn = get_db_connection()
    row = conn.execute("SELECT questions_id FROM answers WHERE user_id = ? AND test_id = ?",(user_id, test_id))
    test_check_db = row.fetchall()
    conn.close()

    if len(test_check_db) > 0:
        # if len is greater than 0 set index to len
        index = len(test_check_db)
        return redirect(f"/test/{test_id}/question/{index}")
    # if query returns nothing, no answers have been recorded and index remains 0
    return redirect(f"/test/{test_id}/question/{index}")
        
@quiz_bp.route("/test/<int:test_id>/question/<int:index>")
@login_required
def getNextQuestion(test_id, index):

    user_id = session["user_id"]

    first_name_db = db_first("SELECT firstname FROM users WHERE id = ?", user_id)
    first_name = first_name_db["firstname"]

    # get question ids for current test
    questions_ids_db = db_query("SELECT questions_id FROM questions_tests_rel WHERE test_id = ? ORDER BY questions_id",test_id)

    question_ids = []
    i = 0
    while i < len(questions_ids_db):
        question = questions_ids_db[i]["questions_id"]
        question_ids.append(question)
        i += 1

    # get point values for the current question
    point_values_db = db_first("SELECT point_value FROM questions WHERE id = ?", question_ids[index])
    point_value = point_values_db["point_value"]

    # get the question for the current question id
    questions_db = db_first("SELECT question FROM questions WHERE id = ?",question_ids[index])
    question = questions_db["question"]

    # get the correct answer and wrong ansers for current question
    answers = []
    answers_db = db_query("SELECT correct_answer, wrong_1, wrong_2, wrong_3 FROM questions WHERE id = ?", question_ids[index])
    answer = answers_db[0]["correct_answer"]
    answers.append(answer)
    answer = answers_db[0]["wrong_1"]
    answers.append(answer)
    answer = answers_db[0]["wrong_2"]
    answers.append(answer)
    answer = answers_db[0]["wrong_3"]
    answers.append(answer)     
   
    # randomize where answer choices will be located
    random.shuffle(answers)

    try:
        # get user's quiz points
        conn = get_db_connection()
        row = conn.execute("SELECT points_earned FROM users_tests_rel WHERE test_id = ? AND user_id = ?",(test_id, user_id))
        quiz_points_db = row.fetchone()
        quiz_points = quiz_points_db["points_earned"]

        question_number = index + 1
    
    except:
        # if no points, set to 0
        question_number = index + 1
        quiz_points = 0
    # get user's total points
    total_points_db = db_first("SELECT points FROM users WHERE id = ?", user_id)
    total_points = total_points_db["points"]


    return render_template("question.html", index=index, test_id=test_id, question=question, answer1=answers[0], answer2=answers[1], answer3=answers[2], answer4=answers[3],question_id=question_ids[index], point_value=point_value, total_points=total_points, quiz_points=quiz_points, question_number=question_number, first_name=first_name)

@quiz_bp.route("/test/<int:test_id>/question/<int:index>", methods=["POST"])
@login_required
def answerQuestion(test_id, index):
    # establish user and test ids
    user_id = session["user_id"]
    test_id = test_id 

    # get question ids for test
    questions_ids_db = db_query("SELECT questions_id FROM questions_tests_rel WHERE test_id = ? ORDER BY questions_id",test_id)
    
    question_ids = []
    i = 0
    while i < len(questions_ids_db):
        question = questions_ids_db[i]["questions_id"]
        question_ids.append(question)
        i += 1

    # get user answer
    user_answer = request.form.get("answer")

    if not user_answer:
        return redirect(f"/test/{test_id}/question/{index}")

    # get correct answer to applicable question
    correct_answer_db = db_first("SELECT * FROM questions WHERE id = ?", question_ids[index])
    
    correct_answer_text = correct_answer_db["correct_answer"]

    successful_answer = True

    # check answer
    if user_answer == correct_answer_text:
        successful_answer = True
    else:
        successful_answer = False

    # update user records
    if successful_answer == True:
        quiz_points = 0
        result = 1
        # save answer to answer table
        conn = get_db_connection()
        conn.execute("INSERT INTO answers (test_id, user_id, questions_id, user_answer, result) VALUES(?,?,?,?,?)",(test_id, user_id, question_ids[index], user_answer, result))
        conn.commit()
        conn.close()

        # get user's correct answers
        conn = get_db_connection()
        row = conn.execute("SELECT questions_id FROM answers WHERE result = 1 AND test_id = ? AND user_id = ?", (test_id, user_id))
        correct_answers_ids_db = row.fetchall()
        conn.close()

        # make list of correct answers
        i = 0
        correct_answers_ids = []
        for item in correct_answers_ids_db:
            correct_answer_id = correct_answers_ids_db[i]["questions_id"]
            correct_answers_ids.append(correct_answer_id)
            i += 1

        # update correct answers
        conn = get_db_connection()
        conn.execute("UPDATE users_tests_rel SET correct_answers = ? WHERE user_id = ? AND test_id = ?", (len(correct_answers_ids), user_id, test_id))
        conn.commit()
        conn.close()

        # get point value of most recent correct answer
        i = 0
        for item in correct_answers_ids:
            new_points_db = db_query("SELECT point_value FROM questions WHERE id = ?", question_ids[i])
            new_points = new_points_db[0]["point_value"]
            quiz_points = quiz_points + new_points
            i += 1
        # update points earned for this test
        conn = get_db_connection()
        conn.execute("UPDATE users_tests_rel SET points_earned = ? WHERE user_id = ? AND test_id = ?",(quiz_points, user_id, test_id))
        conn.commit()
        conn.close()

        # get user's total points and add new points
        total_points_db = db_query("SELECT points FROM users WHERE id = ?", user_id)
        total_points = total_points_db[0]["points"]
        total_points = total_points + new_points

        # update user's total points
        conn = get_db_connection()
        conn.execute("UPDATE users SET points = ? WHERE id = ?", (total_points , user_id))
        conn.commit()
        conn.close()
        
        # Flash feedback
        flash(f"Great job! {correct_answer_text} was correct. You earned {new_points} points, good luck on your next question!","correct")
   

    # update user records if incorrect
    else:

        result = 0

        # save answer to answer table
        conn = get_db_connection()
        conn.execute("INSERT INTO answers (test_id, user_id, questions_id, user_answer, result) VALUES(?,?,?,?,?)",(test_id, user_id, question_ids[index], user_answer, result))
        conn.commit()
        conn.close()

        # get user's wrong answers
        conn = get_db_connection()
        row = conn.execute("SELECT questions_id FROM answers WHERE result = 0 AND test_id = ? AND user_id = ?", (test_id, user_id))
        wrong_answers_db = row.fetchall()
        conn.commit()
        conn.close()
        
        # update wrong answers
        conn = get_db_connection()
        conn.execute("UPDATE users_tests_rel SET wrong_answers = ? WHERE user_id = ? AND test_id = ?", (len(wrong_answers_db), user_id, test_id))
        conn.commit()
        conn.close()

        if user_answer == "none":
            flash(f"Time ran out! The correct answer was {correct_answer_text}. Good luck on your next question!","wrong")
        else:
            flash(f"{user_answer} is incorrect. The correct answer was {correct_answer_text}. Good luck on your next question!","wrong")

    # figure out next question
    index += 1
    if index > len(question_ids) - 1:

        conn = get_db_connection()
        row = conn.execute("SELECT points_earned FROM users_tests_rel WHERE test_id = ? AND user_id = ?",(test_id, user_id))
        quiz_points_db = row.fetchone()
        conn.close()
        quiz_points = quiz_points_db["points_earned"]

        conn = get_db_connection()
        row = conn.execute("SELECT questions_id FROM answers WHERE result = 1 AND test_id = ? AND user_id = ?", (test_id, user_id))
        correct_answers_ids_db = row.fetchall()
        conn.close()

        if quiz_points == 0:
            correct_answers_ids = []
            
            # update points earned for this test
            conn = get_db_connection()
            conn.execute("UPDATE users_tests_rel SET points_earned = ? WHERE user_id = ? AND test_id = ?",(quiz_points, user_id, test_id))
            conn.commit()
            conn.close()

        points_possible_db = db_first("SELECT SUM(point_value) FROM questions WHERE id IN(SELECT questions_id FROM questions_tests_rel WHERE test_id = ?)", test_id)

        points_possible = points_possible_db["SUM(point_value)"]
        score = len(correct_answers_ids_db) * len(question_ids)
        # record date of submission, number of correct answers, points possible and score
        conn = get_db_connection()
        conn.execute("UPDATE users_tests_rel SET submit_date = CURRENT_DATE, points_possible = ?, score = ? WHERE user_id = ? AND test_id = ?",(points_possible, score, user_id, test_id))
        conn.commit()
        conn.close()

        # get number of tests taken by users previously
        db_tests_taken = db_first("SELECT tests_taken FROM users WHERE id = ?", user_id)
        tests_taken = db_tests_taken["tests_taken"]

        # update the number of tests taken
        tests_taken = tests_taken + 1
        conn = get_db_connection()
        conn.execute("UPDATE users SET tests_taken = ? WHERE id = ?",(tests_taken, user_id))
        conn.commit()
        conn.close()

        # mark test as completed for user
        conn = get_db_connection()
        conn.execute("UPDATE users_tests_rel SET test_completed = 1 WHERE test_id = ? AND user_id = ?",(test_id, user_id))
        conn.commit()
        conn.close()

        return redirect(f"/test_summary/{test_id}")

    # update total answers
    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute("SELECT correct_answers, wrong_answers FROM users_tests_rel WHERE user_id = ? AND test_id = ?",(user_id, test_id))
    total_answers_db = row.fetchall()
    conn.close()

    correct_answers = total_answers_db[0]["correct_answers"]
    wrong_answers = total_answers_db[0]["wrong_answers"]
    total_answers = correct_answers + wrong_answers

    conn = get_db_connection()
    conn.execute("UPDATE users_tests_rel SET total_answers = ? WHERE test_id = ? AND user_id = ?",(total_answers, test_id, user_id))
    conn.commit()
    conn.close()

    return getNextQuestion(test_id, index)

@quiz_bp.route("/test_summary/<int:test_id>", methods=["GET","POST"])
def summary(test_id):
    user_id = session["user_id"]

    if request.method == "POST":
        test_id = test_id

    # get information needed for test summary
    test = db_query("SELECT * FROM questions WHERE id IN(SELECT questions_id FROM questions_tests_rel WHERE test_id = ? ORDER BY questions_id)",(test_id))
    
    # get user's first name
    first_name_db = db_first("SELECT firstname FROM users WHERE id = ?", user_id)
    first_name = first_name_db["firstname"]

    # get user's answer to each question
    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute("SELECT user_answer FROM answers WHERE user_id = ? AND test_id = ?", (user_id,test_id))
    user_answers_db = row.fetchall()
    conn.close()

    # create a list of user's answers
    i = 0
    user_answers = []
    for item in user_answers_db:
        user_answer = user_answers_db[i]["user_answer"]
        user_answers.append(user_answer)
        i += 1

    conn = get_db_connection()
    conn.row_factory = dict_factory
    row = conn.execute("SELECT correct_answers, wrong_answers, points_earned, points_possible, score FROM users_tests_rel WHERE user_id = ? AND test_id = ?", (user_id,test_id))
    user_results_db = row.fetchall()
    conn.close()

    correct_answers = user_results_db[0]["correct_answers"]
    wrong_answers = user_results_db[0]["wrong_answers"]
    points_earned = user_results_db[0]["points_earned"]
    points_possible = user_results_db[0]["points_possible"]
    score = user_results_db[0]["score"]

    questions = correct_answers + wrong_answers

    return render_template("test_summary.html", test=test, user_answers=user_answers, test_id=test_id, first_name=first_name, correct_answers=correct_answers, questions = questions, points_earned=points_earned, points_possible=points_possible, score=score)
