

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    points NUMERIC NOT NULL DEFAULT 0,
    email TEXT,
    tests_taken INTEGER DEFAULT 0,
    confirmed TEXT DEFAULT 'no'
    );

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    point_value NUMERIC,
    category TEXT,
    question TEXT,
    correct_answer TEXT,
    wrong_1 TEXT,
    wrong_2 TEXT,
    wrong_3 TEXT,
    date_used TEXT DEFAULT '2023-01-01'
);

CREATE TABLE tests(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    difficulty TEXT NOT NULL,
    creation_date TEXT,
    categories TEXT
);

CREATE TABLE IF NOT EXISTS questions_tests_rel (
    test_id INTEGER NOT NULL,
    questions_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users_tests_rel (
    user_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    submit_date TEXT DEFAULT,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    points_earned INTEGER,
    points_possible INTEGER,
    score INTEGER,
    test_completed INTEGER DEFAULT 0
);

CREATE TABLE answers(
    test_id INTEGER,
    user_id INTEGER,
    questions_id INTEGER,
    user_answer TEXT,
    result INTEGER
);