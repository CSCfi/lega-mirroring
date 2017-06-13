#!/usr/bin/env python
import requests
import sys
import argparse
import logging

# Use these parameters for testing
#file_path = '/data/NA12878.mapped.ILLUMINA.bwa.CEU.high_coverage_pcr_free.20130906.bam.cip'
#host_url = 'http://86.50.169.120:9090/file/'
logging.basicConfig(filename='decrypt_log.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%d-%m-%Y %I:%M:%S',
                    level=logging.INFO)


def decrypt(host_url, file_path):
    """ This function returns a stream of decrypted data """
    params = {'filePath': file_path,
              'sourceFormat': 'aes128',
              'sourceKey': 'aeskey',
              'destinationFormat': 'plain'}
    r = requests.get(host_url, params, stream=True)
    log_event(r, host_url, file_path)
    return r


def write_to_file(feed):
    """ This function handles a stream of data and writes
    it to file """
    with open('decrypted_file.txt', 'wb+') as f:
        for chunk in feed.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return

    
def log_event(event, host, path):
    """ This function logs successes and failures to file """
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
    """ This function runs the script with given arguments (host and path) """
    args = parse_arguments(arguments)
    write_to_file(decrypt(args.host, args.path))
    return


def parse_arguments(arguments):
    """ This function returns the parsed arguments host and path
    host : url to RES microservice
    path : path to crypted file (to be decrypted) """
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('path')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
