#!/usr/bin/env python3.4
import requests
import sys
import argparse
import logging
from configparser import ConfigParser
from collections import namedtuple

logging.basicConfig(filename='res_log.log',
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
    conf = {'chunk_size': config.getint('func_conf', 'chunk_size'),
            'res_url': config.get('func_conf', 'res_url')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named


def decrypt(host_url, file_path):
    """ 
    This function sends an HTTP request to an active
    RES microservice and returns a stream of decrypted data 
    
    :host_url: address of RES microservice
    :file_path: full path to .cip file to be decrypted
    """
    params = {'filePath': file_path,
              'sourceFormat': 'aes128',
              'sourceKey': 'aeskey',
              'destinationFormat': 'plain'}
    r = requests.get(host_url, params, stream=True)
    if not r:
        raise Exception('decryption failed')
    log_event(r, host_url, file_path)
    return r


def encrypt(host_url, file_path):
    """ 
    This function sends an HTTP request to an active
    RES microservice and returns a stream of encrypted data 
    
    :host_url: address of RES microservice
    :file_path: full path to .bam file to be encrypted
    """
    params = {'filePath': file_path,
              'destinationFormat': 'aes128',
              'destinationKey': 'aeskey'}
    r = requests.get(host_url, params, stream=True)
    if not r:
        raise Exception('encryption failed')
    log_event(r, host_url, file_path)
    return r


def write_to_file(crypt, feed, chnk, path):
    """ 
    This function handles a stream of data and writes
    it to file. The function determines the file extension
    by itself according to the given method (main parameter)
    
    :crypt: operating method given in main
    :feed: stream of decrypted/encrypted data
    :chnk: size of data read from stream and written to file
    :path: full path to destination file
    """
    if crypt == 'decrypt':
        if path.endswith('.cip'):
            newpath = path.replace('.cip', '')
        elif path.endswith('.gpg'):
            newpath = path.replace('.gpg', '')
        with open(newpath, 'wb+') as f:
            for chunk in feed.iter_content(chunk_size=chnk):
                if chunk:
                    f.write(chunk)
    elif crypt == 'encrypt':
        newpath = path.replace('.bam', '.bam.cip.csc')
        with open(newpath, 'wb+') as f:
            for chunk in feed.iter_content(chunk_size=chnk):
                if chunk:
                    f.write(chunk)
    else:
        raise Exception('invalid var(crypt) for write_to_file()')
    return


def log_event(event, host, path):
    """ 
    This function logs successes and failures to file 
    
    :event: pass or failed
    :host: address of RES microservice
    :path: full path to original file (before crypt-operations)
    """
    if event:
        logging.info(' OK: http-request: ' + host +
                     ' path: ' + path)
    else:
        logging.info(' ERROR: Check that url and path are correct -'
                     ' http-request: ' + host +
                     ' path: ' + path)
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
    method = args.method
    path = args.path
    conf = args.config
    config = get_conf(conf)
    if method == 'decrypt':
        ext = ['.cip', '.gpg']  # allowed extensions
        if path.endswith(tuple(ext)):
            write_to_file(method, decrypt(config.res_url, path), config.chunk_size, path)
        elif path.endswith('.bam'):
            print('Can\'t decrypt .bam file, already plain text. Step skipped.')
    elif method == 'encrypt':
        write_to_file(method, encrypt(config.res_url, path), config.chunk_size, path)
    else:
        raise Exception('invalid method, must be \'encrypt\' or \'decrypt\'')
    return


def parse_arguments(arguments):
    """ 
    This function parses command line inputs and returns them for main()
    
    :method: parameter that determines the operation of the script
             either encrypt or decrypt, can not be left empty
    :path: path to file to be worked on 
    :path_to_config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    parser = argparse.ArgumentParser(description='Utilizes RES Microservice'
                                     ' to decrypt or encrypt files.')
    parser.add_argument('method',
                        help='encrypt or decrypt')
    parser.add_argument('path',
                        help='path to file to be worked on')
    parser.add_argument('config',
                        help='location of config.ini')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
