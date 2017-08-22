#!/usr/bin/env python3.4
import MySQLdb
import sys
import argparse
import os
import json
import ntpath
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
            'db': config.get('database', 'db')}
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
    
    
def main(arguments=None):
    """ 
    This function runs the script
    
    :arguments: contains parsed command line parameters
    """
    args = parse_arguments(arguments)
    n = read_json(args.path)  # n_files and n_bytes
    dataset = ntpath.basename(args.path)
    dataset_id = dataset.replace('.json', '')  # plain EGAD, no path
    method = args.method
    config = get_conf(args.config)
    # Establish database connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    if method == 'date_requested':
        db_date_requested(db, dataset_id, n)
    elif method == 'date_download_start':
        db_date_download_start(db, dataset_id)
    elif method == 'date_download_end':
        db_date_download_end(db, dataset_id)
    elif method == 'date_processing_end':
        db_date_processing_end(db, dataset_id)
    else:
        print('Invalid method: ' + method)
    return


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :method: parameter that determines the operation of the script
    :path: path to .json 
    :config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Generate md5 hash '
                                     'or check md5 sum '
                                     'for given file.')
    parser.add_argument('method',
                        help='determines which operation date is logged.')
    parser.add_argument('path',
                        help='path to dataset metadata.json')  # later replace with api request
    parser.add_argument('config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)