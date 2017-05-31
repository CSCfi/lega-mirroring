import mysql.connector

db = mysql.connector.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="elixir",
                             buffered=True)

cur = db.cursor()


def haku_1(path):
    cur.execute('SELECT * FROM files WHERE name="' + path + '";')
    return cur.fetchall()

def haku_2(path):
    cur.execute('SELECT * FROM files WHERE name=%s', path)
    return cur.fetchall()

def haku_3(path):
    cur.execute('SELECT * FROM files WHERE name=%s', [path])
    return cur.fetchall()
