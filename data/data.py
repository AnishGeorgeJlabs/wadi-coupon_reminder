import pymysql
import json
import os
from . import sql_conf

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
            connection = _open_connection(sql_conf[con], db)
            return _execute_query(query, connection)
        return execute_query
    return execute_on_db

def execute_fn_dabba(db):
    return execute("dabba")(db)

execute_on_referaly = execute("referaly")("referaly")

