#!/usr/bin/env python3.4
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
    """ This function reads configuration variables from an external file
    and returns the configuration variables as a class object """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'chunk_size': config.getint('func_conf', 'chunk_size')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def hash_md5_for_file(method, path, chunk_size):
    """ This function reads a file and returns a
    generated md5 checksum """
    hash_md5 = hashlib.md5()
    md5 = False
    if os.path.exists(path):
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hash_md5.update(chunk)
            md5 = hash_md5.hexdigest()
            if method == 'hash':
                with open(path + '.md5', 'w') as fmd5:
                    fmd5.write(md5)
    else:
        raise Exception('file ' + path + ' not found')
    return md5


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
    """ This function runs the script with given arguments """
    args = parse_arguments(arguments) 
    config = get_conf(args.config)
    retval = False
    # Generate md5 hash and save to file.md5
    if args.method == 'hash':
        md5 = hash_md5_for_file(args.method, args.path, config.chunk_size)
        retval = md5  # always true if path exists
        if md5:
            logging.info('Created md5 hash for ' + args.path + ' (' + md5 + ')')
        else:
            logging.info('Error creating md5 hash for ' + args.path + ', file not found.')
    # Read md5 checksum from external file and compare it to hashed value
    elif args.method == 'check':
        md5 = hash_md5_for_file(args.method, args.path, config.chunk_size)
        key_md5 = get_md5_from_file(args.path)
        retval = (md5 == key_md5)  # true if checksums match
        if md5 == key_md5:
            logging.info('OK (md5 checksums match)'
                         ' From: ' + args.path +
                         ' Hashed md5: ' + md5 +
                         ' Received md5: ' + key_md5)
        else:
            logging.info('ERROR (md5 checksums don\'t match)'
                         ' From: ' + args.path +
                         ' Hashed md5: ' + md5 +
                         ' Received md5: ' + key_md5)
    else:
        raise Exception('invalid method, but be \'hash\' or \'check\'')
    return retval


def parse_arguments(arguments):
    """ This function returns the parsed argument path """
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
