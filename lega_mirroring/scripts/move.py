#!/usr/bin/env python3.4
import os
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
    """ 
    This function reads configuration variables from an external file
    and returns the configuration variables as a class object 
    
    :path_to_config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'end_storage': config.get('workspaces', 'end_storage'),
            'path_processing': config.get('workspaces', 'processing')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def move(file, md5, dest, pathp):
    """ 
    This function moves files from current directory to another directory
    atomically, and removes the original working files
    
    :file: file that will be moved
    :md5: associated md5-file that will be moved
    :dest: destination directory
    """
    try:
        basefile = file.replace(pathp, '')
        basemd5 = md5.replace(pathp, '')
        os.rename(file, os.path.join(dest, basefile))
        os.rename(md5, os.path.join(dest, basemd5))
        '''
        FILE REMOVAL DISABLED FOR PORIN TESTING
        
        # Remove up to two extensions
        basefile, extension = os.path.splitext(file)  # .bam.cip -> .bam or .bam -> ''
        basefile, extension = os.path.splitext(basefile)  # .bam -> '' or '' -> '' (precaution)
        try:
            os.remove(os.path.join(pathp, basefile))  # rm .bam
            os.remove(os.path.join(pathp, basefile + '.cip'))  # rm .bam.cip
        except:
            pass
        '''
    except:
        pass
    log_event(file, dest)
    return


def log_event(file, dest):
    """ 
    This function logs moving events 
    
    :file: file that was moved
    :dest: destination directory of file
    """
    logging.info(file + ' moved to ' + dest)
    return


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ 
    This function runs the script
    
    :arguments: contains parsed command line parameters
    """
    args = parse_arguments(arguments)
    conf = args.path_to_config
    config = get_conf(conf)
    move(args.file, args.md5, config.end_storage, config.path_processing)
    return


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :file: file.bam.cip.csc that will be moved final-archive
    :md5: file.bam.cip.csc.md5 that will be moved to final-archive
    """
    parser = argparse.ArgumentParser(description='Move file to'
                                     ' predetermined location set in'
                                     ' config.ini')
    parser.add_argument('file',
                        help='path to file to be moved')
    parser.add_argument('md5',
                        help='path to md5 to be moved')
    parser.add_argument('path_to_config',
                        help='path to configuration file.')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
