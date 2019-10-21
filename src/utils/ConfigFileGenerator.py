from enum import Enum
from typing import List

from src.utils import RoutesGenerator as rg
from lxml import html

etree = html.etree  # ???


class ConfigFileGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_routes_xml(route_immediate_entity: rg.RouteImmediateEntity):
        filteringDatabase: etree.Element = etree.Element('filteringDatabase')
        pass

    def generate_intermediate_routes(self):
        pass
