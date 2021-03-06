#!/usr/bin/env python3.4

import pymysql
import os
import time
import datetime
import calendar
import sys
import argparse
import logging
from configparser import ConfigParser
from collections import namedtuple
import lega_mirroring.scripts.datasetlogger

# Log events to file
logging.basicConfig(filename='monitor_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)


def get_conf(path_to_config):
    """
    This function reads configuration variables from an external file
    and returns the configuration variables as a class object

    :path_to_config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'passwd': config.get('database', 'passwd'),
            'db': config.get('database', 'db'),
            'chunk': config.getint('func_conf', 'chunk_size'),
            'age_limit': config.getint('func_conf', 'age_limit'),
            'pass_limit': config.getint('func_conf', 'pass_limit'),
            'path_receiving': config.get('workspaces', 'receiving'),
            'path_processing': config.get('workspaces', 'processing')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def db_init(hostname, username, password, database):
    """
    This function initializes database connection and returns a connection
    object that will be used as an executale cursor object

    :hostname: address of mysql server
    :username: username to log in to mysql server
    :password: password associated with :username: to log in to mysql server
    :database: database to be worked on
    """
    db = pymysql.connect(host=hostname,
                         user=username,
                         passwd=password,
                         db=database)
    return db


def get_file_size(path):
    """
    This function reads a file and returns it's byte size as numeral string

    :path: file to be read
    """
    return os.path.getsize(path)


def get_file_age(path):
    """
    This function reads a file and returns it's last modified date as
    mtime(float) in string form

    :path: file to be read
    """
    return os.path.getmtime(path)


def get_time_now():
    """
    This function returns the current time as mtime(float) in string form
    """
    return calendar.timegm(time.gmtime())


def db_get_file_details(path, db):
    """
    This function queries the database for file details
    and returns a list of results or false

    :path: filename to be queried
    :db: database connection object
    """
    status = False
    cur = db.cursor()
    cur.execute('SELECT * '
                'FROM trackingtable '
                'WHERE name=%s;',
                [path])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            status = {'id': row[0],
                      'name': path,
                      'size': int(row[2]),
                      'age': float(row[3]),
                      'passes': row[4]}
    return status


def db_update_file_details(path, db):
    """
    This function updates file size and age to database
    as well as resets the passes value to zero

    :path: filename
    :db: database connection object
    """
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    file_id = db_get_file_details(path, db)['id']
    params = [file_size, file_age, file_id]
    cur = db.cursor()
    cur.execute('UPDATE trackingtable '
                'SET size=%s, '
                'age=%s, '
                'passes=0 '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_increment_passes(path, db):
    """
    This function increments the number of passes by 1

    :path: filename
    :db: database connection object
    """
    file_id = db_get_file_details(path, db)['id']
    file_passes = db_get_file_details(path, db)['passes']+1
    params = [file_passes, file_id]
    cur = db.cursor()
    cur.execute('UPDATE trackingtable '
                'SET passes=%s '
                'WHERE id=%s;',
                params)
    db.commit()
    return


def db_insert_new_file(path, db):
    """
    This function creates a new database entry of a new file

    :path: filename
    :db: database connection object
    """
    file_size = get_file_size(path)
    file_age = get_file_age(path)
    params = [path, file_size, file_age]
    cur = db.cursor()
    cur.execute('INSERT INTO trackingtable '
                'VALUES (NULL, %s, %s, %s, 0);',
                params)
    db.commit()
    return


def log_event(path, db):
    """
    This function prints monitoring events to log file

    :path: filename
    :db: database connection object
    """
    time_now = get_time_now()
    file_size = db_get_file_details(path, db)['size']
    file_age = db_get_file_details(path, db)['age']
    file_passes = db_get_file_details(path, db)['passes']
    logging.info(path + ' last updated: ' + str(file_age) +
                 ' size: ' + str(file_size) + ' passes: ' + str(file_passes))
    return


def par(branches, branch, pathr):
    """
    This function reads a directory and generates a list
    of files to be checked by a single parallel process

    :branches:  number of branches to be run
    :branch:  id of branch
    :pathr:  path_receiving from config.ini
    """
    complete_set = []  # to be appended
    selected_set = []  # to be appended
    for root, dirs, files in os.walk(pathr):
        for item in files:
            # form full path
            fullpath = os.path.join(root, item)
            # strip path (to leave subdirs if they exist)
            relpath = fullpath.replace(pathr, '')
            complete_set.append(relpath)
    i = 0
    while i <= len(complete_set):
        index = branch+i*branches
        if index <= len(complete_set):
            selected_set.append(complete_set[index-1])
        i += 1
    return selected_set


def lookup_dataset_id(db, file):
    """
    This function finds the dataset id the given file
    belongs to and returns it as a string

    :db: database connection object
    :file: datafile belonging to a dataset
    """
    dataset_id = 0
    cur = db.cursor()
    cur.execute('SELECT dataset_id '
                'FROM filedataset '
                'WHERE file_id=('
                'SELECT file_id '
                'FROM file '
                'WHERE file_name=%s);',
                [file])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            dataset_id = row[0]
    return dataset_id

'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """
    This function runs the script

    :arguments: contains parsed command line parameters
    """
    start_time = time.time()
    args = parse_arguments(arguments)
    branches = int(args.branches)
    branch = int(args.branch)
    conf = args.config
    # Get configuration values from external file
    config = get_conf(conf)
    path = config.path_receiving
    # Establish database connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    # Begin file checking process
    selected_set = par(branches, branch, config.path_receiving)
    for file in selected_set:
        rawfile = file
        file = os.path.join(path, file)
        if db_get_file_details(file, db):  # Old file
            if db_get_file_details(file, db)['passes'] < config.pass_limit:
                # File transfer is incomplete
                if (get_file_size(file) >
                        db_get_file_details(file, db)['size']):
                    #   File size has changed
                    db_update_file_details(file, db)
                else:  # File size hasn't changed
                    if (get_time_now() -
                            db_get_file_details(file, db)['age'] >
                            config.age_limit):
                        #   File hasn't changed in some time
                        # Mark a pass on db table 0..3
                        db_increment_passes(file, db)
                log_event(file, db)
            else:
                # move file from receiving(wf1) to processing(wf2)
                try:
                    os.rename(file, os.path.join(config.path_processing,
                              rawfile))
                    # put timestamp to dataset_log table
                    dataset_id = lookup_dataset_id(db, file)
                    lega_mirroring.scripts.datasetlogger.main(
                        ['date_download_end', dataset_id, conf])
                except:
                    pass
        else:  # New file
            # Create new directory to processing
            if os.path.dirname(rawfile):
                if not os.path.exists(os.path.join(config.path_processing,
                                                   os.path.dirname(rawfile))):
                    os.mkdir(os.path.join(config.path_processing,
                                          os.path.dirname(rawfile)))
            db_insert_new_file(file, db)
            # put timestamp to dataset_log table
            dataset_id = lookup_dataset_id(db, file)
            lega_mirroring.scripts.datasetlogger.main(['date_download_start',
                                                       dataset_id, conf])
            log_event(file, db)
    return ('Runtime: ' + str(time.time()-start_time) + ' seconds')


def parse_arguments(arguments):
    """
    This function parses command line inputs and returns them for main()

    :branches: this is the total number of parallelizations to be run
    :branch: this is a fraction of the parallelizations, e.g. 1 of 4
    :config: full path to config.ini (or just config.ini if
             cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Check files\' age and size'
                                     ' in target directory and track them '
                                     ' using a MySQL database.')
    parser.add_argument('branches',
                        help='number of parallelizations')
    parser.add_argument('branch',
                        help='unique id of machine')
    parser.add_argument('config',
                        help='location of configuration file')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
