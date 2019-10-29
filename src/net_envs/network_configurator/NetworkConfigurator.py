# design model: Visitor Model
# use to configure network elements
import abc


# network-configurator, base class
class NetworkConfigurator(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def configure(self, obj: object):
        pass
