#!/usr/bin/env python3.4
#import requests
import MySQLdb
import argparse
from configparser import ConfigParser
from collections import namedtuple
import sys
import json
import os
import ntpath
import lega_mirroring.scripts.logger


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
            'metadata': config.get('workspaces', 'metadata')}
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


def request_dataset_metadata(egad):
    '''
    proto: read file and return mock json
    actual: http request using egad, receive json
    #response = requests.get(url, egad)
    '''
    # read dataset metadata from .json file
    with open(egad, encoding='utf-8') as metadata:
        values = json.loads(metadata.read())
    return values


def db_insert_metadata(db, metadata):
    cur = db.cursor()
    for i in range(len(metadata)):
        params_file = [metadata[i]['fileId'], metadata[i]['fileName'],
                       int(metadata[i]['fileSize']), metadata[i]['fileMd5'],
                       metadata[i]['fileStatus']]
        params_data = [metadata[i]['datasetId'], metadata[i]['fileId']]
        try:
            cur.execute('INSERT INTO file VALUES '
                        '(%s, %s, %s, %s, %s);', params_file)
            cur.execute('INSERT INTO filedataset VALUES '
                        '(%s, %s);', params_data)
        except:
            pass
        i += 1
    db.commit()
    return


def main(arguments=None):
    args = parse_arguments(arguments)
    conf = args.config
    #egad = args.dataset_id
    config = get_conf(conf)
    # Establish DB connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    # add all datasets and related files to database
    for file in os.listdir(config.metadata):
        file = os.path.join(config.metadata, file)
        db_insert_metadata(db, request_dataset_metadata(file))
        # strip /path/ and .json to get EGAD
        dataset = ntpath.basename(file)
        dataset_id = dataset.replace('.json', '')
        lega_mirroring.scripts.logger.main(['date_requested', dataset_id, conf])


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='This script reads dataset'
                                     ' metadata from json and inserts it to'
                                     ' a database table')
    parser.add_argument('config',
                        help='path to config.ini')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
