import mysql.connector, os, time, datetime, calendar, hashlib, sys, argparse

# Establish database connection
db = mysql.connector.connect (host="localhost",
                              user="root",
                              passwd="root",
                              db="elixir",
                              buffered=True)

# This function checks if file transmission has been completed
def checkFileTransmission(path):

    passes = 0
    p = False

    # Get file size in bits
    file_size = os.path.getsize(path)

    # Get last modified datetime as float
    file_age = os.path.getmtime(path)
    time_now = calendar.timegm(time.gmtime())

    # Check if file already exists in database
    cur = db.cursor()
    cur.execute('SELECT id, verified FROM files WHERE name="' + path + '";')
    result = cur.fetchall()

    if cur.rowcount>=1: # Records found: old file
        for row in result:
            if row[1] == 1:
                # File has already been verified, ignore this file and continue to the next file
                p = False
            else:
                # Old file -> request old details from database
                params = [row[0], path]
                cur.execute('SELECT * FROM files WHERE id=%s AND name=%s;', params)
                result = cur.fetchall()
                for row in result:
                    if file_size > int(row[2]):
                        # If current(new) file size is larger than old file size in database, update file size and age to database
                        params = [file_size, file_age, row[0]]
                        cur.execute('UPDATE files SET size=%s, age=%s, passes=0 WHERE id=%s;', params)
                        passes = 0
                    else:
                        # File size hasn't changed, check age
                        if time_now - file_age > 60:
                            # Enough time has passed since file was last updated -> increment passes
                            params = [row[4]+1, row[0]]
                            cur.execute('UPDATE files SET passes=%s WHERE id=%s;', params)
                            passes = row[4]+1
                            p = True
    else: # New file
        # New file -> add new entry to database
        params = [path, file_size, file_age]
        cur.execute('INSERT INTO files VALUES (NULL, %s, %s, %s, 0, 0);', params)
        p = True

    # Execute database changes
    db.commit()
    if p == True:
        print(time_now, '>', path, ' Current size: ', file_size, ' Last updated: ', file_age, ' Number of passes: ', passes)
    else:
        print(path, ' has already been verified: stopping checking process')
    
    passed = False
    if passes >= 3:
        passed = True
    else:
        passed = False
        
    return passed


# This function verifies file integrity by hashing a checksum from the file and comparing it to a given checksum
def verifyFileIntegrity(path, key):
    
    # Generate md5 hash for file contents
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()

    # Fetch md5 checksum from external file
    key_md5 = open(key, 'r')
    key_md5= key_md5.read()

    # Get id from database for updating 'verified' status
    cur = db.cursor()
    cur.execute('SELECT id FROM files WHERE name="' + path + '";')
    result = cur.fetchall()

    for row in result:
        # Compare md5 hashes
        if path_md5 == key_md5:
            # If file was successfully verified with md5 checksum, update it's 'verified' status
            # in database table to exclude it from future inspection iterations
            params = [1, row[0]]
            cur.execute('UPDATE files SET verified=%s WHERE id=%s;', params)
            db.commit()
            print(path, 'OK: Verified successfully')
        else:
            # If file failed to verify, keep 'verified' status as 0 in database table
            print('FILE ERROR with ', path, ': Transmitted file and md5checksum do not match')
    return path_md5 == key_md5 # Returns boolean value of comparison



'''*************************************************************'''
#                         cmd-executable                          #
'''*************************************************************'''

def main(arguments=None):
    path = parse_arguments(arguments).message
    
    # Take directory as input, and read all files in that directory
    # Push all files through the two functions checkFileTransmission() and verifyFileIntegrity()
    # Loop through the process at set time intervals, exclude verified files from the process
    while True:
        for filename in os.listdir(path):
            if filename.endswith('.txt'):
                time.sleep(1)
                if checkFileTransmission(filename):
                    key = filename + '.md5'
                    verifyFileIntegrity(filename, key)
        time.sleep(10)

    return

# This function enables the script to intake parameters
def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('message')
    return parser.parse_args(arguments)

if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)




'''
TODO. TODO. TODO, TODO, TODO, TODO, TODOOOOOOOO, DODODODOODOO.
http://img13.deviantart.net/c82b/i/2013/231/6/4/pink_panther_s_to_do_list_by_makssarts-d6iuvby.jpg


_ File size doesn't update for a long time, but code keeps incrementing passes
    - error/stopped column? or just select passes>=3 verified=0?
_ Testing
_ Verified variable?
_ Larger cache size for hash_md5?
    - 2^20 in pastesti example
_ Running conditions?
    - Check if directory contains files with verified=0 status?
        - Make a new function out of it? if(ver=0){if(cFT){vFI}}
    - Logged information?
'''
