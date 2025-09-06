from easy_sql_data_access.easy_open_data_connection import easy_open_data_connection
from easy_sql_data_access.easy_sql_data_connection_builder import EasySQLDataConnectionBuilder


class EasySQLConnectionFactory:
    def __init__(self, constr: str, autocommit: bool = True, timeout=300):
        self.constr = constr
        self.autocommit = autocommit
        self.timeout = timeout

    @staticmethod
    def create_from_builder(builder: EasySQLDataConnectionBuilder, autocommit: bool = True, timeout=300):
        return EasySQLConnectionFactory(builder.constr, autocommit, timeout)

    def open(self, autocommit: bool = None, timeout=300) -> easy_open_data_connection:
        if autocommit is None:
            autocommit = self.autocommit
        if timeout is None:
            timeout = self.timeout
        return easy_open_data_connection(self.constr, autocommit, timeout)
