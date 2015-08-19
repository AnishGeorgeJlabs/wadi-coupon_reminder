import pymysql
import json
import os

def _get_conf():
    cdir = os.path.dirname(__file__)
    filename = os.path.join(cdir, 'sql_conf.json')
    with open(filename, 'r') as cfile:
        return json.loads(cfile.read())

_conf = _get_conf()


# ----------- Blocking methods ---------------- #
def _execute_query(query, connection):
    cursor = connection.cursor()
    cursor.execute(query)
    res = map(lambda k: list(k), list(cursor))
    cursor.close()
    return res

def _open_connection(conf, db):
    return pymysql.connect(user=conf['username'],
                           password=conf['password'],
                           database=db,
                           host=conf['host'])

def execute(con):
    """ Curried function to execute on connection -> database -> query """
    def execute_on_db(db):
        def execute_query(query):
            connection = _open_connection(_conf[con], db)
            return _execute_query(query, connection)
        return execute_query
    return execute_on_db

