import mysql.connector
import os
import time
import datetime
import calendar
import hashlib
import sys
import argparse

# Establish database connection
db = mysql.connector.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="elixir",
                             buffered=True)

cur = db.cursor()

def get_file_details(path):
    """ This function queries the database for details
    and returns a list of results of false """
    db_file_id = 0
    db_file_size = 0
    db_file_passes = 0
    db_file_verified = 0
    cur.execute('SELECT * '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()
    for row in result:
        db_file_id = row[0]
        # file name = path # for clarity (skipping row[1])
        db_file_size = row[2]
        db_file_age = row[3]
        db_file_passes = row[4]
        db_file_verified = row[5]
    if db_file_size == 0:
        status = False
    else:
        status = [db_file_id, 
                  path, 
                  db_file_size, 
                  db_file_age, 
                  db_file_passes, 
                  db_file_verified]
    return status
