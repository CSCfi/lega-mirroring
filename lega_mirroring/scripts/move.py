#!/usr/bin/env python
import shutil
import argparse
import sys
import logging
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='move_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)


def get_conf(path_to_config):
    """ This function reads configuration variables from an external file
    and returns the configuration variables as a class object """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'end_storage': config.getint('workspaces', 'end_storage')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def move(file, dest):
    """ Moves file 'file' to destination directory 'dest'
    Operation is atomic within the same disk partition """
    shutil.move(file, dest)
    log_event(file, dest)
    return


def log_event(file, dest):
    """ This function logs moving events """
    logging.info(file + ' moved to ' + dest)
    return


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function moves given file to end storage location """
    args = parse_arguments(arguments)
    conf = args.path_to_config
    config = get_conf(conf)
    move(args.file, config.end_storage)
    return


def parse_arguments(arguments):
    """ This function returns the parsed arguments
    file(which is a file) and dest(which is a directory) """
    parser = argparse.ArgumentParser(description='Move file to'
                                     ' predetermined location set in'
                                     ' config.ini')
    parser.add_argument('file',
                        help='path to file to be moved')
    parser.add_argument('path_to_config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
