#!/usr/bin/env python3.4
import sys
import argparse
import logging
import hashlib
import os
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='create_md5_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%M-%Y %H:%M:%S',
                    level=logging.INFO)


def get_conf(path_to_config):
    """ This function reads configuration variables from an external file
    and returns the configuration variables as a class object """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'chunk_size': config.getint('func_conf', 'chunk_size')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def hash_md5_for_file(path, chunk_size):
    """ This function reads a file and returns a
    generated md5 checksum """
    hash_md5 = hashlib.md5()
    md5 = False
    if os.path.exists(path):
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hash_md5.update(chunk)
                md5 = hash_md5.hexdigest()
            with open(path + '.md5', 'w') as f:
                f.write(md5)
    else:
        raise Exception('file ' + path + ' not found')
    return md5


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script with given argument (path) """
    args = parse_arguments(arguments)
    path = args.path
    conf = args.path_to_config
    config = get_conf(conf)
    md5 = hash_md5_for_file(path, config.chunk_size)
    if md5:
        logging.info('Created md5 hash for ' + path + ' (' + md5 + ')')
    else:
        logging.info('Error creating md5 hash for ' + path + ', file not found.')
    return


def parse_arguments(arguments):
    """ This function returns the parsed argument path """
    parser = argparse.ArgumentParser(description='Create md5 hash '
                                     'for given file.')
    parser.add_argument('path',
                        help='path to file that will be hashed.')
    parser.add_argument('path_to_config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
