from contextlib import contextmanager

import pyodbc


@contextmanager
def easy_open_data_connection(constr: str, autocommit: bool = True, timeout=300):
    con = None
    try:
        con = pyodbc.connect(constr, autocommit=autocommit)
        con.timeout = timeout
        yield con
    finally:
        if con:
            con.close()
