# step 1 create .bam files
# step 2 hash md5 values for files and save them to .json file
# step 3 encrypt .bam files to .bam.cip, then remove .bam files

import time
import hashlib
import os
import argparse
import sys
import lega_mirroring.scripts.res
import lega_mirroring.scripts.md5
import random

'''
    # end-to-end test tool #
    
    This is a test tool that creates .bam.cip files
    and .json metadata files.
    
    Note: There is no configuration file, paths are
    hard coded.
    
    # step 1 create .bam files
    # step 2 hash md5 values for files and save them to .json file
    # step 3 encrypt .bam files to .bam.cip, then remove .bam files
'''


def step1(amount):
    start_time = time.time()
    for i in range(amount):
        f = open('/data/incoming/gridftp-endpoint/file' + str(i) + '.bam', 'w')
        for j in range(100000):  # increase range to create larger files
            f.write(str(i) + 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
            'Aenean gravida ligula id semper maximus. Etiam sagittis, augue eget accumsan '
            'posuere, tellus lectus ultrices mi, non dignissim nisl risus vel orci. Curabitur '
            'consequat lorem mauris, eu efficitur felis ultrices bibendum. Fusce nec ipsum tincidunt, '
            'varius diam in, venenatis odio. Vestibulum massa lectus, cursus vitae orci vitae, '
            'fringilla tincidunt augue. Vivamus vel massa porta, maximus mauris sit amet, luctus risus. '
            'Ut nulla nisi, finibus quis sapien id, viverra congue urna.')
            j += 1
        i += 1
    print('Step [2/4]: generate .bam files, runtime: ' + str(time.time()-start_time)[:6] + 's')
    return
    
    
def step2():
    start_time = time.time()
    path = '/data/incoming/gridftp-endpoint/'
    dirlist = os.listdir(path)
    try:
        while len(dirlist) > 0:
            nfiles = random.randint(3, 9)
            if nfiles > len(dirlist):
                nfiles = len(dirlist)
            egad = random.randint(100000,900000)
            egaf = random.randint(100000,900000)
            f = open('/data/incoming/metadata/EGAD0000' + str(egad) + '.json', 'w')
            f.write('\n[')
            for n in range(nfiles):
                file = dirlist.pop()
                file = os.path.join(path, file)
                filesize = os.path.getsize(file)
                hash_md5 = hashlib.md5()
                filemd5 = 'md5'
                if os.path.exists(file):
                    with open(file, 'rb') as fi:
                        for chunk in iter(lambda: fi.read(4096), b''):
                            hash_md5.update(chunk)
                        filemd5 = hash_md5.hexdigest()
                f.write(
                        '\n    {"fileId":"EGAF0000' + str(egaf) + '",'
                        '\n    "datasetId":"EGAD0000' + str(egad) + '",'
                        '\n    "fileName":"' + file + '",'
                        '\n    "fileSize":' + str(filesize) + ','
                        '\n    "fileMd5":"' + filemd5 + '",'
                        '\n    "fileStatus":"pending"}'
                        )
                if nfiles > 1 and n < (nfiles-1):
                    f.write(',')
                egaf += 1
            f.write('\n]')
            f.close()
    except:
        pass
    print('Step [3/4]: generate .json files (metadata), runtime: ' + str(time.time()-start_time)[:6] + 's')
    return
    
    
def step3():
    start_time = time.time()
    path = '/data/incoming/gridftp-endpoint/'
    for file in os.listdir(path):
        file = os.path.join(path, file)
        lega_mirroring.scripts.res.main(['encrypt', file, 'config.ini'])
        os.rename(file + '.cip.csc', file + '.cip')
        os.remove(file)
    print('Step [4/4]: encrypt .bam files to .bam.cip and remove .bam files, runtime: ' + str(time.time()-start_time)[:6] + 's')
    return
    
    
def emptyall():
    start_time = time.time()
    path_grid = '/data/incoming/gridftp-endpoint/'
    path_proc = '/data/incoming/processing/'
    path_arch = '/data/incoming/final-archive/'
    path_meta = '/data/incoming/metadata/'
    for file in os.listdir(path_grid):
            file = os.path.join(path_grid, file)
            os.remove(file)
    for file in os.listdir(path_proc):
            file = os.path.join(path_proc, file)
            os.remove(file)
    for file in os.listdir(path_arch):
            file = os.path.join(path_arch, file)
            os.remove(file)
    for file in os.listdir(path_meta):
            file = os.path.join(path_meta, file)
            os.remove(file)
    print('Step [1/4]: clean directories, runtime: ' + str(time.time()-start_time)[:6] + 's')
    return
    
    
def main(arguments=None):
    args = parse_arguments(arguments) 
    emptyall()
    step1(args.amount)
    step2()
    step3()
    print(str(args.amount) + ' test files created')
    return


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('amount', type=int, help='amount of test files')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)