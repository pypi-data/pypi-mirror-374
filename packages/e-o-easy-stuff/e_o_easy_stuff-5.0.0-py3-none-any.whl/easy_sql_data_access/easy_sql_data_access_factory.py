from easy_sql_data_access.easy_sql_data_connection_builder import EasySQLDataConnectionBuilder
from easy_sql_data_access.easy_sql_manage_data_access import EasySQLManageDataAccess


class EasySQLDataAccessFactory:
    def __init__(self, constr: str, autocommit: bool = True, timeout=300):
        self.constr = constr
        self.autocommit = autocommit
        self.timeout = timeout

    @staticmethod
    def create_from_builder(builder: EasySQLDataConnectionBuilder, autocommit: bool = True, timeout=300):
        return EasySQLDataAccessFactory(builder.constr, autocommit, timeout)

    def open(self, autocommit: bool = None, timeout=300) -> EasySQLManageDataAccess:
        if autocommit is None:
            autocommit = self.autocommit
        if timeout is None:
            timeout = self.timeout
        return EasySQLManageDataAccess(self.constr, autocommit, timeout)
