#!/usr/bin/env python3.4

import os

'''
    # simple test tool #
    
    This script is a simple test tool to quickly check
    file count in working directories.
    Note: There is no configuration file, the paths
    are hard coded.
'''

def fc():
    grid = len(os.listdir('/data/incoming/gridftp-endpoint/'))
    pro = len(os.listdir('/data/incoming/processing/'))
    arc = len(os.listdir('/data/incoming/final-archive/'))
    meta = len(os.listdir('/data/incoming/metadata/'))
    print('gridftp-endpoint: ' + str(grid) + ' files')
    print('processing: ' + str(pro) + ' files')
    print('final-archive: ' + str(arc) + ' files')
    print('metadata: ' + str(meta) + ' files')
    return

fc()
