import requests
import sys
import argparse
import logging
import datetime

# Use these parameters for testing
#file_path = '/data/NA12878.mapped.ILLUMINA.bwa.CEU.high_coverage_pcr_free.20130906.bam.cip'
#host_url = 'http://86.50.169.120:9090/file/'
logging.basicConfig(filename='decrypt_log.log', level=logging.INFO)


def decrypt(host_url, file_path):
    """ This function decrypts file type file.bam.cip
    and saves the decrypted file to file.txt """
    params = {'filePath': file_path,
              'sourceFormat': 'aes128',
              'sourceKey': 'aeskey',
              'destinationFormat': 'plain'}
    r = requests.get(host_url, params, stream=True)
    if r:
        with open('decrypted_file.txt', 'wb+') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logging.info(str(datetime.datetime.now()) +
                 ' http-request: ' + host_url +
                 ' path: ' + file_path)
    else:
        logging.info(str(datetime.datetime.now()) +
                 ' ERROR: Check that url and path are correct -'
                 ' http-request: ' + host_url +
                 ' path: ' + file_path)
    return


'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''


def main(arguments=None):
    """ This function runs the script with given arguments (host and path) """
    args = parse_arguments(arguments)
    decrypt(args.host, args.path)
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
