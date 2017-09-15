#!/usr/bin/env python3.4

import requests
import pymysql
import argparse
from configparser import ConfigParser
from collections import namedtuple
import sys
import os
import lega_mirroring.scripts.datasetlogger


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
            'api_url': config.get('api', 'api_url'),
            'api_user': config.get('api', 'api_user'),
            'api_pass': config.get('api', 'api_pass'),
            'path_gridftp': config.get('workspaces', 'receiving'),
            'extensions': config.get('func_conf', 'extensions')}
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


def request_dataset_metadata(api_url, api_user, api_pass, did):
    """
    This function does an HTTP request to EGA API to get
    dataset metadata and returns it as a stream
    
    :api_url: address of ega api_url
    :api_user: username to access api
    :api_pass: password for :api_user:
    :did: dataset id
    """
    api_url = api_url.replace('DATASETID', did)
    metadata = requests.get(api_url, 
                            auth=(api_user, api_pass), 
                            stream=True)
    if not metadata:
        raise Exception('\n\nAPI Error'
                        '\napi_url=' + api_url +
                        '\napi_user=' + api_user +
                        '\napi_pass=' + api_pass +
                        '\ndataset_id=' + did +
                        '\n\n')
    return metadata.json()


def db_insert_metadata(db, metadata, did, path_gridftp, ext):
    """
    This function takes a stream of metadata as input
    and inserts it into database
    
    :db: database connection object
    :metadata: stream of metadata from EGA API
    :did: dataset id
    :path_gridftp: path to receiving directory
    :ext: crypto-extensions
    """
    
    cur = db.cursor()
    n_bytes = 0
    n_files = 0
    
    for i in range(len(metadata)):
    
        filename = os.path.basename(metadata[i]['fileName'])
        filename = os.path.join(path_gridftp, filename)
        
        # Removes crypto-extension if it exists
        if filename.endswith(ext):
            filename, extension = os.path.splitext(filename)
            
        n_files += 1
        n_bytes += int(metadata[i]['fileSize'])
        params_file = [metadata[i]['fileId'], filename,
                       int(metadata[i]['fileSize']), metadata[i]['checksum'],
                       'pending']
        params_data = [did, metadata[i]['fileId']]
        params_log = [did, n_files, n_bytes]
        
        try:
            cur.execute('INSERT INTO file VALUES '
                        '(%s, %s, %s, %s, %s);', params_file)
            cur.execute('INSERT INTO filedataset VALUES '
                        '(%s, %s);', params_data)
            cur.execute('INSERT INTO dataset_log VALUES '
                        '(%s, %s, %s, NOW(), NULL, NULL, NULL);', params_log)
        except:
            pass
            
        i += 1
        
    db.commit()
    return


def main(arguments=None):
    args = parse_arguments(arguments)
    conf = args.config
    config = get_conf(conf)
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    ext = tuple(config.extensions.split(','))
    metadata = request_dataset_metadata(config.api_url, config.api_user,
                                        config.api_pass, args.dataset)
    db_insert_metadata(db, metadata, args.dataset, config.path_gridftp, ext)
    return


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='This script does an HTTP'
                                     ' request to EGA API to get dataset'
                                     ' metadata')
    parser.add_argument('dataset',
                        help='dataset id, e.g. EGAD00000...')
    parser.add_argument('config',
                        help='path to config.ini')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
