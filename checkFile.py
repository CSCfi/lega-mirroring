import mysql.connector, os, time, datetime, calendar, hashlib

# Establish database connection
db = mysql.connector.connect (host="localhost",
                              user="root",
                              passwd="root",
                              db="elixir",
                              buffered=True)

passes = 0
# This function checks if file transmission has been completed
def checkFileTransmission(path):

    global passes

    # Get file size in bits
    file_size = os.path.getsize(path)

    # Get last modified datetime as float
    file_age = os.path.getmtime(path)
    time_now = calendar.timegm(time.gmtime())

    # Check if file already exists in database
    cur = db.cursor()
    cur.execute('SELECT id FROM files WHERE name="' + path + '";')
    result = cur.fetchall()
    
    if cur.rowcount>=1:
        # Old file -> request old details from database
        cur.execute('SELECT * FROM files WHERE name="' + path + '";')
        result = cur.fetchall()
        for row in result:
            if file_size > int(row[2]):
                # If current(new) file size is larger than old file size in database, update file size and age to database
                params = [file_size, file_age, row[0]]
                cur.execute('UPDATE files SET size=%s, age=%s, passes=0 WHERE id=%s;', params)
                passes = 0
            else:
                # If file size hasn't changed, check if file has been untouched for a set amount of time (short time in testing)
                if time_now - file_age > 60:
                    params = [row[4]+1, row[0]]
                    cur.execute('UPDATE files SET passes=%s WHERE id=%s;', params)
                    passes = row[4]+1
    else:
        # New file -> add new entry to database
        params = [path, file_size, file_age]
        cur.execute('INSERT INTO files VALUES (NULL, %s, %s, %s, 0);', params)

    # Execute database changes and print state of process (for testing purposes)
    db.commit()
    print(time_now, '> Current size: ', file_size, ' Last updated: ', file_age, ' Number of passes: ', passes)

    # As long as file keeps updating, re-run the program
    while (passes < 3):
        print("jee")
        time.sleep(10)
        checkFileTransmission(path)
    else:
        print("wuu")
        # After file transmission is complete, compare md5 checksums
        key = path + '.md5'
        verifyFileIntegrity(path, key)
    
    return


# This function verifies file integrity by hashing a checksum from the file and comparing it to a given checksum
def verifyFileIntegrity(path, key):

    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        path_md5 = hash_md5.hexdigest()
        
    key_md5 = open(key, 'r')
    key_md5= key_md5.read()
    
    if path_md5 == key_md5:
        print('File verified successfully')
        return True
    else:
        print('ERROR: Transmitted file and md5checksum do not match')
        return False
    return






'''

while else rakenne tulee lopulta main metodiin, jotta skripti voidaan ajaa suoraan komentotulkista parametrina tiedosto/hakemisto

'''








    
