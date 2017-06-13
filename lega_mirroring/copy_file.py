import shutil
import argparse
import sys
import logging

logging.basicConfig(filename='copy_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %I:%M:%S',
                    level=logging.INFO)


def copy(file, dest):
    """ Copies file 'file' to destination directory 'dest' """
    shutil.copy2(file, dest)
    log_event(file, dest)
    return


def log_event(file, dest):
    """ This function logs copying events """
    logging.info(file + ' copied to ' + dest)
    return


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script with given arguments (file and dest) """
    args = parse_arguments(arguments)
    copy(args.file, args.dest)
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
