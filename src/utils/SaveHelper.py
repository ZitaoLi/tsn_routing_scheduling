from src import config
from src.utils.Singleton import SingletonDecorator
from os import path


@SingletonDecorator
class SaveHelper(object):
    project_path: str
    save_path: str

    def __init__(self):
        self.project_path = config.pro_dir
        self.save_path = config.OPTIMIZATION['results-root-path']
