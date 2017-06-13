#!/usr/bin/env python
import sys
import argparse
import logging
import hashlib

logging.basicConfig(filename='md5checksum_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%M-%Y %I:%M:%S',
                    level=logging.INFO)


def hash_md5_for_file(path):
    """ This function reads a file and returns a
    generated md5 checksum """
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
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
    path_md5 = hash_md5_for_file(args.path)
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
    return


def parse_arguments(arguments):
    """ This function returns the parsed argument path """
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
