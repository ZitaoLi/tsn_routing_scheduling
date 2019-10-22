from typing import Dict, List

from pycparser.c_ast import Switch

import src.utils.MacAddressGenerator as MAG
from src.utils.Singleton import SingletonDecorator


@SingletonDecorator
class SwitchController(object):
    switch_list: List[Switch]

    def __init__(self):
        self.switch_list = []

    def add_switch(self, switch: Switch):
        self.switch_list.append(switch)

    @staticmethod
    def set_all_filtering_database():
        pass
