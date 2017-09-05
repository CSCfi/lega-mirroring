#!/usr/bin/env python3.4
import MySQLdb
import sys
import argparse
import os
from configparser import ConfigParser
from collections import namedtuple

'''
    # dsin.py Dataset Input #
    
    This script is used to input metadata to dev_ega_downloader tables
    file, filedataset and dataset_log from external (non-EGA format) sources.
'''


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

    
def parse_file(file):
    """
    This function reads a given file and returns a list of rows
    
    :file: file input
    """
    rows = []
    for line in open(file, 'r'):
        rows.append(line.strip().split('\t'))
    return rows
    
    
def db_insert_metadata(db, dataset_id, metadata):
    """
    This function inserts received data to database
    
    :db: database connection object
    :dataset_id: string, e.g. EGAD000 or SN000
    :metadata: list of rows containing datafile metadata
    """
    cur = db.cursor()
    for i in range(len(metadata)):
        file_id = metadata[i][0].replace('.bam', '')
        file_name = metadata[i][0]
        file_md5 = metadata[i][1]
        params_file = [file_id, file_name, file_md5]
        params_data = [dataset_id, file_id]
        try:
            cur.execute('INSERT INTO file VALUES '
                        '(%s, %s, NULL, %s, "pending");', params_file)
            cur.execute('INSERT INTO filedataset VALUES '
                        '(%s, %s);', params_data)
        except:
            pass
        i += 1
    db.commit()
    return
    
    
def db_date_requested(db, dataset_id):
    """
    This function update the dataset_log table to fill in a requested date
    
    :db: database connection object
    :dataset_id: string, e.g. EGAD000 or SN000
    """
    cur = db.cursor()
    cur.execute('INSERT INTO dataset_log '
                'VALUES (%s, NULL, NULL, NOW(), NULL, NULL, NULL);',
                [dataset_id])
    db.commit()
    return
    
    
def main(arguments=None):
    args = parse_arguments(arguments)
    conf = args.config
    config = get_conf(conf)
    # Establish DB connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    dataset_id = args.metafile.replace('.txt', '')
    metafile = parse_file(args.metafile)
    db_date_requested(db, dataset_id)
    db_insert_metadata(db, dataset_id, metafile)
    return


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('metafile',
                        help='File containing dataset metadata')
    parser.add_argument('config',
                        help='Path to configuration file')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)