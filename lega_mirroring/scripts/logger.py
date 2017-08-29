#!/usr/bin/env python3.4
import MySQLdb
import sys
import argparse
import os
import json
from configparser import ConfigParser
from collections import namedtuple


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
            'path_metadata': config.get('workspaces', 'metadata')}
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
    db = MySQLdb.connect(host=hostname,
                         user=username,
                         passwd=password,
                         db=database)
    return db


def read_json(jsonpath):
    metadata = 0
    n_files = 0
    n_bytes = 0
    with open(jsonpath, encoding='utf-8') as data:
        metadata = json.loads(data.read())
    for i in range(len(metadata)):
        n_files += 1
        n_bytes += metadata[i]['fileSize']
    return (n_files, n_bytes)
    
   
def db_dataset_exists(db, dataset_id):
    exists = False
    cur = db.cursor()
    cur.execute('SELECT dataset_id '
                'FROM dataset_log '
                'WHERE dataset_id=%s',
                [dataset_id])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        exists = True
    return exists

   
def db_date_requested(db, dataset_id, n):
    cur = db.cursor()
    n_files = n[0]
    n_bytes = n[1]
    params = [dataset_id, n_files, n_bytes]
    cur.execute('INSERT INTO dataset_log '
                'VALUES (%s, %s, %s, NOW(), NULL, NULL, NULL);',
                params)
    db.commit()
    return
    
    
def db_date_download_start(db, dataset_id):
    cur = db.cursor()
    cur.execute('UPDATE dataset_log '
                'SET date_download_start=NOW() '
                'WHERE dataset_id=%s;',
                [dataset_id])
    db.commit()
    return

    
def db_date_download_end(db, dataset_id):
    cur = db.cursor()
    cur.execute('UPDATE dataset_log '
                'SET date_download_end=NOW() '
                'WHERE dataset_id=%s;',
                [dataset_id])
    db.commit()
    return
    
    
def db_date_processing_end(db, dataset_id):
    cur = db.cursor()
    cur.execute('UPDATE dataset_log '
                'SET date_processing_end=NOW() '
                'WHERE dataset_id=%s;',
                [dataset_id])
    db.commit()
    return
    
    
def db_date_is_null(db, dataset_id):
    status = False
    cur = db.cursor()
    cur.execute('SELECT date_download_start '
                'FROM dataset_log '
                'WHERE dataset_id=%s',
                [dataset_id])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            if row[0] is None:
                # if query is empty, date is null
                status = True
    return status

    
def main(arguments=None):
    """ 
    This function runs the script
    
    :arguments: contains parsed command line parameters
    """
    args = parse_arguments(arguments)
    dataset_id = args.dataset_id
    method = args.method
    config = get_conf(args.config)
    # Establish database connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    # Check if dataset is already added to log
    if (db_dataset_exists(db, dataset_id)):
        if method == 'date_download_start':
            # If date is NULL on column, update date, else don't
            if db_date_is_null(db, dataset_id):
                db_date_download_start(db, dataset_id)
        elif method == 'date_download_end':
            db_date_download_end(db, dataset_id)
        elif method == 'date_processing_end':
            db_date_processing_end(db, dataset_id)
        else:
            print('Invalid method: ' + method + ' for dataset: ' + dataset_id)
    else:  # If not, create new entry
        if method == 'date_requested':
            # put /path/ and .json to EGAD
            path = args.dataset_id + '.json'
            path = os.path.join(config.path_metadata, path)
            n = read_json(path)  # n_files and n_bytes
            db_date_requested(db, dataset_id, n)
        else:
            print('Error: ' + dataset_id + ' not in table, and wrong method:'
                  ' ("' + method + '") used.')
    return


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :method: parameter that determines the operation of the script
    :path: path to .json 
    :config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Logs dataset processes '
                                     'to database with timestamps.')
    parser.add_argument('method',
                        help='determines which operation date is logged. '
                        '\nPossible values are: '
                        '\ndate_requested '
                        '\ndate_download_start '
                        '\ndate_download_end '
                        '\ndate_processing_end')
    parser.add_argument('dataset_id',
                        help='EGAD0000....')
    parser.add_argument('config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)