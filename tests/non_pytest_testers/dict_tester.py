import mysql.connector

db = mysql.connector.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="elixir",
                             buffered=True)

cur = db.cursor()


def db_get_file_details(path):
    """ This function queries the database for details
    and returns a list of results or false """
    status = False
    cur.execute('SELECT * '
                'FROM files '
                'WHERE name="' + path + '";')
    result = cur.fetchall()
    if cur.rowcount >= 1:
        for row in result:
            # See other/db_script.txt for table structure
            status = {'id': row[0],
                      'name': path,
                      'size': int(row[2]),
                      'age': float(row[3]),
                      'passes': row[4],
                      'verified': row[5]}
    else:
        status = False
    return status
