#!/usr/bin/env python
import mysql.connector
import os
import time
import datetime
import calendar
import hashlib
import sys
import argparse
import logging
from configparser import ConfigParser

# Log events to file
logging.basicConfig(filename='cf_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)


def get_conf(path_to_config):
    """ This function reads configuration variables from an external file
    and returns the configuration variables as a dictionary """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'passwd': config.get('database', 'user'),
            'db': config.get('database', 'db'),
            'chunk_size': config.getint('func_conf', 'chunk_size'),
            'age_limit': config.getint('func_conf', 'age_limit'),
            'pass_limit': config.getint('func_conf', 'pass_limit')}
    return conf


def db_init(path_to_config):
    """ This function initializes database connection and returns cursor """
    db = mysql.connector.connect(host=get_conf(path_to_config)['host'],
                                 user=get_conf(path_to_config)['user'],
                                 passwd=get_conf(path_to_config)['passwd'],
                                 db=get_conf(path_to_config)['db'],
                                 buffered=True)
    return db.cursor()


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


def db_get_file_details(path, conf):
    """ This function queries the database for details
    and returns a list of results or false """
    status = False
    cur = db_init(conf)
    cur.execute('SELECT * '
                'FROM files '
                'WHERE name=%s;',
                [path])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            status = {'id': row[0],
                      'name': path,
                      'size': int(row[2]),
                      'age': float(row[3]),
                      'passes': row[4],
                      'verified': row[5]}
    #else:
    #    status = False
    return status


def db_update_file_details(path, conf):
    """ This function updates file size and age to database
    as well as resets the passes value to zero"""
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    file_id = db_get_file_details(path)['id']
    params = [file_size, file_age, file_id]
    cur = db_init(conf)
    cur.execute('UPDATE files '
                'SET size=%s, '
                'age=%s, '
                'passes=0 '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_increment_passes(path, conf):
    """ This function increments the number of passes by 1 """
    file_id = db_get_file_details(path)['id']
    file_passes = db_get_file_details(path)['passes']+1
    params = [file_passes, file_id]
    cur = db_init(conf)
    cur.execute('UPDATE files '
                'SET passes=%s '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_insert_new_file(path, conf):
    """ This function creates a new database entry database
    table structure can be viewed in other\db_script.txt """
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    params = [path, file_size, file_age]
    cur = db_init(conf)
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
    logging.info(path + ' last updated: ' + str(file_age) +
                 ' size: ' + str(file_size) + ' passes: ' + str(file_passes))
    return


def hash_md5_for_file(path, conf):
    """ This function reads a file and returns a
    generated md5 checksum """
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(get_conf(conf)['chunk_size']), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()
    return path_md5


def get_md5_from_file(path):
    """ This function reads a file type file.txt.md5
    and returns the  md5 checksum """
    path_to_md5 = path + '.md5'
    md5 = False
    if os.path.isfile(path_to_md5):
        with open(path_to_md5, 'r') as f:
            md5 = f.read()
    else:
        logging.info(path + ' .md5 file not found')
    return md5


def db_verify_file_integrity(path, conf):
    """ This function updates file verified status from 0 to 1 """
    file_id = db_get_file_details(path)['id']
    params = [1, file_id]
    cur = db_init(conf)
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
    args = parse_arguments(arguments)
    path = args.path_to_dir
    conf = args.path_to_config
    for file in os.listdir(path):
        if file.endswith('.txt'):
            if db_get_file_details(file, conf):
                # Old file
                if db_get_file_details(file, conf)['verified'] == 0:
                    # File is not verified
                    if (get_file_size(file) >
                            db_get_file_details(file, conf)['size']):
                        # File size has changed
                        db_update_file_details(file, conf)
                    else:
                        # File size hasn't changed
                        if (get_time_now() -
                                db_get_file_details(file, conf)['age'] >
                                get_conf(conf)['age_limit']):
                            # File is older than c_pass_limit (see config.ini)
                            if (db_get_file_details(file, conf)['passes'] >=
                                    get_conf(conf)['pass_limit']):
                                # At least c_pass_limit passes (see config.ini)
                                if (hash_md5_for_file(file, conf) ==
                                        get_md5_from_file(file)):
                                    # Verify md5 checksum
                                    db_verify_file_integrity(file, conf)
                            else:
                                # Increment passes
                                db_increment_passes(file, conf)
                    log_event(file)
            else:
                # New file
                db_insert_new_file(file, conf)
                log_event(file)
    return


def parse_arguments(arguments):
    """ This function returns the parsed arguments path to
    target dir and location of configuration file """
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_dir')
    parser.add_argument('path_to_config')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
