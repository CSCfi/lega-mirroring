#!/usr/bin/env python
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


def get_file_size(path):
    """ This function reads a file and returns
    it's byte size as numeral string """
    return os.path.getsize(path)


def get_file_age(path):
    """ This function reads a file and returns it's last
    modified date as mtime(float) in string form """
    return os.path.getmtime(path)


def get_time_now():
    """ This function returns the current time
    as mtime(float) in string form """
    return calendar.timegm(time.gmtime())


def db_get_file_details(path):
    """ This function queries the database for details
    and returns a list of results or false """
    status = {'id': 0,
              'name': 0,
              'size': 0,
              'age': 0,
              'passes': 0,
              'verified': 0}
    cur.execute('SELECT * '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            # See other/db_script.txt for table structure
            status = {'id': row[0],
                      'name': path,
                      'size': int(row[2]),
                      'age': float(row[3]),
                      'passes': row[4],
                      'verified': row[5]}
    return status


def db_update_file_details(path):
    """ This function updates file size and age to database
    as well as resets the passes value to zero"""
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    file_id = db_get_file_details(path)['id']
    params = [file_size, file_age, file_id]
    cur.execute('UPDATE files '
                'SET size=%s, '
                'age=%s, '
                'passes=0 '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_increment_passes(path):
    """ This function increments the number of passes by 1 """
    file_id = db_get_file_details(path)['id']
    file_passes = db_get_file_details(path)['passes']+1
    params = [file_passes, file_id]
    cur.execute('UPDATE files '
                'SET passes=%s '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_insert_new_file(path):
    """ This function creates a new database entry database
    table structure can be viewed in other\db_script.txt """
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    params = [path, file_size, file_age]
    cur.execute('INSERT INTO files '
                'VALUES (NULL, %s, %s, %s, 0, 0);',
                params)
    db.commit()
    return


def log_event(path):
    """ This function prints the event to log """
    time_now = get_time_now()
    file_size = db_get_file_details(path)['size']
    file_age = db_get_file_details(path)['age']
    file_passes = db_get_file_details(path)['passes']
    print(time_now, '>', path,
          ' Current size: ', file_size,
          ' Last updated: ', file_age,
          ' Number of passes: ', file_passes)
    return


def hash_md5_for_file(path):
    """ This function reads a file and returns a
    generated md5 checksum """
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()
    return path_md5


def get_md5_from_file(path):
    """ This function reads a file type file.txt.md5
    and returns the  md5 checksum """
    key_md5 = path + '.md5'
    key_md5 = open(key_md5, 'r')
    key_md5 = key_md5.read()
    return key_md5


def db_verify_file_integrity(path):
    """ This function updates file verified status from 0 to 1 """
    file_id = db_get_file_details(path)['id']
    params = [1, file_id]
    cur.execute('UPDATE files '
                'SET verified=%s '
                'WHERE id=%s;',
                params)
    db.commit()
    return


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script when executed and given
    a directory as parameter """
    path = parse_arguments(arguments).message
    for file in os.listdir(path):
        if file.endswith('.txt'):
            if db_get_file_details(file)['id'] > 0:
                # Old file
                if db_get_file_details(file)['verified'] == 0:
                    # File is not verified
                    if (get_file_size(file) >
                        db_get_file_details(file)['size']):
                        # File size has changed
                        db_update_file_details(file)
                    else:
                        # File size hasn't changed
                        if (get_time_now() -
                            db_get_file_details(file)['age']) > 60:
                            # File is older than 60s
                            if db_get_file_details(file)['passes'] >= 3:
                                # At least 3 passes
                                if (hash_md5_for_file(file) ==
                                    get_md5_from_file(file)):
                                    # Verify md5 checksum
                                    db_verify_file_integrity(file)
                            else:
                                # Increment passes
                                db_increment_passes(file)
                    log_event(file)
            else:
                # New file
                db_insert_new_file(file)
                log_event(file)
    return


def parse_arguments(arguments):
    """ This function returns the parsed argument (path) """
    parser = argparse.ArgumentParser()
    parser.add_argument('message')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
