import sqlite3
from helpers import db_first, db_no_paramater_query, db_query, get_db_connection, dict_factory
from threading import Timer
import random
import time
from sys import exit
from datetime import date
# from apscheduler.schedulers.background import BackgroundScheduler
# from flask import Flask
# from werkzeug.security import check_password_hash, generate_password_hash

# requests = ["POST", "GET", "PATCH", "NO", ]

# def test_needed():
#     test_needed = True
#     latest_test_db = db_no_paramater_query("SELECT creation_date FROM tests ORDER BY rowid DESC")
#     latest_test = latest_test_db[0]["creation_date"]

#     current_date = date.today()
#     if latest_test == current_date:
#         test_needed = False

#     return test_needed

# print(test_needed())


def prime_finder(n):
  # Write your code here
  primeNums = []
  primeCheck = [2, 3, 5, 7, 11]
  while n > 0:
    for item in primeCheck:
      if n == item:
        continue
      if n == 1:
        continue
      result = n % item
      if result == 0:
        break
    
    primeNums.append(n)  
    n -= 1  
    
  

  return primeNums
print(prime_finder(11))