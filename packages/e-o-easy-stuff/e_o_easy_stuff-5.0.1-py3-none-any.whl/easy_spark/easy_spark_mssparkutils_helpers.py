# TODO: Add import
from notebookutils import mssparkutils


class EasySparkMSSparkUtilsHelpers:
    def __init__(self):
        pass

    @staticmethod
    def create_directory(path: str):
        mssparkutils.fs.mkdirs(path)

    @staticmethod
    def delete(path: str):
        mssparkutils.fs.rm(path, True)

    @staticmethod
    def file_exists(path: str) -> bool:
        return mssparkutils.fs.exists(path)

    @staticmethod
    def move_file(source_path: str, destination_path: str):
        mssparkutils.fs.mv(source_path, destination_path)

    @staticmethod
    def get_files_in_directory(path: str) -> list:
        return mssparkutils.fs.ls(path)
