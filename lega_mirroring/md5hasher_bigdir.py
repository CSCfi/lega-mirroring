import hashlib, os, sys
import argparse


# This function generates  an md5 hash for a given file and saves it to a text file
def md5(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
        path = path + '.md5'
        file = open(path, 'w')
        file.write(hash_md5.hexdigest())
        file.close()
    print(path, ' created')
    return hash_md5.hexdigest()


def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('path')

    return parser.parse_args()


def main(arguments=None):
    args = parse_arguments(arguments)

    for filename in os.listdir(args.path):
        if filename.endswith('.txt'):
            md5(filename)

if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
