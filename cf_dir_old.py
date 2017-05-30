#!/usr/bin/env python
__author__ = "Teemu Kataja"
__copyright__ = "Copyright 2017, CSC - IT Center for Science"

__license__ = "GPL"
__version__ = "0.1.3"
__maintainer__ = "Teemu kataja"
__email__ = "teemu.kataja@csc.fi"
__status__ = "Development"

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


# This function checks if file transmission has been completed
def check_file_transmission(path):

    passes = 0

    # Get file size in bits
    file_size = os.path.getsize(path)

    # Get last modified datetime as float
    file_age = os.path.getmtime(path)
    time_now = calendar.timegm(time.gmtime())

    # Check if file already exists in database
    cur.execute('SELECT id, verified '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()

    if cur.rowcount >= 1:  # Records found: old file
        for row in result:
            if row[1] == 0:  # 0 = file not verified->check it
                # Old file -> request old details from database
                params = [row[0], path]
                cur.execute('SELECT * FROM files '
                            'WHERE id=%s '
                            'AND name=%s;',
                            params)
                result = cur.fetchall()
                for row in result:
                    if file_size > int(row[2]):
                        # If current(new) file sizeis larger
                        # than old file size in database,
                        # update file size and age to database
                        params = [file_size, file_age, row[0]]
                        cur.execute('UPDATE files '
                                    'SET size=%s, '
                                    'age=%s, '
                                    'passes=0 '
                                    'WHERE id=%s;',
                                    params)
                        passes = 0
                    else:
                        # File size hasn't changed, check age
                        if time_now - file_age > 60:
                            # Enough time has passed since
                            # file was last updated -> increment passes
                            params = [row[4]+1, row[0]]
                            cur.execute('UPDATE files '
                                        'SET passes=%s '
                                        'WHERE id=%s;',
                                        params)
                            passes = row[4]+1
    else:  # New file
        # New file -> add new entry to database
        params = [path, file_size, file_age]
        cur.execute('INSERT INTO files '
                    'VALUES (NULL, %s, %s, %s, 0, 0);',
                    params)

    # Execute database changes
    db.commit()
    print(time_now, '>', path,
          ' Current size: ', file_size,
          ' Last updated: ', file_age,
          ' Number of passes: ', passes)
    passed = False
    if passes >= 3:
        passed = True
    else:
        passed = False
    return passed


# This function verifies file integrity by hashing a
# checksum from the file and comparing it to a given checksum
def verify_file_integrity(path, key):

    # Generate md5 hash for file contents
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()

    # Fetch md5 checksum from external file
    key_md5 = open(key, 'r')
    key_md5 = key_md5.read()

    # Get id from database for updating 'verified' status
    cur.execute('SELECT id '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()

    for row in result:
        # Compare md5 hashes
        if path_md5 == key_md5:
            # If file was successfully verified with
            # md5 checksum, update it's 'verified' status
            # in database table to exclude it from
            # future inspection iterations
            params = [1, row[0]]
            cur.execute('UPDATE files '
                        'SET verified=%s '
                        'WHERE id=%s;',
                        params)
            db.commit()
            print(path, 'OK: Verified successfully')
        else:
            # If file failed to verify, keep
            # 'verified' status as 0 in database table
            print('FILE ERROR with ', path,
                  ': Transmitted file and md5checksum do not match')
    return path_md5 == key_md5  # Returns boolean value of comparison


def is_verified(filename):
    verified = False
    cur.execute('SELECT verified '
                'FROM files '
                'WHERE name="' + filename + '";')
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            if row[0] == 1:
                verified = True
            else:
                verified = False
    else:
        verified = False
    return verified

'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    path = parse_arguments(arguments).message
    # Take directory as input, and read all files in that directory
    # Check if files have already been verified with is_verified(),
    # if not, push them through
    # check_file_transmission() and verify_file_integrity()
    # exclude verified files from the process
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            if is_verified(filename):
                print(filename, ' already verified')
            else:
                if check_file_transmission(filename):
                    key = filename + '.md5'
                    verify_file_integrity(filename, key)
    return


# This function enables the script to intake parameters
def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('message')
    return parser.parse_args(arguments)

if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)

'''
TODO. TODO. TODO, TODO, TODO, TODO, TODOOOOOOOO, DODODODOODOO.
http://img13.deviantart.net/c82b/i/2013/231/6/4/pink_panther_s_to_do_list_by_makssarts-d6iuvby.jpg


_ File size doesn't update for a long time, but code keeps incrementing passes
    - error/stopped column? or just select passes>=3 verified=0?
    - incrementing has to stop at some point so as not to overload memory
_ Testing
_ Larger cache size for hash_md5?
    - 2^20 in pastesti example
'''
