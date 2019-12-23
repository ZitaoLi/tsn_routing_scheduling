# design model: Visitor Model
# use to configure network elements
import abc


# network-configurator, base class
class NetworkConfigurator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def configure(self, obj: object):
        pass
