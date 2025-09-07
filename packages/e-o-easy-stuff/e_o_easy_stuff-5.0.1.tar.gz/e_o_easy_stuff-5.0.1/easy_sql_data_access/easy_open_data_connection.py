from contextlib import contextmanager
import time

import pyodbc


@contextmanager
def easy_open_data_connection(constr: str, autocommit: bool = True, timeout=300):
    """Open a pyodbc connection with up to 5 retry attempts.

    Parameters:
        constr: ODBC connection string
        autocommit: Whether to autocommit
        timeout: Connection timeout in seconds applied after successful open
    Raises:
        pyodbc.Error: If all retry attempts fail
    """
    con = None
    # Retry up to 5 times
    last_exc = None
    for attempt in range(1, 6):
        try:
            con = pyodbc.connect(constr, autocommit=autocommit)
            con.timeout = timeout
            break
        except pyodbc.Error as e:  # Narrow to pyodbc errors
            last_exc = e
            if attempt == 5:
                raise
            # Simple incremental backoff (1s,2s,3s,4s) capped at 4 seconds before next attempt
            time.sleep(min(attempt, 4))
    try:
        yield con
    finally:
        if con:
            con.close()
