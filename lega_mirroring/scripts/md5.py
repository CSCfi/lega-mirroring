#!/usr/bin/env python3.4
import pymysql
import sys
import argparse
import logging
import hashlib
import os
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='md5_log.log',
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
    conf = {'chunk_size': config.getint('func_conf', 'chunk_size'),
            'extensions': config.get('func_conf', 'extensions'),
            'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'passwd': config.get('database', 'passwd'),
            'db': config.get('database', 'db'),
            'path_gridftp': config.get('workspaces', 'receiving'),
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
    

def hash_md5_for_file(method, path, chunk_size, ext):
    """ 
    This function reads a file and returns a generated md5 checksum 
    
    :method: operating method given in main, hash or check
             hash: md5 is generated and written to .md5 file
             check: md5 is generated and returned
    :path: path to file that md5 will be hashed for
    :chunk_size: chunk size for reading original file
    """
    hash_md5 = hashlib.md5()
    md5 = False
    if os.path.exists(path):
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hash_md5.update(chunk)
            md5 = hash_md5.hexdigest()
            if method == 'hash':
                if not path.endswith(ext):
                    # if path is file.bam, add .cip.csc to it
                    path = path + '.cip.csc'
                with open(path + '.md5', 'w') as fmd5:
                    fmd5.write(md5)
    else:
        raise Exception('file ' + path + ' not found')
    return md5


def db_fetch_md5(db, path_file, path_gridftp, path_processing):
    """
    This function queries the database for an md5 hash matching
    the given filename and returns it
    
    :db: database connection object
    :path_file: path to file to be checked
    :path_gridftp: path to receiving folder, needed for db query
    """
    # fix path to match that in db
    #filename = os.path.join(path_gridftp, os.path.basename(path_file))
    filename = path_file.replace(path_processing, path_gridftp)
    md5 = False
    cur = db.cursor()
    cur.execute('SELECT file_md5 '
                'FROM file '
                'WHERE file_name=%s;',
                [filename])
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            md5 = row[0]
    return md5


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ 
    This function runs the script
    
    :arguments: contains parsed command line parameters
    """
    args = parse_arguments(arguments) 
    config = get_conf(args.config)
    ext = tuple(config.extensions.split(','))
    # Establish database connection
    db = db_init(config.host,
                 config.user,
                 config.passwd,
                 config.db)
    retval = False
    # Generate md5 hash and save to file.md5
    if args.method == 'hash':
        md5 = hash_md5_for_file(args.method, args.path, config.chunk_size, ext)
        retval = md5  # always true if path exists
        if md5:
            logging.info('Created md5 hash for ' + args.path + ' (' + md5 + ')')
        else:
            logging.info('Error creating md5 hash for ' + args.path + ', file not found.')
    # Read md5 checksum from database and compare it to hashed value
    elif args.method == 'check':
        md5 = hash_md5_for_file(args.method, args.path, config.chunk_size, ext)
        key_md5 = db_fetch_md5(db, args.path, config.path_gridftp, config.path_processing)
        retval = (md5 == key_md5)  # true if checksums match
        if md5 == key_md5:
            logging.info('OK (md5 checksums match)'
                         ' File: ' + args.path +
                         ' Hashed md5: ' + md5 +
                         ' Received md5: ' + str(key_md5))
        else:
            logging.info('ERROR (md5 checksums don\'t match)'
                         ' File: ' + args.path +
                         ' Hashed md5: ' + md5 +
                         ' Received md5: ' + str(key_md5))
    else:
        raise Exception('invalid method, but be \'hash\' or \'check\'')
    return retval


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :method: parameter that determines the operation of the script
             either hash or check, can not be left empty
    :path: path to file to be worked on 
    :config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Generate md5 hash '
                                     'or check md5 sum '
                                     'for given file.')
    parser.add_argument('method',
                        help='hash or check.')
    parser.add_argument('path',
                        help='path to file that will be checked or hashed.')
    parser.add_argument('config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
