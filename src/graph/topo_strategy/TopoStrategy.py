import abc
import networkx as nx


class TopoStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self) -> nx.Graph:
        pass
