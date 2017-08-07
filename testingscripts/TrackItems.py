import os
import argparse
import sys

''' lega end-to-end test tool '''

def write_gridftp():
    contents = os.listdir('/data/incoming/gridftp-endpoint/')
    f = open('contents_gridftp.txt', 'w')
    for item in contents:
        f.write('%s\n' % item)
    f.close()
    return


def write_archive():
    contents = os.listdir('/data/incoming/final-archive/')
    f = open('contents_archive.txt', 'w')
    for item in contents:
        item = item.replace('.csc', '')
        f.write('%s\n' % item)
    f.close()
    return


def compare():
    fgrid = open('contents_gridftp.txt', 'r')
    contents_grid = fgrid.readlines()
    fgrid.close()
    farc = open('contents_archive.txt', 'r')
    contents_arc = farc.readlines()
    farc.close()
    missing_items = set(contents_grid) - set(contents_arc)
    f = open('missing_items.txt', 'w')
    for item in missing_items:
        f.write('%s' % item)
    f.close()
    return


def main(arguments=None):
    args = parse_arguments(arguments) 
    if args.cmd == 'start':
        write_gridftp()
    elif args.cmd == 'end':
        write_archive()
    elif args.cmd == 'compare':
        compare()
    else:
        print('invalid command')
    return


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('cmd', help='must be start, end or compare')
    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)