import abc

from src.net_elem.NetworkDevice import NetworkDevice


class NetworkDeviceFactory(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def product(self):
        network_device: NetworkDevice = NetworkDevice()
        pass
