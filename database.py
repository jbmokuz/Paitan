import sqlite3

DATABASE = "database.db"

def dbfun(fun):
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DATABASE)

        ret = fun(conn,*args, **kwargs)
        
        conn.commit()
        conn.close()

        return ret
        
    return wrapper


@dbfun
def initDB(conn):
    try:
        conn.execute('''CREATE TABLE USERS
             (ID INT PRIMARY KEY     NOT NULL,
             NICK           TEXT    NOT NULL);''')
    except:
        pass

@dbfun
def addUser(conn,id,nick):
    try:
        conn.execute(f"INSERT INTO USERS (ID,NICK) VALUES ({id}, '{nick}');")
    except sqlite3.IntegrityError:
        conn.execute(f"UPDATE USERS set NICK = '{nick}' where ID = {id}")

@dbfun
def getUser(conn,id):
    cursor = conn.execute(f"SELECT NICK from USERS WHERE ID is {id}")
    a = [i for i in cursor][0][0]
    return a
