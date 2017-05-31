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

def db_get_file_details(path):
    """ This function queries the database for details
    and returns a list of results or false """
    status = [0, 0, 0, 0, 0, 0]
    cur.execute('SELECT * '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            # See other/db_script.txt for table structure
            status = [row[0],
                      path,
                      row[2],
                      row[3],
                      row[4],
                      row[5]]
    return status
