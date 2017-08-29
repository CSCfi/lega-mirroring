#!/usr/bin/env python3.4
import MySQLdb
import sys
import argparse
import logging
import os
from configparser import ConfigParser
from collections import namedtuple
import lega_mirroring.scripts.logger

logging.basicConfig(filename='update_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%M-%Y %H:%M:%S',
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
            'path_archive': config.get('workspaces', 'end_storage'),
            'path_gridftp': config.get('workspaces', 'receiving')}
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


def db_update_file(db, filename, path_archive, path_gridftp):
    """
    This function updates file path and status to database
    
    :db: database connection object
    :path_file: path to file
    :path_archive: path to end storage
    :path_gridftp: path to receivings directory
    """
    oldfile = os.path.join(path_gridftp, filename)
    newfile = os.path.join(path_archive, filename)
    params = ['available', newfile, oldfile]
    cur = db.cursor()
    cur.execute('UPDATE file '
                'SET status=%s, file_name=%s '
                'WHERE file_name=%s;',
                params)
    db.commit()
    return

    
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
    args = parse_arguments(arguments)
    conf = args.config
    # Get configuration values from external file
    config = get_conf(conf)
    # Establish database connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    db_update_file(db, args.path, config.path_archive, config.path_gridftp)
    # put timestamp to dataset_log table
    file = os.path.join(config.path_archive, args.path)
    dataset_id = lookup_dataset_id(db, file)
    lega_mirroring.scripts.logger.main(['date_processing_end', dataset_id, conf])
    return


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :path: path to file that\'s details are updated 
    :config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Update file status '
                                     'and path')
    parser.add_argument('path',
                        help='base filename')
    parser.add_argument('config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
