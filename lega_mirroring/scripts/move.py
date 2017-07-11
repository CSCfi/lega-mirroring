#!/usr/bin/env python
import shutil
import argparse
import sys
import logging

logging.basicConfig(filename='move_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)


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
    """ This function runs the script with given arguments (file and dest) """
    args = parse_arguments(arguments)
    move(args.file, args.dest)
    return


def parse_arguments(arguments):
    """ This function returns the parsed arguments
    file(which is a file) and dest(which is a directory) """
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('dest')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
