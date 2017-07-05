#!/usr/bin/env python
import sys
import argparse
import logging
import hashlib
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='md5checksum_log.log',
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
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()
    return path_md5


def get_md5_from_file(path):
    """ This function reads a file type file.md5
    and returns the md5 checksum inside """
    path_to_md5 = path + '.md5'
    with open(path_to_md5, 'r') as f:
        md5 = f.read()
    return md5


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script with given argument (path) """
    args = parse_arguments(arguments)
    conf = args.path_to_config
    config = get_conf(conf)
    path_md5 = hash_md5_for_file(args.path, config.chunk_size)
    key_md5 = get_md5_from_file(args.path)
    if path_md5 == key_md5:
        logging.info('OK (md5 checksums match)'
                     ' From: ' + args.path +
                     ' Hashed md5: ' + path_md5 +
                     ' Received md5: ' + key_md5)
    else:
        logging.info('ERROR (md5 checksums don\'t match)'
                     ' From: ' + args.path +
                     ' Hashed md5: ' + path_md5 +
                     ' Received md5: ' + key_md5)
    return (path_md5 == key_md5)


def parse_arguments(arguments):
    """ This function returns the parsed argument path """
    parser = argparse.ArgumentParser(description='Create md5 hash '
                                     'for given file.')
    parser.add_argument('path',
                        help='path to file that will be checked.')
    parser.add_argument('path_to_config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
