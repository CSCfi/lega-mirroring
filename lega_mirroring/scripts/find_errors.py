#!/usr/bin/env python
import mysql.connector
import sys
import logging
import argparse
import calendar
import time
from datetime import datetime
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='errors.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)


def get_conf(path_to_config):
    """ This function reads configuration variables from an external file
    and returns the configuration variables as a class object """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'passwd': config.get('database', 'passwd'),
            'db': config.get('database', 'db'),
            'threshold': config.getint('func_conf', 'age_error_threshold')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def db_init(hostname, username, password, database):
    """ This function initializes database
    connection and returns db-object """
    db = mysql.connector.connect(host=hostname,
                                 user=username,
                                 passwd=password,
                                 db=database,
                                 buffered=True)
    return db


def find_errors(db, threshold):
    """ This function queries the database for file details
    and determines if certain files have transfer problems and
    logs results to file """
    errors = False
    cur = db.cursor()
    cur.execute('SELECT name, age, passes, verified '
                'FROM files;')
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            name = row[0]
            age_difference = (calendar.timegm(time.gmtime()) -
                              float(row[1]))
            age = datetime.fromtimestamp(float(row[1])).strftime(
                '%d-%m-%Y %H:%M:%S')
            passes = row[2]
            verified = row[3]
            if (age_difference >= threshold):
                if (passes >= 5 and verified == 0):
                    errors = True
                    logging.info('Possible error with ' + name +
                                 ' (file not verified)'
                                 ' last updated at ' + age)
                elif (passes < 5):
                    errors = True
                    logging.info('Possible error with ' + name +
                                 ' (file transfer stopped)'
                                 ' last updated at ' + age)
    return errors


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script """
    args = parse_arguments(arguments)
    conf = args.path_to_config
    config = get_conf(conf)
    db = db_init(config.host,
                  config.user,
                  config.passwd,
                  config.db)
    if find_errors(db, config.threshold):
        print('Errors found, see errors.log')
    else:
        print('No errors found.')
    return


def parse_arguments(arguments):
    """ This function returns the parsed arguments """
    parser = argparse.ArgumentParser(description='Look for errors from '
                                     'database tracking table where files '
                                     'that have not been updated in some '
                                     'time have not been verified')
    parser.add_argument('path_to_config',
                        help='location of configuration file')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
